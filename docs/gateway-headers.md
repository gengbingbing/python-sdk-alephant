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
