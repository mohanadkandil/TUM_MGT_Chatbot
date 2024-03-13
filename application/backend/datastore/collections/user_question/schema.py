import os
from typing import Any

import weaviate.classes as wvc
from weaviate import WeaviateClient
from weaviate.collections import Collection

COLLECTION_NAME = "UserQuestion"


class Question:
    """
    Represents a chunk of a document as stored in Weaviate.
    This is the entity class for the main data Weaviate collection.
    """

    CONTENT = "content"  # summarized and anonymized content of the question
    HIT_TIMES = "hit_times"  # list of times the question was asked

    content: str
    hit_times: list[float]
    uuid: Any  # This is a Weaviate UUID, will only be set in a query result

    def __init__(
            self,
            content: str,
            hit_times: list[float] = None,
            uuid=None,
    ):
        self.content = content
        self.hits = hit_times if hit_times is not None else []
        self.uuid = uuid

    def as_properties(self) -> dict[str, Any]:
        """
        Convert the chunk to a dictionary of properties.
        :return: The properties of the chunk as a dictionary
        """
        return {
            Question.CONTENT: self.content,
            Question.HIT_TIMES: self.hit_times,
        }


def recreate_schema(client: WeaviateClient) -> Collection:
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)
    return init_schema(client)


def init_schema(client: WeaviateClient) -> Collection:
    if client.collections.exists(COLLECTION_NAME):
        return client.collections.get(COLLECTION_NAME)
    return client.collections.create(
        name=COLLECTION_NAME,
        # By specifying a vectorizer, weaviate will automatically vectorize the text content of the chunks
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_azure_openai(
            resource_name=os.getenv("AZURE_OPENAI_RESOURCE_NAME"),
            deployment_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
            vectorize_collection_name=False,
        ),
        # HNSW is preferred over FLAT for large amounts of data, which is the case here
        vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
            distance_metric=wvc.config.VectorDistances.COSINE  # select preferred distance metric
        ),
        inverted_index_config=wvc.config.Configure.inverted_index(
            index_property_length=True
        ),
        # The properties are like the columns of a table in a relational database
        properties=[
            wvc.config.Property(
                name=Question.CONTENT,
                description="Summarized and anonymized content of the user's question",
                data_type=wvc.config.DataType.TEXT
            ),
            wvc.config.Property(
                name=Question.HIT_TIMES,
                description="List of times the question was asked",
                data_type=wvc.config.DataType.NUMBER_ARRAY,
                skip_vectorization=True,
            ),
        ]
    )
