# Integration Submission Materials Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create reusable submission materials for making Alephant AI discoverable in LangChain and LlamaIndex ecosystems.

**Architecture:** Keep all external-facing submission copy in `docs/integration-submissions/` so it can be copied into upstream PRs without changing SDK runtime code. Separate framework-specific drafts from provider profile and PR response templates.

**Tech Stack:** Markdown, MDX, existing `alephantai` Python SDK APIs, LangChain `ChatOpenAI`, LlamaIndex OpenAI-compatible LLM and embedding clients.

---

### Task 1: Create Submission Material Files

**Files:**
- Create: `docs/integration-submissions/langchain-alephantai.mdx`
- Create: `docs/integration-submissions/llamaindex-submission.md`
- Create: `docs/integration-submissions/provider-profile.md`
- Create: `docs/integration-submissions/pr-templates.md`

- [x] **Step 1: Confirm public SDK APIs**

Read:

```bash
sed -n '1,240p' src/alephantai/langchain/openai.py
sed -n '1,260p' src/alephantai/llamaindex/openai.py
sed -n '1,220p' docs/langchain.md
sed -n '1,220p' docs/llamaindex.md
```

Expected: Files show `create_chat_openai`, `create_openai_llm`, and `create_openai_embedding` as the public helper APIs.

- [x] **Step 2: Draft LangChain MDX material**

Write `docs/integration-submissions/langchain-alephantai.mdx` with installation, credentials, chat model usage, session attribution, custom gateway URL, and API reference sections.

- [x] **Step 3: Draft LlamaIndex submission material**

Write `docs/integration-submissions/llamaindex-submission.md` with recommended upstream package path, `pyproject.toml` metadata draft, README draft, and PR description draft.

- [x] **Step 4: Draft provider profile**

Write `docs/integration-submissions/provider-profile.md` with short descriptions, links, install commands, imports, keywords, maintainer statement, and current SDK scope.

- [x] **Step 5: Draft PR templates**

Write `docs/integration-submissions/pr-templates.md` with LangChain docs PR text, LlamaIndex integration PR text, and common reviewer answers.

- [x] **Step 6: Run sanity checks**

Run:

```bash
rg -n "Elephant|TODO|TBD|fill in" docs/integration-submissions
for f in docs/integration-submissions/*; do printf "%s " "$f"; rg -o '^`{3,4}' "$f" | wc -l; done
git status --short
```

Expected: No accidental `Elephant` typo, no TODO/TBD placeholders, even code fence counts, and only intended docs files listed as untracked or modified.

