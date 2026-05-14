# LangChain

```python
from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

ctx = AlephantGatewayContext(session_name="langchain-chat")
llm = create_chat_openai(api_key="vk-...", model="gpt-4o-mini", context=ctx)

llm.invoke("Hello")
```

该 helper 会把请求发到 Alephant Gateway，并携带 `Alephant-Session-Id`。v1 只保证 session 级请求/费用归因，不把 LangChain 内部 span tree 映射成完整 journey steps。
