# Alephant Python SDK：Gateway 集成实施计划

> **给执行 agent：** 按任务顺序实施；每个任务先写失败测试，再实现，再运行对应测试。步骤使用 checkbox（`- [ ]`）跟踪。

**目标：** 构建 Alephant Python SDK 第一版，让用户能便捷请求 Alephant Gateway、自动携带 session header、读取 Virtual Key 用量/费用（Cockpit API）统计，并接入 LangChain / LlamaIndex。

**架构边界：** SDK 是 Gateway convenience layer，不是直接写 Collector 的 ingestion SDK。核心模块负责 session/header 生成和 OpenAI-compatible Gateway client 创建；LangChain / LlamaIndex 通过 extras 提供 helper，不进入核心依赖。

**技术栈：** Python 3.10+、`httpx`、`openai`、可选 `langchain-openai`、可选 `llama-index-llms-openai`、可选 `llama-index-embeddings-openai`、`pytest`、`ruff`、`build`。

**后端契约：** Gateway 已支持把入站 `alephant-session-id` 映射到 Collector payload 的 `log.request.sessionId`，而不只是写入 log properties；SDK 发出的 session header 可以进入 RMT `session_id` 归因链路。

**生产 host：** Gateway OpenAI-compatible host 为 `https://ai.alephant.io/v1`；Cockpit API host 为 `https://alephant.io/api/v1`；低层 Analytics API host 为 `https://analytics.alephant.io`。

---

## File Structure

- Create `pyproject.toml`: package metadata, dependencies, extras, pytest/ruff config.
- Modify `README.md`: Chinese quickstart for gateway client, analytics, LangChain, LlamaIndex.
- Create `src/alephantai/__init__.py`: public exports.
- Create `src/alephantai/context.py`: `AlephantGatewayContext`.
- Create `src/alephantai/headers.py`: `GatewayHeaders`, `CacheHeaders`, validation and serialization.
- Create `src/alephantai/openai.py`: `create_openai_client`.
- Create `src/alephantai/analytics.py`: `AlephantAnalyticsClient`.
- Create `src/alephantai/langchain/__init__.py`: LangChain public exports.
- Create `src/alephantai/langchain/openai.py`: `create_chat_openai`.
- Create `src/alephantai/langchain/callback.py`: `AlephantCallbackHandler`.
- Create `src/alephantai/llamaindex/__init__.py`: LlamaIndex public exports.
- Create `src/alephantai/llamaindex/openai.py`: `create_openai_llm`, `create_openai_embedding`.
- Create `docs/gateway-headers.md`: SDK header behavior.
- Create `docs/analytics.md`: VK-authenticated usage/cost API usage.
- Create `docs/langchain.md`: LangChain setup.
- Create `docs/llamaindex.md`: LlamaIndex setup.
- Create `examples/openai_gateway_chat.py`: Gateway chat example.
- Create `examples/gateway_analytics.py`: usage/cost API example.
- Create `examples/langchain_chat.py`: LangChain helper example.
- Create `examples/llamaindex_rag.py`: LlamaIndex helper example.
- Add release note: after publish, update frontend/public quickstarts from `alephantai-saas-api`
  to the new runtime `alephantai` SDK where the user journey is Gateway usage.
- Create `tests/test_context_headers.py`: context/header tests.
- Create `tests/test_gateway_headers.py`: behavior header tests.
- Create `tests/test_openai_gateway_client.py`: OpenAI helper tests.
- Create `tests/test_analytics_client.py`: analytics tests.
- Create `tests/test_langchain_integration.py`: LangChain import/helper/callback tests.
- Create `tests/test_llamaindex_integration.py`: LlamaIndex import/helper tests.

## Task 1: Package Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/alephantai/__init__.py`
- Create: `tests/test_package_import.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing package import test**

Create `tests/test_package_import.py`:

```python
def test_core_package_imports_without_optional_frameworks():
    import alephantai

    assert alephantai.__version__ == "0.1.0"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
pytest tests/test_package_import.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'alephantai'`.

- [ ] **Step 3: Add package metadata**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling>=1.24"]
build-backend = "hatchling.build"

[project]
name = "alephantai"
version = "0.1.0"
description = "Python SDK for Alephant Gateway sessions, analytics, and framework integrations."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Alephant AI" }]
keywords = ["alephant", "llm", "gateway", "langchain", "llamaindex", "cost"]
dependencies = [
  "httpx>=0.24,<1",
  "openai>=1.0,<3",
]

[project.optional-dependencies]
langchain = [
  "langchain-core>=1,<2",
  "langchain-openai>=1.2,<2",
]
llamaindex = [
  "llama-index-core>=0.14,<0.15",
  "llama-index-llms-openai>=0.7,<0.8",
  "llama-index-embeddings-openai>=0.6,<0.7",
]
dev = ["pytest>=8", "ruff>=0.6", "build>=1.2", "twine>=5"]

[tool.hatch.build.targets.wheel]
packages = ["src/alephantai"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
line-length = 100
target-version = "py310"
```

