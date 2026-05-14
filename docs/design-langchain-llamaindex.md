# Alephant Python SDK: LangChain and LlamaIndex Gateway Integration Design

Date: 2026-05-14
Status: Approved for implementation planning
Scope: `python-sdk-alephant`

## Goal

Build a Python SDK that makes Alephant Gateway easy to use from Python AI applications, especially LangChain and LlamaIndex applications.

The SDK should help developers:

- Start or reuse an Alephant session.
- Configure Alephant Gateway request headers without hand-writing header dictionaries.
- Send OpenAI-compatible requests through Alephant Gateway with minimal setup.
- Attach the same gateway/session configuration to LangChain and LlamaIndex flows.

Alephant Gateway and Collector remain the source of truth for cost, token usage, provider, model, cache behavior, and request logs. The Python SDK does not directly ingest logs and does not calculate billing facts.

## Non-Goals

- No direct POST to Collector `/v1/log/request`.
- No local cost calculation.
- No automatic `Collector-Step-Id`, `Collector-Parent-Step-Id`, or `Collector-Retry-Count` headers in v1.
- No attempt to recreate LangChain or LlamaIndex internal span trees in Alephant.
- No default behavior that changes routing, cache, prompt templating, or log omission unless explicitly configured by the user.

## Product Boundary

Alephant is a cost attribution gateway product. A request has cost attribution value when it goes through Alephant Gateway with a virtual key.

Therefore, the SDK is a gateway convenience layer:

```text
Python app
  -> Alephant Python SDK creates session/header/client config
  -> LangChain/LlamaIndex LLM client calls Alephant Gateway
  -> Gateway authenticates VK, applies routing/policy/cache, logs request
  -> Collector stores request/cost/session data
  -> Alephant UI/API queries sessions, requests, costs
```

## Package Strategy

Use one distribution with optional extras:

```bash
pip install alephantai
pip install "alephantai[langchain]"
pip install "alephantai[llamaindex]"
pip install "alephantai[langchain,llamaindex]"
```

The core package must import successfully without LangChain or LlamaIndex installed.

Proposed layout:

```text
python-sdk-alephant/
  pyproject.toml
  README.md
  docs/
    design-langchain-llamaindex.md
    gateway-headers.md
    langchain.md
    llamaindex.md
  examples/
    openai_gateway_chat.py
    langchain_chat.py
    llamaindex_rag.py
  src/
    alephantai/
      __init__.py
      config.py
      context.py
      headers.py
      openai.py
      langchain/
        __init__.py
        callback.py
        openai.py
      llamaindex/
        __init__.py
        instrumentation.py
        openai.py
  tests/
    test_context_headers.py
    test_gateway_headers.py
    test_openai_gateway_client.py
    test_langchain_callback.py
    test_llamaindex_instrumentation.py
```

## Core API

### Gateway Context

`AlephantGatewayContext` owns the session and header configuration for a logical chat, agent run, or RAG query.

```python
from alephantai import AlephantGatewayContext

ctx = AlephantGatewayContext(
    session_name="support-chat",
    session_path="/prod/support-chat",
)
```

If `session_id` is omitted, the SDK generates one. If it is provided, the SDK uses it exactly after validation.

```python
ctx = AlephantGatewayContext(session_id="support-session-001")
```

Default headers:

```python
ctx.headers()
# {
#   "Alephant-Session-Id": "sess_..."
# }
```

With optional session metadata:

```python
{
    "Alephant-Session-Id": "sess_...",
    "Alephant-Session-Name": "support-chat",
    "Alephant-Session-Path": "/prod/support-chat",
}
```

### Gateway Headers

`GatewayHeaders` models optional Alephant Gateway request headers. The SDK should provide typed configuration instead of requiring users to remember exact header names.

```python
from alephantai import AlephantGatewayContext, GatewayHeaders, CacheHeaders

ctx = AlephantGatewayContext(
    headers=GatewayHeaders(
        forced_routing="openai",
        prompt_id="prompt_123",
        cache=CacheHeaders(enabled=True, read=True, save=True),
        model_override="gpt-4o-mini",
    )
)
```

Header policy:

