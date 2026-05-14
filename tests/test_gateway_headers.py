import pytest

from alephantai import AlephantGatewayContext, CacheHeaders, GatewayHeaders


def test_behavior_headers_are_explicit_only():
    ctx = AlephantGatewayContext()

    assert "alephant-forced-routing" not in ctx.headers()
    assert "Alephant-Cache-Enabled" not in ctx.headers()


def test_explicit_gateway_headers_are_serialized():
    ctx = AlephantGatewayContext(
        session_id="sess-manual",
        headers=GatewayHeaders(
            forced_routing="openai",
            prompt_id="prompt_123",
            cache=CacheHeaders(enabled=True, read=True, save=True, bucket_max_size=3),
        ),
        properties={"framework": "langchain", "app": "support-agent"},
    )

    assert ctx.headers() == {
        "Alephant-Session-Id": "sess-manual",
        "alephant-forced-routing": "openai",
        "alephant-prompt-id": "prompt_123",
        "Alephant-Cache-Enabled": "true",
        "Alephant-Cache-Read": "true",
        "Alephant-Cache-Save": "true",
        "Alephant-Cache-Bucket-Max-Size": "3",
        "alephant-property-framework": "langchain",
        "alephant-property-app": "support-agent",
    }


def test_invalid_cache_bucket_size_is_rejected():
    with pytest.raises(ValueError, match="bucket_max_size"):
        CacheHeaders(enabled=True, bucket_max_size=21)


def test_cache_boolean_fields_reject_non_bool_values():
    for field in ("enabled", "read", "save"):
        with pytest.raises(ValueError, match=field):
            CacheHeaders(**{field: "false"})


def test_cache_seed_rejects_non_int_values():
    with pytest.raises(ValueError, match="seed"):
        CacheHeaders(seed="1")

    with pytest.raises(ValueError, match="seed"):
        CacheHeaders(seed=True)


def test_gateway_boolean_fields_reject_non_bool_values():
    for field in ("omit_request", "omit_response", "webhook_enabled"):
        with pytest.raises(ValueError, match=field):
            GatewayHeaders(**{field: "true"})


def test_gateway_false_boolean_fields_are_omitted():
    headers = GatewayHeaders(
        omit_request=False,
        omit_response=False,
        webhook_enabled=False,
    )

    assert headers.to_headers() == {}


def test_gateway_cache_rejects_non_cache_headers_values():
    with pytest.raises(ValueError, match="cache"):
        GatewayHeaders(cache={})


def test_collector_step_headers_are_not_generated():
    ctx = AlephantGatewayContext()

    assert "Collector-Step-Id" not in ctx.headers()
    assert "Collector-Parent-Step-Id" not in ctx.headers()
    assert "Collector-Retry-Count" not in ctx.headers()


def test_sensitive_observability_headers_are_not_supported():
    assert "posthog_api_key" not in GatewayHeaders.__dataclass_fields__
    assert "lytix_key" not in GatewayHeaders.__dataclass_fields__


def test_invalid_property_keys_are_rejected():
    with pytest.raises(ValueError, match="property key"):
        AlephantGatewayContext(properties={"Api-Key": "secret"}).headers()

    with pytest.raises(ValueError, match="property key"):
        AlephantGatewayContext(properties={"token": "secret"}).headers()
