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
- **Current phase:** documentation first (bootstrap / definition coverage)
- **Important constraints:** Local-first; diff-scoped analysis only; no web UI in v1;
  humans merge; agents never merge

## Current phase

documentation first

Bootstrap and project definition are in progress. Product code has not started.

## What exists today

- AI workflow working system (`.ai/`) from `ai-project-template`
- Project definition and requirements documentation (this bootstrap)
- No CLI package or commands yet

## What does not exist yet

- `numbat` CLI entry point
- Diff ingestion and report generation
- Optional LLM-backed analysis layer

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
- Do not invent stack commands — record real commands when scaffold exists
- Local git data only in v1; no sending repo contents to external services unless
  explicitly configured for optional LLM analysis

## References

- Requirements: `.ai/docs/project-requirements.md`
- Scope: `.ai/project/scope.md`
- Architecture direction: `.ai/docs/architecture-direction.md`
