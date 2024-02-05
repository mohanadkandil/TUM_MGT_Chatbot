import json
import openai
import requests


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


# Main function to test chatbot locally in terminal
def main():
    bot = Chatbot()

    while True:
        usr_input = input("User: ")
        if usr_input == "quit":
            break
        resp = bot.chat(usr_input)
        print(f"Bot: {resp}")


if __name__ == "__main__":
    main()
