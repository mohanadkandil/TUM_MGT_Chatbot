from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate


# TODO: ADD filter when TUM = false returned, just make normal AI call (potentially just standard answer) and tell the AI to not retrieve context.

first_filter_template = """
    
    You're given a question and a chat history and need to decide 4 things about it:

    Decide if the question is not TUM related or contains sensitive topics based on the chat history. Here is what you need to do exactly:
    
    1. If there is something that specifically rules out that the question is about the Technical University of Munich (TUM), add "is_tum: false" to the JSON. Otherwise, add "is_tum: true". 
    
    2. Assess if the question has an inherently super sensitive topic. If it does, add "is_sensitive: true" to the JSON. Otherwise, add "is_sensitive: false".
    If the question is sensitive and also not related to TUM, you should always return "is_tum: true" and "is_sensitive: true" to avoid any potential sensitive information being handled by the non-tum case.
    
    3. Assess the question's language. If it's in English, add "language: English" to the JSON. If it's in German, add "language: German" to the JSON.

    4. Based on the chat history and new question, provide a short informative string including the most important keywords that can be used for querying our vector database afterwards. If the question is not TUM related, you can leave this field empty. 

    Your output should be strictly in JSON format with the following keys:
        
        "is_tum": boolean,
        "is_sensitive": boolean,
        "language": string,
        "keywords": string
        
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


answer_template = """
You are a young, nice and friendly chatbot specialized in answering questions about the TUM School of Management. At the bottom you have a questions asked by a user to you. 

A previous function has retrieved the following information from the Chatbot database given the user's question and the chat history:
    <context>
    {context}
    </context>

    Use the provided information to give the user the most specific answer. If you use a certain context for answering the question please put it the end of the corresponding sentence in the following way '[x]' with the number it has. 
    If you cannot find the answer in the provided context, you can use your best knowledge to answer the question if you are 100 percent sure.
    IF you are not 100 percent sure YOU MUST tell the user that currently the information required to answer the question is not yet present in your database but the user can 
    share their feedback in the next message which will help the chatbot team to update the database with the required info. 
    
    If you can answer the question given the context, always provide the corresponding "Document Index" in the following way '[x]' with the number where you took the information from.

    YOU MUST only provide contact persons if you can find specific informations related to the questions in the context. DO NOT just list any information that you think is correct.

    Here's some examples of questions and answers that are related to the questions and have been previously asked. You can use them as further guidance for your writing style 
    and important information. 

    <examples>
    {few_shot_qa_pairs}
    </examples>

    Here is the question and history:
    
    {question}

    <history>
    {chat_history}
    </history>


    YOU MUST keep your answers short and precise and don't waste time with unnecessary information.
    YOU MUST answer the question in the same language as the question was asked.

    YOU MUST write informal but professional using simple english language. Meaning in the german "du" form e.g. 
    YOU MUST also not follow typical formalities like "Mit freundlichen Grüßen" or "Hochachtungsvoll" etc.

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
