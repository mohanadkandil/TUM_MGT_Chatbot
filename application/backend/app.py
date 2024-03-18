import logging
import os
from operator import itemgetter
from application.backend.chatbot.chatbot import Chatbot, Message, Conversation
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

load_dotenv(find_dotenv())

bot = Chatbot()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


origins = ["http://localhost:3000"]

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
async def ask_question(question: str, conversation: Conversation, study_program: str = "") -> dict:
    print(question)
    print(conversation)
    answer = bot.chat(question=question, conversation=conversation, study_program=study_program)

    return {"answer": answer}

@app.post("/chat_stream/")
async def chat_stream_endpoint(question: str, conversation: Conversation, study_program: str = ""):
    return StreamingResponse(
        bot.chat_stream(question=question, conversation=conversation, study_program=study_program),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    os.environ["APP_PATH"] = "../.."
    uvicorn.run(app, host="0.0.0.0", port=8000)
