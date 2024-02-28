import hashlib
from typing import Any
import os

import weaviate.classes as wvc
from langchain_community.document_loaders import UnstructuredFileLoader
from weaviate import WeaviateClient
from weaviate.collections import Collection

COLLECTION_NAME = "ChatbotData"


class Chunk:
    """
    Represents a chunk of a document as stored in Weaviate.
    This is the entity class for the main data Weaviate collection.
    """

    TEXT = "text"
    FACULTY = "faculty"
    TARGET_GROUPS = "target_groups"
    TOPIC = "topic"
    SUBTOPIC = "subtopic"
    TITLE = "title"
    DEGREE_PROGRAMS = "degree_programs"
    LANGUAGES = "languages"
    HASH = "hash"
    URL = "url"
    HITS = "hits"

    text: str
    faculty: str | None
    target_groups: set[str]
    topic: str | None
    subtopic: str | None
    title: str | None
    degree_programs: set[str]
    languages: set[str]
    hash: str | None
    url: str | None
    hits: int

    def __init__(
        self,
        text: str,
        faculty: str | None,
        target_groups: set[str],
        topic: str | None,
        subtopic: str | None,
        title: str | None,
        degree_programs: set[str],
        languages: set[str],
        hash: str | None = None,
        url: str | None = None,
        hits: int = 0,
    ):
        self.text = text
        self.faculty = faculty
        self.target_groups = target_groups
        self.topic = topic
        self.subtopic = subtopic
        self.title = title
        self.degree_programs = degree_programs
        self.languages = languages
        self.hash = hash
        self.url = url
        self.hits = hits

    def as_properties(self) -> dict[str, Any]:
        """
        Convert the chunk to a dictionary of properties.
        :return: The properties of the chunk as a dictionary
        """
        return {
            Chunk.TEXT: self.text,
            Chunk.FACULTY: self.faculty,
            Chunk.TARGET_GROUPS: self.target_groups,
            Chunk.TOPIC: self.topic,
            Chunk.SUBTOPIC: self.subtopic,
            Chunk.TITLE: self.title,
            Chunk.DEGREE_PROGRAMS: list(self.degree_programs),
            Chunk.LANGUAGES: list(self.languages),
            Chunk.HASH: self.hash,
            Chunk.URL: self.url,
            Chunk.HITS: self.hits,
        }


class LocalDocument:
    """
    Represents a document that has not been chunked yet.
    This is more of a conceptual class than a practical one, as it shares all the same properties as a Chunk.
    """
    file_path: str
    item: Any
    faculty: str | None
    target_groups: set[str]
    topic: str | None
    subtopic: str | None
    title: str | None
    degree_programs: set[str]
    languages: set[str]
    url: str | None
    _hash: str | None

    def __init__(self, file_path: str, item):
        self.file_path = file_path
        self.item = item
        self.faculty = item.fields.get("Faculty", None)
        self.target_groups = set(item.fields.get("TargetGroups", []))
        self.topic = item.fields.get("Topic", None)
        self.subtopic = item.fields.get("Subtopic", None)
        self.title = item.fields.get("Title", None)
        self.degree_programs = set(item.fields.get("DegreePrograms", []))
        self.languages = set(item.fields.get("Language", []))
        self.url = item.web_url
        self._hash = None  # The hash is computed lazily

    @property
    def hash(self) -> str:
        """
        The hash of the document.
        """
        if self._hash is None:
            self._hash = self._compute_hash()
        return self._hash

    def _compute_hash(self):
        """
        Compute the hash of the document using the raw bytes from the file and the properties from SharePoint.
        This hash is used to correlate chunks in Weaviate with their owning documents.
        """
        with open(self.file_path, "rb") as file:
            content_bytes = file.read()

        sha1 = hashlib.sha1()
        sha1.update(content_bytes)
        if self.faculty:
            sha1.update(self.faculty.encode("utf-8"))
        sha1.update(str(sorted(self.target_groups)).encode("utf-8"))
        if self.topic:
            sha1.update(self.topic.encode("utf-8"))
        if self.subtopic:
            sha1.update(self.subtopic.encode("utf-8"))
        if self.title:
            sha1.update(self.title.encode("utf-8"))
        sha1.update(str(sorted(self.degree_programs)).encode("utf-8"))
        sha1.update(str(sorted(self.languages)).encode("utf-8"))
        if self.url:
            sha1.update(self.url.encode("utf-8"))

        return sha1.hexdigest()

    def chunk(self) -> list["Chunk"]:
        """
        Use Unstructured to turn a LocalDocument into chunks, which can then be batch imported into Weaviate.
        """
        splitter = UnstructuredFileLoader(
            file_path=self.file_path,
            mode="elements",
            strategy="fast"
        )
        chunks = [
            Chunk(
                text=chunk.page_content,  # The text content of the chunk
                faculty=self.faculty,
                target_groups=self.target_groups,
                topic=self.topic,
                subtopic=self.subtopic,
                title=self.title,
                degree_programs=self.degree_programs,
                languages=self.languages,
                hash=self.hash,  # Every chunk from the same document will have the same hash
                url=self.url,
                hits=0,
            )
            for chunk in splitter.load()
        ]
        return chunks

    def update_sync_status(self, status: bool | None):
        """
        Update the sync status of the document in SharePoint.
        :param status: Success or failure, or None to set it to "Not Yet Synced"
        """
        self.item.fields["SyncStatus"] = None
        if status is not None:
            self.item.update_fields({"SyncStatus": "Synced" if status else "Could Not Sync"})
        else:
            self.item.update_fields({"SyncStatus": "Not Yet Synced"})
        self.item.save_updates()

    def delete(self):
        """
        Delete the file from the local file system.
        """
        os.remove(self.file_path)


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
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
        # HNSW is preferred over FLAT for large amounts of data, which is the case here
        vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
            distance_metric=wvc.config.VectorDistances.COSINE  # select preferred distance metric
        ),
        # The properties are like the columns of a table in a relational database
        properties=[
            wvc.config.Property(
                name=Chunk.TEXT,
                description="The original text content of the chunk",
                data_type=wvc.config.DataType.TEXT,
                # This is the property that will be vectorized, we do not skip it here like the others
            ),
            wvc.config.Property(
                name=Chunk.FACULTY,
                description="The faculty of the owning document",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.TARGET_GROUPS,
                description="The target group(s) of the owning document",
                data_type=wvc.config.DataType.TEXT_ARRAY,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.TOPIC,
                description="The topic of the owning document",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.SUBTOPIC,
                description="The subtopic of the owning document",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.TITLE,
                description="The title of the owning document",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.LANGUAGES,
                description="The language(s) of the owning document",
                data_type=wvc.config.DataType.TEXT_ARRAY,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.DEGREE_PROGRAMS,
                description="The degree program(s) the owning document is associated with",
                data_type=wvc.config.DataType.TEXT_ARRAY,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.HASH,
                description="The hash of the owning document",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.URL,
                description="The URL of the owning document",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.HITS,
                description="The number of times the chunk has been retrieved",
                data_type=wvc.config.DataType.INT,
                skip_vectorization=True,
            ),
        ],
    )
