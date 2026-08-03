# Feedback checklist (1.0.0)

Short session for external testers and dogfood. Goal: feedback on the **CLI
product**, not on private AI workflow tooling.

Time budget: about 10–15 minutes.

## Setup (product only)

```bash
git clone https://github.com/szymoniwacz/numbat.git
cd numbat
pip install -e .
numbat --version
```

Do **not** run `./scripts/setup-ai-workflow.sh` or init the private submodule.

Optional (only if you will try `--check`):

```bash
pip install -e ".[dev]"
```

## Commands to try

Run these from inside a git repo that has a real diff (feature branch vs
`main`, or local unstaged/staged edits). On a clean `main` with no changes,
`numbat review` / `numbat review --base main` exit `2` — that is expected.

```bash
# Unstaged / staged
numbat review
numbat review --staged

# Branch vs base
numbat review --base main

# JSON for scripting
numbat review --base main --json

# Optional gates / deep view
numbat review --base main --fail-on=possible_secret,docs_touched
numbat review --base main --hunks-for=<path-in-diff>

# Optional local checks (needs .[dev] for pytest/mypy/ruff)
numbat review --base main --check
```

Optional LLM (only if you choose to send diff-scoped prompts off-machine):

```bash
export NUMBAT_LLM_PROVIDER=...
export NUMBAT_LLM_API_KEY=...
# optional: export NUMBAT_LLM_BASE_URL=...
numbat review --base main
```

## Questions to answer

1. What was confusing or unexpected in Setup or the first successful report?
2. Which Focus/Risk hints felt useful? Which felt like false positives or noise?
3. Was Review order / risk scoring helpful for deciding what to look at first?
4. Did `--json` fit how you would script or gate a review?
5. What is the one thing you most wanted that is missing?

## What not to evaluate

- Private AI delivery workflow / `.ai-template` / maintainer scripts
- PyPI packaging (not published yet)
- CI bots / GitHub App (Phase 4 deferred)
