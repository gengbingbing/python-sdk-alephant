# PR Templates

## LangChain docs PR

Title:

```text
docs: add Alephant AI integration
```

Body:

````markdown
## Summary

Adds documentation for the published `alephantai` Python package, which provides
a LangChain helper for routing `ChatOpenAI` requests through Alephant Gateway.

## Package

- PyPI: https://pypi.org/project/alephantai/
- Install: `pip install "alephantai[langchain]"`
- Import: `from alephantai.langchain import create_chat_openai`

## Validation

- The package is published on PyPI.
- The example uses the public SDK API.
- The integration returns a standard `langchain_openai.ChatOpenAI` instance.
````

Reviewer notes:

```markdown
Alephant AI is submitted as a chat model gateway integration. The SDK also
contains a lightweight callback handler, but this page intentionally focuses on
the chat model helper because LangChain's current integration guidance does not
prioritize callback-only integrations.
```

## LlamaIndex integration PR

Title:

```text
add Alephant AI LLM integration
```

Body:

````markdown
## Summary

Adds Alephant AI as a LlamaIndex integration for OpenAI-compatible LLM requests
through Alephant Gateway.

Alephant Gateway supports model routing, session metadata, and request/cost
analytics. This package depends on the published `alephantai` SDK for gateway
context and header generation.

## Usage

```python
import os

from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_llm

ctx = AlephantGatewayContext(session_name="llamaindex-rag")

llm = create_openai_llm(
    api_key=os.environ["ALEPHANT_API_KEY"],
    model="gpt-4o-mini",
    context=ctx,
)
```

## Package

- SDK PyPI package: https://pypi.org/project/alephantai/
- Install standalone SDK support: `pip install "alephantai[llamaindex]"`
- Gateway base URL: `https://ai.alephant.io/v1`

## Scope

SDK v1 provides session-level request and cost attribution. It does not map the
full LlamaIndex event tree into Alephant journey steps.
````

## Common review answers

Question:

```text
Why does this depend on `alephantai` instead of implementing headers directly?
```

Answer:

````markdown
The published `alephantai` package owns gateway context construction, default
header merging, and compatibility with Alephant Gateway. Keeping that logic in
one SDK avoids drift across framework integrations.
````

Question:

```text
Is this a new model provider or an OpenAI-compatible proxy?
```

Answer:

````markdown
Alephant AI is an OpenAI-compatible gateway. The integration is intentionally
built on top of OpenAI-compatible LLM and embedding clients while adding
Alephant Gateway routing and attribution headers.
````

Question:

```text
Does this provide tracing for all LangChain or LlamaIndex internal spans?
```

Answer:

````markdown
Not in SDK v1. The current release guarantees session-level request and cost
attribution. Full framework span or journey mapping requires a future step/span
contract and is not claimed in this submission.
````
