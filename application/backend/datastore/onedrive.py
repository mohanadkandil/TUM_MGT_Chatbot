import os
from typing import Iterable

from langchain_community.document_loaders import OneDriveLoader
from langchain_core.documents import Document


def load_from_onedrive(drive_id: str, folder_path: str) -> Iterable[Document]:
    """
    Load documents from OneDrive.

    This method expects the following environment variables to be set:
    - O365_CLIENT_ID: The client ID for the OneDrive API
    - O365_CLIENT_SECRET: The client secret for the OneDrive API

    :param drive_id: The ID of the OneDrive drive
    :param folder_path: The path of the folder in OneDrive

    :return: A lazy-loaded iterable of documents from OneDrive
    """
    assert os.environ['O365_CLIENT_ID'], "O365_CLIENT_ID not set"
    assert os.environ['O365_CLIENT_SECRET'], "O365_CLIENT_SECRET not set"

    loader = OneDriveLoader(drive_id=drive_id, folder_path=folder_path, auth_with_token=True)

    return loader.lazy_load()

