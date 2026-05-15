# langchain-alephantai

LangChain integration package for Alephant AI Gateway.

This package currently exposes the existing Alephant LangChain helper from the
core `alephantai` SDK while keeping a standalone package boundary for the
official LangChain provider package.

```bash
pip install langchain-alephantai
```

```python
from alephantai import AlephantGatewayContext
from langchain_alephantai import create_chat_openai

llm = create_chat_openai(
    api_key="vk-...",
    model="gpt-4o-mini",
    context=AlephantGatewayContext(session_name="langchain-chat"),
)
```
