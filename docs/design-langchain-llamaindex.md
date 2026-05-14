# Alephant Python SDK：LangChain / LlamaIndex 网关集成设计

日期：2026-05-14  
状态：已确认，进入实施计划前复审  
范围：`python-sdk-alephant`

## 目标

构建一个 Python SDK，让 Python AI 应用可以更方便地使用 Alephant Gateway，尤其是 LangChain 和 LlamaIndex 应用。

SDK 应帮助开发者：

- 快速创建或复用 Alephant 会话。
- 自动生成并携带 `Alephant-Session-Id`。
- 用类型化配置生成 Alephant Gateway 请求头，避免手写 header 字典。
- 快速创建 OpenAI-compatible Gateway client。
- 快速创建已配置好 Alephant Gateway 的 LangChain / LlamaIndex LLM client。
- 可选读取 VK 认证的用量、成本、预算和模型分布；实时统计依赖 VK 绑定到 agent/member。

Alephant Gateway 和 Collector 仍然是成本、tokens、provider、model、缓存行为、请求日志的事实来源。Python SDK 不直接写 Collector，不在本地计算账单事实。

## 非目标

- 不直接 POST 到 Collector `/v1/log/request`。
- 不在 SDK 本地计算成本或账单。
- v1 不自动生成 `Collector-Step-Id`、`Collector-Parent-Step-Id`、`Collector-Retry-Count`。
- v1 不尝试把 LangChain / LlamaIndex 的内部 span tree 还原成 Alephant step tree。
- 不默认改变网关行为，例如强制路由、缓存、prompt 模板合并、日志省略等。
- 不用 SDK 绕过 Alephant Gateway 调用上游 provider。

## 产品边界

Alephant 是成本归因类网关产品。一次 AI 请求只有经过 Alephant Gateway，才具备完整的成本归因、会话归因、策略、缓存、日志和审计意义。

SDK 的定位是 **Gateway convenience layer**：

```text
Python 应用
  -> Alephant Python SDK 创建 session / headers / gateway client
  -> LangChain 或 LlamaIndex 通过 SDK helper 调用 Alephant Gateway
  -> Gateway 校验 Virtual Key，执行路由、策略、缓存、日志
  -> Collector 落库请求、成本、tokens、session 数据
  -> Alephant UI/API 查询 Sessions、Requests、Costs、Usage
```

## 包策略

使用一个 Python distribution，通过 extras 控制可选框架依赖：

```bash
pip install alephantai
pip install "alephantai[langchain]"
pip install "alephantai[llamaindex]"
pip install "alephantai[langchain,llamaindex]"
```

核心包必须在没有安装 LangChain / LlamaIndex 的情况下正常 import。
v1 建议支持 Python 3.10+，以匹配当前 LangChain / LlamaIndex split packages 的实际 Python 版本要求。

建议目录：

```text
python-sdk-alephant/
  pyproject.toml
  README.md
  docs/
    design-langchain-llamaindex.md
    gateway-headers.md
    analytics.md
    langchain.md
    llamaindex.md
  examples/
    openai_gateway_chat.py
    gateway_analytics.py
    langchain_chat.py
    llamaindex_rag.py
  src/
    alephantai/
      __init__.py
      config.py
      context.py
      headers.py
      openai.py
      analytics.py
      langchain/
        __init__.py
        callback.py
        openai.py
      llamaindex/
        __init__.py
        openai.py
  tests/
    test_context_headers.py
    test_gateway_headers.py
    test_openai_gateway_client.py
    test_analytics_client.py
    test_langchain_callback.py
    test_llamaindex_integration.py
```

## 核心 API

### AlephantGatewayContext

`AlephantGatewayContext` 表示一次 chat、agent run、RAG query 或业务会话的网关上下文。

```python
from alephantai import AlephantGatewayContext

ctx = AlephantGatewayContext(
    session_name="support-chat",
    session_path="/prod/support-chat",
)
```

