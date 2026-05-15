# PR Templates

## LangChain docs PR

Title:

```text
docs: add Alephant AI integration
```

Body:

````markdown
## Summary

Adds documentation for the published `langchain-alephantai` Python package,
which provides `ChatAlephantAI` for routing LangChain chat model requests
through Alephant Gateway.

## Package

- PyPI: https://pypi.org/project/langchain-alephantai/
- Install: `pip install langchain-alephantai`
- Import: `from langchain_alephantai import ChatAlephantAI`

## Validation

- The package is published on PyPI.
- The example uses the public provider package API.
- `pytest packages/langchain-alephantai/tests -q` passes with LangChain standard
  unit tests.
- Live standard integration tests are available with `ALEPHANT_API_KEY`.
````

Reviewer notes:

```markdown
Alephant AI is submitted as a chat model gateway integration. The provider
package depends on the core `alephantai` SDK for gateway context and header
generation, and exposes `ChatAlephantAI` as the LangChain-facing API.
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

Alephant Gateway supports model routing, session headers, and request/cost
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

SDK v1 attaches session headers and exposes request and aggregate usage metrics
through Cockpit APIs. It does not provide session-level query APIs or map the
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
Not in SDK v1. The current release attaches session headers and exposes request
and aggregate usage metrics through Cockpit APIs. Full framework span or journey
mapping requires a future step/span contract and is not claimed in this
submission.
````
