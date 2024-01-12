import logging
import os
import requests
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from langchain.document_loaders import AzureBlobStorageContainerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = func.FunctionApp()

# Environment variables and constants
FASTAPI_ENDPOINT = os.getenv("FASTAPI_INDEX_DOCUMENTS_ENDPOINT")
BLOB_CONN_STRING = os.getenv("BLOB_CONN_STRING")
CONTAINER_NAME = os.getenv("BLOB_CONTAINER")
CHUNK_SIZE = 250
CHUNK_OVERLAP = 20

# Blob service client initialization
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)


@app.function_name(name="myblobtrigger")
@app.event_grid_trigger(arg_name="event")
def eventGridTest(event: func.EventGridEvent):
    ...


# Check if FASTAPI_ENDPOINT is set
if not FASTAPI_ENDPOINT:
    raise ValueError(
        "FASTAPI_INDEX_DOCUMENTS_ENDPOINT environment variable is not set."
    )
