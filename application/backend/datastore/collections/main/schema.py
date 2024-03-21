import os
from typing import Any

import weaviate.classes as wvc
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
    target_groups: list[str]
    topic: str | None
    subtopic: str | None
    title: str | None
    degree_programs: list[str]
    languages: list[str]
    hash: str | None
    url: str | None
    hits: int
    uuid: Any  # This is a Weaviate UUID, will only be set in a query result

    def __init__(
        self,
        text: str,
        faculty: str | None,
        target_groups: list[str],
        topic: str | None,
        subtopic: str | None,
        title: str | None,
        degree_programs: list[str],
        languages: list[str],
        hash: str | None = None,
        url: str | None = None,
        hits: int = 0,
        uuid=None,
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
        self.uuid = uuid

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
            Chunk.DEGREE_PROGRAMS: self.degree_programs,
            Chunk.LANGUAGES: self.languages,
            Chunk.HASH: self.hash,
            Chunk.URL: self.url,
            Chunk.HITS: self.hits,
        }


def recreate_schema(client: WeaviateClient) -> Collection:
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)
    return init_schema(client)


def init_schema(client: WeaviateClient) -> Collection:
    if client.collections.exists(COLLECTION_NAME):
        return client.collections.get(COLLECTION_NAME)

    resource_name = os.getenv("AZURE_OPENAI_RESOURCE_NAME")
    deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
    assert resource_name, "AZURE_OPENAI_RESOURCE_NAME environment variable must be set"
    assert deployment_id, "AZURE_OPENAI_DEPLOYMENT_NAME environment variable must be set"
    assert base_url, "AZURE_OPENAI_ENDPOINT environment variable must be set"

    return client.collections.create(
        name=COLLECTION_NAME,
        # By specifying a vectorizer, weaviate will automatically vectorize the text content of the chunks
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_azure_openai(
            resource_name=resource_name,
            deployment_id=deployment_id,
            base_url=base_url,
            vectorize_collection_name=False,
        ),
        # HNSW is preferred over FLAT for large amounts of data, which is the case here
        vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
            distance_metric=wvc.config.VectorDistances.COSINE  # select preferred distance metric
        ),
        inverted_index_config=wvc.config.Configure.inverted_index(
            index_property_length=True
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
