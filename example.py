from os import environ
from Bard import Chatbot

token = environ.get("BARD_TOKEN")

chatbot = Chatbot(token)

chatbot.ask("Hello, how are you?")
