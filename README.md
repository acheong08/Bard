# Bard <img src="https://www.gstatic.com/lamda/images/favicon_v1_150160cddff7f294ce30.svg" width="35px" />
Reverse engineering of Google's Bard chatbot API

## Installation
```bash
 $ pip3 install --upgrade GoogleBard
```

## Authentication
Go to https://bard.google.com/

- F12 for console
- Copy the values
  - Session: Go to Application → Cookies → `__Secure-1PSID`. Copy the value of that cookie.

## Usage

```bash
$ python3 -m Bard -h
usage: Bard.py [-h] --session SESSION

options:
  -h, --help         show this help message and exit
  --session SESSION  __Secure-1PSID cookie.
```

### Quick mode
```
$ export BARD_QUICK="true"
$ export BARD_SESSION="<__Secure-1PSID>"
$ python3 -m Bard
```
Environment variables can be placed in .zshrc.

Example bash shortcut:
```bash
# USAGE1: bard QUESTION
# USAGE2: echo "QUESTION" | bard
bard () {
	export BARD_QUICK=true
	export BARD_SESSION=<REDACTED>.
	python3 -m Bard "${@:-$(</dev/stdin)}" | tail -n+7
}
```

## [Developer Documentation](https://github.com/acheong08/Bard/blob/main/DOCUMENTATION.md)
```python
from os import environ
from Bard import Chatbot

token = environ.get("BARD_TOKEN")

chatbot = Chatbot(token)

chatbot.ask("Hello, how are you?")
```

Credits:
- [discordtehe](https://github.com/discordtehe) - Derivative of his original reverse engineering
