import os

from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_llm

ctx = AlephantGatewayContext(session_name="llamaindex-example")
llm = create_openai_llm(api_key=os.environ["ALEPHANT_VK"], model="gpt-4o-mini", context=ctx)
print(llm.complete("Hello from LlamaIndex through Alephant Gateway"))
