# Changelog

## 0.1.0 - 2026-05-14

Initial Alephant Python SDK release.

- Added Gateway runtime helpers under the `alephantai` package.
- Added automatic Alephant session header support with explicit cache, routing, and prompt header controls.
- Added an OpenAI-compatible Gateway client defaulting to `https://ai.alephant.io/v1`.
- Added Virtual Key Cockpit analytics client support for usage, budget, model cost, daily cost, scope, recent request, and health endpoints.
- Added LangChain integration via `alephantai[langchain]`.
- Added LlamaIndex LLM and embedding helpers via `alephantai[llamaindex]`.
- Documented production hosts for Gateway, Cockpit, and lower-level Analytics API separation.
