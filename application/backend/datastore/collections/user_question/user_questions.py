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

    def keep_only_since(self, seconds: float = 30 * 24 * 60 * 60):
        """
        Clears all records of any question being asked before the given number of seconds ago.
        Questions which were asked at least once since then will remain in the collection, while others will be removed.
        """
        since = time.time() - seconds
        for question in self.get_all_questions():
            question.hit_times = [time for time in question.hit_times if time > since]
            if question.hit_times:
                self.collection.data.update(uuid=question.uuid, properties=question.as_properties())
            else:
                self.collection.data.delete_by_id(question.uuid)

    def add_question(self, content: str, difference_threshold: float = 0.1):
        """
        Add a question to the collection.
        This queries the current questions in the collection to see if there is a similar question already present.
        If there exists a question with less than certain difference in content, we consider it the same question and
        update the hit times. Otherwise, we add a new question to the collection.

        :param content: The content of the question that was asked.
        :param difference_threshold: The difference threshold past which we consider a question different to those
        already in the collection. Defaults to 0.1.
        """
        result = self.collection.query.near_text(
            query=content,
            limit=1,
            return_metadata=wvc.query.MetadataQuery(distance=True)
        )
        closest = result.objects[0] if result.objects else None
        # If there is no closest question or the distance is greater than the threshold, add a new question
        if closest is None or closest.metadata.distance > difference_threshold:
            self.collection.data.insert(Question(content=content, hit_times=[time.time()]).as_properties())
        else:
            # Otherwise, we already have a similar question in the collection, so update the hit times
            closest.properties[Question.HIT_TIMES].append(time.time())
            self.collection.data.update(uuid=closest.uuid, properties=closest.properties)

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

    def get_all_questions_since(self, seconds: float = 30 * 24 * 60 * 60) -> list[Question]:
        """
        Get all the questions in the collection that have been asked in the last `since` seconds,
        ordered by most frequently asked.
        :param seconds: The number of seconds to search backwards from. Defaults to 30 * 24 * 60 * 60 seconds (30 days).
        """
        since = time.time() - seconds
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
