import hashlib
from typing import Any, Type

import langchain_core.documents
import weaviate.classes as wvc
from langchain_community.document_loaders import UnstructuredFileLoader
from unstructured.cleaners.core import clean_extra_whitespace
from weaviate import WeaviateClient
from weaviate.collections import Collection

COLLECTION_NAME = "ChatbotData"


class Document:
    """
    Represents a document that has not been chunked yet.
    This is more of a conceptual class than a practical one, as it shares all the same properties as a Chunk.
    """
    # Property names
    TEXT = "text"
    FILEPATH = "filepath"
    LINKS = "links"
    LANGUAGE = "language"
    DEGREE_PROGRAMS = "degree_programs"
    TOPICS = "topics"
    HASH = "hash"

    def __init__(self,
                 text: str,
                 filepath: str,  # FIXME: Unused?
                 links: list[str],  # FIXME: Unused?
                 language: str,
                 degree_programs: list[str],
                 topics: list[str],
                 hash: str = None,
                 **kwargs  # Could come from Weaviate retrieval
                 ):
        self.text = text
        self.filepath = filepath
        self.links = links
        self.language = language
        self.degree_programs = degree_programs
        self.topics = topics
        self._hash = hash
        self.metadata = kwargs

    @property
    def hash(self):
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def compute_hash(self):
        sha1 = hashlib.sha1()
        sha1.update(self.text.encode("utf-8"))
        sha1.update(self.filepath.encode("utf-8"))
        sha1.update(str(self.links).encode("utf-8"))
        sha1.update(self.language.encode("utf-8"))
        sha1.update(str(self.degree_programs).encode("utf-8"))
        sha1.update(str(self.topics).encode("utf-8"))
        return sha1.hexdigest()

    def __getitem__(self, item):
        return getattr(self, item, None)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @classmethod
    def _merge_properties(cls: Type["Document"], first: "Document", priority: "Document") -> "Document":
        """
        Merge two Documents, with the properties of the first document taking priority.
        :param first: The document to merge into
        :param priority: The document whose properties override the first document
        :return: The merged document
        """
        return cls(**{**vars(first), **vars(priority)})

    @classmethod
    def from_langchain(cls, document: langchain_core.documents.Document) -> "Document":
        """
        Convert a langchain Document to a schema Document.
        This assumes that the text content of the document is in the "page_content" attribute,
        and that the rest of the properties are in the "metadata" attribute.
        Missing properties will be set to their default values.
        :param document: The langchain Document
        :return: The schema Document
        """
        return Document(
            text=document.page_content,
            filepath=document.metadata.get("filepath", ""),
            links=document.metadata.get("links", []),
            language=document.metadata.get("language", ""),
            degree_programs=document.metadata.get("degree_programs", []),
            topics=document.metadata.get("topics", []),
        )

    def chunk(self) -> list["Chunk"]:
        """
        Chunk a langchain Document into smaller pieces.
        This method should be called on a document before adding it to Weaviate.
        :return: The chunks with all the properties of the original document (and some chunk-specific overrides)
        """
        chunks = UnstructuredFileLoader(
            self.text,
            mode="elements",
            post_processors=[clean_extra_whitespace]
        ).load()
        # Convert from langchain Documents to Chunks (slight misnomer, but it's the same thing)
        chunks = [Chunk.from_langchain(chunk) for chunk in chunks]
        # Use the properties of the original document but override with the chunk-specific properties
        chunks = [Chunk._merge_properties(self, chunk) for chunk in chunks]
        return chunks


class Chunk(Document):
    """
    Class representing a chunk of a document as stored in Weaviate.
    """

    def chunk(self) -> list["Chunk"]:
        raise NotImplementedError("Chunks cannot be chunked further")  # FIXME: This violates Liskov substitution

    @classmethod
    def from_weaviate(cls, obj: Any) -> "Chunk":
        """
        Convert a Weaviate object to a Chunk.
        This expects that the Weaviate object has attributes "properties" and "metadata",
        and that the union of these two dictionaries contains all the properties of a Chunk.
        :param obj: The Weaviate object
        :return: The Chunk
        """
        return Chunk(**{**obj.properties, **obj.metadata})


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
                name=Chunk.FILEPATH,
                description="The path of the owning document in OneDrive",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.LINKS,
                description="The links in the chunk",
                data_type=wvc.config.DataType.TEXT_ARRAY,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.LANGUAGE,
                description="The language of the owning document",  # TODO: by-chunk language detection? Unstructured?
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.DEGREE_PROGRAMS,
                # Empty = general. TODO: Can a document be about multiple degree programs?
                description="The degree program(s) the owning document is associated with",
                data_type=wvc.config.DataType.TEXT_ARRAY,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.TOPICS,
                description="The topic(s) of the owning document",
                data_type=wvc.config.DataType.TEXT_ARRAY,
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name=Chunk.HASH,
                description="The hash of the owning document",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
            ),
        ]
    )
