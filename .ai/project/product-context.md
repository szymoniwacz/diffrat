# Product Context

## Purpose

This is the main context file for AI-assisted work in this repository.

Before planning or changing anything, an AI assistant should read this file.

## Project identity

- **Project name:** Numbat
- **Project type:** Local Python CLI for diff and PR review assistance
- **Target users:** Developers doing self-review before push/PR; reviewers assessing
  someone else's diff
- **Core problem:** Diff review is slow, inconsistent, and context-poor without
  structured assistance grounded in git changes
- **Current phase:** Phase 2 complete — v1 static core on `main`
- **Important constraints:** Local-first; diff-scoped analysis only; no web UI in v1;
  no LLM in v1 (D-005); humans merge; agents never merge

## Current phase

Phase 2 complete (v1 close bar). Optional Phase 3 LLM is deferred / out of v1
per D-005.

## What exists today

- AI workflow working system (`.ai/`) from `ai-project-template`
- Project definition and requirements documentation
- Installable `numbat` CLI (`pip install -e ".[dev]"`)
- `numbat review` — unstaged, `--staged`, `--base` (merge-base), `--range` (two-ref), `--json`
- Human-readable report with file categories and deterministic Focus/Risk hints
- Git context on branch-vs-base reviews
- pytest / ruff / mypy green on main

## What does not exist yet

- Optional LLM-backed analysis layer (out of v1; D-005)
- CI bots, GitHub App, PyPI publication (Phase 4 / later)

## Core workflows (intended)

### Self-review before push

1. Developer finishes changes on a feature branch
2. Runs Numbat against the diff vs base branch (or staged/unstaged changes)
3. Reads terminal report (or `--json` for scripting)
4. Addresses flagged risks and focus areas before opening a PR

### Reviewer triage

1. Reviewer checks out branch or receives diff context locally
2. Runs Numbat with branch/range arguments
3. Uses summary and risk signals to prioritize review time
4. Cross-checks findings manually — Numbat assists, does not approve

## Constraints for AI work

- Respect scope in `.ai/project/scope.md`
- Prefer small, reviewable changes; one Agent Goal at a time
- Do not invent stack commands — use recorded README / pyproject commands
- Local git data only in v1; do not send repo contents to external services

## References

- Requirements: `.ai/docs/project-requirements.md`
- Scope: `.ai/project/scope.md`
- Architecture direction: `.ai/docs/architecture-direction.md`
- Decisions: `.ai/project/decisions.md` (D-005)
