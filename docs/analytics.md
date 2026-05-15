# Analytics

`AlephantAnalyticsClient` defaults to `https://alephant.io/api/v1` and uses
`Authorization: Bearer vk-...` to query Virtual Key-authenticated usage and cost
data from the Cockpit API. Cockpit API routes are exposed by the SaaS backend.
The lower-level Collector Analytics API host is `https://analytics.alephant.io`;
do not mix that host with Cockpit API routes.

Real-time usage, daily costs, cost by model, and budget spent are scoped by the
Virtual Key. If the key is bound to an agent or member, `cost_by_model()` uses
that entity scope; otherwise it falls back to the workspace scope. Call
`scope()` first to inspect the current key's workspace and optional entity. The
current Cockpit API surfaces request and aggregate usage metrics; it does not
currently expose session-level query APIs. Full journey steps, policy events,
and grading require a future step/span contract.

Supported methods:

- `usage_summary(period="billing_cycle")`
- `budget_status(period=None)`
- `cost_by_model(period="billing_cycle")`
- `daily_costs(period="billing_cycle")`
- `scope()`
- `recent_requests(limit=20, offset=0)`
- `health()`

`usage_summary()`, `budget_status()`, `cost_by_model()`, and `daily_costs()`
return the backend `data` payload. `scope()` returns `data` when the backend
includes it, otherwise it returns the top-level JSON response. `recent_requests()`
and `health()` return top-level JSON responses. Callers should inspect
`degraded` and `data_source`, and should treat amount fields such as
`cost_cents` and `spent_cents` according to their backend units.

Token fields follow the Cockpit API response:

- `usage_summary().total_tokens.input` is Collector prompt/input tokens.
- `usage_summary().total_tokens.output` is Collector completion/output tokens.
- `daily_costs().data[*].tokens` is the total token count for that day.

`recent_requests()` returns live request rows after the Collector-backed fix,
including `tokens_in`, `tokens_out`, `status`, `latency_ms`, and `created_at`.
`degraded=true` means the backend, Collector, or requested scope could not
provide live rows; it is not the normal success state. SDK v1 does not provide
admin-level workspace analytics.
