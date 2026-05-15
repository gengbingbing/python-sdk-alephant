# LlamaIndex

```python
from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_llm

ctx = AlephantGatewayContext(session_name="llamaindex-rag")
llm = create_openai_llm(api_key="vk-...", model="gpt-4o-mini", context=ctx)
```

LLM and embedding requests must go through Alephant Gateway for request and
usage analytics. Current Cockpit analytics surfaces request and aggregate usage
metrics; it does not expose session-level query APIs or map LlamaIndex internal
events into complete journey steps.
