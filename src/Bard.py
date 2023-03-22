"""
Reverse engineering of Google Bard
"""
import argparse
import json
import random
import re
import string

import requests
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markdown import Markdown


def create_session() -> PromptSession:
    return PromptSession(history=InMemoryHistory())


def create_completer(commands: list, pattern_str: str = "$") -> WordCompleter:
    return WordCompleter(words=commands, pattern=re.compile(pattern_str))


def get_input(
    session: PromptSession = None,
    completer: WordCompleter = None,
    key_bindings: KeyBindings = None,
) -> str:
    """
    Multiline input function.
    """
    return (
        session.prompt(
            completer=completer,
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=key_bindings,
        )
        if session
        else prompt(multiline=True)
    )


class Chatbot:
    """
    A class to interact with Google Bard.
    """

    __slots__ = [
        "headers",
        "_reqid",
        "at",
        "conversation_id",
        "response_id",
        "choice_id",
    ]

    def __init__(self, session_id, at):
        self.headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
            "Cookie": "__Secure-1PSID=" + session_id + ";",
        }
        self._reqid = int("".join(random.choices(string.digits, k=4)))
        self.at = at  # window.WIZ_global_data.SNlM0e
        self.conversation_id = ""
        self.response_id = ""
        self.choice_id = ""

    def ask(self, message: str) -> dict:
        """
        Send a message to Google Bard and return the response.
        :param message: The message to send to Google Bard.
        :return: A dict containing the response from Google Bard.
        """
        # url params
        params = {
            "bl": "boq_assistant-bard-web-server_20230315.04_p1",  # 2023/03/15
            "_reqid": str(self._reqid),
            "rt": "c",
        }

        # message arr -> data["f.req"]. Message is double json stringified
        message_struct = [
            [message],
            None,
            [self.conversation_id, self.response_id, self.choice_id],
        ]
        data = {"f.req": json.dumps([None, json.dumps(message_struct)]), "at": self.at}

        # do the request!
        resp = requests.post(
            "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
            headers=self.headers,
            params=params,
            data=data,
            timeout=120,
        )

        chat_data = json.loads(resp.content.splitlines()[3])[0][2]
        if not chat_data:
            return {"content": f"Google Bard encountered an error: {resp.content}."}
        json_chat_data = json.loads(chat_data)
        results = {
            "content": json_chat_data[0][0],
            "conversation_id": json_chat_data[1][0],
            "response_id": json_chat_data[1][1],
            "factualityQueries": json_chat_data[3],
            "textQuery": json_chat_data[2][0] if json_chat_data[2] is not None else "",
            "choices": [{"id": i[0], "content": i[1]} for i in json_chat_data[4]],
        }
        self.conversation_id = results["conversation_id"]
        self.response_id = results["response_id"]
        self.choice_id = results["choices"][0]["id"]
        self._reqid += 100000
        return results


if __name__ == "__main__":
    print(
        """
        ChatGPT - A command-line interface to Google's Bard (https://bard.google.com/)
        Repo: github.com/acheong08/Bard

        Enter `alt+enter` or `esc+enter` to send a message.
        """,
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session",
        help="__Secure-1PSID cookie.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--at",
        help="window.WIZ_global_data.SNlM0e",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    chatbot = Chatbot(args.session, args.at)
    prompt_session = create_session()
    completions = create_completer(["!exit", "!reset"])
    console = Console()
    try:
        while True:
            console.print("You:")
            user_prompt = get_input(session=prompt_session, completer=completions)
            console.print()
            if user_prompt == "!exit":
                break
            elif user_prompt == "!reset":
                chatbot.conversation_id = ""
                chatbot.response_id = ""
                chatbot.choice_id = ""
                continue
            print("Google Bard:")
            response = chatbot.ask(user_prompt)
            console.print(Markdown(response["content"]))
            print()
    except KeyboardInterrupt:
        print("Exiting...")
