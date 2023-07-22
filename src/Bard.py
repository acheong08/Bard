import argparse
import asyncio
import json
import os
import random
import re
import string
import sys
from typing import Dict
from typing import List

import httpx
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
    Synchronous wrapper for the AsyncChatbot class.
    """

    def __init__(
        self,
        secure_1psid: str,
        secure_1psidts: str,
        proxy: dict = None,
        timeout: int = 20,
    ):
        self.loop = asyncio.get_event_loop()
        self.async_chatbot = self.loop.run_until_complete(
            AsyncChatbot.create(secure_1psid, secure_1psidts, proxy, timeout),
        )

    def save_conversation(self, file_path: str, conversation_name: str):
        return self.loop.run_until_complete(
            self.async_chatbot.save_conversation(file_path, conversation_name),
        )

    def load_conversations(self, file_path: str) -> List[Dict]:
        return self.loop.run_until_complete(
            self.async_chatbot.load_conversations(file_path),
        )

    def load_conversation(self, file_path: str, conversation_name: str) -> bool:
        return self.loop.run_until_complete(
            self.async_chatbot.load_conversation(file_path, conversation_name),
        )

    def ask(self, message: str) -> dict:
        return self.loop.run_until_complete(self.async_chatbot.ask(message))


class AsyncChatbot:
    """
    A class to interact with Google Bard.
    Parameters
        session: str
            The __Secure_1PSID cookie.
        session_ts: str
            The __Secure_1PSIDTS cookie.
        proxy: str
        timeout: int
            Request timeout in seconds.
    """

    __slots__ = [
        "headers",
        "_reqid",
        "SNlM0e",
        "conversation_id",
        "response_id",
        "choice_id",
        "proxy",
        "secure_1psidts",
        "secure_1psid",
        "session",
        "timeout",
    ]

    def __init__(
        self,
        secure_1psid: str,
        secure_1psidts: str,
        proxy: dict = None,
        timeout: int = 20,
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
        self.secure_1psid = secure_1psid
        self.secure_1psidts = secure_1psidts
        self.session = httpx.AsyncClient(proxies=self.proxy)
        self.session.headers = headers
        self.session.cookies.set("__Secure-1PSID", secure_1psid)
        if secure_1psidts:
            self.session.cookies.set("__Secure-1PSIDTS", secure_1psidts)
        self.timeout = timeout

    @classmethod
    async def create(
        cls,
        secure_1psid: str,
        secure_1psidts: str,
        proxy: dict = None,
        timeout: int = 20,
    ) -> "AsyncChatbot":
        """
        Async constructor.
        """
        instance = cls(secure_1psid, secure_1psidts, proxy, timeout)
        instance.SNlM0e = await instance.__get_snlm0e()
        return instance

    async def save_conversation(self, file_path: str, conversation_name: str) -> None:
        """
        Saves conversation to the file
        :param file_path: file to save (json)
        :param conversation_name: any name of current conversation (unique one)
        :return: None
        """
        # Load conversations from file
        conversations = await self.load_conversations(file_path)

        # Update existing one
        conversation_exists = False
        for conversation in conversations:
            if conversation["conversation_name"] == conversation_name:
                conversation["conversation_name"] = conversation_name
                conversation["_reqid"] = self._reqid
                conversation["conversation_id"] = self.conversation_id
                conversation["response_id"] = self.response_id
                conversation["choice_id"] = self.choice_id
                conversation["SNlM0e"] = self.SNlM0e
                conversation_exists = True

        # Create conversation object
        if not conversation_exists:
            conversation = {
                "conversation_name": conversation_name,
                "_reqid": self._reqid,
                "conversation_id": self.conversation_id,
                "response_id": self.response_id,
                "choice_id": self.choice_id,
                "SNlM0e": self.SNlM0e,
            }
            conversations.append(conversation)

        # Save to the file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversations, f, indent=4)

    async def load_conversations(self, file_path: str) -> List[Dict]:
        # Check if file exists
        if not os.path.isfile(file_path):
            return []
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    async def load_conversation(self, file_path: str, conversation_name: str) -> bool:
        """
        Loads a conversation from history file. Returns whether the conversation was found
        :param file_path: File with conversations (json)
        :param conversation_name: unique conversation name
        :return: True if the conversation was found
        """
        conversations = await self.load_conversations(file_path)
        for conversation in conversations:
            if conversation["conversation_name"] == conversation_name:
                self._reqid = conversation["_reqid"]
                self.conversation_id = conversation["conversation_id"]
                self.response_id = conversation["response_id"]
                self.choice_id = conversation["choice_id"]
                self.SNlM0e = conversation["SNlM0e"]
                return True
        return False

    async def __get_snlm0e(self):
        # Find "SNlM0e":"<ID>"
        if (
            not (self.secure_1psid and self.secure_1psidts)
            or self.secure_1psid[-1] != "."
        ):
            raise Exception(
                "Enter correct __Secure_1PSID and __Secure_1PSIDTS value. __Secure_1PSID value must end with a single dot. ",
            )
        resp = await self.session.get(
            "https://bard.google.com/",
            timeout=10,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            raise Exception(
                f"Response code not 200. Response Status is {resp.status_code}",
            )
        SNlM0e = re.search(r"SNlM0e\":\"(.*?)\"", resp.text)
        if not SNlM0e:
            raise Exception(
                "SNlM0e value not found in response. Check __Secure_1PSID value.",
            )
        return SNlM0e.group(1)

    async def ask(self, message: str) -> dict:
        """
        Send a message to Google Bard and return the response.
        :param message: The message to send to Google Bard.
        :return: A dict containing the response from Google Bard.
        """
        # url params
        params = {
            "bl": "boq_assistant-bard-web-server_20230713.13_p0",
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
        resp = await self.session.post(
            "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
            params=params,
            data=data,
            timeout=self.timeout,
        )
        chat_data = json.loads(resp.content.splitlines()[3])[0][2]
        if not chat_data:
            return {"content": f"Google Bard encountered an error: {resp.content}."}
        json_chat_data = json.loads(chat_data)
        images = []
        if len(json_chat_data) >= 3:
            if len(json_chat_data[4][0]) >= 4:
                if json_chat_data[4][0][4]:
                    for img in json_chat_data[4][0][4]:
                        images.append(img[0][0][0])
        results = {
            "content": json_chat_data[4][0][1][0],
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
        Secure_1PSID = os.getenv("BARD__Secure_1PSID")
        Secure_1PSIDTS = os.getenv("BARD__Secure_1PSIDTS")
        if not (Secure_1PSID and Secure_1PSIDTS):
            print(
                "BARD__Secure_1PSID or BARD__Secure_1PSIDTS environment variable not set.",
            )
            sys.exit(1)
        chatbot = Chatbot(Secure_1PSID, Secure_1PSIDTS)
        # Join arguments into a single string
        MESSAGE = " ".join(sys.argv[1:])
        response = chatbot.ask(MESSAGE)
        console.print(Markdown(response["content"]))
        console.print(response["images"] if response["images"] else "")
        sys.exit(0)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session",
        help="__Secure-1PSID cookie",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--session_ts",
        help="__Secure_1PSIDTS cookie.",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    chatbot = Chatbot(args.session, args.session_ts)
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
