import os
from functools import reduce

import weaviate
import weaviate.classes as wvc
from langchain_core.documents import Document

import properties
from application.backend.datastore.onedrive import load_onedrive_diff

# This is the name of the one (current) collection in the Weaviate instance
COLLECTION_NAME = "ChatbotData"


class ChatbotVectorDatabase:
    """
    This class is responsible for managing the vector database of the chatbot,
    and is intended to be used as a singleton.
    The intention is to have an abstraction layer over the following operations:

    - Synchronize the database with the latest documents in OneDrive
    - Retrieve the most similar documents to a given query with optional filters

    The class should additionally ensure that the schema exists in the Weaviate instance upon initialization.
    """

    def __init__(self):
        """
        Initialize the vector database.
        This method expects the following environment variables to be set:

        - WEAVIATE_URL: The URL of the Weaviate instance
        - WEAVIATE_API_KEY: The API key for the Weaviate instance
        - OPENAI_API_KEY: The API key for the OpenAI API
        """
        url = os.getenv("WEAVIATE_CLUSTER_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_deployment_id = os.getenv("AZURE_DEPLOYMENT_ID")
        assert url, "WEAVIATE_URL environment variable must be set"
        assert weaviate_api_key, "WEAVIATE_API_KEY environment variable must be set"
        assert openai_api_key, "OPENAI_API_KEY environment variable must be set"
        assert azure_deployment_id, "AZURE_DEPLOYMENT_ID environment variable must be set"

        self.client = weaviate.connect_to_wcs(
            cluster_url=url,
            auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key),
            headers={
                "X-Azure-Api-Key": openai_api_key,
                "deploymentId": azure_deployment_id
            }
        )
        self._init_schema()
        self.collection = self.client.collections.get(COLLECTION_NAME)

    def _init_schema(self):
        """
        Create the Weaviate schema if it does not exist.
        This method should be called upon initialization.
        """
        if self.client.collections.exists(COLLECTION_NAME):
            # The collection already exists
            # TODO: Add logic to update the schema if necessary
            return
        self.client.collections.create(
            name=COLLECTION_NAME,
            # By specifying a vectorizer, weaviate will automatically vectorize the text content of the chunks
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(model="text-embedding-3-large"),
            # HNSW is preferred over FLAT for large amounts of data, which is the case here
            vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
                distance_metric=wvc.config.VectorDistances.COSINE  # select preferred distance metric
            ),
            # The properties are like the columns of a table in a relational database
            properties=[
                wvc.config.Property(
                    name=properties.TEXT,
                    description="The original text content of the chunk",
                    data_type=wvc.config.DataType.TEXT,
                    # This is the property that will be vectorized, we do not skip it here like the others
                ),
                wvc.config.Property(
                    name=properties.FILEPATH,
                    description="The path of the owning document in OneDrive",
                    data_type=wvc.config.DataType.TEXT,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name=properties.HASH,
                    description="The hash of the owning document",
                    data_type=wvc.config.DataType.TEXT,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name=properties.LINKS,
                    description="The links in the chunk",
                    data_type=wvc.config.DataType.TEXT_ARRAY,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name=properties.LANGUAGE,
                    description="The language of the owning document",
                    data_type=wvc.config.DataType.TEXT,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name=properties.DEGREE_PROGRAM,
                    description="The degree program the owning document is associated with",
                    data_type=wvc.config.DataType.TEXT,
                    skip_vectorization=True,
                ),
                wvc.config.Property(
                    name=properties.TOPIC,
                    description="The topic of the owning document",
                    data_type=wvc.config.DataType.TEXT,
                    skip_vectorization=True,
                ),
            ]
        )

    def _fetch_distinct_hashes(self) -> set[str]:
        """
        Fetch distinct hashes from the vector database.
        TODO: Any possibility of performing a distinct fetch straight from Weaviate?
        :return: A set of distinct hashes
        """
        hashes = set()
        for entry in self.collection.iterator(return_properties=[properties.HASH]):
            hashes.add(entry.properties[properties.HASH])
        return hashes

    def sync_with_onedrive(self):
        """
        Synchronize the database with the latest documents in OneDrive.
        This method should be called periodically to ensure that the database is up-to-date.
        """
        current_hashes = self._fetch_distinct_hashes()  # Fetch the current hashes from Weaviate
        missing_hashes, docs_to_add = load_onedrive_diff(current_hashes)  # Load the diff from OneDrive

        # Remove documents that are no longer in OneDrive
        self.collection.data.delete_many(
            where=wvc.query.Filter.by_property(properties.HASH).contains_any(val=missing_hashes)
        )
        # Add new documents
        with self.collection.batch.dynamic() as batch:
            for entry in docs_to_add:
                batch.add_object(properties=entry)

    def search(
            self,
            query: str,
            limit: int = 5,
            filters: dict[str, str] = None
    ) -> list[Document]:
        """
        Retrieve the most similar documents to the given query with optional filters.
        This performs a hybrid search in Weaviate.
        TODO: Experiment with different search strategies and parameters
        :param query: The query to search for
        :param limit: The number of documents to retrieve
        :param filters: Additional filters to apply to the search in the form of a dictionary.
        The keys may only be properties from `properties.ALL` and the values are the values to filter by.
        :return: The most similar documents to the given query which satisfy the filters
        """
        if filters is not None:
            filters = [wvc.query.Filter.by_property(key).equal(val) for key, val in filters]
            filters = reduce(lambda a, b: a & b, filters)
        result = self.collection.query.hybrid(
            query=query,
            limit=limit,
            filters=filters,
            alpha=0.5,  # alpha=1.0 is pure vector search, alpha=0.0 is pure text search. 0.5 is equal weight
            return_metadata=wvc.query.MetadataQuery(score=True, explain_score=True),  # Return the score and explain it
        )
        docs = []
        for entry in result.objects:
            doc = Document(
                page_content=entry.properties.pop(properties.TEXT),  # Pop the text content
                metadata=entry.properties  # The rest of the properties are metadata
            )
            docs.append(doc)
        return docs

    def __del__(self):
        # Close the connection to Weaviate when the object is deleted
        self.client.close()
