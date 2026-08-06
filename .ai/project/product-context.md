# Product Context

## Purpose

This is the main context file for AI-assisted work in this repository.

Before planning or changing anything, an AI assistant should read this file.

## Project identity

- **Project name:** Diffrat (formerly Numbat; see D-008)
- **Project type:** Local Python CLI for diff and PR review assistance
- **Target users:** Developers doing self-review before push/PR; reviewers assessing
  someone else's diff
- **Core problem:** Diff review is slow, inconsistent, and context-poor without
  structured assistance grounded in git changes
- **Current phase:** Phase 3 complete — **1.0.0** product release; PyPI publish
  in progress (D-008)
- **Important constraints:** Local-first; diff-scoped analysis only; no web UI in v1;
  optional LLM when `DIFFRAT_LLM_*` env vars are set (diff-scoped prompts only);
  humans merge; agents never merge

## Current phase

Phase 3 complete (optional LLM layer per D-005 / ADR-0001). Rebrand to Diffrat
and PyPI publication underway (D-008). Phase 4 integrations (CI bots, GitHub App)
remain deferred.

## What exists today

- AI workflow working system (`.ai/`) from `ai-project-template`
- Project definition and requirements documentation
- Installable `diffrat` CLI (`pip install -e ".[dev]"` or `pip install diffrat`)
  at version **1.0.0**
- `diffrat review` — unstaged, `--staged`, `--base` (merge-base), `--range` (two-ref), `--json`
- Human-readable report with file categories and deterministic Focus/Risk hints
  (including git-context hints: `many_commits`, `wip_commits`, `mixed_concerns`)
- Git context on branch-vs-base and commit-range reviews
- Optional LLM-backed analysis when `DIFFRAT_LLM_*` env vars are set; heuristics-only
  report remains the default without API keys
- `CHANGELOG.md` for the 1.0.0 release
- pytest / ruff / mypy green on main
- PyPI name `diffrat` reserved (`0.0.1` stub); product wheel publish follows rebrand

## What does not exist yet

- CI bots, GitHub App (Phase 4)
- Shared/remote rule packs beyond repo-local TOML

## Core workflows (intended)

### Self-review before push

1. Developer finishes changes on a feature branch
2. Runs Diffrat against the diff vs base branch (or staged/unstaged changes)
3. Reads terminal report (or `--json` for scripting)
4. Addresses flagged risks and focus areas before opening a PR

### Reviewer triage

1. Reviewer checks out branch or receives diff context locally
2. Runs Diffrat with branch/range arguments
3. Uses summary and risk signals to prioritize review time
4. Cross-checks findings manually — Diffrat assists, does not approve

## Constraints for AI work

- Respect scope in `.ai/project/scope.md`
- Prefer small, reviewable changes; one Agent Goal at a time
- Do not invent stack commands — use recorded README / pyproject commands
- Local git data only by default; optional LLM sends diff-scoped prompts only when
  explicitly configured via `DIFFRAT_LLM_*`

## References

- Requirements: `.ai/docs/project-requirements.md`
- Scope: `.ai/project/scope.md`
- Architecture direction: `.ai/docs/architecture-direction.md`
- Decisions: `.ai/project/decisions.md` (D-005, D-008)
- ADR: `.ai/architecture/adr-0001-llm-analysis-layer.md`
