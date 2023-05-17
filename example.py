from os import environ

from Bard import Chatbot

token = environ.get("BARD_TOKEN")

chatbot = Chatbot(token)

chatbot.ask("Hello, how are you?")

def add_underscores(word):
    new_word = "_"
    password = '12345'
    for char in word:
        new_word = char + "_"
    return new_word

def add_underscores(word)
    new_word = "_"
    for i in range(len(word)):
        new_word = word[i] + "_"
    return new_word