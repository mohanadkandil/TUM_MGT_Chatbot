import json
import uuid
import os
import asyncio
from typing import List, Optional
from operator import itemgetter
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import AzureChatOpenAI
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
    map_study_program,
    extract_documents
)

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
    uuid: Optional[str] = None
    study_program: Optional[str] = None


# Define Chatbot class (Decision-Making Module)
class Chatbot:
    def __init__(self, session_id: str = str(uuid.uuid4())):
        self.conversation_history = Conversation(conversation=[])
        self.chatvec = ChatbotVectorDatabase()
        self.postgres_history = PostgresChatMessageHistory(session_id=session_id)

    def _format_chat_history(self, conversation: Conversation) -> str:
        formatted_history = ""
        if not conversation.conversation:
            return formatted_history
        for message in conversation.conversation:
            formatted_history += f"{message.role}: {message.content}\n"
        return formatted_history.rstrip()

    def chat(
        self, question: str, conversation: Conversation, study_program: str = ""
    ) -> str:
        """
        Chat with the chatbot
        :param question: The question to ask the chatbot
        :param chat_history: The chat history
        :return: The chatbot's answer and the session id
        """

        llm = AzureChatOpenAI(
            openai_api_version="2023-05-15",
            deployment_name="ChatbotMGT",
            azure_endpoint=azure_endpoint,
            openai_api_key=openai_api_key,
        )

        history = self._format_chat_history(conversation)
        first_filter_result = parse_and_filter_question(question, history, llm)

        if first_filter_result and first_filter_result.get("decision") == "stop":
            print("First filter applied, stopping here.")
            self.postgres_history.add_user_message(question)
            self.postgres_history.add_ai_message(
                first_filter_result.get("answer", "Stopped at first filter")
            )
            return {
                "answer": first_filter_result.get(
                    "answer", "Something didn't work with filtering"
                ),
                "session_id": self.postgres_history.session_id,
            }

        # to-do: get degree program from frontend
        language_of_query = "English"  # first_filter_result.get("language", "English")
        degree_program = map_study_program(study_program)
        print(f"Degree program: {degree_program}")

        keyword_string = first_filter_result.get("keywords", "")

        print(f"keyword_string: {keyword_string}")

        few_shot_qa_pairs = get_qa_pairs(degree_program, language_of_query)
        print(f"Few shot QA pairs: {few_shot_qa_pairs}")
        print("-------------------")

        """ _inputs = RunnableParallel(
            standalone_answer=RunnablePassthrough.assign(
                chat_history=lambda x: self._format_chat_history(x["chat_history"])
            )
            | CONDENSE_QUESTION_PROMPT
            | llm
            | StrOutputParser(),
        )
        print("Type, ", type(_inputs))
        print(f"Inputs: {_inputs}")
        print("-------------------") """

        _context = {
            "context": lambda x: " ".join(
                [
                    f"{res.text}, {res.subtopic}, {res.url}"
                    for res in self.chatvec.main.search(
                        query=keyword_string,
                        k=3,
                        language=language_of_query,
                        degree_programs=degree_program,
                    )
                ]
            ),
            # "question": itemgetter("question"),  # itemgetter("standalone_question")
            # "few_shot_qa_pairs": itemgetter("few_shot_qa_pairs"),
        }

        conversational_qa_chain = (
            {
                "context": _context,
                "question": RunnablePassthrough(),
                "chat_history": RunnablePassthrough(),
                "few_shot_qa_pairs": lambda x: few_shot_qa_pairs,
            }
            | ANSWER_PROMPT
            | llm
            | StrOutputParser()
        )

        answer = conversational_qa_chain.invoke(
            {"question": question, "chat_history": conversation.conversation}
        )
        print(f"Answer: {answer}")
        print("-------------------")

        self.postgres_history.add_user_message(question)
        self.postgres_history.add_ai_message(answer)

        feedback_trigger = get_feedback_trigger(question, answer, llm)
        print(feedback_trigger)
        print(f"Feedback trigger: {feedback_trigger}")
        # to-do: pass feedback_trigger to frontend, create api endpoint to store feedback
        if feedback_trigger.get("trigger_feedback", False):
            print("Feedback triggered")

        return {"answer": answer, "session_id": self.postgres_history.session_id}

    async def chat_stream(
        self, question: str, conversation: Conversation, study_program: str = ""
    ):
        """
        Chat with the chatbot
        :param question: The question to ask the chatbot
        :param chat_history: The chat history
        :return: The chatbot's answer and the session id
        """
        print(conversation)
        llm = AzureChatOpenAI(
            openai_api_version="2023-05-15",
            deployment_name="ChatbotMGT",
            azure_endpoint=azure_endpoint,
            openai_api_key=openai_api_key,
        )

        history = self._format_chat_history(conversation)
        first_filter_result = parse_and_filter_question(question, history, llm)

        if first_filter_result and first_filter_result.get("decision") == "stop":
            print("First filter applied, stopping here.")
            self.postgres_history.add_user_message(question)
            self.postgres_history.add_ai_message(
                first_filter_result.get("answer", "Stopped at first filter")
            )

            answer = first_filter_result.get("answer", "Stopped at first filter")

            final_data = {
                "type": "final",
                "data": {
                    "session_id": self.postgres_history.session_id,
                    "full_answer": answer,
                    "feedback_trigger": False,
                },
            }

            yield f"{json.dumps(final_data)}\n\n"
        else:
            language_of_query = first_filter_result.get("language", "English")
            degree_program = map_study_program(study_program)
            
            print(f"Degree program: {degree_program}")
            print("-------------------")
            keyword_string = first_filter_result.get("keywords", "")

            print(f"keyword_string: {keyword_string}")
            print("-------------------")

            few_shot_qa_pairs = get_qa_pairs(degree_program, language_of_query)
            print(f"Few shot QA pairs: {few_shot_qa_pairs}")
            print("-------------------")


            context = ""
            look_up_table = {}

            docs_from_vdb = self.chatvec.main.search(
                query=question,
                k=3,
                language=language_of_query,
                degree_programs=degree_program,
            )
            
            
            for i, res in enumerate(docs_from_vdb):
                context += f"Document Index: {i+1}, {res.text.replace("\n", " ")}, {res.subtopic} \n"
                look_up_table[i+1] = {"title": res.title, "url": res.url}

            print(f"look_up_table: {look_up_table}")
            print("-------------------")
            
            
            _context = {
                "context": context     # "question": itemgetter("question"),  # itemgetter("standalone_question")
                # "few_shot_qa_pairs": itemgetter("few_shot_qa_pairs"),
            }
            print(f"_context: {_context}")

            

            conversational_qa_chain = (
                {
                    "context": lambda x: _context,
                    "question": RunnablePassthrough(),
                    "chat_history": RunnablePassthrough(),
                    "few_shot_qa_pairs": lambda x: few_shot_qa_pairs,
                }
                | ANSWER_PROMPT
                | llm
                | StrOutputParser()
            )

            answer = ""

            async for chunk in conversational_qa_chain.astream(
                {"question": question, "chat_history": history}
            ):
                data_to_send = {"type": "stream", "data": chunk}
                yield f"{json.dumps(data_to_send)}\n\n"
                answer += chunk

            print(f"Answer from streaming: {answer}")

            self.postgres_history.add_user_message(question)
            self.postgres_history.add_ai_message(answer)

            feedback_trigger = get_feedback_trigger(question, answer, llm)
            print(f"Feedback trigger: {feedback_trigger}")

            
            
            final_data = {
                "type": "final",
                "data": {
                    "session_id": self.postgres_history.session_id,
                    "full_answer": answer,
                    "feedback_trigger": feedback_trigger.get("trigger_feedback", False),
                    "referenced documents": extract_documents(answer, look_up_table)
                },
            }

            yield f"{json.dumps(final_data)}\n\n"


# Main function to test chatbot locally in terminal
async def main():
    bot = Chatbot()

    while True:
        usr_input = input("User: ")
        if usr_input == "quit":
            break

        async for r in bot.chat_stream(usr_input, bot.conversation_history):
            try:
                response_dict = json.loads(r)
                print(f"Bot: {response_dict['data']}")
            except json.JSONDecodeError:
                print(f"Bot: {r}")

        # resp = bot.chat(usr_input, bot.conversation_history)
        # print(f"Bot: {resp}")


if __name__ == "__main__":
    asyncio.run(main())
    # main()
