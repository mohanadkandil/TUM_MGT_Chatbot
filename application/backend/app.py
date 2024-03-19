import logging
import os
from operator import itemgetter
from application.backend.chatbot.chatbot import Chatbot, Message, Conversation
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel, Field
from uuid import UUID

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


# Define the request model for feedback
class Feedback(BaseModel):
    uuid: str = Field(
        ..., description="The unique identifier for the feedback session as a string"
    )
    feedback_classification: str = Field(
        ..., description="The classification of the feedback"
    )
    feedback_text: str = Field(..., description="The detailed feedback text")


@app.get("/test")
async def test():
    return {"test": "works"}


@app.post("/conversation")
async def ask_question(
    question: str, conversation: Conversation, study_program: str = ""
) -> dict:
    print(question)
    print(conversation)
    answer = bot.chat(
        question=question, conversation=conversation, study_program=study_program
    )

    return {"answer": answer}


@app.post("/chat_stream/")
async def chat_stream_endpoint(
    question: str, conversation: Conversation, study_program: str = ""
):
    return StreamingResponse(
        bot.chat_stream(
            question=question, conversation=conversation, study_program=study_program
        ),
        media_type="text/event-stream",
    )


@app.post("/feedback")
async def send_feedback(feedback: Feedback):
    # logging to write feedback to db.
    logger.info(f"Feedback received: {feedback}")
    return {"message": "Feedback received successfully"}


if __name__ == "__main__":
    os.environ["APP_PATH"] = "../.."
    uvicorn.run(app, host="0.0.0.0", port=8000)
