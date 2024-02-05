import hashlib
import os

from langchain.schema import Document
from langchain_community.document_loaders import OneDriveLoader
from langchain_community.document_loaders import UnstructuredFileLoader
from unstructured.cleaners.core import clean_extra_whitespace

import properties


def load_onedrive_diff(db_hashes: set[str]) -> tuple[list[str], list[Document]]:
    """
    Loads the documents from OneDrive and compares their hashes to the hashes of the documents currently in Weaviate.
    If a document is found in OneDrive that is not yet in Weaviate, it should be chunked and added to Weaviate.
    If a document is found in Weaviate that is no longer in OneDrive, it should be removed from Weaviate.

    This method expects the following environment variables to be set:
    - O365_CLIENT_ID: The client ID for the OneDrive API
    - O365_CLIENT_SECRET: The client secret for the OneDrive API
    - O365_DRIVE_ID: The ID of the OneDrive drive to load data from
    - O365_FOLDER_PATH: The path to the folder to load data from
    - OPENAI_API_KEY: The API key for the OpenAI API

    :param db_hashes: The set of hashes of the documents currently in Weaviate. The hashes of the documents
    from OneDrive are removed from this set as they are found, so that at the end of the method,
    it contains only the hashes of documents that are no longer in OneDrive and should be removed from Weaviate.

    :return: A tuple containing the list of missing hashes to remove and the list of documents chunks to add
    """
    assert os.environ['O365_CLIENT_ID'], "O365_CLIENT_ID not set"
    assert os.environ['O365_CLIENT_SECRET'], "O365_CLIENT_SECRET not set"
    assert os.environ["OPENAI_API_KEY"], "OPENAI_API_KEY not set"
    drive_id = os.environ["O365_DRIVE_ID"]
    folder_path = os.environ["O365_FOLDER_PATH"]
    assert drive_id, "O365_DRIVE_ID not set"
    assert folder_path, "O365_FOLDER_PATH not set"

    doc_loader = OneDriveLoader(drive_id=drive_id, folder_path=folder_path, auth_with_token=True)

    # TODO: Check how many docs + Check if loading works for pdf, word, ppt

    sha1 = hashlib.sha1()
    new_chunks = []

    for doc in doc_loader.lazy_load():
        file_content = doc.page_content

        sha1.update(file_content.encode("utf-8"))
        doc_hash = sha1.hexdigest()
        if doc_hash in db_hashes:
            # This document has not changed since the last sync
            # We should not re-embed it, nor remove it from the database
            # Remove the hash from the set of hashes to remove, and continue to the next document
            db_hashes.remove(doc_hash)
            continue

        # At this point we know that the document is new/updated and needs to be chunked and added to Weaviate
        chunked_docs = UnstructuredFileLoader(
            file_content,
            mode="elements",
            post_processors=[clean_extra_whitespace]
        ).load()

        document_metadata = {
            properties.FILEPATH: doc.metadata["source"] if "source" in doc.metadata else "",
            properties.HASH: doc_hash,
            # TODO: Add more document metadata to the chunks here
            # For example, degree program, topic, etc.
        }
        for chunk in chunked_docs:
            # Attach the document metadata to each chunk
            chunk.metadata.update(document_metadata)

        new_chunks.extend(chunked_docs)

    # db_hashes now contains the hashes of documents that are no longer in OneDrive
    # new_chunks contains the chunks of the new/updated documents
    return list(db_hashes), new_chunks
