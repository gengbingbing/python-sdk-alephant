import sys
import types

import pytest

from alephantai import AlephantGatewayContext
from alephantai.langchain import AlephantCallbackHandler, create_chat_openai
from alephantai.openai import DEFAULT_GATEWAY_USER_AGENT


def test_langchain_callback_reuses_context_headers():
    ctx = AlephantGatewayContext(session_id="sess-langchain")
    handler = AlephantCallbackHandler(context=ctx)

    assert handler.context.headers()["Alephant-Session-Id"] == "sess-langchain"


def test_langchain_callback_does_not_raise_by_default():
    handler = AlephantCallbackHandler(context=AlephantGatewayContext())

    handler.on_chain_start(serialized={}, inputs={})
    handler.on_chain_end(outputs={})


def test_create_chat_openai_passes_gateway_config_to_langchain(monkeypatch):
    seen = {}

    class FakeChatOpenAI:
        def __init__(self, **kwargs):
            seen.update(kwargs)

    fake_module = types.ModuleType("langchain_openai")
    fake_module.ChatOpenAI = FakeChatOpenAI
    monkeypatch.setitem(sys.modules, "langchain_openai", fake_module)

    ctx = AlephantGatewayContext(session_id="sess-langchain")
    llm = create_chat_openai(
        api_key="vk-test",
        base_url="https://gateway.example.test/v1",
        context=ctx,
        model="gpt-4o-mini",
        default_headers={"x-user-header": "1", "alephant-session-id": "wrong"},
    )

    assert isinstance(llm, FakeChatOpenAI)
    assert seen["api_key"] == "vk-test"
    assert seen["base_url"] == "https://gateway.example.test/v1"
    assert seen["model"] == "gpt-4o-mini"
    assert seen["default_headers"]["x-user-header"] == "1"
    assert "alephant-session-id" not in seen["default_headers"]
    assert seen["default_headers"]["Alephant-Session-Id"] == "sess-langchain"
    assert seen["default_headers"]["User-Agent"] == DEFAULT_GATEWAY_USER_AGENT


def test_create_chat_openai_accepts_positional_api_key_and_model(monkeypatch):
    seen = {}

    class FakeChatOpenAI:
        def __init__(self, **kwargs):
            seen.update(kwargs)

    fake_module = types.ModuleType("langchain_openai")
    fake_module.ChatOpenAI = FakeChatOpenAI
    monkeypatch.setitem(sys.modules, "langchain_openai", fake_module)

    ctx = AlephantGatewayContext(session_id="sess-langchain")
    llm = create_chat_openai(
        "vk-test",
        "gpt-4o-mini",
        context=ctx,
        base_url="https://gateway.example.test/v1",
    )

    assert isinstance(llm, FakeChatOpenAI)
    assert seen["api_key"] == "vk-test"
    assert seen["model"] == "gpt-4o-mini"
    assert seen["base_url"] == "https://gateway.example.test/v1"
    assert seen["default_headers"]["Alephant-Session-Id"] == "sess-langchain"


def test_create_chat_openai_reports_missing_extra(monkeypatch):
    monkeypatch.setitem(sys.modules, "langchain_openai", None)

    with pytest.raises(ImportError, match='alephantai\\[langchain\\]'):
        create_chat_openai(api_key="vk-test", model="gpt-4o-mini")
