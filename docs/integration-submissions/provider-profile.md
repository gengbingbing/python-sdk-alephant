# Alephant AI Provider Profile

## One-line description

Alephant AI is an OpenAI-compatible gateway for model routing, session headers,
and request-level usage and cost analytics.

## Short description

Alephant AI helps teams route LLM traffic through a central gateway while adding
session headers. The Python packages support direct
OpenAI-compatible requests plus helper integrations for LangChain and
LlamaIndex.

## Links

- PyPI: https://pypi.org/project/alephantai/
- LangChain PyPI: https://pypi.org/project/langchain-alephantai/
- Gateway base URL: https://ai.alephant.io/v1
- Analytics API base URL: https://alephant.io/api/v1
- Website: https://alephant.io
- Repository: https://github.com/gengbingbing/python-sdk-alephant
- Documentation: https://github.com/gengbingbing/python-sdk-alephant/tree/main/docs

## Installation

```bash
pip install alephantai
pip install langchain-alephantai
pip install "alephantai[llamaindex]"
```

## Python imports

```python
from alephantai import AlephantGatewayContext, create_openai_client
from langchain_alephantai import create_chat_openai
from alephantai.llamaindex import create_openai_embedding, create_openai_llm
```

## Keywords

```text
alephant
llm gateway
openai compatible
langchain
llamaindex
usage analytics
cost analytics
session headers
model routing
```

## Maintainer statement

Alephant AI maintains the `alephantai` Python SDK and is responsible for
compatibility with Alephant Gateway, LangChain, LlamaIndex, and OpenAI-compatible
request semantics.

## Current SDK scope

SDK v1 attaches session headers and exposes request and aggregate usage metrics
through Cockpit APIs. It does not currently provide session-level query APIs.
Full journey steps, policy events, and grading require a future step/span
contract and should not be claimed in integration submissions.
