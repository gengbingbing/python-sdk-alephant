# Alephant Python SDK

Alephant Python SDK helps you call Alephant Gateway, generate session headers,
query Virtual Key usage and cost analytics, and integrate with LangChain or
LlamaIndex.

## Installation

```bash
pip install alephantai
pip install "alephantai[langchain]"
pip install "alephantai[llamaindex]"
```

## Gateway Chat

The production Gateway host is `https://ai.alephant.io/v1`.

```python
from alephantai import AlephantGatewayContext, create_openai_client

ctx = AlephantGatewayContext(session_name="quickstart")
client = create_openai_client(api_key="vk-...", context=ctx)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
)
```

By default, the SDK only generates `Alephant-Session-Id`. Behavior headers such
as cache controls, forced routing, and prompt template identifiers must be
configured explicitly. Version 1 guarantees session-level request and cost
attribution only; full journey steps, policy events, and grading require a
future step/span contract.

## Analytics

```python
from alephantai import AlephantAnalyticsClient

analytics = AlephantAnalyticsClient(api_key="vk-...")
print(analytics.usage_summary(period="7d"))
```