- [ ] **Step 4: Add the minimal package module**

Create `src/alephantai/__init__.py`:

```python
"""Alephant Python SDK."""

__version__ = "0.1.0"

__all__ = ["__version__"]
```

- [ ] **Step 5: Add a minimal README**

Replace `README.md`:

```markdown
# python-sdk-alephant

Alephant Python SDK 用于便捷配置 Alephant Gateway 请求、自动生成会话 header、查询 Virtual Key 用量/费用，并接入 LangChain / LlamaIndex。
```

- [ ] **Step 6: Install editable dev package and run the import test**

Run:

```bash
python -m pip install -e ".[dev]"
pytest tests/test_package_import.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml README.md src/alephantai/__init__.py tests/test_package_import.py
git commit -m "feat: scaffold alephant python sdk"
```

## Task 2: Session Context and Gateway Headers

**Files:**
- Create: `src/alephantai/context.py`
- Create: `src/alephantai/headers.py`
- Modify: `src/alephantai/__init__.py`
- Create: `tests/test_context_headers.py`
- Create: `tests/test_gateway_headers.py`

- [ ] **Step 1: Write failing context/header tests**

Create `tests/test_context_headers.py`:

```python
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


def test_context_rejects_empty_session_id():
    with pytest.raises(ValueError, match="session_id"):
        AlephantGatewayContext(session_id="")
```

Create `tests/test_gateway_headers.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_context_headers.py tests/test_gateway_headers.py -v
```

Expected: FAIL because `AlephantGatewayContext`, `GatewayHeaders`, and `CacheHeaders` are undefined.

- [ ] **Step 3: Implement header models**

Create `src/alephantai/headers.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


def _bool_header(value: bool) -> str:
    return "true" if value else "false"


def _validate_text(name: str, value: Optional[str], max_length: int) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{name} must be a non-empty string")
    if len(value) > max_length:
        raise ValueError(f"{name} must be at most {max_length} characters")
    if "\r" in value or "\n" in value:
        raise ValueError(f"{name} must not contain newlines")
    return value


@dataclass(frozen=True)
class CacheHeaders:
    enabled: Optional[bool] = None
    read: Optional[bool] = None
    save: Optional[bool] = None
    bucket_max_size: Optional[int] = None
    seed: Optional[int] = None
    cache_control: Optional[str] = None

    def __post_init__(self) -> None:
        if self.bucket_max_size is not None and not (1 <= self.bucket_max_size <= 20):
            raise ValueError("bucket_max_size must be between 1 and 20")
        _validate_text("cache_control", self.cache_control, 128)

    def to_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.enabled is not None:
            headers["Alephant-Cache-Enabled"] = _bool_header(self.enabled)
        if self.read is not None:
            headers["Alephant-Cache-Read"] = _bool_header(self.read)
        if self.save is not None:
            headers["Alephant-Cache-Save"] = _bool_header(self.save)
        if self.bucket_max_size is not None:
            headers["Alephant-Cache-Bucket-Max-Size"] = str(self.bucket_max_size)
        if self.seed is not None:
            headers["Alephant-Cache-Seed"] = str(self.seed)
        if self.cache_control is not None:
            headers["Alephant-Cache-Control"] = self.cache_control
        return headers


@dataclass(frozen=True)
class GatewayHeaders:
    forced_routing: Optional[str] = None
    prompt_id: Optional[str] = None
    omit_request: Optional[bool] = None
    omit_response: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    cache: Optional[CacheHeaders] = None

    def __post_init__(self) -> None:
        _validate_text("forced_routing", self.forced_routing, 64)
        _validate_text("prompt_id", self.prompt_id, 128)

    def to_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.forced_routing is not None:
            headers["alephant-forced-routing"] = self.forced_routing
        if self.prompt_id is not None:
            headers["alephant-prompt-id"] = self.prompt_id
        if self.omit_request is True:
            headers["alephant-omit-request"] = "true"
        if self.omit_response is True:
            headers["alephant-omit-response"] = "true"
        if self.webhook_enabled is True:
            headers["x-alephant-webhook-enabled"] = "true"
        if self.cache is not None:
            headers.update(self.cache.to_headers())
        return headers
```

