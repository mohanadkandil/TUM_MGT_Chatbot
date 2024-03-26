import os
import time
import urllib.parse

from O365 import Account
from O365.drive import Folder, File
from dotenv import load_dotenv

from application.backend.datastore.db import ChatbotVectorDatabase
from application.backend.datastore.collections.main.main_data import elapsed
from application.backend.datastore.collections.main.sharepoint_document import SharepointDocument

load_dotenv()

DOWNLOAD_CHUNK_SIZE = 8 * 1024
DATA_FOLDER = "/Data_ChatBot"
TEMP_DIR = "sharepoint_temp"


def load_file_structure(folder: Folder, path: str) -> dict[str, File]:
    """
    Loads the file structure of a folder in SharePoint.

    :param folder: The folder to load the file structure from
    :param path: The path prefix for the files in the folder
    :return: A dictionary of file paths to files
    """
    files = {}
    for item in folder.get_items():
        item_path = f"{path}/{item.name}"
        if item.is_folder:
            files.update(load_file_structure(item, item_path))
        elif item.is_file:
            files[item_path] = item
    return files


def load_from_sharepoint() -> list[SharepointDocument]:
    """
    Loads documents from SharePoint including their column values, downloading them onto the local file system.

    Expects the following environment variables to be set:
    O365_CLIENT_ID: The client ID for the SharePoint API
    O365_CLIENT_SECRET: The client secret for the SharePoint API
    O365_DRIVE_ID: The ID of the SharePoint drive
    O365_FOLDER_PATH: The path of the folder in SharePoint

    :return: a list of SharepointDocuments
    """
    client_id = os.environ["O365_CLIENT_ID"]
    client_secret = os.environ["O365_CLIENT_SECRET"]
    drive_id = os.environ["O365_DRIVE_ID"]
    folder_path = os.environ["O365_FOLDER_PATH"]
    assert client_id, "O365_CLIENT_ID not set"
    assert client_secret, "O365_CLIENT_SECRET not set"
    assert drive_id, "O365_DRIVE_ID not set"
    assert folder_path, "O365_FOLDER_PATH not set"

    start = time.time()

    account = Account(
        (client_id, client_secret),
        auth_flow_type="credentials",
        tenant_id="5d7b49e9-50d2-40dc-bab1-14a2d903542c",
    )
    if account.authenticate():
        print("Authenticated with SharePoint")
    # First load the files with OneDrive, so we know what items we need to fetch from SharePoint
    root = account.storage().get_drive(drive_id).get_item_by_path(DATA_FOLDER)
    downloadable_files = load_file_structure(root, "")
    total_files = len(downloadable_files)

    local_documents = []
    print(f"Downloading {total_files} files from SharePoint...")
    # Load all list items (files and folders) from SharePoint with their column data
    sharepoint_items = (
        account.sharepoint()
        .get_site("tumde.sharepoint.com", "/sites/MGTChatbot")
        .get_list_by_name(folder_path)
        .get_items(expand_fields=[
            SharepointDocument.FACULTY,
            SharepointDocument.TARGET_GROUPS,
            SharepointDocument.TOPIC,
            SharepointDocument.SUBTOPIC,
            SharepointDocument.TITLE,
            SharepointDocument.DEGREE_PROGRAMS,
            SharepointDocument.LANGUAGES,
            SharepointDocument.SYNC_STATUS
        ])
    )
    downloaded = 0
    cached = 0
    for sharepoint_item in sharepoint_items:
        # Format the web_url to get rid of encoding (e.g. %20), then split by / and get the last part
        # If this is a file name we got from OneDrive, we can get its fields
        url = urllib.parse.unquote(sharepoint_item.web_url)
        index = url.find(DATA_FOLDER)  # Try to find the root folder
        if index == -1:  # Data root folder was not found, this path is not relevant
            continue
        file_path = url[index + len(DATA_FOLDER):]
        if file_path not in downloadable_files:  # This path is not one of the files we found in OneDrive to download
            continue
        file = downloadable_files.pop(file_path)
        download_path = f"{TEMP_DIR}{file_path}"  # Create a local path for the file (file_path has a leading /)
        progress = f"{total_files - len(downloadable_files)}/{total_files}"
        if os.path.isfile(download_path):
            print(f"({progress}) File {file_path} already exists, skipping download.")
            cached += 1
        else:
            download_folder = os.path.dirname(download_path)
            os.makedirs(download_folder, exist_ok=True)
            print(f"({progress}) Downloading {file_path}...", end="\r")
            download_start = time.time()
            file.download(to_path=download_folder, chunk_size=DOWNLOAD_CHUNK_SIZE)
            print(f"({progress}) Downloading {file_path}... (done in {elapsed(download_start)})")
            downloaded += 1
        local_documents.append(SharepointDocument(download_path, sharepoint_item))

    print(f"Downloaded {downloaded} files ({cached} cached) from SharePoint in {elapsed(start)}.")
    if downloadable_files:
        print(f"Warning: The following files were found in OneDrive, but not SharePoint (what does this mean?):"
              f"{downloadable_files.keys()}")
    return local_documents


if __name__ == "__main__":
    db = ChatbotVectorDatabase()
    documents = load_from_sharepoint()
    db.main.synchronize(documents)
    # print(db.main.count_documents())
    # db.main.clear()
    # db.main.increment_hits(docs)
    # print(hashes)