```text
Automatically generated:
- Alephant-Session-Id

Generated only when explicitly configured:
- Alephant-Session-Name
- Alephant-Session-Path
- alephant-property-*
- Alephant-Cache-*
- alephant-forced-routing
- alephant-prompt-id
- x-alephant-model-override
- alephant-omit-request
- alephant-omit-response
- x-alephant-webhook-enabled
- x-alephant-posthog-api-key
- x-alephant-posthog-host
- x-alephant-lytix-key

Not generated in v1:
- Collector-Step-Id
- Collector-Parent-Step-Id
- Collector-Retry-Count
```

Behavior headers are explicit because they can change gateway routing, cache semantics, prompt merging, or logging behavior.

### Properties

Custom properties are explicit:

```python
ctx = AlephantGatewayContext(
    properties={
        "framework": "langchain",
        "app": "support-agent",
    }
)
```

Output:

```http
alephant-property-framework: langchain
alephant-property-app: support-agent
```

The SDK must validate property keys and values. It should reject or omit unsafe values rather than sending sensitive or malformed data.

## OpenAI-Compatible Gateway Helper

Because Alephant Gateway is OpenAI-compatible for common `/v1/...` flows, provide a small helper to reduce setup friction:

```python
from alephantai import AlephantGatewayContext
from alephantai.openai import create_openai_client

ctx = AlephantGatewayContext(session_name="quickstart-chat")

client = create_openai_client(
    api_key="vk-...",
    base_url="https://gateway.alephant.ai/v1",
    context=ctx,
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Explain BYOK cost attribution."}],
)
```

This helper should configure the official OpenAI Python client with Alephant Gateway base URL, virtual key, and context headers.

It should not wrap every provider SDK in v1. Additional provider helpers can be added later if product usage proves demand.

## LangChain Integration

LangChain integration should focus on making a LangChain app use Alephant Gateway with the same session across calls.

The primary LangChain developer experience should be a helper that creates a gateway-configured LangChain model:

```python
from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

ctx = AlephantGatewayContext(session_name="langchain-chat")

llm = create_chat_openai(
    api_key="vk-...",
    base_url="https://gateway.alephant.ai/v1",
    context=ctx,
    model="gpt-4o-mini",
)

llm.invoke("Hello")
```

This keeps the quick path under the SDK's control: virtual key auth, gateway base URL, and `Alephant-Session-Id` are configured together.

For users who already construct their own LangChain models, expose the callback and raw headers:

```python
from alephantai import AlephantGatewayContext
from alephantai.langchain import AlephantCallbackHandler

ctx = AlephantGatewayContext(session_name="langchain-chat")
handler = AlephantCallbackHandler(context=ctx)
```

Usage with an OpenAI-compatible LangChain model:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="https://gateway.alephant.ai/v1",
    api_key="vk-...",
    default_headers=ctx.headers(),
)

llm.invoke(
    "Hello",
    config={"callbacks": [handler]},
)
```

Responsibilities:

- Provide helper factories for common OpenAI-compatible LangChain models.
- Keep the same `Alephant-Session-Id` for a chain, agent, or chat run.
- Provide a convenient callback object for LangChain users.
- Avoid throwing exceptions from callback methods by default.
- Avoid generating step or parent-step headers in v1.

The callback may record lightweight local run metadata for debugging, but it must not send it to Alephant unless a stable gateway/backend contract exists. The callback is secondary; gateway-configured model helpers are the main convenience path.

## LlamaIndex Integration

LlamaIndex integration should follow the same gateway-session model. The primary path should configure LlamaIndex LLMs and embeddings to use Alephant Gateway.

```python
from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_llm

ctx = AlephantGatewayContext(session_name="llamaindex-rag")

llm = create_openai_llm(
    api_key="vk-...",
    base_url="https://gateway.alephant.ai/v1",
    context=ctx,
    model="gpt-4o-mini",
)
```

Instrumentation remains available when users want to bind a broader query lifecycle to the same context:

```python
from alephantai import AlephantGatewayContext
from alephantai.llamaindex import AlephantLlamaIndexHandler