- [ ] **Step 4: Implement gateway context**

Create `src/alephantai/context.py`:

```python
from __future__ import annotations

import re
import secrets
import string
from typing import Dict, Mapping, Optional

from .headers import GatewayHeaders

_ID_ALPHABET = string.ascii_letters + string.digits + "_-"
_PROPERTY_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_SENSITIVE_PROPERTY_KEY_PARTS = ("token", "secret", "password", "api_key", "apikey")


def _new_session_id() -> str:
    return "sess_" + "".join(secrets.choice(_ID_ALPHABET) for _ in range(24))


def _validate_header_value(name: str, value: str, max_length: int) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{name} must be a non-empty string")
    if len(value) > max_length:
        raise ValueError(f"{name} must be at most {max_length} characters")
    if "\r" in value or "\n" in value:
        raise ValueError(f"{name} must not contain newlines")
    return value


def _normalize_path(path: Optional[str]) -> Optional[str]:
    if path is None:
        return None
    value = _validate_header_value("session_path", path, 256)
    return value if value.startswith("/") else f"/{value}"


def _property_header_name(key: str) -> str:
    if not isinstance(key, str) or not _PROPERTY_KEY_RE.fullmatch(key):
        raise ValueError("property key must match ^[a-z0-9][a-z0-9_-]{0,63}$")
    if any(part in key for part in _SENSITIVE_PROPERTY_KEY_PARTS):
        raise ValueError("property key must not look like a secret")
    return f"alephant-property-{key}"


class AlephantGatewayContext:
    def __init__(
        self,
        *,
        session_id: Optional[str] = None,
        session_name: Optional[str] = None,
        session_path: Optional[str] = None,
        headers: Optional[GatewayHeaders] = None,
        properties: Optional[Mapping[str, object]] = None,
    ) -> None:
        self.session_id = (
            _validate_header_value("session_id", session_id, 128)
            if session_id is not None
            else _new_session_id()
        )
        self.session_name = (
            _validate_header_value("session_name", session_name, 128)
            if session_name is not None
            else None
        )
        self.session_path = _normalize_path(session_path)
        self.gateway_headers = headers
        self.properties = dict(properties or {})

    def headers(self) -> Dict[str, str]:
        result: Dict[str, str] = {"Alephant-Session-Id": self.session_id}
        if self.session_name is not None:
            result["Alephant-Session-Name"] = self.session_name
        if self.session_path is not None:
            result["Alephant-Session-Path"] = self.session_path
        if self.gateway_headers is not None:
            result.update(self.gateway_headers.to_headers())
        for key, raw_value in self.properties.items():
            value = _validate_header_value(f"property {key}", str(raw_value), 512)
            result[_property_header_name(key)] = value
        return result
```

- [ ] **Step 5: Export public classes**

Modify `src/alephantai/__init__.py`:

```python
"""Alephant Python SDK."""

from .context import AlephantGatewayContext
from .headers import CacheHeaders, GatewayHeaders

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "AlephantGatewayContext",
    "CacheHeaders",
    "GatewayHeaders",
]
```

- [ ] **Step 6: Run tests**

Run:

```bash
pytest tests/test_context_headers.py tests/test_gateway_headers.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/alephantai/__init__.py src/alephantai/context.py src/alephantai/headers.py tests/test_context_headers.py tests/test_gateway_headers.py
git commit -m "feat: add gateway session headers"
```

## Task 3: OpenAI-Compatible Gateway Client Helper

**Files:**
- Create: `src/alephantai/openai.py`
- Create: `tests/test_openai_gateway_client.py`
- Modify: `src/alephantai/__init__.py`

- [ ] **Step 1: Write failing helper tests**

Create `tests/test_openai_gateway_client.py`:

```python
from alephantai import AlephantGatewayContext
from alephantai.openai import create_openai_client


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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_openai_gateway_client.py -v
```

Expected: FAIL because `alephantai.openai` does not exist.

- [ ] **Step 3: Implement OpenAI helper**

Create `src/alephantai/openai.py`:

