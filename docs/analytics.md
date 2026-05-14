# Analytics

`AlephantAnalyticsClient` 默认使用 `https://analytics.alephant.io/api/v1`，并通过 `Authorization: Bearer vk-...` 查询 Virtual Key 认证的用量/费用（Cockpit API）数据。实时 usage、daily costs、cost by model、budget spent 依赖该 VK 绑定到 agent 或 member；建议先调用 `scope()` 判断当前 key 的 scope/entity。SaaS 后端 host 是 `https://alephant.io/`，不要和 analytics host 混用。v1 只保证 session 级请求/费用归因；完整 journey steps、policy events、grade 需要后续 step/span 契约。

支持：

- `usage_summary(period="billing_cycle")`
- `budget_status(period=None)`
- `cost_by_model(period="billing_cycle")`
- `daily_costs(period="billing_cycle")`
- `scope()`
- `recent_requests(limit=20, offset=0)`
- `health()`

`usage_summary()`、`budget_status()`、`cost_by_model()` 和 `daily_costs()` 返回后端 `data` payload；`scope()` 有 `data` 时返回 `data`，没有 `data` 时返回后端顶层 JSON；`recent_requests()` 和 `health()` 返回后端顶层 JSON。调用方需要检查 `degraded` / `data_source`，并按后端字段单位处理 `cost_cents`、`spent_cents` 等金额字段。`recent_requests()` 当前可能返回 `degraded=true` 的空列表。v1 不提供管理员级 workspace analytics。
