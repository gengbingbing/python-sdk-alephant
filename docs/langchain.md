# LangChain

```python
from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

ctx = AlephantGatewayContext(session_name="langchain-chat")
llm = create_chat_openai(api_key="vk-...", model="gpt-4o-mini", context=ctx)

llm.invoke("Hello")
```

This helper sends requests through Alephant Gateway and includes
`Alephant-Session-Id`. Current Cockpit analytics surfaces request and aggregate
usage metrics; it does not expose session-level query APIs or map LangChain's
internal span tree into complete journey steps.
