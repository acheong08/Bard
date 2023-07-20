<a id="Bard"></a>

# Bard

<a id="Bard.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

Synchronous wrapper for the AsyncChatbot class.

<a id="Bard.AsyncChatbot"></a>

## AsyncChatbot Objects

```python
class AsyncChatbot()
```

A class to interact with Google Bard.
Parameters
    session: str
        The __Secure_1PSID cookie.
    session_ts: str
        The __Secure_1PSIDTS cookie
    proxy: str
    timeout: int
        Request timeout in seconds.

<a id="Bard.AsyncChatbot.create"></a>

#### create

```python
@classmethod
async def create(cls,
                 secure_1psid: str,
                 secure_1psidts: str,
                 proxy: dict = None,
                 timeout: int = 20) -> "AsyncChatbot"
```

Async constructor.

<a id="Bard.AsyncChatbot.save_conversation"></a>

#### save\_conversation

```python
async def save_conversation(file_path: str, conversation_name: str) -> None
```

Saves conversation to the file

**Arguments**:

- `file_path`: file to save (json)
- `conversation_name`: any name of current conversation (unique one)

**Returns**:

None

<a id="Bard.AsyncChatbot.load_conversation"></a>

#### load\_conversation

```python
async def load_conversation(file_path: str, conversation_name: str) -> bool
```

Loads a conversation from history file. Returns whether the conversation was found

**Arguments**:

- `file_path`: File with conversations (json)
- `conversation_name`: unique conversation name

**Returns**:

True if the conversation was found

<a id="Bard.AsyncChatbot.ask"></a>

#### ask

```python
async def ask(message: str) -> dict
```

Send a message to Google Bard and return the response.

**Arguments**:

- `message`: The message to send to Google Bard.

**Returns**:

A dict containing the response from Google Bard.
