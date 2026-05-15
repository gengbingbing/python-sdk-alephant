# LlamaIndex Submission Materials: Alephant AI

## Recommended positioning

Alephant AI should be submitted as a LlamaIndex LLM and embedding integration
for an OpenAI-compatible gateway. The integration should wrap the published
`alephantai` package rather than duplicating gateway header logic inside the
LlamaIndex repository.

Suggested package path in the LlamaIndex monorepo:

```text
llama-index-integrations/llms/llama-index-llms-alephantai
```

If maintainers prefer separating embeddings, use this companion package path:

```text
llama-index-integrations/embeddings/llama-index-embeddings-alephantai
```

## Package metadata draft

```toml
[project]
name = "llama-index-llms-alephantai"
description = "LlamaIndex LLM integration for Alephant AI Gateway."
requires-python = ">=3.10"
dependencies = [
  "alephantai>=0.1.0",
  "llama-index-core>=0.14,<0.15",
  "llama-index-llms-openai>=0.7,<0.8",
]

[project.optional-dependencies]
embeddings = [
  "llama-index-embeddings-openai>=0.6,<0.7",
]

[tool.llamahub]
contains_example = true
import_path = "llama_index.llms.alephantai"

[tool.llamahub.class_authors]
AlephantAI = "Alephant-AI"
```

If embeddings are accepted in the same package, add the embedding class author:

```toml
[tool.llamahub.class_authors]
AlephantAI = "Alephant-AI"
AlephantAIEmbedding = "Alephant-AI"
```

## README draft

````markdown
# Alephant AI LlamaIndex Integration

Alephant AI provides an OpenAI-compatible gateway for model routing, session
metadata, and usage/cost attribution. This package connects LlamaIndex LLM and
embedding requests to Alephant Gateway.

## Installation

```bash
pip install llama-index-llms-alephantai
````

If using the standalone Alephant SDK directly:

```bash
pip install "alephantai[llamaindex]"
```

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

response = llm.complete("Write a one-sentence summary of LlamaIndex.")
print(response)
```

## Embeddings

```python
import os

from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_embedding

ctx = AlephantGatewayContext(session_name="llamaindex-embeddings")

embed_model = create_openai_embedding(
    api_key=os.environ["ALEPHANT_API_KEY"],
    model="text-embedding-3-small",
    context=ctx,
)
```

## Session attribution

The SDK attaches Alephant gateway headers to LlamaIndex LLM and embedding
requests. Version 1 exposes request and aggregate usage metrics through Cockpit
APIs. It does not expose session-level query APIs or map LlamaIndex internal
events into complete Alephant journey steps.
```

## PR description draft

````markdown
## Summary

Adds Alephant AI as a LlamaIndex integration for routing OpenAI-compatible LLM
and embedding requests through Alephant Gateway.

The integration depends on the published `alephantai` SDK, which owns Alephant
gateway context and request header generation. This keeps the LlamaIndex package
small and avoids duplicating Alephant-specific transport logic.

## Package

- PyPI SDK: https://pypi.org/project/alephantai/
- Gateway base URL: `https://ai.alephant.io/v1`
- LLM helper: `alephantai.llamaindex.create_openai_llm`
- Embedding helper: `alephantai.llamaindex.create_openai_embedding`

## Notes

SDK v1 attaches session headers and exposes request and aggregate usage metrics
through Cockpit APIs. It does not provide session-level query APIs or map the
full LlamaIndex event tree into Alephant journey steps.
````
