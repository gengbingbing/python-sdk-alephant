import httpx

from alephantai.analytics import AlephantAnalyticsClient


def test_constructor_accepts_positional_api_key():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": {"total_requests": 1}})

    client = AlephantAnalyticsClient(
        "vk-test",
        base_url="https://api.example.test/api/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.usage_summary()["total_requests"] == 1


def test_usage_summary_sends_vk_authorization_and_period():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["authorization"] = request.headers["Authorization"]
        return httpx.Response(
            200,
            json={
                "data": {
                    "total_requests": 3,
                    "total_tokens": 1200,
                    "total_cost_cents": 123,
                    "period": "7d",
                    "degraded": False,
                    "data_source": "clickhouse",
                }
            },
        )

    client = AlephantAnalyticsClient(
        api_key="vk-test",
        base_url="https://api.example.test/api/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.usage_summary(period="7d")

    assert seen["url"] == "https://api.example.test/api/v1/cockpit/usage-summary?period=7d"
    assert seen["authorization"] == "Bearer vk-test"
    assert result["total_requests"] == 3
    assert result["total_cost_cents"] == 123


def test_analytics_methods_accept_positional_parameters():
    seen_urls = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        return httpx.Response(200, json={"data": {"ok": True}})

    client = AlephantAnalyticsClient(
        "vk-test",
        base_url="https://api.example.test/api/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.usage_summary("7d") == {"ok": True}
    assert client.budget_status("7d") == {"ok": True}
    assert client.cost_by_model("7d") == {"ok": True}
    assert client.daily_costs("7d") == {"ok": True}
    assert client.recent_requests(10, 5) == {"data": {"ok": True}}

    assert seen_urls == [
        "https://api.example.test/api/v1/cockpit/usage-summary?period=7d",
        "https://api.example.test/api/v1/cockpit/budget-status?period=7d",
        "https://api.example.test/api/v1/cockpit/cost-by-model?period=7d",
        "https://api.example.test/api/v1/cockpit/daily-costs?period=7d",
        "https://api.example.test/api/v1/cockpit/recent-requests?limit=10&offset=5",
    ]


def test_scope_accepts_top_level_degraded_response():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"degraded": True, "scope": "unknown"})

    client = AlephantAnalyticsClient(
        api_key="vk-test",
        base_url="https://api.example.test/api/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.scope()["degraded"] is True


def test_degraded_response_is_returned_without_masking():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"degraded": True, "data": []})

    client = AlephantAnalyticsClient(
        api_key="vk-test",
        base_url="https://api.example.test/api/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.recent_requests()["degraded"] is True


def test_health_does_not_send_authorization():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers.get("Authorization")
        return httpx.Response(200, json={"status": "healthy"})

    client = AlephantAnalyticsClient(
        api_key="vk-test",
        base_url="https://api.example.test/api/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.health() == {"status": "healthy"}
    assert seen["authorization"] is None


def test_analytics_client_closes_owned_http_client():
    client = AlephantAnalyticsClient(api_key="vk-test")

    client.close()

    assert client._client.is_closed
