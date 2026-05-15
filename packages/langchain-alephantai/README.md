# langchain-alephantai

LangChain integration package for Alephant AI Gateway.

This package provides a LangChain chat model configured for Alephant AI Gateway.

```bash
pip install langchain-alephantai
```

```python
from langchain_alephantai import ChatAlephantAI

llm = ChatAlephantAI(
    api_key="vk-...",
    model="gpt-4o-mini",
    session_name="langchain-chat",
)
```

The package also exports `create_chat_openai` for compatibility with the core
`alephantai` SDK helper.

## Development

Install the package with development dependencies:

```bash
python -m pip install -e ../alephantai -e ".[dev]"
```

Run the package tests, including LangChain standard unit tests:

```bash
pytest tests -m "not integration" -q
```

The standard integration tests require live Alephant Gateway credentials and are
skipped by default:

```bash
ALEPHANT_API_KEY="vk-..." pytest tests/test_standard_integration.py -m integration -q
```

Set `ALEPHANT_TEST_MODEL` to override the default integration-test model.
