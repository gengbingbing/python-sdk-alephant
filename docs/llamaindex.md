# LlamaIndex

```python
from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_llm

ctx = AlephantGatewayContext(session_name="llamaindex-rag")
llm = create_openai_llm(api_key="vk-...", model="gpt-4o-mini", context=ctx)
```

LLM and embedding requests must go through Alephant Gateway for cost and session
attribution. SDK v1 guarantees session-level request and cost attribution only;
it does not map LlamaIndex internal events into complete journey steps.
