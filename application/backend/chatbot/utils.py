from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from application.backend.chatbot.prompts import (
    FIRST_FILTER_PROMPT,
    FEEDBACK_TRIGGER_PROMPT,
)
from application.backend.datastore.qa_pairs.qa_loader import PostgresLoader
from typing import List
import random, os
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser, Document, format_document


openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
llm = AzureChatOpenAI(
    openai_api_version="2023-05-15",
    deployment_name="ChatbotMGT",
    azure_endpoint=azure_endpoint,
    openai_api_key=openai_api_key,
)
import re


def parse_and_filter_question(
    question: str, history: List, llm: AzureChatOpenAI
) -> dict:
    """
    Invokes the language model with a filter prompt, parses the JSON response,
    and determines the response based on 'is_tum' and 'is_sensitive' fields.

    :param question: The question to be processed.
    :param llm: An instance of AzureChatOpenAI to use for invoking the language model.
    :return: A dictionary containing the answer and filtering decision. Additionally the language is returned if no filtering is applied.
    """
    json_parser = JsonOutputParser()
    filter_prompt = FIRST_FILTER_PROMPT.format(history=history, question=question)
    response = llm.invoke(filter_prompt)
    parsed_response = json_parser.parse(response.content)

    if not parsed_response.get("is_tum", True):
        print("Not TUM related")
        answer = "I'm sorry, I can't answer that question. Please ask me about TUM School of Management."
        prompt = ChatPromptTemplate.from_template(
            """You are specialized chatbot at the TUM School of Management providing the students relevant answers to their study related questions. A function was triggered that symbolized that the question was not related to any 
                                                  Study specific questions. 
                                                  Please provide the user an understandable answer to the question and ask the user to ask a question related to the TUM School of Management.
                                                  The following question was asked: {question}
                                                  Answer it in the language of the question. So it should probably be in English or German."""
        )

        chain = prompt | llm | StrOutputParser()

        answer = chain.invoke({"question": question})

        return {"answer": answer, "decision": "stop"}
    elif parsed_response.get("is_sensitive", False):
        print("Sensitive data")
        answer = "I'm sorry, I can't answer that question. Make sure to not include any sensitive data in your inquiry or contact the SOM directly."
        return {"answer": answer, "decision": "stop"}

    language = parsed_response.get("language", "English")

    keywords = parsed_response.get("keywords", "")

    return {
        "answer": None,
        "decision": "continue",
        "language": language,
        "keywords": keywords,
    }


def get_qa_pairs(degree_program: str, language: str) -> str:
    """
    Returns a string of few-shot QA pairs for the given degree program and language.

    :param degree_program: The degree program to get few-shot QA pairs for.
    :param language: The language to get few-shot QA pairs for.
    :return: A string of few-shot QA pairs.
    """

    postgres_qa = PostgresLoader()
    qa_pairs = postgres_qa.get_data(degree_program, language)
    postgres_qa.close_connection()

    num_to_sample = min(len(qa_pairs), 2)

    few_shot_qa_pairs = (
        "\n\n".join(
            [
                f"Question: {qa_pair[3]}\n Answer: {qa_pair[4]}"
                for qa_pair in random.sample(qa_pairs, num_to_sample)
            ]
        )
        if num_to_sample > 0
        else "No few-shot examples available."
    )

    return few_shot_qa_pairs


def get_feedback_trigger(question: str, answer: str, llm: AzureChatOpenAI) -> dict:
    """
    Invokes the language model with a feedback trigger prompt and parses the JSON response.

    :param question: The question to be processed.
    :param answer: The answer to the question.
    :param llm: An instance of AzureChatOpenAI to use for invoking the language model.
    :return: A dictionary containing the feedback trigger.
    """

    json_parser = JsonOutputParser()
    feedback_prompt = FEEDBACK_TRIGGER_PROMPT.format(question=question, answer=answer)
    response = llm.invoke(feedback_prompt)
    feedback_trigger = json_parser.parse(response.content)

    return feedback_trigger


def map_study_program(full_name):
    # Mapping of full program names to abbreviations
    program_mapping = {
        "Management & Technology - Munich": "BMT",
        "Management & Technology - Heilbronn": "BMT Heilbronn",
        "Bachelor Sustainable Management & Technology": "BSMT",
        "Master Management & Technology": "MMT",
        "Master Management & Digital Technology - Heilbronn": "MMDT Heilbronn",
        "Master Management - Munich": "MiM",
        "Master Management - Heilbronn": "MiM Heilbronn",
        "Master Finance & Information Technology": "FIM",
        "Master Computer Science": "MCS",
        "Master Sustainable Management & Technology": "MSMT",
        "Doctorate Program": "PHD",
    }

    # Find the abbreviation for a given full program name
    for program, abbreviation in program_mapping.items():
        if full_name == program:
            print(abbreviation)
            return abbreviation

    # Return "Unknown Abbreviation" if the full name is not in the mapping
    return ""


def extract_documents(text, look_up_table):
    """
    Extract numbers from text and retrieve corresponding documents from the lookup table along with their index.

    Parameters:
    - text: str, the input text from which to extract numbers enclosed in square brackets.
    - look_up_table: dict, a lookup table where keys are numbers (as strings or ints) and
                     values are dicts with 'title', 'url', and possibly other metadata.

    Returns:
    - A list of dicts, each containing the 'index', 'title', and 'url' of a document from the lookup table.
    """
    # Regular expression to find numbers enclosed in square brackets
    pattern = r"\[([0-9]+)\]"

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text)

    # Retrieve documents from the lookup table along with their index
    documents_with_index = []
    for match in matches:
        index = int(match)  # Convert match to integer for lookup
        document = look_up_table.get(index)
        if document:
            # Append document info along with its index to the result list
            documents_with_index.append({"index": index, **document})

    return documents_with_index
