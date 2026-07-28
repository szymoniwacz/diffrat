# Agent Instructions

Root-level adapter for AI coding agents.

## Repository role

This repository contains **Numbat**, a local Python CLI for diff and PR review
assistance. Product code lives under `src/numbat/`. The `.ai/` folder holds the
AI working system inherited from `ai-project-template`.

v1 on `main` is complete: `numbat review` (modes, JSON, hunks, Focus/Risk hints,
optional `--check`). LLM and CI integrations are deferred (D-005, roadmap Phase 3–4).
Stack profile: `.ai/stack-profiles/numbat-cli.md`. User-facing docs: `README.md`.

## Source of truth

`.ai/` is the source of truth for project context, workflow, conventions, policies, prompts, skills, and quality rules.

Do not duplicate workflow content here. Follow the documents in `.ai/`.

## Read first

- Start at `.ai/README.md`.
- Product context: `.ai/project/product-context.md`.
- Roadmap and deferred work: `.ai/project/roadmap.md`, `.ai/project/decisions.md`.
- For an end-to-end goal, follow `.ai/skills/execute-goal.md`.
- Never merge pull requests.

## Workflow rules

Follow `.ai/instructions/workflow.md` and the policies in `.ai/policies/`.
Do not duplicate workflow, quality, review, or Git rules here.

## Adapter files

Tool-specific files (`CLAUDE.md`, `.cursor/rules/`, `.github/copilot-instructions.md`) are thin adapters. They import or reference this file and point to `.ai/`; they do not replace it.
