import hashlib
from typing import Any

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
    TARGET_GROUP = "target_group"
    TOPIC = "topic"
    SUBTOPIC = "subtopic"
    TITLE = "title"
    DEGREE_PROGRAMS = "degree_programs"
    LANGUAGE = "language"
    HASH = "hash"
    HITS = "hits"

    text: str
    faculty: str | None
    target_group: str | None
    topic: str | None
    subtopic: str | None
    title: str | None
    degree_programs: set[str]
    language: str | None
    hash: str | None
    hits: int

    def __init__(
        self,
        text: str,
        faculty: str | None,
        target_group: str | None,
        topic: str | None,
        subtopic: str | None,
        title: str | None,
        degree_programs: set[str],
        language: str | None,
        hash: str | None = None,
        hits: int = 0,
    ):
        self.text = text
        self.faculty = faculty
        self.target_group = target_group
        self.topic = topic
        self.subtopic = subtopic
        self.title = title
        self.degree_programs = degree_programs
        self.language = language
        self.hash = hash
        self.hits = hits

    @classmethod
    def from_properties(cls, properties: dict[str, Any]) -> "Chunk":
        """
        Create a Chunk from a dictionary of properties.
        :param properties: The properties of the chunk as a dictionary
        :return: The chunk
        """
        return cls(
            text=properties[Chunk.TEXT],
            faculty=properties[Chunk.FACULTY],
            target_group=properties[Chunk.TARGET_GROUP],
            topic=properties[Chunk.TOPIC],
            subtopic=properties[Chunk.SUBTOPIC],
            title=properties[Chunk.TITLE],
            degree_programs=set(properties[Chunk.DEGREE_PROGRAMS]),
            language=properties[Chunk.LANGUAGE],
            hash=properties[Chunk.HASH],
            hits=properties[Chunk.HITS],
        )

    def as_properties(self) -> dict[str, Any]:
        """
        Convert the chunk to a dictionary of properties.
        :return: The properties of the chunk as a dictionary
        """
        return {
            Chunk.TEXT: self.text,
            Chunk.FACULTY: self.faculty,
            Chunk.TARGET_GROUP: self.target_group,
            Chunk.TOPIC: self.topic,
            Chunk.SUBTOPIC: self.subtopic,
            Chunk.TITLE: self.title,
            Chunk.DEGREE_PROGRAMS: list(self.degree_programs),
            Chunk.LANGUAGE: self.language,
            Chunk.HASH: self.hash,
            Chunk.HITS: self.hits,
        }


class LocalDocument:
    """
    Represents a document that has not been chunked yet.
    This is more of a conceptual class than a practical one, as it shares all the same properties as a Chunk.
    """

    def __init__(
        self,
        file_path: str,
        faculty: str | None,
        target_group: str | None,
        topic: str | None,
        subtopic: str | None,
        title: str | None,
        degree_programs: set[str],
        language: str | None,
    ):
        self.file_path = file_path
        self.faculty = faculty
        self.target_group = target_group
        self.topic = topic
        self.subtopic = subtopic
        self.title = title
        self.degree_programs = degree_programs
        self.language = language
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
        sha1.update(self.faculty.encode("utf-8"))
        sha1.update(self.target_group.encode("utf-8"))
        sha1.update(self.topic.encode("utf-8"))
        sha1.update(self.subtopic.encode("utf-8"))
        sha1.update(self.title.encode("utf-8"))
        sha1.update(str(sorted(self.degree_programs)).encode("utf-8"))
        sha1.update(self.language.encode("utf-8"))

        return sha1.hexdigest()

    def chunk(self) -> list["Chunk"]:
        """
        Use Unstructured to turn a LocalDocument into chunks, which can then be batch imported into Weaviate.
        """
        chunks = UnstructuredFileLoader(
            file_path=self.file_path,
            mode="elements",
        ).load()
        # Convert from langchain Documents to Chunks (slight misnomer, but it's the same thing)
        chunks = [
            Chunk(
                text=chunk.page_content,  # The text content of the chunk
                faculty=self.faculty,
                target_group=self.target_group,
                topic=self.topic,
                subtopic=self.subtopic,
                title=self.title,
                degree_programs=self.degree_programs,
                language=self.language,
                hash=self.hash,  # Every chunk from the same document will have the same hash
                hits=0,
            )
            for chunk in chunks
        ]
        return chunks

    def __del__(self):
        """
        A LocalDocument is a temporary file and will delete itself when it is no longer needed.
        """
        import os

        os.remove(self.file_path)


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
                name=Chunk.TARGET_GROUP,
                description="The target group of the owning document",
                data_type=wvc.config.DataType.TEXT,
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
                name=Chunk.LANGUAGE,
                description="The language of the owning document",
                data_type=wvc.config.DataType.TEXT,
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
                name=Chunk.HITS,
                description="The number of times the chunk has been retrieved",
                data_type=wvc.config.DataType.INT,
                skip_vectorization=True,
            ),
        ],
    )
