import os
import weaviate
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.weaviate import Weaviate
from application.backend.datastore.ingest import load_onedrive_diff


# TODO: Further refine what metadata to store
# Unstructured provides quite a lot of metadata that we could add here
# Some of this metadata we will need to generate with AI
FILEPATH = "filepath"
FILE_DIRECTORY = "file_directory"
LANGUAGE = "language"
DEGREE_PROGRAM = "degree_program"
TOPIC = "topic"


class ChatbotVectorDatabase:
    """
    This class is responsible for managing the vector database of the chatbot.
    This class uses the LangChain Weaviate wrapper to interact with the Weaviate instance,
    and is intended to be used as a singleton.
    The intention is to have an abstraction layer over the following operations:

    - Synchronize the database with the latest documents in OneDrive
    - Retrieve the most similar documents to a given query

    The class should additionally ensure that the schema exists upon initialization.
    """

    def __init__(self):
        """
        Initialize the vector database.
        This method expects the following environment variables to be set:

        - WEAVIATE_URL: The URL of the Weaviate instance
        - WEAVIATE_API_KEY: The API key for the Weaviate instance
        - OPENAI_API_KEY: The API key for the OpenAI API

        Since this class is intended to be used as a singleton,
        the environment variables should be set upon application startup.
        """
        url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        assert url, "WEAVIATE_URL environment variable must be set"
        assert weaviate_api_key, "WEAVIATE_API_KEY environment variable must be set"
        assert openai_api_key, "OPENAI_API_KEY environment variable must be set"

        client = weaviate.Client(url, weaviate_api_key)
        index_name = "tum-mgt-chatbot"  # Do we have a predefined index name to use instead?
        text_key = "text"  # The name of the key that contains the text in the documents
        embedding = OpenAIEmbeddings(model="text-embedding-3-large")
        self.wrapper = Weaviate(
            client,
            index_name,
            text_key,
            embedding=embedding,
            attributes=[FILEPATH, FILE_DIRECTORY, LANGUAGE, DEGREE_PROGRAM, TOPIC],
            by_text=False  # Set this to False because we want queries to be vectorized during search
        )
        self.load_schema()  # TODO: Call this here, or in the application startup?

    def load_schema(self, file_path="weaviate_schema.json"):
        """
        Create the schema for the database if it does not exist.
        This method should be called when the application starts.
        """
        with open(file_path, "r") as file:
            schema = file.read()

        # TODO: Research better way to check if schema exists, update if necessary
        # See: /weaviate/schema/crud_schema.py
        if self.wrapper._client.schema.contains(schema):
            print("Schema already exists.")
            return

        print("Deleting existing schema...")
        self.wrapper._client.schema.delete_all()
        print("Creating schema...")
        self.wrapper._client.schema.create(schema)
        print("Schema was created.")

    def sync_with_onedrive(self):
        """
        Synchronize the database with the latest documents in OneDrive.
        This method should be called periodically to ensure that the database is up-to-date.
        """
        # TODO: Enter OneDrive drive_id and folder_path
        ids_to_remove, docs_to_add = load_onedrive_diff("drive_id", "folder_path")
        # TODO: Integrate relational database to store hashes of files
        self.wrapper.delete(ids_to_remove)  # Delete documents that are no longer in OneDrive
        self.wrapper.add_documents(docs_to_add)  # Add new documents to the vector database

    def search(
            self,
            query: str,
            k: int = 5,
            language: str | None = None,
            degree_program: str | None = None,
            topic: str | None = None,
    ) -> list[Document]:
        """
        Retrieve the most similar documents to the given query.
        :param query: The query to search for
        :param k: The number of documents to retrieve
        :param language: Filter the documents by language
        :param degree_program: Filter the documents by degree program
        :param topic: Filter the documents by topic
        :return: A list of documents
        """
        filters = None
        if language or degree_program or topic:
            filters = {
                'operator': 'And',
                'operands': []
            }
            if language:
                filters['operands'].append({
                    'path': [LANGUAGE],
                    'operator': 'Equal',
                    'valueString': language
                })
            if degree_program:
                filters['operands'].append({
                    'path': [DEGREE_PROGRAM],
                    'operator': 'Equal',
                    'valueString': degree_program
                })
            if topic:
                filters['operands'].append({
                    'path': [TOPIC],
                    'operator': 'Equal',
                    'valueString': topic
                })
        # I think this causes all metadata to be returned for each document
        # TODO: Check if this is necessary
        additional = [FILEPATH, FILE_DIRECTORY, LANGUAGE, DEGREE_PROGRAM, TOPIC]
        return self.wrapper.similarity_search(query, k=k, where_filter=filters, additional=additional)