ctx = AlephantGatewayContext(session_name="llamaindex-rag")
handler = AlephantLlamaIndexHandler(context=ctx)
handler.install()
```

The LlamaIndex LLM and embedding models must still be configured to call Alephant Gateway and include `ctx.headers()`. The helper should do this automatically for OpenAI-compatible LlamaIndex integrations.

Responsibilities:

- Provide helper factories for common OpenAI-compatible LlamaIndex LLM and embedding models.
- Keep all LlamaIndex LLM/embedding requests in the same Alephant session.
- Use LlamaIndex instrumentation when available.
- Avoid breaking query execution if instrumentation APIs change.
- Avoid direct log ingestion and local cost calculation.

## Backend Alignment

Current backend and collector behavior:

- Gateway expects `Alephant-Session-Id` on incoming requests for session attribution.
- Collector has an RMT `session_id` column.
- Sessions analytics queries group by `request_response_rmt.session_id`.
- Step columns exist in ClickHouse migrations, but current SDK v1 does not emit step headers.

Backend-sensitive requirement:

Requests made via the SDK must go through Alephant Gateway. If users call providers directly, Alephant cannot reliably attribute gateway cost or session behavior.

## Validation and Safety

The SDK should validate generated and user-provided headers:

- `session_id`: non-empty string, max length 128.
- `session_name`: optional, max length 128.
- `session_path`: optional, max length 256, normalized to start with `/` when provided.
- property keys: lowercase-safe header suffix preferred, max length 64, no whitespace.
- property values: stringified, max length 512.
- cache bucket max size: integer `1..20`.
- booleans serialized as `"true"` / `"false"`.

Sensitive headers and values should not be generated by default. The SDK must not set `Authorization` unless a helper explicitly creates a provider client with the user-provided virtual key.

## Error Handling

Default behavior should be non-disruptive:

- Header validation errors should raise at context construction time for explicit user input.
- Framework callback errors should be swallowed and logged at debug level by default.
- `strict=True` should raise callback errors for tests and advanced debugging.
- Missing optional framework dependencies should produce clear import errors only when those integrations are imported.

## Tests

Core tests:

- Auto-generates a stable session id per context.
- Uses user-provided `session_id` unchanged after validation.
- Default headers only contain `Alephant-Session-Id`.
- Session name/path are only emitted when configured.
- Behavior headers are only emitted when configured.
- Properties are emitted as `alephant-property-*` only when configured.
- Invalid values are rejected or omitted according to the API contract.

OpenAI helper tests:

- Builds a client with the configured `base_url`.
- Injects `Alephant-Session-Id`.
- Does not mutate a context across requests unexpectedly.

LangChain tests:

- Core package imports without LangChain installed.
- LangChain integration imports when the extra is installed.
- `create_chat_openai` builds a model configured with gateway `base_url`, virtual key auth, and context headers.
- Callback methods do not raise in default mode.
- Callback uses the provided context and does not create unrelated sessions.

LlamaIndex tests:

- Core package imports without LlamaIndex installed.
- LlamaIndex integration imports when the extra is installed.
- LlamaIndex OpenAI helper builds an LLM/embedding client configured with gateway `base_url`, virtual key auth, and context headers.
- Handler install/uninstall is idempotent when possible.
- Handler uses the provided context and does not create unrelated sessions.

## Documentation

Required docs:

- `README.md`: quickstart with OpenAI-compatible gateway helper.
- `docs/gateway-headers.md`: authoritative SDK header behavior.
- `docs/langchain.md`: LangChain setup with Alephant Gateway.
- `docs/llamaindex.md`: LlamaIndex setup with Alephant Gateway.

Docs must clearly state:

- The LLM client must call Alephant Gateway.
- The SDK auto-generates `Alephant-Session-Id`.
- Users can manually specify or override `session_id`.
- Behavior-changing gateway headers require explicit configuration.
- v1 does not emit Collector step headers.

## MVP Acceptance Criteria

- A Python developer can create an Alephant gateway session in under five lines.
- A Python developer can create an OpenAI-compatible client pointed at Alephant Gateway with virtual key auth and session headers.
- A LangChain developer can create a gateway-configured `ChatOpenAI` model without manually building headers.
- A LlamaIndex developer can create a gateway-configured OpenAI-compatible LLM/embedding model without manually building headers.
- LangChain and LlamaIndex examples show how to reuse the same session context.
- Default SDK behavior only affects session attribution.
- No SDK path bypasses Alephant Gateway for cost attribution.
