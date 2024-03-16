from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate


# TODO: ADD filter when TUM = false returned, just make normal AI call (potentially just standard answer) and tell the AI to not retrieve context.

first_filter_template = """
    
    You're given a question and a chat history and need to decide 3 things about it:

    1. If there is something that specifically rules out that the question is about the Technical University of Munich (TUM), add "is_tum: false" to the JSON. Otherwise, add "is_tum: true". 
    2. Assess if the question has an inherently super sensitive topic. If it does, add "is_sensitive: true" to the JSON. Otherwise, add "is_sensitive: false".
    3. Assess the question's language. If it's in English, add "language: English" to the JSON. If it's in German, add "language: German" to the JSON.

    Your output should be strictly in JSON format with the following keys:
        
        "is_tum": boolean,
        "is_sensitive": boolean,
        "language": string
        
    Chat History:

    <chat_history>
    {history}
    </chat_history>

    Question:
    
    <question>
    {question}
    </question>

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
    
    Answer:
"""

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_question_template)


answer_template = """Answer the question based on the following context:
    <context>
    {context}
    </context>

    Use the provided information to give the user the most specific answer. Always provide the links after the relevant sentence that you used for your answer.

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
    {{
        "trigger_feedback": boolean
    }}

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

create_email_template = """
    Based on the following conversation between a user and a chatbot, create an email that can be sent to student support at the Technical University of Munich for more specific information.
    The email should be in the same language as the conversation and the tone should be polite but not overly formal.
    Don't use fancy adjectives or words that are too complex.

    <chat_history>
    {chat_history}
    </chat_history>

    Email:
"""

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")
