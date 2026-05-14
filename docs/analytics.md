# Analytics

`AlephantAnalyticsClient` defaults to `https://alephant.io/api/v1` and uses
`Authorization: Bearer vk-...` to query Virtual Key-authenticated usage and cost
data from the Cockpit API. Cockpit API routes are exposed by the SaaS backend.
The lower-level Collector Analytics API host is `https://analytics.alephant.io`;
do not mix that host with Cockpit API routes.

Real-time usage, daily costs, cost by model, and budget spent depend on the
Virtual Key being bound to an agent or member. Call `scope()` first to inspect
the current key's scope and entity. SDK v1 guarantees session-level request and
cost attribution only; full journey steps, policy events, and grading require a
future step/span contract.

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
`recent_requests()` can return an empty list with `degraded=true`. SDK v1 does
not provide admin-level workspace analytics.