如果用户不传 `session_id`，SDK 自动生成一个稳定的 session id。  
如果用户显式传入 `session_id`，SDK 校验后按原值使用。

```python
ctx = AlephantGatewayContext(session_id="support-session-001")
```

默认输出：

```python
ctx.headers()
# {
#   "Alephant-Session-Id": "sess_..."
# }
```

配置了会话元数据时：

```python
{
    "Alephant-Session-Id": "sess_...",
    "Alephant-Session-Name": "support-chat",
    "Alephant-Session-Path": "/prod/support-chat",
}
```

### GatewayHeaders

`GatewayHeaders` 用类型化方式描述可选 Alephant Gateway header。

```python
from alephantai import AlephantGatewayContext, GatewayHeaders, CacheHeaders

ctx = AlephantGatewayContext(
    headers=GatewayHeaders(
        forced_routing="openai",
        prompt_id="prompt_123",
        cache=CacheHeaders(enabled=True, read=True, save=True),
    )
)
```

Header 策略：

```text
SDK 自动生成：
- Alephant-Session-Id

用户显式配置才生成：
- Alephant-Session-Name
- Alephant-Session-Path
- alephant-property-*
- Alephant-Cache-Enabled
- Alephant-Cache-Read
- Alephant-Cache-Save
- Alephant-Cache-Bucket-Max-Size
- Alephant-Cache-Seed
- Alephant-Cache-Control
- alephant-forced-routing
- alephant-prompt-id
- alephant-omit-request
- alephant-omit-response
- x-alephant-webhook-enabled

v1 不生成：
- Collector-Step-Id
- Collector-Parent-Step-Id
- Collector-Retry-Count
```

行为类 header 必须显式配置，因为它们会改变网关行为，例如路由、缓存、prompt 合并或日志保存。

HTTP header 名大小写不敏感。SDK 对会话头使用 `Alephant-Session-Id` / `Alephant-Session-Name` /
`Alephant-Session-Path` 作为文档和示例里的规范写法；网关侧也应继续接受小写形式。

`x-alephant-webhook-enabled` 是 presence-based header，只有用户显式启用时才发送；不发送 `false`。

SDK v1 不暴露 `x-alephant-model-override`、`x-alephant-posthog-api-key`、`x-alephant-posthog-host`、`x-alephant-lytix-key` 等日志/观测配置头；这些应在服务端或 workspace 配置中管理，避免在客户端代码、代理或日志中泄漏。

### 自定义属性

自定义属性也必须显式配置：

```python
ctx = AlephantGatewayContext(
    properties={
        "framework": "langchain",
        "app": "support-agent",
    }
)
```

输出：

```http
alephant-property-framework: langchain
alephant-property-app: support-agent
```

SDK 必须校验 property key/value，避免把敏感值、非法字符或过长内容放入请求头。Property key 必须匹配 `^[a-z0-9][a-z0-9_-]{0,63}$`，并拒绝 `token`、`secret`、`password`、`api_key` 等敏感命名。

## OpenAI-Compatible Gateway Helper

Alephant Gateway 支持常见 OpenAI-compatible `/v1/...` 调用，所以 SDK 应提供快速创建 Gateway client 的 helper。

```python
from alephantai import AlephantGatewayContext
from alephantai.openai import create_openai_client

ctx = AlephantGatewayContext(session_name="quickstart-chat")

client = create_openai_client(
    api_key="vk-...",
    base_url="https://ai.alephant.io/v1",
    context=ctx,
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Explain BYOK cost attribution."}],
)
```

该 helper 配置官方 OpenAI Python client：

- `base_url` 指向 Alephant Gateway。
- `api_key` 使用 Alephant Virtual Key。
- 默认携带 `ctx.headers()`，包括自动生成的 `Alephant-Session-Id`。

v1 不封装所有 provider SDK。后续是否增加 Anthropic、Gemini 等 helper，取决于实际用户需求。

