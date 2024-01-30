import logging
import os
from operator import itemgetter
from application.backend.chatbot import Chatbot
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


load_dotenv(find_dotenv())

bot = Chatbot()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: str


class Conversation(BaseModel):
    conversation: list[Message]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test")
async def test():
    return {"test": "works"}


@app.post("/conversation")
async def ask_question(question: str, conversation: Conversation) -> dict:
    answer = bot.chat({"question": question, "chat_history": conversation.conversation})
    return {"answer": answer}
