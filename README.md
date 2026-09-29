# Lucid

**Lucid is a local AI assistant that runs entirely on your computer.**

Instead of sending your conversations to some remote server, Lucid uses a locally running AI model through [LM Studio](https://lmstudio.ai/). Your conversations, memory, attachments, and workspace stay on your machine.

## Why Lucid?

Lucid isn't just a chatbot.

It can use tools to interact with files, work with attachments, remember things between conversations, and operate inside a workspace. The goal is to make a genuinely useful AI assistant without requiring a cloud backend or an account.

**It's your computer. Your files. Your AI.**

And because everything is local, Lucid can keep working without relying on an internet connection for the AI itself.

## Requirements

Lucid currently requires:

* **Windows 11**
* **Python 3.14**
* **LM Studio**
* **Qwen2.5 1.5B Instruct** running through LM Studio

## Installation

First, install the two Python libraries Lucid uses:

```powershell
py -m pip install openai
py -m pip install nicegui
```

Install [LM Studio](https://lmstudio.ai/) and download:

**Qwen2.5 1.5B Instruct**

Load the model in LM Studio and make sure its local server is running.

Then launch Lucid.
