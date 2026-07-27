# Task Workflows

## Purpose

This folder contains procedures for common AI-assisted task types.

Each workflow defines when to use it, required input, steps, validation, and what to avoid.

## Available workflows

| Workflow | Use for |
|---|---|
| [feature.md](feature.md) | Adding or extending product capability |
| [bugfix.md](bugfix.md) | Fixing a defect with minimal scope |
| [refactor.md](refactor.md) | Structural improvement without behavior change |
| [test-writing.md](test-writing.md) | Adding or updating tests |
| [documentation-update.md](documentation-update.md) | Updating docs or `.ai/` context |

## How to use

1. Start from a task route and required preparation per `.ai/quality/definition-of-ready.md`.
2. Select one primary workflow that matches the task type.
3. Confirm ready for planning.
4. Create the required plan in `.ai/plans/` when the preparation matrix requires it.
5. Record required approvals before `implementation-ready` when applicable.
6. Confirm implementation-ready before changing files.
7. Follow steps in order; do not skip required input. Supporting work (for example, tests during a bugfix) stays part of the primary workflow.
8. Complete via the canonical lifecycle in `.ai/docs/full-workflow.md`. Prefer
   independent review when available; self-review is the fallback. Agents never
   merge.

A review handoff is a review packet created from `.ai/packets/review-packet.template.md` or an equivalent drafted PR description. Reference these canonical files instead of copying their procedures here.

## Relationship to skills

Skills (`.ai/skills/`) are slash-command procedures for specific actions like `/add-idea`.

Workflows are task-type playbooks that may span planning, implementation, and review.

Do not duplicate skill procedures here. Link to skills when relevant.

## Rule

Select one primary workflow per task. Do not combine unrelated task types in one branch.
