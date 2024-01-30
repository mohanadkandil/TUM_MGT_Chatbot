import enum
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

chat = ChatOpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0,
                  max_tokens=8)


class Intent(enum.Enum):
    """Enumeration for classifying user intent."""
    COURSE_AND_PROGRAM_MANAGEMENT = enum.auto()
    ACADEMIC_PROCEDURES_AND_POLICIES = enum.auto()
    CREDIT_AND_ACADEMIC_RECOGNITION = enum.auto()
    THESIS_AND_PROJECT_SUPPORT = enum.auto()
    TECHNICAL_AND_ACCESS_ISSUES = enum.auto()


INTENT_DETECTION_PROMPT = f"""
You are an intelligent classification algorithm for the support at the TUM School of Management, your mission is to accurately detect and understand the user's intent from a given set of options. You have the ability to analyze user input and classify it into the following categories: {", ".join(e.name for e in Intent)}. Your goal is to assist in developing conversational agents for a student chatbot that can appropriately respond to user interactions based on their intent. You excel at natural language processing and machine learning techniques to effectively identify and classify user intents. Your superpower is understanding the nuances of user language and providing precise intent detection for seamless user experiences.

                    ###

                    EXAMPLES:

                    // Course and Program Management
                    INPUT: "Can I enroll in courses even though I'm not fully registered yet?"
                    OUTPUT:"COURSE_AND_PROGRAM_MANAGEMENT"
                    ---
                    INPUT: "When does course registration open for next semester?"
                    OUTPUT:"COURSE_AND_PROGRAM_MANAGEMENT"
                    ---
                    INPUT: "Do I need to complete any prerequisites before enrolling in an advanced module?"
                    OUTPUT:"COURSE_AND_PROGRAM_MANAGEMENT"
                    ---

                    // Academic Procedures and Policies
                    INPUT: "What is the procedure for credit transfer?"
                    OUTPUT:"ACADEMIC_PROCEDURES_AND_POLICIES"
                    ---
                    INPUT: "How does the grading system work?"
                    OUTPUT:"ACADEMIC_PROCEDURES_AND_POLICIES"
                    ---
                    INPUT: "Can I request a deadline extension for my assignment?"
                    OUTPUT:"ACADEMIC_PROCEDURES_AND_POLICIES"
                    ---

                    // Credit and Academic Recognition
                    INPUT: "How can I get my previous coursework recognized for credit here?"
                    OUTPUT:"CREDIT_AND_ACADEMIC_RECOGNITION"
                    ---
                    INPUT: "Will the credits from my summer course count towards my major?"
                    OUTPUT:"CREDIT_AND_ACADEMIC_RECOGNITION"
                    ---
                    INPUT: "Is there a process for appealing a grade I received last semester?"
                    OUTPUT:"CREDIT_AND_ACADEMIC_RECOGNITION"
                    ---

                    // Thesis and Project Support
                    INPUT: "I need help with my thesis supervision."
                    OUTPUT:"THESIS_AND_PROJECT_SUPPORT"
                    ---
                    INPUT: "What are the requirements for completing a capstone project?"
                    OUTPUT:"THESIS_AND_PROJECT_SUPPORT"
                    ---
                    INPUT: "Can I collaborate with an external company for my final year project?"
                    OUTPUT:"THESIS_AND_PROJECT_SUPPORT"
                    ---

                    // Technical and Access Issues
                    INPUT: "I'm having trouble accessing the online course platform. Can you help?"
                    OUTPUT:"TECHNICAL_AND_ACCESS_ISSUES"
                    ---
                    INPUT: "The link to my lecture recording isn't working. What should I do?"
                    OUTPUT:"TECHNICAL_AND_ACCESS_ISSUES"
                    ---
                    INPUT: "I can't log in to my student account, is there a way to reset my password?"
                    OUTPUT:"TECHNICAL_AND_ACCESS_ISSUES"

                    ###

The user message is: {{message}}
Detected intent category:
"""


def llm_call_intent(message: str):
    """
    Call the language model to classify the intent of a given message.

    Args:
    message (str): The user's message for which intent is to be detected.

    Returns:
    str: The detected intent based on the model's prediction.
    """
    llm_input = [SystemMessage(content=INTENT_DETECTION_PROMPT.format(message=message))]
    llm_output = chat(llm_input, max_tokens=13, stop=["\n"])
    return llm_output.content


def detect_intent(message: str):
    """
    Detect user intent based on the message.

    Args:
    message (str): The user's message for which intent is to be detected.

    Returns:
    Intent: An enum member representing the detected intent.
    """
    llm_output = llm_call_intent(message)
    intent = Intent[llm_output.strip()]
    print(f"Detected intent: {intent.name}")
    return intent
