import os

from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

ctx = AlephantGatewayContext(session_name="langchain-example")
llm = create_chat_openai(api_key=os.environ["ALEPHANT_VK"], model="gpt-4o-mini", context=ctx)
print(llm.invoke("Hello from LangChain through Alephant Gateway"))
