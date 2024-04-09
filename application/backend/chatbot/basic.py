import json
import uuid
import os
import asyncio
from typing import List, Optional
from operator import itemgetter
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.schema import StrOutputParser, Document, format_document

from application.backend.datastore.db import ChatbotVectorDatabase
from application.backend.chatbot.history import PostgresChatMessageHistory
from application.backend.chatbot.prompts import (
    CONDENSE_QUESTION_PROMPT,
    ANSWER_PROMPT,
    DEFAULT_DOCUMENT_PROMPT,
)
from application.backend.chatbot.utils import (
    parse_and_filter_question,
    get_qa_pairs,
    get_feedback_trigger,
)

load_dotenv(find_dotenv())

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__57d4de111e7247f5b3559f13e8650ea8"
os.environ["LANGCHAIN_PROJECT"] = "MGTChatbot"

openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

llm = AzureChatOpenAI(
    openai_api_version="2023-05-15",
    deployment_name="ChatbotMGT",
    azure_endpoint=azure_endpoint,
    openai_api_key=openai_api_key,
)

#llm = ChatOpenAI()


print(llm.invoke("Hello World!"))
