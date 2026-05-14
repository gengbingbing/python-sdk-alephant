import os

from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_embedding, create_openai_llm
from llama_index.core import Document, Settings, VectorStoreIndex

ctx = AlephantGatewayContext(session_name="llamaindex-example")
llm = create_openai_llm(api_key=os.environ["ALEPHANT_VK"], model="gpt-4o-mini", context=ctx)
embed_model = create_openai_embedding(
    api_key=os.environ["ALEPHANT_VK"],
    model="text-embedding-3-small",
    context=ctx,
)

Settings.llm = llm
Settings.embed_model = embed_model

documents = [
    Document(text="Alephant Gateway routes OpenAI-compatible LLM calls and tracks session cost."),
    Document(text="Alephant Python SDK injects Alephant-Session-Id for session-level attribution."),
]
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

print(query_engine.query("How does Alephant track this session?"))
