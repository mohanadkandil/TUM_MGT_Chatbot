import logging
import os
from operator import itemgetter

from azure.storage.blob import BlobServiceClient
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.indexes import SQLRecordManager, index
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import Document, StrOutputParser, format_document
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from langchain.vectorstores.pgvector import PGVector
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Load environment variables
load_dotenv(find_dotenv())

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Connection strings and configurations
conn_str = os.getenv("BLOB_CONN_STRING")
container_name = os.getenv("BLOB_CONTAINER")
host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
COLLECTION_NAME = os.getenv("PGDATABASE")
CONNECTION_STRING = ...

namespace = ...
record_manager = SQLRecordManager(namespace, db_url=CONNECTION_STRING)
record_manager.create_schema()

embeddings = OpenAIEmbeddings()
vector_store = PGVector(...)
retriever = vector_store.as_retriever()


# Models
class Message(BaseModel):
    ...


class Conversation(BaseModel):
    ...


class DocumentIn(BaseModel):
    ...


# Helper functions
def _format_chat_history(conversation):
    ...


def _combine_documents(docs, document_prompt, document_separator):
    ...


# Language model instances and prompt templates
llm = ChatOpenAI(...)
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(...)
ANSWER_PROMPT = ChatPromptTemplate.from_template(...)
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(...)

# Runnable chain setup
_inputs = RunnableParallel(...)
_context = {...}
conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | llm | StrOutputParser()

# FastAPI instance and middleware
app = FastAPI()
app.add_middleware(...)


# API Endpoints
@app.get("/test")
async def test():
    ...


def get_row_count():
    ...


@app.get("/row_count")
async def row_count():
    ...


@app.post("/conversation")
async def ask_question(question, conversation):
    ...


@app.get("/listfiles")
async def list_files(page, page_size):
    ...


@app.delete("/deletefile/{filename}")
async def delete_file(filename):
    ...


@app.post("/uploadfiles")
async def upload_files(files):
    ...


@app.post("/index_documents/")
async def index_documents(documents_in):
    ...
