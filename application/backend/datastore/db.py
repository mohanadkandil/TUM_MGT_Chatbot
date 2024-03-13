import os

import weaviate
from dotenv import find_dotenv, load_dotenv

from application.backend.datastore.collections.main.collection import MainDataCollection
from application.backend.datastore.collections.user_question.collection import UserQuestionCollection

load_dotenv(find_dotenv())

class ChatbotVectorDatabase:
    """
    This class is responsible for managing the vector database of the chatbot, and should be used as a singleton.
    This class provides access to the main chatbot data under the `main` attribute.
    """

    def __init__(self):
        """
        Initialize the vector database.
        This method expects the following environment variables to be set:

        - WCS_URL: The URL of the Weaviate instance
        - WEAVIATE_API_KEY: The API key for the Weaviate instance
        - OPENAI_API_KEY: The API key for the OpenAI API
        """
        url = os.getenv("WCS_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        assert url, "WEAVIATE_URL environment variable must be set"
        assert weaviate_api_key, "WEAVIATE_API_KEY environment variable must be set"
        assert azure_openai_api_key, "AZURE_OPENAI_API_KEY environment variable must be set"

        self.client = weaviate.connect_to_wcs(
            cluster_url=url,
            auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key),
            headers={"X-Azure-Api-Key": azure_openai_api_key},
        )
        self.main = MainDataCollection(self.client)
        self.questions = UserQuestionCollection(self.client)

    def __del__(self):
        # Close the connection to Weaviate when the object is deleted
        self.client.close()
