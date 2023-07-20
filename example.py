from os import environ

from Bard import Chatbot

Secure_1PSID = environ.get("BARD__Secure-1PSID")
Secure_1PSIDTS = environ.get("BARD__Secure-1PSIDTS")

chatbot = Chatbot(Secure_1PSID, Secure_1PSIDTS)

chatbot.ask("Hello, how are you?")
