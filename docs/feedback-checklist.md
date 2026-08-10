# Feedback checklist (1.1.2)

Short session for external testers and dogfood. Goal: feedback on the **CLI
product**, not on private AI workflow tooling.

Time budget: about 10–15 minutes.

## Setup (product only)

Preferred (PyPI):

```bash
pip install diffrat
diffrat --version
```

Expect `diffrat 1.1.2` (or newer).

From source:

```bash
git clone https://github.com/szymoniwacz/diffrat.git
cd diffrat
pip install -e .
diffrat --version
```

Do **not** run `./scripts/setup-ai-workflow.sh` or init the private submodule.

Optional (only if you will try `--check`):

```bash
pip install -e ".[dev]"
# or: pip install 'diffrat[dev]' after extras are needed from a clone
```

## Commands to try

Run these from inside a git repo that has a real diff (feature branch vs
`main`, or local unstaged/staged edits). On a clean `main` with no changes,
`diffrat review` / `diffrat review --base main` exit `2` — that is expected.

```bash
# Unstaged / staged
diffrat review
diffrat review --staged

# Branch vs base
diffrat review --base main

# Triage-first (omit Changes hunks); note Review quality pillars after Summary
diffrat review --base main --brief

# JSON for scripting
diffrat review --base main --json
diffrat review --base main --brief --json

# Optional gates / deep view
diffrat review --base main --fail-on=possible_secret,docs_touched
diffrat review --base main --hunks-for=<path-in-diff>

# Optional local checks (needs .[dev] for pytest/mypy/ruff)
diffrat review --base main --check
```

Optional LLM (only if you choose to send diff-scoped prompts off-machine).
See [`docs/llm.md`](llm.md) for copy-paste OpenAI and Ollama setup:

```bash
export DIFFRAT_LLM_PROVIDER=...
export DIFFRAT_LLM_API_KEY=...
# optional: export DIFFRAT_LLM_BASE_URL=...
diffrat review --base main
```

## Questions to answer

1. What was confusing or unexpected in Setup or the first successful report?
2. Which Focus/Risk hints felt useful? Which felt like false positives or noise?
3. Was Review order / risk scoring helpful for deciding what to look at first?
4. Did the Review quality pillars (understand / one thing well / maintainable) help?
5. Did `--json` fit how you would script or gate a review?
6. What is the one thing you most wanted that is missing?

## What not to evaluate

- Private AI delivery workflow / `.ai-template` / maintainer scripts
- CI bots / GitHub App (Phase 4 deferred)
