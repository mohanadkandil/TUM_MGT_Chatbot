import time

import weaviate
import weaviate.classes as wvc

from application.backend.datastore.collections.user_question.schema import Question


class UserQuestionCollection:
    """
    This class is responsible for tracking user questions in Weaviate.

    The questions are anonymized and summarized, and the collection keeps track of
    how often similar questions have been asked.
    """

    def __init__(self, collection: weaviate.collections.Collection):
        self.collection = collection

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
        closest = result.objects[0] if result.objects else None
        if closest is None or closest.metadata.distance > 0.5:
            self.collection.data.insert(Question(content=content, hit_times=[time.time()]).as_properties())
        else:
            closest.properties[Question.HIT_TIMES].append(time.time())
            self.collection.data.update(closest)

    def get_all_questions(self) -> list[Question]:
        """
        Get all the questions in the collection,
        ordered by most frequently asked.
        """
        questions = []
        for obj in self.collection.iterator():
            questions.append(Question(
                content=obj.properties[Question.CONTENT],
                hit_times=obj.properties[Question.HIT_TIMES],
                uuid=obj.uuid
            ))
        return sorted(questions, key=lambda q: len(q.hit_times), reverse=True)

    def get_all_questions_since(self, since: float = 30 * 24 * 60 * 60) -> list[Question]:
        """
        Get all the questions in the collection that have been asked in the last `since` seconds,
        ordered by most frequently asked.
        :param since: The number of seconds to search backwards from. Defaults to 30 * 24 * 60 * 60 seconds (30 days).
        """
        questions = []
        for obj in self.collection.iterator():
            hit_times = obj.properties.get(Question.HIT_TIMES, [])
            hit_times = [time for time in hit_times if time > since]
            if hit_times:
                questions.append(Question(
                    content=obj.properties[Question.CONTENT],
                    hit_times=hit_times,
                    uuid=obj.uuid
                ))
        return sorted(questions, key=lambda q: len(q.hit_times), reverse=True)
