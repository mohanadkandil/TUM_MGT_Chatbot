import json
import requests
import logging
import uuid
import os
from operator import itemgetter
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.schema import StrOutputParser, Document, format_document
from dotenv import find_dotenv, load_dotenv
from application.backend.datastore.db import ChatbotVectorDatabase
from pydantic import BaseModel, Field
from langchain.schema import Document
from application.backend.chatbot.history import PostgresChatMessageHistory

load_dotenv(find_dotenv())

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__57d4de111e7247f5b3559f13e8650ea8"
os.environ["LANGCHAIN_PROJECT"] = "MGTChatbot"

openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

class Message(BaseModel):
    role: str
    content: str


class Conversation(BaseModel):
    conversation: list[Message]


# Define Chatbot class (Decision-Making Module)
class Chatbot:
    def __init__(self, session_id: str = str(uuid.uuid4())):
        self.conversation_history = Conversation(conversation=[])
        self.chatvec = ChatbotVectorDatabase()
        self.postgres_history = PostgresChatMessageHistory(session_id=session_id)

    def _format_chat_history(self, conversation: list) -> str:
        formatted_history = ""
        for message in conversation:
            formatted_history += f"{message.role}: {message.content}\n"
        return formatted_history.rstrip()

    def chat(self, question: str, conversation: Conversation) -> str:
        """
        Chat with the chatbot
        :param question: The question to ask the chatbot
        :param chat_history: The chat history
        :return: The chatbot's answer
        """

        llm = AzureChatOpenAI(
            openai_api_version="2023-05-15",
            deployment_name="ChatbotMGT",
            azure_endpoint=azure_endpoint,
            openai_api_key=openai_api_key,
        )

        condense_question_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
        Chat History:
        {chat_history}
        Follow Up Input: {question}
        Standalone question:"""
        CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
            condense_question_template
        )

        answer_template = """Answer the question based only on the following context:
        {context}

        If you don´t find the answer in the context, tell the user that you are happy to help with different questions about TUM.

        Question: {question}
        """
        ANSWER_PROMPT = ChatPromptTemplate.from_template(answer_template)

        DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(
            template="{page_content}"
        )

        def _combine_documents(
            docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
        ):
            doc_strings = [format_document(doc, document_prompt) for doc in docs]
            return document_separator.join(doc_strings)

        _inputs = RunnableParallel(
            standalone_question=RunnablePassthrough.assign(
                chat_history=lambda x: self._format_chat_history(x["chat_history"])
            )
            | CONDENSE_QUESTION_PROMPT
            | llm
            | StrOutputParser(),
        )

        _context = {
            "context": lambda x: " ".join(
                [
                    res.text
                    for res in self.chatvec.main.search(
                        itemgetter("standalone_question")(x)
                    )
                ]
            ),
            "question": itemgetter("standalone_question"),
        }
        print(_context)
        conversational_qa_chain = (
            _inputs | _context | ANSWER_PROMPT | llm | StrOutputParser()
        )

        answer = conversational_qa_chain.invoke(
            {"question": question, "chat_history": conversation.conversation}
        )

        self.postgres_history.add_user_message(question)
        self.postgres_history.add_ai_message(answer)

        return {"answer": answer, "session_id": self.postgres_history.session_id}


# Main function to test chatbot locally in terminal
def main():
    bot = Chatbot()

    while True:
        usr_input = input("User: ")
        if usr_input == "quit":
            break
        resp = bot.chat(usr_input, bot.conversation_history)
        print(f"Bot: {resp}")


if __name__ == "__main__":
    main()
