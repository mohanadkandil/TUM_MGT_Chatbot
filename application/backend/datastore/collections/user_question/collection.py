import weaviate
import weaviate.classes as wvc

import application.backend.datastore.collections.user_question.schema as user_question_schema


class UserQuestionCollection:
    """
    This class is responsible for tracking user questions in Weaviate.

    The questions are anonymized and summarized, and the collection keeps track of
    how often similar questions have been asked.
    """

    def __init__(self, client: weaviate.WeaviateClient):
        self.client = client
        self.collection = user_question_schema.init_schema(client)

    def clear(self):
        """
        Delete the entire collection from Weaviate.
        """
        print("Clearing the entire main data collection from Weaviate...")
        user_question_schema.recreate_schema(self.client)

    def add_question(self, content: str):
        """
        Add a question to the collection.

        :param content: The content of the question
        """
        result = self.collection.query.near_text(
            query=content,
            limit=1,
            return_metadata=wvc.query.MetadataQuery(distance=True)
        )
