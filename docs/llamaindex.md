# LlamaIndex

```python
from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_llm

ctx = AlephantGatewayContext(session_name="llamaindex-rag")
llm = create_openai_llm(api_key="vk-...", model="gpt-4o-mini", context=ctx)
```

LLM 和 embedding 请求必须经过 Alephant Gateway 才能进行成本和会话归因。v1 只保证 session 级请求/费用归因，不把 LlamaIndex 内部事件映射成完整 journey steps。