## 用量/费用读取能力

SDK 可以提供 Virtual Key 认证的用量/费用读取能力，但第一版应限制在 **Cockpit API 范围**，也就是适合终端开发者用自己的 `vk-...` 查询该 key 可见的数据。

注意：后端实时 usage、daily costs、cost by model、budget spent 依赖 Virtual Key 绑定到 `agent` 或 `member` 实体。未绑定实体的 VK 可能返回 degraded/empty 数据。SDK 文档应建议先调用 `scope()` 判断当前 key 的 scope/entity，再解释统计结果。

推荐新增 `AlephantAnalyticsClient`：

```python
from alephantai.analytics import AlephantAnalyticsClient

analytics = AlephantAnalyticsClient(
    api_key="vk-...",
    base_url="https://analytics.alephant.io/api/v1",
)

summary = analytics.usage_summary(period="billing_cycle")
models = analytics.cost_by_model(period="7d")
budget = analytics.budget_status()
daily = analytics.daily_costs(period="30d")
scope = analytics.scope()
recent = analytics.recent_requests(limit=20)
```

对应后端已有 Cockpit API 语义：

- `GET /api/v1/cockpit/usage-summary`
- `GET /api/v1/cockpit/budget-status`
- `GET /api/v1/cockpit/cost-by-model`
- `GET /api/v1/cockpit/daily-costs`
- `GET /api/v1/cockpit/scope`
- `GET /api/v1/cockpit/recent-requests`，如果后端仍标记 degraded，SDK 文档应如实说明。
- `GET /api/v1/cockpit/health`，用于无认证健康检查，不代表某个 Virtual Key 的统计数据。

v1 不建议默认暴露完整工作区管理员 analytics，因为那通常需要 SaaS 用户身份、workspace 权限、`X-Workspace-Id`、以及更复杂的 RBAC。Analytics API 生产 host 为 `https://analytics.alephant.io`；SaaS 后端生产 host 为 `https://alephant.io/`，可以后续作为 `alephantai-saas-api` 或 admin extra 的能力。

包命名上，`alephantai` 定位为运行时 Gateway SDK；`alephantai-saas-api` / Fern 生成客户端定位为 SaaS 管理 API 或后台管理客户端。SDK 发布后，需要同步更新前端和公开 quickstart，避免两个包在用户路径里混用。

用量/费用能力边界：

```text
v1 支持：
- VK 认证的 scope 信息
- entity-bound VK 的 usage summary
- entity-bound VK 的 budget status / spent
- entity-bound VK 的 cost by model
- entity-bound VK 的 daily costs
- VK 认证的 recent requests；若响应包含 `degraded: true`，SDK 原样返回并在文档中说明
- Cockpit health check；该接口无认证，仅用于连通性/健康状态检查

v1 暂不支持：
- 管理员级全 workspace analytics
- 跨成员/部门/agent 的 SaaS 管理分析
- 直接查询 Collector 私有 API
```

这样 SDK 既能帮助用户“发起网关请求”，也能帮助用户“看到这个 key 产生了什么成本和使用情况”。

`usage_summary()`、`budget_status()`、`cost_by_model()`、`daily_costs()` 和 `scope()` 返回后端 `data` payload，隐藏 `{"data": ...}` envelope。`recent_requests()` 和 `health()` 返回后端顶层 JSON，因为它们当前不是同一 envelope 形状。SDK 不转换 UI 展示单位，调用方需要按响应字段判断 `degraded`、`data_source`，并按后端 schema 处理 `cost_cents`、`spent_cents` 等金额单位。

## LangChain 集成

LangChain 集成的主要体验应是 helper：直接创建已配置好 Alephant Gateway 的 LangChain model。

```python
from alephantai import AlephantGatewayContext
from alephantai.langchain import create_chat_openai

ctx = AlephantGatewayContext(session_name="langchain-chat")

llm = create_chat_openai(
    api_key="vk-...",
    base_url="https://ai.alephant.io/v1",
    context=ctx,
    model="gpt-4o-mini",
)

llm.invoke("Hello")
```

