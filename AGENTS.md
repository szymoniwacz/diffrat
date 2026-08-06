# Agent Instructions

Root-level adapter for AI coding agents.

## Repository role

This repository contains **Diffrat**, a local Python CLI for diff and PR review
assistance. Product code lives under `src/diffrat/`.

The reusable AI workflow is **not** committed here. It comes from the private
submodule `.ai-template/` (`ai-project-template`). Run
`./scripts/setup-ai-workflow.sh` after clone to materialize `.ai/`.
See `docs/ai-workflow-setup.md`.

**1.0.0** on `main` is the first product release: `diffrat review` (modes, JSON,
hunks, Focus/Risk hints, optional `--check`, optional Phase 3 LLM via
`DIFFRAT_LLM_*` per D-005 / ADR-0001). Phase 4 integrations (CI bots, GitHub App)
remain deferred. Stack profile: `.ai/stack-profiles/diffrat-cli.md`. User-facing
docs: `README.md`.

## Source of truth

`.ai/` is the source of truth for project context, workflow, conventions, policies, prompts, skills, and quality rules.

Do not duplicate workflow content here. Follow the documents in `.ai/`.

## Read first

- Start at `.ai/README.md`.
- Product context: `.ai/project/product-context.md`.
- Roadmap and deferred work: `.ai/project/roadmap.md`, `.ai/project/decisions.md`.
- For an end-to-end goal, follow `.ai/skills/execute-goal.md`.
- Never merge pull requests except under authorized eligible
  `self-correcting-review auto-merge`
  (`.ai/policies/autonomy-and-authorization.md`).

## Workflow rules

Follow `.ai/instructions/workflow.md` and the policies in `.ai/policies/`.
Do not duplicate workflow, quality, review, or Git rules here.

## Adapter files

Tool-specific files (`CLAUDE.md`, `.cursor/rules/`, `.github/copilot-instructions.md`) are thin adapters. They import or reference this file and point to `.ai/`; they do not replace it.