```python
from __future__ import annotations

from typing import Dict, Mapping, Optional

from openai import OpenAI

from .context import AlephantGatewayContext

DEFAULT_GATEWAY_BASE_URL = "https://ai.alephant.io/v1"


def merge_default_headers(
    user_headers: Optional[Mapping[str, str]],
    context_headers: Mapping[str, str],
) -> Dict[str, str]:
    """Merge headers with Alephant context headers winning case-insensitively."""
    merged = dict(user_headers or {})
    context_lower = {name.lower() for name in context_headers}
    for name in list(merged):
        if name.lower() in context_lower:
            del merged[name]
    merged.update(context_headers)
    return merged


def create_openai_client(
    *,
    api_key: str,
    context: Optional[AlephantGatewayContext] = None,
    base_url: str = DEFAULT_GATEWAY_BASE_URL,
) -> OpenAI:
    """Create an OpenAI-compatible client configured for Alephant Gateway."""
    ctx = context or AlephantGatewayContext()
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers=ctx.headers(),
    )
```

- [ ] **Step 4: Export helper**

Modify `src/alephantai/__init__.py`:

```python
"""Alephant Python SDK."""

from .context import AlephantGatewayContext
from .headers import CacheHeaders, GatewayHeaders
from .openai import create_openai_client

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "AlephantGatewayContext",
    "CacheHeaders",
    "GatewayHeaders",
    "create_openai_client",
]
```

- [ ] **Step 5: Run test**

Run:

```bash
pytest tests/test_openai_gateway_client.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/alephantai/__init__.py src/alephantai/openai.py tests/test_openai_gateway_client.py
git commit -m "feat: add openai gateway helper"
```

## Task 4: Virtual Key Cockpit Analytics Client

**Files:**
- Create: `src/alephantai/analytics.py`
- Create: `tests/test_analytics_client.py`
- Modify: `src/alephantai/__init__.py`

- [ ] **Step 1: Write failing analytics tests**

Create `tests/test_analytics_client.py`:

```python
import httpx

from alephantai.analytics import AlephantAnalyticsClient


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_analytics_client.py -v
```

Expected: FAIL because `AlephantAnalyticsClient` does not exist.

- [ ] **Step 3: Implement analytics client**

Create `src/alephantai/analytics.py`:

```python
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

DEFAULT_API_BASE_URL = "https://alephant.io/api/v1"


class AlephantAnalyticsClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_API_BASE_URL,
        http_client: Optional[httpx.Client] = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "AlephantAnalyticsClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _get_raw(self, path: str, **params: object) -> Dict[str, Any]:
        clean_params = {key: value for key, value in params.items() if value is not None}
        response = self._client.get(
            f"{self.base_url}{path}",
            params=clean_params,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Alephant analytics response must be a JSON object")
        return data

    def _get_data(self, path: str, **params: object) -> Any:
        envelope = self._get_raw(path, **params)
        if "data" not in envelope:
            raise ValueError("Alephant analytics data response must contain a data field")
        return envelope["data"]

    def _get_data_or_raw(self, path: str, **params: object) -> Any:
        envelope = self._get_raw(path, **params)
        return envelope["data"] if "data" in envelope else envelope

    def usage_summary(self, *, period: str = "billing_cycle") -> Any:
        return self._get_data("/cockpit/usage-summary", period=period)

    def budget_status(self, *, period: Optional[str] = None) -> Any:
        return self._get_data("/cockpit/budget-status", period=period)

    def cost_by_model(self, *, period: str = "billing_cycle") -> Any:
        return self._get_data("/cockpit/cost-by-model", period=period)

    def daily_costs(self, *, period: str = "billing_cycle") -> Any:
        return self._get_data("/cockpit/daily-costs", period=period)

    def scope(self) -> Any:
        return self._get_data_or_raw("/cockpit/scope")

    def recent_requests(self, *, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self._get_raw("/cockpit/recent-requests", limit=limit, offset=offset)

    def health(self) -> Dict[str, Any]:
        response = self._client.get(f"{self.base_url}/cockpit/health")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Alephant analytics response must be a JSON object")
        return data
```

- [ ] **Step 4: Export analytics client**

Modify `src/alephantai/__init__.py`:

```python
"""Alephant Python SDK."""

from .analytics import AlephantAnalyticsClient
from .context import AlephantGatewayContext
from .headers import CacheHeaders, GatewayHeaders
from .openai import create_openai_client

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "AlephantAnalyticsClient",
    "AlephantGatewayContext",
    "CacheHeaders",
    "GatewayHeaders",
    "create_openai_client",
]
```

- [ ] **Step 5: Run analytics tests**

Run:

```bash
pytest tests/test_analytics_client.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/alephantai/__init__.py src/alephantai/analytics.py tests/test_analytics_client.py
git commit -m "feat: add cockpit analytics client"
```

