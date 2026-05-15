import re

import pytest

from alephantai import AlephantGatewayContext


def test_context_auto_generates_stable_session_header():
    ctx = AlephantGatewayContext()

    first = ctx.headers()
    second = ctx.headers()

    assert first == second
    assert set(first.keys()) == {"Alephant-Session-Id"}
    assert re.match(r"^sess_[A-Za-z0-9_-]{16,}$", first["Alephant-Session-Id"])


def test_context_uses_user_supplied_session_id():
    ctx = AlephantGatewayContext(session_id="support-session-001")

    assert ctx.headers() == {"Alephant-Session-Id": "support-session-001"}


def test_context_includes_optional_session_name_and_path():
    ctx = AlephantGatewayContext(session_name="support", session_path="prod/support")

    assert ctx.headers()["Alephant-Session-Name"] == "support"
    assert ctx.headers()["Alephant-Session-Path"] == "/prod/support"


def test_context_rejects_session_path_exceeding_normalized_length():
    with pytest.raises(ValueError, match="session_path"):
        AlephantGatewayContext(session_path="a" * 256)


def test_context_rejects_empty_session_id():
    with pytest.raises(ValueError, match="session_id"):
        AlephantGatewayContext(session_id="")


def test_context_rejects_control_characters_in_header_values():
    with pytest.raises(ValueError, match="control characters"):
        AlephantGatewayContext(session_id="sess_\x00bad")

    with pytest.raises(ValueError, match="control characters"):
        AlephantGatewayContext(session_name="support\x1fbad")

    with pytest.raises(ValueError, match="control characters"):
        AlephantGatewayContext(session_path="prod/\x7fbad")

    with pytest.raises(ValueError, match="control characters"):
        AlephantGatewayContext(properties={"app": "support\x00agent"})


def test_context_rejects_invalid_headers_during_construction():
    with pytest.raises(ValueError, match="headers"):
        AlephantGatewayContext(headers={})


def test_context_rejects_non_mapping_properties_during_construction():
    for properties in ([], "", 0, [("app", "x")]):
        with pytest.raises(ValueError, match="properties"):
            AlephantGatewayContext(properties=properties)


def test_context_rejects_non_scalar_property_values():
    for value in ({"api_key": "sk-test"}, ["support"], ("support",), object(), None):
        with pytest.raises(ValueError, match="property app"):
            AlephantGatewayContext(properties={"app": value})


def test_context_rejects_invalid_properties_during_construction():
    with pytest.raises(ValueError, match="property key"):
        AlephantGatewayContext(properties={"Api-Key": "secret"})

    with pytest.raises(ValueError, match="property key"):
        AlephantGatewayContext(properties={"api-key": "secret"})

    with pytest.raises(ValueError, match="property key"):
        AlephantGatewayContext(properties={"api_key": "secret"})

    with pytest.raises(ValueError, match="property key"):
        AlephantGatewayContext(properties={"apikey": "secret"})

    with pytest.raises(ValueError, match="property key"):
        AlephantGatewayContext(properties={"token": "secret"})

    with pytest.raises(ValueError, match="property app"):
        AlephantGatewayContext(properties={"app": ""})
