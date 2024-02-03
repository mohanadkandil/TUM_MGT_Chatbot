from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import OneDriveLoader
from unstructured.cleaners.core import clean_extra_whitespace
from langchain.schema import Document
import os


def load_onedrive_diff(drive_id: str, folder_path: str) -> tuple[list[str], list[Document]]:
    """
    Loads the documents from OneDrive and returns them as a list of chunks to be embedded in Weaviate.
    In the future, this method should also return a list of IDs to remove from Weaviate (for now, empty list).
    :param drive_id: The ID of the OneDrive drive
    :param folder_path: The path of the folder in OneDrive
    :return: A tuple containing the list of IDs to remove and the list of documents to add
    """
    assert os.environ['O365_CLIENT_ID'], "O365_CLIENT_ID not set"
    assert os.environ['O365_CLIENT_SECRET'], "O365_CLIENT_SECRET not set"
    assert os.environ["OPENAI_API_KEY"], "OPENAI_API_KEY not set"

    loader = OneDriveLoader(drive_id=drive_id, folder_path=folder_path, auth_with_token=True)

    # Check how many docs + Check if loading works for pdf, word, ppt

    new_chunks = []

    for onedrive_doc in loader.lazy_load():

        # TODO: Add custom metadata to the documents here with AI
        # For example, degree program, topic, etc.

        # for now, we assume that every document is new and needs to be chunked and added to weaviate
        # TODO: Future work
        # We don't have to re-embed the entire document if it hasn't changed
        # We can check to see if we recognize the hash of the document like so:
        # Check relational db for hashes of files currently in weaviate
        # (maybe we can also just store the hash in weaviate as metadata!)
        # If hash exists in db, but not in the OneDrive docs: file must have been removed/modified -> delete from db
        # If hash from OneDrive is not in db: file must be new -> embed and add to weaviate
        # Maybe in the far future we could even update individual chunks by comparing their hashes
        metadata = onedrive_doc.metadata
        doc_loader = UnstructuredFileLoader(onedrive_doc.page_content, mode="elements", post_processors=[clean_extra_whitespace])
        chunked_docs = doc_loader.load()
        for chunk in chunked_docs:
            chunk.metadata.update(metadata)
        new_chunks.extend(chunked_docs)

    # For now, we return an empty list of IDs to remove and the new chunks to add
    return [], new_chunks