## Task 5: LangChain Integration

**Files:**
- Create: `src/alephantai/langchain/__init__.py`
- Create: `src/alephantai/langchain/openai.py`
- Create: `src/alephantai/langchain/callback.py`
- Create: `tests/test_langchain_integration.py`

- [ ] **Step 1: Write failing LangChain tests**

Create `tests/test_langchain_integration.py`:

```python
import sys
import types

import pytest

from alephantai import AlephantGatewayContext
from alephantai.langchain import AlephantCallbackHandler, create_chat_openai


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


def test_create_chat_openai_reports_missing_extra(monkeypatch):
    monkeypatch.setitem(sys.modules, "langchain_openai", None)

    with pytest.raises(ImportError, match='alephantai\\[langchain\\]'):
        create_chat_openai(api_key="vk-test", model="gpt-4o-mini")
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_langchain_integration.py -v
```

Expected: FAIL because `alephantai.langchain` does not exist.

- [ ] **Step 3: Implement LangChain callback**

Create `src/alephantai/langchain/callback.py`:

```python
from __future__ import annotations

import logging
from typing import Any, Optional

from alephantai.context import AlephantGatewayContext

logger = logging.getLogger(__name__)

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    class BaseCallbackHandler:  # type: ignore[no-redef]
        pass


class AlephantCallbackHandler(BaseCallbackHandler):
    """Lightweight LangChain callback that keeps an Alephant context available."""

    def __init__(self, *, context: Optional[AlephantGatewayContext] = None, strict: bool = False) -> None:
        super().__init__()
        self.context = context or AlephantGatewayContext()
        self.strict = strict
        self.raise_error = strict

    def on_chain_start(self, serialized: Any, inputs: Any, **kwargs: Any) -> None:
        return None

    def on_chain_end(self, outputs: Any, **kwargs: Any) -> None:
        return None

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        if self.strict:
            logger.debug("Alephant LangChain callback observed chain error: %s", error)
        return None

    def on_llm_start(self, serialized: Any, prompts: Any, **kwargs: Any) -> None:
        return None

    def on_chat_model_start(self, serialized: Any, messages: Any, **kwargs: Any) -> None:
        return None

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        return None

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        if self.strict:
            logger.debug("Alephant LangChain callback observed LLM error: %s", error)
        return None
```

- [ ] **Step 4: Implement LangChain OpenAI helper**

Create `src/alephantai/langchain/openai.py`:

```python
from __future__ import annotations

from typing import Optional

from alephantai.context import AlephantGatewayContext
from alephantai.openai import DEFAULT_GATEWAY_BASE_URL, merge_default_headers


def create_chat_openai(
    *,
    api_key: str,
    model: str,
    context: Optional[AlephantGatewayContext] = None,
    base_url: str = DEFAULT_GATEWAY_BASE_URL,
    **kwargs: object,
):
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ImportError(
            'Install LangChain support with: pip install "alephantai[langchain]"'
        ) from exc

    ctx = context or AlephantGatewayContext()
    default_headers = merge_default_headers(
        kwargs.pop("default_headers", None),
        ctx.headers(),
    )
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        default_headers=default_headers,
        **kwargs,
    )
```

- [ ] **Step 5: Export LangChain integration**

Create `src/alephantai/langchain/__init__.py`:

```python
from .callback import AlephantCallbackHandler
from .openai import create_chat_openai

__all__ = ["AlephantCallbackHandler", "create_chat_openai"]
```

- [ ] **Step 6: Run LangChain tests**

Run:

```bash
pytest tests/test_langchain_integration.py -v
```

Expected: PASS. Optional framework modules are mocked, and missing-extra behavior is tested directly.

- [ ] **Step 7: Commit**

```bash
git add src/alephantai/langchain tests/test_langchain_integration.py
git commit -m "feat: add langchain gateway helpers"
```

## Task 6: LlamaIndex Integration

**Files:**
- Create: `src/alephantai/llamaindex/__init__.py`
- Create: `src/alephantai/llamaindex/openai.py`
- Create: `tests/test_llamaindex_integration.py`

- [ ] **Step 1: Write failing LlamaIndex tests**

Create `tests/test_llamaindex_integration.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_llamaindex_integration.py -v
```

Expected: FAIL because `alephantai.llamaindex` does not exist.

- [ ] **Step 3: Implement LlamaIndex OpenAI helpers**

Create `src/alephantai/llamaindex/openai.py`:

