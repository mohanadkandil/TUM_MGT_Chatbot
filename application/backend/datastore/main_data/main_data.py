import time
import sys

import weaviate.classes as wvc

import application.backend.datastore.main_data.main_schema as main_schema
from application.backend.datastore.main_data.main_schema import (
    LocalDocument,
    Chunk,
)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class MainData:
    """
    This class is responsible for managing the main data of the chatbot.

    - Synchronize the database with a source of truth
    - Retrieve the most similar documents to a given query with optional filters
    """

    def __init__(self, db):
        self.db = db
        self.collection = main_schema.init_schema(db.client)

    def clear(self):
        """
        Delete the entire collection from Weaviate.
        """
        print("Clearing the entire main data collection from Weaviate...")
        main_schema.recreate_schema(self.db.client)

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

    def _remove_by_hashes(self, hashes: set[str]):
        """
        Remove documents from Weaviate by their hashes.
        :param hashes: The hashes of the documents to remove
        """
        print(f"{len(hashes)} documents are no longer in the source of truth and will be removed from Weaviate...")
        result = self.collection.data.delete_many(
            where=wvc.query.Filter.by_property(Chunk.HASH).contains_any(
                list(hashes)
            )
        )
        print(f"Successfully removed {result.successful} documents, {result.failed} failed.")

    def synchronize(self, documents: list[LocalDocument]) -> (list[LocalDocument], list[LocalDocument]):
        """
        Synchronize the database with the provided LocalDocuments as the source of truth.
        This will add new documents to the database that are not already in it,
        and remove documents from the database that are no longer in the provided documents.
        Provided documents that are already in the database will not be re-added.
        This is done by comparing the hashes of the documents.
        This method should be called periodically to ensure that the database is up-to-date.
        :param documents: The source of truth
        :return: A tuple of two lists: the first list contains the documents that were successfully added/updated,
        the second list contains the documents that failed to be added/updated
        """
        start = time.time()
        # Fetch the current hashes from Weaviate
        db_hashes = self._fetch_distinct_hashes()
        print(f"Found {len(db_hashes)} documents in vector database, comparing with source of truth...")
        truth_docs_by_hash = {doc.hash: doc for doc in documents}
        unchanged_hashes = db_hashes & truth_docs_by_hash.keys()
        print(f"{len(unchanged_hashes)} documents have not changed since the last sync and will not be re-added.")

        # Remove documents that are no longer in the source of truth
        hashes_to_remove = db_hashes - unchanged_hashes
        if hashes_to_remove:
            self._remove_by_hashes(hashes_to_remove)

        # Add new documents from the source of truth
        new_hashes = truth_docs_by_hash.keys() - db_hashes
        new_documents = [truth_docs_by_hash[hash] for hash in new_hashes]
        print(f"{len(new_documents)} documents are new/updated and will be imported into the vector database.")
        synced = [truth_docs_by_hash[hash] for hash in unchanged_hashes]
        failures = []
        for i, document in enumerate(new_documents):
            progress = f"({i + 1}/{len(new_documents)})"
            print(f"{progress} Chunking document '{document.file_path}'... ", end="\r")
            try:
                chunk_start = time.time()
                chunks = document.chunk()
                chunk_end = time.time()
                synced.append(document)
            except Exception as e:
                print(f"Error while chunking {document.file_path}: {e}")
                eprint(f"Stack trace: {e.__traceback__}")
                failures.append(document)
                continue
            print(f"{progress} Chunked document '{document.file_path}' (done in {chunk_end - chunk_start:.2f}s).")
            print(f"Uploading {len(chunks)} chunks...", end="\r")
            upload_start = time.time()
            with self.collection.batch.dynamic() as batch:
                for document_chunk in chunks:
                    batch.add_object(properties=document_chunk.as_properties())
            upload_end = time.time()
            print(f"Uploaded {len(chunks)} chunks (done in {upload_end - upload_start:.2f}s).")
        end = time.time()
        print(f"Successfully synchronized {len(synced)} documents, {len(new_documents) - len(failures)} new, "
              f"{len(failures)} failed (done in {end - start:.2f}s).")
        return synced, failures

    def search(
        self,
        query: str,
        k: int = 3,
        degree_programs: set[str] = None,
        language: str = None,
    ) -> list[Chunk]:
        """
        Retrieve the most similar documents to the given query with optional filtering.
        This performs a hybrid search in Weaviate.
        TODO: Experiment with different search strategies and parameters
        :param query: The query to search for
        :param k: The number of documents to retrieve
        :param degree_programs: Only fetch documents that are about at least one of these degree programs.
        General documents will always be included. An empty set will only fetch general documents.
        :param language: Only fetch documents that are (at least partially) in this language.
        """
        # By default only fetch general documents
        filter = wvc.query.Filter.by_property(Chunk.DEGREE_PROGRAMS).equal([])
        if degree_programs:
            # Fetch general data and data about the specified degree programs
            filter = filter | wvc.query.Filter.by_property(
                Chunk.DEGREE_PROGRAMS
            ).contains_any(list(degree_programs))
        if language:
            filter = filter & wvc.query.Filter.by_property(Chunk.LANGUAGES).contains_any([language])
        result = self.collection.query.hybrid(
            query=query,
            limit=k,
            filters=filter,
            alpha=0.5,  # alpha=1.0 is pure vector search, alpha=0.0 is pure text search. 0.5 is equal weight
        )  # TODO: Also fetch object IDs to increment the hits
        # Convert from Weaviate objects to Chunks
        relevant_chunks = [
            Chunk(
                text=obj.properties[Chunk.TEXT],
                faculty=obj.properties[Chunk.FACULTY],
                target_groups=obj.properties[Chunk.TARGET_GROUPS],
                topic=obj.properties[Chunk.TOPIC],
                subtopic=obj.properties[Chunk.SUBTOPIC],
                title=obj.properties[Chunk.TITLE],
                degree_programs=set(obj.properties[Chunk.DEGREE_PROGRAMS]),
                languages=obj.properties[Chunk.LANGUAGES],
                hash=obj.properties[Chunk.HASH],
                url=obj.properties[Chunk.URL],
                hits=obj.properties[Chunk.HITS],
            ) for obj in result.objects
        ]
        return relevant_chunks
