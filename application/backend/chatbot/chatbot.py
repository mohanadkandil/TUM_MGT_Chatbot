import json
import openai
import requests
from langchain_openai import ChatOpenAI


logger = logger.get_logger(__name__)


# Define Chatbot class (Decision-Making Module)
class Chatbot:
    def __init__(self):
        self.conversation_history = []

    def chat(self, question: str, chat_history: list[dict]) -> str:
        """
        Chat with the chatbot
        :param question: The question to ask the chatbot
        :param chat_history: The chat history
        :return: The chatbot's answer
        """

    # TODO: Add methods to implement and define behavior of chatbot