这条 quick path 应由 SDK 完成：

- Virtual Key 认证配置。
- Gateway `base_url` 配置。
- `Alephant-Session-Id` 注入。
- 可选 gateway headers 注入。

高级用户如果已经自己创建 LangChain model，也可以直接使用 headers 或 callback：

```python
from alephantai import AlephantGatewayContext
from alephantai.langchain import AlephantCallbackHandler

ctx = AlephantGatewayContext(session_name="langchain-chat")
handler = AlephantCallbackHandler(context=ctx)
```

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="https://ai.alephant.io/v1",
    api_key="vk-...",
    default_headers=ctx.headers(),
)

llm.invoke(
    "Hello",
    config={"callbacks": [handler]},
)
```

职责：

- 提供常见 OpenAI-compatible LangChain model helper。
- 确保同一次 chain、agent 或 chat 使用同一个 `Alephant-Session-Id`，实现 session 级归因和费用聚合。
- 提供 callback 给已有 LangChain 工程使用。
- callback 默认不抛异常，不能影响用户 chain 执行。
- v1 不生成 step / parent-step header。

Callback 可以记录轻量本地调试信息，但在没有稳定网关/后端 step/span 契约之前，不主动上报到 Alephant。SDK v1 不承诺把 LangChain 内部 span tree 映射成前端完整 journey steps。

## LlamaIndex 集成

LlamaIndex 集成同样以 Gateway helper 为主，让 LlamaIndex 的 LLM / embedding model 调用 Alephant Gateway。

```python
from alephantai import AlephantGatewayContext
from alephantai.llamaindex import create_openai_llm

ctx = AlephantGatewayContext(session_name="llamaindex-rag")

llm = create_openai_llm(
    api_key="vk-...",
    base_url="https://ai.alephant.io/v1",
    context=ctx,
    model="gpt-4o-mini",
)
```

后续也可以提供 embedding helper：

```python
from alephantai.llamaindex import create_openai_embedding

