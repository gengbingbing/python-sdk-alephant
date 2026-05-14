# Gateway Headers

The SDK generates this header automatically:

- `Alephant-Session-Id`

The SDK sends these headers only when you configure them explicitly:

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
- `x-alephant-webhook-enabled`; sent only when explicitly enabled, never as `false`

SDK v1 does not expose sensitive observability configuration headers such as
PostHog or Lytix keys. Manage those values in server-side or workspace
configuration.

SDK v1 does not generate:

- `Collector-Step-Id`
- `Collector-Parent-Step-Id`
- `Collector-Retry-Count`
