# Alephant Python Packages

This repository uses a monorepo layout for Alephant Python packages.

## Packages

- `packages/alephantai`: core Alephant Python SDK for gateway headers, analytics,
  OpenAI-compatible clients, and framework helpers.
- `packages/langchain-alephantai`: standalone LangChain integration package
  boundary for official provider-package work.

## Development

Run the full test suite from the repository root:

```bash
.venv/bin/python -m pytest -q
```

Run package-specific tests from each package directory when preparing a release.
