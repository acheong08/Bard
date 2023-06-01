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
    session_id: str
        The __Secure-1PSID cookie.
    proxy: str
    timeout: int
        Request timeout in seconds.

<a id="Bard.AsyncChatbot.load_conversation"></a>

#### load\_conversation

```python
async def load_conversation(file_path: str, conversation_name: str) -> bool
```

Loads a conversation from history file. Returns whether the conversation was found.

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
