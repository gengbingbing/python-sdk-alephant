# Alephant Python SDK

Alephant Python SDK 用于便捷请求 Alephant Gateway、自动生成会话 header、查询 Virtual Key 用量/费用，并接入 LangChain / LlamaIndex。

## 安装

```bash
pip install alephantai
pip install "alephantai[langchain]"
pip install "alephantai[llamaindex]"
```

## Gateway Chat

生产 Gateway host 是 `https://ai.alephant.io/v1`。

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
