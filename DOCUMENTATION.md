<a id="Bard"></a>

# Bard

Reverse engineering of Google Bard

<a id="Bard.get_input"></a>

#### get\_input

```python
def get_input(session: PromptSession = None,
              completer: WordCompleter = None,
              key_bindings: KeyBindings = None) -> str
```

Multiline input function.

<a id="Bard.Chatbot"></a>

## Chatbot Objects

```python
class Chatbot()
```

A class to interact with Google Bard.

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