```python
from __future__ import annotations

from typing import Optional

from alephantai.context import AlephantGatewayContext
from alephantai.openai import DEFAULT_GATEWAY_BASE_URL, merge_default_headers


def create_openai_llm(
    *,
    api_key: str,
    model: str,
    context: Optional[AlephantGatewayContext] = None,
    base_url: str = DEFAULT_GATEWAY_BASE_URL,
    **kwargs: object,
):
    try:
        from llama_index.llms.openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            'Install LlamaIndex support with: pip install "alephantai[llamaindex]"'
        ) from exc

    ctx = context or AlephantGatewayContext()
    default_headers = merge_default_headers(
        kwargs.pop("default_headers", None),
        ctx.headers(),
    )
    return OpenAI(
        api_key=api_key,
        api_base=base_url,
        model=model,
        default_headers=default_headers,
        **kwargs,
    )


def create_openai_embedding(
    *,
    api_key: str,
    model: str,
    context: Optional[AlephantGatewayContext] = None,
    base_url: str = DEFAULT_GATEWAY_BASE_URL,
    **kwargs: object,
):
    try:
        from llama_index.embeddings.openai import OpenAIEmbedding
    except ImportError as exc:
        raise ImportError(
            'Install LlamaIndex support with: pip install "alephantai[llamaindex]"'
        ) from exc

    ctx = context or AlephantGatewayContext()
    default_headers = merge_default_headers(
        kwargs.pop("default_headers", None),
        ctx.headers(),
    )
    return OpenAIEmbedding(
        api_key=api_key,
        api_base=base_url,
        model=model,
        default_headers=default_headers,
        **kwargs,
    )
```

- [ ] **Step 4: Export LlamaIndex integration**

Create `src/alephantai/llamaindex/__init__.py`:

```python
from .openai import create_openai_embedding, create_openai_llm

__all__ = ["create_openai_embedding", "create_openai_llm"]
```

- [ ] **Step 5: Run tests**

Run:

```bash
pytest tests/test_llamaindex_integration.py -v
```

Expected: PASS. Optional framework modules are mocked, and missing-extra behavior is tested directly.

- [ ] **Step 6: Commit**

```bash
git add src/alephantai/llamaindex tests/test_llamaindex_integration.py
git commit -m "feat: add llamaindex gateway helpers"
```

## Task 7: Documentation and Examples

**Files:**
- Modify: `README.md`
- Create: `docs/gateway-headers.md`
- Create: `docs/analytics.md`
- Create: `docs/langchain.md`
- Create: `docs/llamaindex.md`
- Create: `examples/openai_gateway_chat.py`
- Create: `examples/gateway_analytics.py`
- Create: `examples/langchain_chat.py`
- Create: `examples/llamaindex_rag.py`

- [ ] **Step 1: Write README quickstart**

Replace `README.md`:

```markdown
# Alephant Python SDK

Alephant Python SDK 用于便捷请求 Alephant Gateway、自动生成会话 header、查询 Virtual Key 用量/费用，并接入 LangChain / LlamaIndex。

## 安装

```bash
pip install alephantai
pip install "alephantai[langchain]"
pip install "alephantai[llamaindex]"
```

## Gateway Chat

```python
from alephantai import AlephantGatewayContext, create_openai_client

ctx = AlephantGatewayContext(session_name="quickstart")
client = create_openai_client(api_key="vk-...", context=ctx)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
)
```

SDK 默认只自动生成 `Alephant-Session-Id`。缓存、强制路由、prompt 模板等行为类 header 需要显式配置。v1 只保证 session 级请求/费用归因；完整 journey steps、policy events、grade 需要后续 step/span 契约。

## Analytics

```python
from alephantai import AlephantAnalyticsClient

analytics = AlephantAnalyticsClient(api_key="vk-...")
print(analytics.usage_summary(period="7d"))
```
```

- [ ] **Step 2: Write gateway headers docs**

Create `docs/gateway-headers.md`:

```markdown
# Gateway Headers

SDK 自动生成：

- `Alephant-Session-Id`

用户显式配置才生成：

- `Alephant-Session-Name`
- `Alephant-Session-Path`
- `alephant-property-*`
- `Alephant-Cache-Enabled`
- `Alephant-Cache-Read`
- `Alephant-Cache-Save`
- `Alephant-Cache-Bucket-Max-Size`
- `Alephant-Cache-Seed`
- `Alephant-Cache-Control`
- `alephant-forced-routing`
- `alephant-prompt-id`
- `alephant-omit-request`
- `alephant-omit-response`
- `x-alephant-webhook-enabled`，仅显式启用时发送，不发送 `false`

SDK v1 不暴露 PostHog/Lytix 等敏感观测配置 header；这些应在服务端/workspace 配置中管理。

v1 不生成：

- `Collector-Step-Id`
- `Collector-Parent-Step-Id`
- `Collector-Retry-Count`
```

