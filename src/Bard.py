import argparse
import json
import os
import random
import re
import string
import sys
import time

import requests
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markdown import Markdown


def __create_session() -> PromptSession:
    return PromptSession(history=InMemoryHistory())


def __create_completer(commands: list, pattern_str: str = "$") -> WordCompleter:
    return WordCompleter(words=commands, pattern=re.compile(pattern_str))


def __get_input(
    prompt_sess: PromptSession = None,
    completer: WordCompleter = None,
    key_bindings: KeyBindings = None,
) -> str:
    """
    Multiline input function.
    """
    return (
        prompt_sess.prompt(
            completer=completer,
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=key_bindings,
        )
        if prompt_sess
        else prompt(multiline=True)
    )


class Chatbot:
    """
    A class to interact with Google Bard.
    Parameters
        session_id: str
            The __Secure-1PSID cookie.
        proxy: str
        timeout: int
            Request timeout in seconds.
        session: requests.Session
            Requests session object.
    """

    __slots__ = [
        "headers",
        "_reqid",
        "SNlM0e",
        "conversation_id",
        "response_id",
        "choice_id",
        "proxy",
        "session_id",
        "session",
        "timeout",
    ]

    def __init__(
        self,
        session_id: str,
        proxy: dict = None,
        timeout: int = 20,
        session: requests.Session = None,
    ):
        headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
        self._reqid = int("".join(random.choices(string.digits, k=4)))
        self.proxy = proxy
        self.conversation_id = ""
        self.response_id = ""
        self.choice_id = ""
        self.session_id = session_id
        self.session = session or requests.Session()
        self.session.headers = headers
        self.session.cookies.set("__Secure-1PSID", session_id)
        self.SNlM0e = self.__get_snlm0e()
        self.timeout = timeout

    def save_conversation(self, file_path: str, conversation_name: str):
        conversations = self.load_conversations(file_path)
        conversation_details = {
            {
                "conversation_name": conversation_name,
                "_reqid": self._reqid,
                "conversation_id": self.conversation_id,
                "response_id": self.response_id,
                "choice_id": self.choice_id,
                "SNlM0e": self.SNlM0e,
            },
        }
        conversations.append(conversation_details)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversations, f, indent=4)

    def load_conversations(self, file_path: str) -> list[dict]:
        # Check if file exists
        if not os.path.isfile(file_path):
            return []
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    def load_conversation(self, file_path: str, conversation_name: str) -> bool:
        """
        Loads a conversation from history file. Returns whether the conversation was found.
        """
        conversations = self.load_conversations(file_path)
        for conversation in conversations:
            if conversation["conversation_name"] == conversation_name:
                self._reqid = conversation["_reqid"]
                self.conversation_id = conversation["conversation_id"]
                self.response_id = conversation["response_id"]
                self.choice_id = conversation["choice_id"]
                self.SNlM0e = conversation["SNlM0e"]
                return True
        return False

    def __get_snlm0e(self):
        # Find "SNlM0e":"<ID>"
        if not self.session_id or self.session_id[-1] != ".":
            raise Exception(
                "__Secure-1PSID value must end with a single dot. Enter correct __Secure-1PSID value.",
            )
        resp = self.session.get(
            "https://bard.google.com/",
            timeout=10,
            proxies=self.proxy,
        )
        if resp.status_code != 200:
            raise Exception(
                f"Response code not 200. Response Status is {resp.status_code}",
            )
        SNlM0e = re.search(r"SNlM0e\":\"(.*?)\"", resp.text)
        if not SNlM0e:
            raise Exception(
                "SNlM0e value not found in response. Check __Secure-1PSID value.",
            )
        return SNlM0e.group(1)

    def ask(self, message: str) -> dict:
        """
        Send a message to Google Bard and return the response.
        :param message: The message to send to Google Bard.
        :return: A dict containing the response from Google Bard.
        """
        # url params
        params = {
            "bl": "boq_assistant-bard-web-server_20230530.14_p0",
            "_reqid": str(self._reqid),
            "rt": "c",
        }

        # message arr -> data["f.req"]. Message is double json stringified
        message_struct = [
            [message],
            None,
            [self.conversation_id, self.response_id, self.choice_id],
        ]
        data = {
            "f.req": json.dumps([None, json.dumps(message_struct)]),
            "at": self.SNlM0e,
        }
        resp = self.session.post(
            "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
            params=params,
            data=data,
            timeout=self.timeout,
            proxies=self.proxy,
        )
        chat_data = json.loads(resp.content.splitlines()[3])[0][2]
        if not chat_data:
            return {"content": f"Google Bard encountered an error: {resp.content}."}
        json_chat_data = json.loads(chat_data)
        images = set()
        if len(json_chat_data) >= 3:
            if len(json_chat_data[4][0]) >= 4:
                if json_chat_data[4][0][4]:
                    for img in json_chat_data[4][0][4]:
                        images.add(img[0][0][0])
        results = {
            "content": json_chat_data[0][0],
            "conversation_id": json_chat_data[1][0],
            "response_id": json_chat_data[1][1],
            "factualityQueries": json_chat_data[3],
            "textQuery": json_chat_data[2][0] if json_chat_data[2] is not None else "",
            "choices": [{"id": i[0], "content": i[1]} for i in json_chat_data[4]],
            "images": images,
        }
        self.conversation_id = results["conversation_id"]
        self.response_id = results["response_id"]
        self.choice_id = results["choices"][0]["id"]
        self._reqid += 100000
        return results


if __name__ == "__main__":
    print(
        """
        Bard - A command-line interface to Google's Bard (https://bard.google.com/)
        Repo: github.com/acheong08/Bard

        Enter `alt+enter` or `esc+enter` to send a message.
        """,
    )
    console = Console()
    if os.getenv("BARD_QUICK"):
        session = os.getenv("BARD_SESSION")
        if not session:
            print("BARD_SESSION environment variable not set.")
            sys.exit(1)
        chatbot = Chatbot(session)
        # Join arguments into a single string
        MESSAGE = " ".join(sys.argv[1:])
        response = chatbot.ask(MESSAGE)
        console.print(Markdown(response["content"]))
        console.print(response["images"] if response["images"] else "")
        sys.exit(0)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session",
        help="__Secure-1PSID cookie.",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    chatbot = Chatbot(args.session)
    prompt_session = __create_session()
    completions = __create_completer(["!exit", "!reset"])

    try:
        while True:
            console.print("You:")
            user_prompt = __get_input(prompt_sess=prompt_session, completer=completions)
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
            console.print(response["images"] if response["images"] else "")
            print()
    except KeyboardInterrupt:
        print("Exiting...")
