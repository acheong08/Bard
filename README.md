# Bard <img src="https://www.gstatic.com/lamda/images/favicon_v1_150160cddff7f294ce30.svg" width="35px" />
Reverse engineering of Google's Bard chatbot

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

## [Developer Documentation](https://github.com/acheong08/Bard/blob/main/DOCUMENTATION.md)


Credits:
- [discordtehe](https://github.com/discordtehe) - Derivative of his original reverse engineering
