import hashlib
import os
from enum import Enum

from O365.sharepoint import SharepointListItem
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from application.backend.datastore.main_data.main_schema import Chunk


class SyncStatus(str, Enum):
    NOT_YET_SYNCED = "Not Yet Synced"
    SYNCED = "Synced"
    COULD_NOT_SYNC = "Could Not Sync"
    MARKED_FOR_RESYNC = "Marked For Resync"


class SharepointDocument:

    FACULTY = "Faculty"
    TARGET_GROUPS = "TargetGroup"
    TOPIC = "Topic"
    SUBTOPIC = "Subtopic"
    TITLE = "Title"
    DEGREE_PROGRAMS = "DegreePrograms"
    LANGUAGES = "Language"
    SYNC_STATUS = "SyncStatus"

    """
    Represents a document in SharePoint which has been downloaded onto the local file system.
    Contains the file path and the SharePoint item.
    Offers methods to hash the document, create chunks, and update the sync status in SharePoint.
    """
    file_path: str
    item: SharepointListItem
    _hash: str | None = None

    def __init__(self, file_path: str, item):
        self.file_path = file_path
        self.item = item
        # Since not all documents have all fields, we need to handle the case where a field is missing
        # We also want to ensure that all multi-value fields are distinct and sorted for hashing consistency
        item.fields[SharepointDocument.FACULTY] = self.item.fields.get(SharepointDocument.FACULTY, None)
        item.fields[SharepointDocument.TARGET_GROUPS] = sorted(set(self.item.fields.get(SharepointDocument.TARGET_GROUPS, [])))
        item.fields[SharepointDocument.TOPIC] = self.item.fields.get(SharepointDocument.TOPIC, None)
        item.fields[SharepointDocument.SUBTOPIC] = self.item.fields.get(SharepointDocument.SUBTOPIC, None)
        item.fields[SharepointDocument.TITLE] = self.item.fields.get(SharepointDocument.TITLE, None)
        item.fields[SharepointDocument.DEGREE_PROGRAMS] = sorted(set(self.item.fields.get(SharepointDocument.DEGREE_PROGRAMS, [])))
        item.fields[SharepointDocument.LANGUAGES] = sorted(set(self.item.fields.get(SharepointDocument.LANGUAGES, [])))
        item.fields[SharepointDocument.SYNC_STATUS] = self.item.fields.get(SharepointDocument.SYNC_STATUS, None)

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
        sha1 = hashlib.sha1()
        with open(self.file_path, "rb") as file:
            sha1.update(file.read())
        for field in [SharepointDocument.FACULTY, SharepointDocument.TARGET_GROUPS, SharepointDocument.TOPIC,
                      SharepointDocument.SUBTOPIC, SharepointDocument.TITLE, SharepointDocument.DEGREE_PROGRAMS,
                      SharepointDocument.LANGUAGES]:
            if self.item.fields[field]:  # Skip None or empty values
                sha1.update(str(self.item.fields[field]).encode("utf-8"))
        sha1.update(self.item.web_url.encode("utf-8"))
        return sha1.hexdigest()

    def chunk(self) -> list[Chunk]:
        """
        Use Unstructured to turn a SharepointDocument into chunks, which can then be batch imported into Weaviate.
        Use different splitting strategies based on the document type:
        - For PDFs: Load the document as a single large chunk and then use RecursiveCharacterTextSplitter.
        - For other types: Use UnstructuredFileLoader with mode="elements".
        """

        if self.file_path.endswith(".pdf"):
            return self._chunk_pdf()

        splitter = UnstructuredFileLoader(
            file_path=self.file_path,
            mode="elements",
            strategy="fast"
        )
        chunks = [
            Chunk(
                text=chunk.page_content,  # The text content of the chunk
                faculty=self.item.fields[SharepointDocument.FACULTY],
                target_groups=self.item.fields[SharepointDocument.TARGET_GROUPS],
                topic=self.item.fields[SharepointDocument.TOPIC],
                subtopic=self.item.fields[SharepointDocument.SUBTOPIC],
                title=self.item.fields[SharepointDocument.TITLE],
                degree_programs=self.item.fields[SharepointDocument.DEGREE_PROGRAMS],
                languages=self.item.fields[SharepointDocument.LANGUAGES],
                hash=self.hash,  # Every chunk from the same document will have the same hash
                url=self.item.web_url,
                hits=0,
            )
            for chunk in splitter.load()
        ]
        return chunks

    def _chunk_pdf(self) -> list[Chunk]:
        """
        Chunk a PDF document using RecursiveCharacterTextSplitter.
        This is a special case because PDFs are not chunked satisfactorily by UnstructuredFileLoader.
        :return: The chunks of the document
        """
        splitter = UnstructuredFileLoader(
            file_path=self.file_path,
            strategy="fast"
        )
        doc = splitter.load()[0]  # Should only be one document
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=20,
        )
        chunks = [
            Chunk(
                text=split_text,  # The text content of the chunk
                faculty=self.item.fields[SharepointDocument.FACULTY],
                target_groups=self.item.fields[SharepointDocument.TARGET_GROUPS],
                topic=self.item.fields[SharepointDocument.TOPIC],
                subtopic=self.item.fields[SharepointDocument.SUBTOPIC],
                title=self.item.fields[SharepointDocument.TITLE],
                degree_programs=self.item.fields[SharepointDocument.DEGREE_PROGRAMS],
                languages=self.item.fields[SharepointDocument.LANGUAGES],
                hash=self.hash,  # Every chunk from the same document will have the same hash
                url=self.item.web_url,
                hits=0,
            )
            for split_text in text_splitter.split(doc.page_content)
        ]
        return chunks

    def should_reembed(self) -> bool:
        """
        Whether the document is marked for resynchronization.
        """
        status = self.item.fields[SharepointDocument.SYNC_STATUS]
        return status in [SyncStatus.MARKED_FOR_RESYNC, SyncStatus.COULD_NOT_SYNC]

    def update_sync_status(self, success: bool):
        """
        Update the sync status of the document in SharePoint.
        :param success: Whether the document was successfully synced
        """
        current_status = self.item.fields[SharepointDocument.SYNC_STATUS]
        new_status = SyncStatus.SYNCED if success else SyncStatus.COULD_NOT_SYNC
        if current_status == new_status:
            return
        self.item.update_fields({SharepointDocument.SYNC_STATUS: new_status})
        self.item.save_updates()

    def delete_local_file(self):
        """
        Delete the file from the local file system.
        """
        os.remove(self.file_path)
