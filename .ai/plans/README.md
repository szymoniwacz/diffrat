# Implementation Plans

## Purpose

Implementation plans break scoped input into small, reviewable steps before
coding.

In the default workflow, a plan is **agent working state during the run**, not a
committed repository artifact.

## When to use

Use the canonical preparation matrix in
`.ai/quality/definition-of-ready.md` to decide when planning is required before
implementation.

When planning is required, the agent must have an internal plan before file
changes. That plan may follow `.ai/plans/implementation-plan.template.md` as a
structure, but do not commit `plan-*.md` files to the PR branch.

Use `/plan-small-step` when you want help preparing scoped input and an
internal plan without implementing.

## Optional file template

`.ai/plans/implementation-plan.template.md` is a structure aid for preparation
or `/plan-small-step`. Files created from it are scratch only unless the
project explicitly chooses a different durable-artifact model.

## Relationship to other documents

| Document | Role |
|---|---|
| Agent Goal issue or brief | Scoped input: what and why |
| `.ai/plans/implementation-plan.template.md` | Optional structure for internal planning |
| PR description | Durable handoff after implementation |
| `.ai/skills/plan-small-step.md` | Skill for preparation via `/plan-small-step` |

## Rule

Implement only what the approved scope covers after implementation-ready is
satisfied. See `.ai/policies/no-blind-coding.md`.
