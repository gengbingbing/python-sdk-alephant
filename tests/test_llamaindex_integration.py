import sys
import types

import pytest

from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_embedding, create_openai_llm


def test_create_openai_llm_passes_gateway_config(monkeypatch):
    seen = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            seen.update(kwargs)

    llama_index = types.ModuleType("llama_index")
    llms = types.ModuleType("llama_index.llms")
    openai_module = types.ModuleType("llama_index.llms.openai")
    openai_module.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "llama_index", llama_index)
    monkeypatch.setitem(sys.modules, "llama_index.llms", llms)
    monkeypatch.setitem(sys.modules, "llama_index.llms.openai", openai_module)

    ctx = AlephantGatewayContext(session_id="sess-llama")
    llm = create_openai_llm(
        api_key="vk-test",
        base_url="https://gateway.example.test/v1",
        context=ctx,
        model="gpt-4o-mini",
        default_headers={"x-user-header": "1", "alephant-session-id": "wrong"},
    )

    assert isinstance(llm, FakeOpenAI)
    assert seen["api_key"] == "vk-test"
    assert seen["api_base"] == "https://gateway.example.test/v1"
    assert seen["model"] == "gpt-4o-mini"
    assert seen["default_headers"]["x-user-header"] == "1"
    assert "alephant-session-id" not in seen["default_headers"]
    assert seen["default_headers"]["Alephant-Session-Id"] == "sess-llama"


def test_create_openai_embedding_passes_gateway_config(monkeypatch):
    seen = {}

    class FakeOpenAIEmbedding:
        def __init__(self, **kwargs):
            seen.update(kwargs)

    llama_index = types.ModuleType("llama_index")
    embeddings = types.ModuleType("llama_index.embeddings")
    openai_module = types.ModuleType("llama_index.embeddings.openai")
    openai_module.OpenAIEmbedding = FakeOpenAIEmbedding
    monkeypatch.setitem(sys.modules, "llama_index", llama_index)
    monkeypatch.setitem(sys.modules, "llama_index.embeddings", embeddings)
    monkeypatch.setitem(sys.modules, "llama_index.embeddings.openai", openai_module)

    ctx = AlephantGatewayContext(session_id="sess-llama")
    embed_model = create_openai_embedding(
        api_key="vk-test",
        base_url="https://gateway.example.test/v1",
        context=ctx,
        model="text-embedding-3-small",
        default_headers={"x-user-header": "1", "alephant-session-id": "wrong"},
    )

    assert isinstance(embed_model, FakeOpenAIEmbedding)
    assert seen["api_key"] == "vk-test"
    assert seen["api_base"] == "https://gateway.example.test/v1"
    assert seen["model"] == "text-embedding-3-small"
    assert seen["default_headers"]["x-user-header"] == "1"
    assert "alephant-session-id" not in seen["default_headers"]
    assert seen["default_headers"]["Alephant-Session-Id"] == "sess-llama"


def test_create_openai_llm_reports_missing_extra(monkeypatch):
    monkeypatch.setitem(sys.modules, "llama_index.llms.openai", None)

    with pytest.raises(ImportError, match='alephantai\\[llamaindex\\]'):
        create_openai_llm(api_key="vk-test", model="gpt-4o-mini")


def test_create_openai_embedding_reports_missing_extra(monkeypatch):
    monkeypatch.setitem(sys.modules, "llama_index.embeddings.openai", None)

    with pytest.raises(ImportError, match='alephantai\\[llamaindex\\]'):
        create_openai_embedding(api_key="vk-test", model="text-embedding-3-small")