- [ ] **Step 3: Write analytics docs**

Create `docs/analytics.md`:

```markdown
# Analytics

`AlephantAnalyticsClient` 默认使用 `https://alephant.io/api/v1`，并通过 `Authorization: Bearer vk-...` 查询 Virtual Key 认证的用量/费用（Cockpit API）数据。Cockpit API 由 SaaS 后端暴露；低层 Collector Analytics API 的 host 是 `https://analytics.alephant.io`，不要和 Cockpit API 混用。实时 usage、daily costs、cost by model、budget spent 依赖该 VK 绑定到 agent 或 member；建议先调用 `scope()` 判断当前 key 的 scope/entity。v1 只保证 session 级请求/费用归因；完整 journey steps、policy events、grade 需要后续 step/span 契约。

支持：

- `usage_summary(period="billing_cycle")`
- `budget_status(period=None)`
- `cost_by_model(period="billing_cycle")`
- `daily_costs(period="billing_cycle")`
- `scope()`
- `recent_requests(limit=20, offset=0)`
- `health()`

`usage_summary()`、`budget_status()`、`cost_by_model()` 和 `daily_costs()` 返回后端 `data` payload；`scope()` 有 `data` 时返回 `data`，没有 `data` 时返回后端顶层 JSON；`recent_requests()` 和 `health()` 返回后端顶层 JSON。调用方需要检查 `degraded` / `data_source`，并按后端字段单位处理 `cost_cents`、`spent_cents` 等金额字段。`recent_requests()` 当前可能返回 `degraded=true` 的空列表。v1 不提供管理员级 workspace analytics。
```

- [ ] **Step 4: Write LangChain docs**

Create `docs/langchain.md`:

```markdown
# LangChain

```python
from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

ctx = AlephantGatewayContext(session_name="langchain-chat")
llm = create_chat_openai(api_key="vk-...", model="gpt-4o-mini", context=ctx)

llm.invoke("Hello")
```

该 helper 会把请求发到 Alephant Gateway，并携带 `Alephant-Session-Id`。v1 只保证 session 级请求/费用归因，不把 LangChain 内部 span tree 映射成完整 journey steps。
```

- [ ] **Step 5: Write LlamaIndex docs**

Create `docs/llamaindex.md`:

```markdown
# LlamaIndex

```python
from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_llm

ctx = AlephantGatewayContext(session_name="llamaindex-rag")
llm = create_openai_llm(api_key="vk-...", model="gpt-4o-mini", context=ctx)
```

LLM 和 embedding 请求必须经过 Alephant Gateway 才能进行成本和会话归因。v1 只保证 session 级请求/费用归因，不把 LlamaIndex 内部事件映射成完整 journey steps。
```

- [ ] **Step 6: Add examples**

Create `examples/openai_gateway_chat.py`:

```python
import os

from alephantai import AlephantGatewayContext, create_openai_client

ctx = AlephantGatewayContext(session_name="example-chat")
client = create_openai_client(api_key=os.environ["ALEPHANT_VK"], context=ctx)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello from Alephant Gateway"}],
)
print(response.choices[0].message.content)
```

Create `examples/gateway_analytics.py`:

```python
import os

from alephantai import AlephantAnalyticsClient

client = AlephantAnalyticsClient(api_key=os.environ["ALEPHANT_VK"])
print(client.usage_summary(period="7d"))
```

Create `examples/langchain_chat.py`:

```python
import os

from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

