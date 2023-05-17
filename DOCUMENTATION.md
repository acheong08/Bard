<a id="Bard"></a>

# Bard

Reverse engineering of Google Bard

<a id="Bard.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

A class to interact with Google Bard.
Parameters
    session_id: str
        The __Secure-1PSID cookie.
    proxy: str

<a id="Bard.Chatbot.ask"></a>

#### ask

```python
def ask(message: str) -> dict
```

Send a message to Google Bard and return the response.

**Arguments**:

- `message`: The message to send to Google Bard.

**Returns**:

A dict containing the response from Google Bard.