embed_model = create_openai_embedding(
    api_key="vk-...",
    base_url="https://ai.alephant.io/v1",
    context=ctx,
    model="text-embedding-3-small",
)
```

Instrumentation 暂不进入 v1。第一版只通过 LLM / embedding helper 把 `Alephant-Session-Id`
稳定注入实际发往 Gateway 的请求，避免发布一个不接入 LlamaIndex dispatcher 的 no-op handler。

职责：

- 提供常见 OpenAI-compatible LlamaIndex LLM / embedding helper。
- 确保 LlamaIndex 的 LLM/embedding 请求进入同一个 Alephant session，实现 session 级归因和费用聚合。
- 不直接写日志、不本地计算成本。

## 后端对齐

当前后端/Collector 相关事实：

- Gateway 请求需要携带 `Alephant-Session-Id` 才能归到对应 session。
- Gateway 已支持把 `alephant-session-id` 映射到 Collector payload 的 `log.request.sessionId`，不能只写入 properties；SDK v1 依赖这个后端契约完成 session 归因。
- Collector 已有 `request_response_rmt.session_id` 列。
- Sessions analytics 基于 `request_response_rmt.session_id` 聚合。
- ClickHouse 已存在 step 相关列，但 SDK v1 不发送 step header。
- SDK v1 只保证 session 级分组、请求记录和费用归因；完整 journey steps、policy events、grade 等前端旅程细节依赖后端已有数据与后续 step/span 契约。

关键要求：

用户通过 SDK 发起的 LLM/embedding 请求必须走 Alephant Gateway。  
如果用户绕过 Gateway 直接调 provider，Alephant 无法可靠提供成本归因和会话归因。

## 校验与安全

SDK 应校验自动生成和用户传入的 header：

- `session_id`：非空字符串，最大 128 字符。
- `session_name`：可选，最大 128 字符。
- `session_path`：可选，最大 256 字符；提供时规范化为 `/` 开头。
- property key：建议小写安全 header suffix，最大 64 字符，不允许空白字符。
- property value：转为字符串，最大 512 字符。
- cache bucket max size：整数 `1..20`。
- boolean header：序列化为 `"true"` / `"false"`。

SDK 默认不生成敏感 header。只有在 helper 明确创建 provider client 时，才使用用户传入的 Virtual Key 配置认证。

## 错误处理

默认行为应尽量不打断用户主流程：

- 显式用户输入非法时，在 context/client 构造阶段抛出清晰异常。
- framework callback 内部异常默认吞掉并写 debug logger。
- `strict=True` 时才抛出 callback 异常，方便测试和调试。
- 未安装可选依赖时，只在 import 对应 integration 时提示明确错误。

## 测试

核心测试：

- 不传 `session_id` 时自动生成稳定 session id。
- 传入 `session_id` 时按原值使用。
- 默认 headers 只包含 `Alephant-Session-Id`。
- `Session-Name` / `Session-Path` 只有配置后输出。
- 行为类 header 只有显式配置后输出。
- properties 只有显式配置后输出为 `alephant-property-*`。
- 非法 header 值按契约拒绝或省略。

OpenAI Gateway helper 测试：

- 使用配置的 `base_url`。
- 使用用户传入的 Virtual Key。
- 注入 `Alephant-Session-Id`。
- 不意外修改 context。

Analytics client 测试：

- 调用 cockpit usage summary 时携带 `Authorization: Bearer vk-...`。
- 支持 `period` 参数。
- 对后端 degraded response 保留原始信号，不假装成功。
- 不需要 LangChain/LlamaIndex 依赖。

LangChain 测试：

- 未安装 LangChain 时 core package 可正常 import。
- 安装 extra 后 integration 可 import。
- `create_chat_openai` 创建的 model 包含 gateway `base_url`、Virtual Key auth、context headers。
- callback 默认不抛异常。
- callback 复用传入的 context，不创建无关 session。

LlamaIndex 测试：

- 未安装 LlamaIndex 时 core package 可正常 import。
- 安装 extra 后 integration 可 import。
- OpenAI LLM / embedding helper 包含 gateway `base_url`、Virtual Key auth、context headers。

## 文档

需要补充：

- `README.md`：OpenAI-compatible Gateway quickstart。
- `docs/gateway-headers.md`：SDK header 行为说明。
- `docs/analytics.md`：VK 认证的用量/费用查询说明。
- `docs/langchain.md`：LangChain + Alephant Gateway 配置。
- `docs/llamaindex.md`：LlamaIndex + Alephant Gateway 配置。

文档必须明确：

- LLM/embedding 请求必须经过 Alephant Gateway。
- SDK 自动生成 `Alephant-Session-Id`。
- 用户可以手动指定或覆盖 `session_id`。
- 行为类 Gateway header 必须显式配置。
- v1 不生成 Collector step headers。
- v1 用量/费用读取聚焦 VK 认证的 Cockpit API 范围；实时统计依赖 VK 绑定到 agent/member。

## MVP 验收标准

- Python 开发者可以在 5 行以内创建 Alephant Gateway session。
- Python 开发者可以快速创建指向 Alephant Gateway 的 OpenAI-compatible client。
- Python 开发者可以用 SDK 查询 VK 认证的 usage/cost/budget/model 分布，并能识别 degraded/empty 响应。
- LangChain 开发者可以不用手写 headers 创建 Gateway-configured `ChatOpenAI`。
- LlamaIndex 开发者可以不用手写 headers 创建 Gateway-configured OpenAI LLM / embedding model。
- 默认 SDK 行为只影响 session 归因，不改变路由、缓存、prompt、日志省略等行为。
- 没有任何 SDK 路径绕过 Alephant Gateway 来做成本归因。