ctx = AlephantGatewayContext(session_name="langchain-example")
llm = create_chat_openai(api_key=os.environ["ALEPHANT_VK"], model="gpt-4o-mini", context=ctx)
print(llm.invoke("Hello from LangChain through Alephant Gateway"))
```

Create `examples/llamaindex_rag.py`:

```python
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
```

- [ ] **Step 7: Commit**

```bash
git add README.md docs/gateway-headers.md docs/analytics.md docs/langchain.md docs/llamaindex.md examples
git commit -m "docs: add gateway sdk usage guides"
```

## Task 8: Final Verification

**Files:**
- Modify only if verification exposes issues.

- [ ] **Step 1: Run full test suite**

Run:

```bash
pytest -v
```

Expected: PASS. Optional framework dependencies are mocked in unit tests; missing-extra behavior is tested explicitly.

- [ ] **Step 2: Run ruff**

Run:

```bash
ruff check .
```

Expected: PASS.

- [ ] **Step 3: Build package**

Run:

```bash
python -m build
```

Expected: `dist/alephantai-0.1.0-py3-none-any.whl` and source distribution are created.

- [ ] **Step 4: Check package metadata**

Run:

```bash
twine check dist/*
```

Expected: PASS.

- [ ] **Step 5: Install built wheel in a clean venv**

Run:

```bash
python -m venv /tmp/alephantai-wheel-smoke
/tmp/alephantai-wheel-smoke/bin/python -m pip install dist/alephantai-0.1.0-py3-none-any.whl
/tmp/alephantai-wheel-smoke/bin/python -m pip check
/tmp/alephantai-wheel-smoke/bin/python -I -c "import alephantai; print(alephantai.__version__)"
```

Expected: prints `0.1.0`.

- [ ] **Step 6: Smoke test real optional dependencies**

Run:

```bash
python -m venv /tmp/alephantai-langchain-smoke
/tmp/alephantai-langchain-smoke/bin/python -m pip install "dist/alephantai-0.1.0-py3-none-any.whl[langchain]"
/tmp/alephantai-langchain-smoke/bin/python -m pip check
/tmp/alephantai-langchain-smoke/bin/python - <<'PY'
from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

llm = create_chat_openai(api_key="vk-test", model="gpt-4o-mini", context=AlephantGatewayContext(session_id="sess-smoke"))
print(type(llm).__name__)
PY

python -m venv /tmp/alephantai-llamaindex-smoke
/tmp/alephantai-llamaindex-smoke/bin/python -m pip install "dist/alephantai-0.1.0-py3-none-any.whl[llamaindex]"
/tmp/alephantai-llamaindex-smoke/bin/python -m pip check
/tmp/alephantai-llamaindex-smoke/bin/python - <<'PY'
from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_embedding, create_openai_llm

ctx = AlephantGatewayContext(session_id="sess-smoke")
print(type(create_openai_llm(api_key="vk-test", model="gpt-4o-mini", context=ctx)).__name__)
print(type(create_openai_embedding(api_key="vk-test", model="text-embedding-3-small", context=ctx)).__name__)
PY
```

Expected: both optional extras install cleanly from the built wheel, `pip check` passes, and real LangChain/LlamaIndex constructors work without making network calls.

- [ ] **Step 7: Inspect git status**

Run:

```bash
git status --short
```

Expected: only intentional files are modified; no generated caches are staged.

- [ ] **Step 8: Commit final fixes if needed**

If verification required changes, stage only SDK source, test, doc, example, and packaging files:

```bash
git add pyproject.toml README.md src/alephantai tests docs examples
git commit -m "fix: stabilize sdk verification"
```

If no changes were needed, do not create an empty commit.

## Task 9: Release Checklist

**Files:**
- Modify only release docs/changelog/frontend quickstarts as needed.

- [ ] Confirm `alephantai` PyPI ownership/name reservation and trusted publishing configuration.
- [ ] Verify production hosts in docs: Gateway `https://ai.alephant.io/v1`, Cockpit `https://alephant.io/api/v1`, Analytics `https://analytics.alephant.io`.
- [ ] Publish to TestPyPI and install from TestPyPI in a clean venv.
- [ ] Publish to PyPI.
- [ ] Verify `pip install alephantai`, `pip install "alephantai[langchain]"`, and `pip install "alephantai[llamaindex]"`.
- [ ] Tag the release and write changelog/release notes.
- [ ] Update frontend/public quickstarts so runtime Gateway usage points to `alephantai`, while `alephantai-saas-api` remains only for SaaS/admin API usage.

## Self-Review Notes

- Spec coverage: plan covers package skeleton, session/header defaults, explicit behavior headers, OpenAI Gateway helper, VK-authenticated usage/cost APIs, LangChain helper/callback, LlamaIndex helpers, docs, examples, and final verification.
- Placeholder scan: no placeholder markers or vague implementation steps remain.
- Type consistency: public names are consistent across tasks: `AlephantGatewayContext`, `GatewayHeaders`, `CacheHeaders`, `create_openai_client`, `AlephantAnalyticsClient`, `create_chat_openai`, `AlephantCallbackHandler`, `create_openai_llm`, `create_openai_embedding`.
