# Agent Instructions

Root-level adapter for AI coding agents.

## Repository role

This is a documentation-first AI workflow template. It is not an application. It provides a structured working system for building real projects with AI assistance in a controlled, reviewable way.

Template defines the working system. Project defines the product.

After bootstrap, update this file so it describes the actual product repository.
See `.ai/onboarding/bootstrap-checklist.md` and
`.ai/onboarding/template-customization-guide.md`.

## Source of truth

`.ai/` is the source of truth for project context, workflow, conventions, policies, prompts, skills, and quality rules.

Do not duplicate workflow content here. Follow the documents in `.ai/`.

## Read first

- Start at `.ai/README.md`.
- For an end-to-end goal, follow `.ai/skills/execute-goal.md`.
- Never merge pull requests.

## Workflow rules

Follow `.ai/instructions/workflow.md` and the policies in `.ai/policies/`.
Do not duplicate workflow, quality, review, or Git rules here.

## Adapter files

Tool-specific files (`CLAUDE.md`, `.cursor/rules/`, `.github/copilot-instructions.md`) are thin adapters. They import or reference this file and point to `.ai/`; they do not replace it.
