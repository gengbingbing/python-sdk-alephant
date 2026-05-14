import os

from alephantai import AlephantGatewayContext, create_openai_client

ctx = AlephantGatewayContext(session_name="example-chat")
client = create_openai_client(api_key=os.environ["ALEPHANT_VK"], context=ctx)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello from Alephant Gateway"}],
)
print(response.choices[0].message.content)
