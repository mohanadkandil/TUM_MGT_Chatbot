from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate

first_filter_template = """
    You're given a question and need to decide 3 things about it:

    1. If the question is about the Technical University of Munich, especially about the School of Management, add "is_tum: true" to the JSON. Otherwise, add "is_tum: false".
    2. Assess if the question has an inherently super sensitive topic. If it does, add "is_sensitive: true" to the JSON. Otherwise, add "is_sensitive: false".
    3. Assess the question's language. If it's in English, add "language: English" to the JSON. If it's in German, add "language: German" to the JSON.

    Your output should be strictly in JSON format with the following keys:
        
        "is_tum": boolean,
        "is_sensitive": boolean,
        "language": string
        
    Question:
    {question}
        
    JSON Output:
"""

FIRST_FILTER_PROMPT = PromptTemplate.from_template(first_filter_template)


condense_question_template = """Given the following chat history and a follow up question, rephrase the follow up question to be a standalone question, and produce an answer to the best of your knowledge about the Technical University of Munich. Use the same language as the follow up question.
    <chat_history>
    {chat_history}
    </chat_history>

    <Follow up question>
    {question}
    </Follow up question>

    Standalone question:
"""

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_question_template)


answer_template = """Answer the question based only on the following context:
    <context>
    {context}
    </context>

    If you don´t find the answer in the context, tell the user that you are happy to help with different questions about TUM.

    Here's some examples of questions and answers:
    <examples>
    {few_shot_qa_pairs}
    </examples>

    Question: {question}

    Answer:
"""

ANSWER_PROMPT = ChatPromptTemplate.from_template(answer_template)


feedback_trigger_query = """
    Provide a json object with one key-value pair as follows:
    {
        "trigger_feedback": boolean
    }

    Base your decision on the quality of the answer to a user query.
    If the user's question is sufficiently answered, set "trigger_feedback" to true.
    Otherwise, set "trigger_feedback" to false.

    <User question>
    {question}
    </User question>

    <Answer>
    {answer}
    </Answer>
"""

FEEDBACK_TRIGGER_PROMPT = PromptTemplate.from_template(feedback_trigger_query)

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")