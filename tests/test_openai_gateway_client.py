from alephantai import AlephantGatewayContext
from alephantai.openai import create_openai_client, merge_default_headers


def test_create_openai_client_configures_gateway_and_session_headers():
    ctx = AlephantGatewayContext(session_id="sess-test")

    client = create_openai_client(
        api_key="vk-test",
        base_url="https://gateway.example.test/v1",
        context=ctx,
    )

    assert str(client.base_url) == "https://gateway.example.test/v1/"
    assert client.api_key == "vk-test"
    assert client.default_headers["Alephant-Session-Id"] == "sess-test"


def test_create_openai_client_accepts_positional_api_key():
    ctx = AlephantGatewayContext(session_id="sess-test")

    client = create_openai_client(
        "vk-test",
        base_url="https://gateway.example.test/v1",
        context=ctx,
    )

    assert str(client.base_url) == "https://gateway.example.test/v1/"
    assert client.api_key == "vk-test"
    assert client.default_headers["Alephant-Session-Id"] == "sess-test"


def test_create_openai_client_uses_default_gateway_base_url():
    ctx = AlephantGatewayContext(session_id="sess-test")

    client = create_openai_client("vk-test", context=ctx)

    assert str(client.base_url) == "https://ai.alephant.io/v1/"


def test_merge_default_headers_preserves_user_headers():
    headers = merge_default_headers(
        {"X-User-Header": "user-value"},
        {"Alephant-Session-Id": "sess-test"},
    )

    assert headers["X-User-Header"] == "user-value"
    assert headers["Alephant-Session-Id"] == "sess-test"


def test_merge_default_headers_removes_case_insensitive_user_duplicates():
    headers = merge_default_headers(
        {
            "alephant-session-id": "user-value",
            "X-User-Header": "user-value",
        },
        {"Alephant-Session-Id": "context-value"},
    )

    assert "alephant-session-id" not in headers
    assert headers["X-User-Header"] == "user-value"


def test_merge_default_headers_context_casing_and_value_win():
    headers = merge_default_headers(
        {"alephant-session-id": "user-value"},
        {"Alephant-Session-Id": "context-value"},
    )

    assert headers["Alephant-Session-Id"] == "context-value"
