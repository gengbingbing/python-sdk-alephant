# LangChain

```python
from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

ctx = AlephantGatewayContext(session_name="langchain-chat")
llm = create_chat_openai(api_key="vk-...", model="gpt-4o-mini", context=ctx)

llm.invoke("Hello")
```

This helper sends requests through Alephant Gateway and includes
`Alephant-Session-Id`. SDK v1 guarantees session-level request and cost
attribution only; it does not map LangChain's internal span tree into complete
journey steps.
