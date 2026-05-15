import sys
import types

from alephantai import AlephantGatewayContext
from alephantai.openai import DEFAULT_GATEWAY_BASE_URL, DEFAULT_GATEWAY_USER_AGENT


def install_fake_langchain_openai(monkeypatch):
    seen = {}

    class FakeChatOpenAI:
        def __init__(self, **kwargs):
            seen.update(kwargs)

    fake_module = types.ModuleType("langchain_openai")
    fake_module.ChatOpenAI = FakeChatOpenAI
    monkeypatch.setitem(sys.modules, "langchain_openai", fake_module)
    sys.modules.pop("langchain_alephantai", None)
    sys.modules.pop("langchain_alephantai.chat_models", None)
    return FakeChatOpenAI, seen


def test_chat_alephantai_injects_gateway_defaults(monkeypatch):
    fake_chat_openai, seen = install_fake_langchain_openai(monkeypatch)

    from langchain_alephantai import ChatAlephantAI

    llm = ChatAlephantAI(
        api_key="vk-test",
        model="gpt-4o-mini",
        session_name="langchain-provider",
    )

    assert isinstance(llm, fake_chat_openai)
    assert seen["api_key"] == "vk-test"
    assert seen["model"] == "gpt-4o-mini"
    assert seen["base_url"] == DEFAULT_GATEWAY_BASE_URL
    assert seen["default_headers"]["Alephant-Session-Name"] == "langchain-provider"
    assert seen["default_headers"]["User-Agent"] == DEFAULT_GATEWAY_USER_AGENT


def test_chat_alephantai_accepts_existing_context_and_header_overrides(monkeypatch):
    install_fake_langchain_openai(monkeypatch)

    from langchain_alephantai import ChatAlephantAI

    ctx = AlephantGatewayContext(session_id="sess-provider")
    llm = ChatAlephantAI(
        api_key="vk-test",
        model="gpt-4o-mini",
        context=ctx,
        default_headers={
            "x-user-header": "1",
            "alephant-session-id": "wrong",
        },
    )

    assert llm is not None
    assert ctx.headers()["Alephant-Session-Id"] == "sess-provider"


def test_chat_alephantai_allows_custom_base_url(monkeypatch):
    _, seen = install_fake_langchain_openai(monkeypatch)

    from langchain_alephantai import ChatAlephantAI

    ChatAlephantAI(
        api_key="vk-test",
        model="gpt-4o-mini",
        base_url="https://gateway.example.test/v1",
        session_id="sess-provider",
    )

    assert seen["base_url"] == "https://gateway.example.test/v1"
    assert seen["default_headers"]["Alephant-Session-Id"] == "sess-provider"


def test_chat_alephantai_is_exported():
    import langchain_alephantai

    assert "ChatAlephantAI" in langchain_alephantai.__all__
