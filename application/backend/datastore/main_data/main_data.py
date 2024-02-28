from typing import Iterable

import weaviate.classes as wvc

import application.backend.datastore.main_data.main_schema as main_schema
from application.backend.datastore.main_data.main_schema import (
    LocalDocument,
    Chunk,
)


class MainData:
    """
    This class is responsible for managing the main data of the chatbot.

    - Synchronize the database with a source of truth
    - Retrieve the most similar documents to a given query with optional filters
    """

    def __init__(self, db):
        self.db = db
        self.collection = main_schema.init_schema(db.client)

    def _fetch_distinct_hashes(self) -> set[str]:
        """
        Fetch the distinct hashes of documents in Weaviate.
        :return: The distinct hashes of the documents in Weaviate
        """
        hashes = set()
        result = self.collection.query.fetch_objects(return_properties=[Chunk.HASH])
        for obj in result.objects:
            hashes.add(obj.properties[Chunk.HASH])
        return hashes

    def synchronize(self, documents: Iterable[LocalDocument]):
        """
        Synchronize the database with the provided LocalDocuments as the source of truth.
        This will add new documents to the database that are not already in it,
        and remove documents from the database that are no longer in the provided documents.
        Provided documents that are already in the database will not be re-added.
        This is done by comparing the hashes of the documents.
        This method should be called periodically to ensure that the database is up-to-date.
        """
        remaining_db_hashes = (
            self._fetch_distinct_hashes()
        )  # Fetch the current hashes from Weaviate
        new_document_chunks = []
        for document in documents:
            if document.hash in remaining_db_hashes:
                # This document has not changed since the last sync
                # We should not re-embed it, nor remove it from the database
                # Remove the hash from the set of hashes to remove, and continue to the next document
                remaining_db_hashes.remove(document.hash)
                continue
            # At this point we know that the document is new/updated and needs to be chunked and added to Weaviate
            # Chunk the document and add it to the list of new chunks to import
            new_document_chunks.extend(document.chunk())

        # Remove documents that are no longer in the source of truth from Weaviate
        if remaining_db_hashes:
            self.collection.data.delete_many(
                where=wvc.query.Filter.by_property(Chunk.HASH).contains_any(
                    list(remaining_db_hashes)
                )
            )
        # Add new documents from the source of truth to Weaviate
        if new_document_chunks:
            with self.collection.batch.dynamic() as batch:
                for document_chunk in new_document_chunks:
                    batch.add_object(properties=document_chunk.as_properties())

    def search(
        self, query: str, k: int = 3, degree_programs: set[str] = None
    ) -> list[Chunk]:
        """
        Retrieve the most similar documents to the given query with optional filtering.
        This performs a hybrid search in Weaviate.
        TODO: Experiment with different search strategies and parameters
        :param query: The query to search for
        :param k: The number of documents to retrieve
        :param degree_programs: Only fetch documents that are about at least one of these degree programs.
        General documents will always be included. An empty set will only fetch general documents.
        """
        filter = wvc.query.Filter.by_property(Chunk.DEGREE_PROGRAMS).equal([])
        if degree_programs:
            filter = filter | wvc.query.Filter.by_property(
                Chunk.DEGREE_PROGRAMS
            ).contains_any(list(degree_programs))
        result = self.collection.query.hybrid(
            query=query,
            limit=k,
            filters=degree_programs,
            alpha=0.5,  # alpha=1.0 is pure vector search, alpha=0.0 is pure text search. 0.5 is equal weight
        )
        # Convert from Weaviate objects to Chunks
        relevant_chunks = [
            Chunk.from_properties(obj.properties) for obj in result.objects
        ]
        return relevant_chunks
