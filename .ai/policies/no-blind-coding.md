# No Blind Coding Policy

## Purpose

Prevent uncontrolled AI implementation that drifts from project context, scope, or review expectations.

## Rules

### No implementation without context

Read relevant project context before changing files:

- `.ai/project/product-context.md`
- `.ai/project/scope.md`
- related `.ai/docs/` and convention files

### No implementation without required preparation

Every meaningful change needs preparation matched to the change type.

Use the canonical preparation matrix in `.ai/quality/definition-of-ready.md`.
Do not start implementation without the required brief, task packet, plan, or
human approval for that change type.

Commands like `/execute-goal` and `/plan-small-step` create or complete required
preparation before coding. They do not imply that every task globally requires
a plan. Required preparation is not the same as a mandatory pause for human
re-prompting between routine phases. See
`.ai/policies/autonomy-and-authorization.md`.

### No broad "improve everything" changes

Reject prompts that refactor, reformat, or "clean up" the repository without scoped boundaries.

One logical change per branch.

### No unrelated cleanup

Do not fix naming, formatting, or structure outside the current task scope.
Note follow-ups in the review handoff: a review packet, equivalent PR
description, or temporary review notes.

### No architecture changes without explicit decision

Important architecture-boundary changes and architecture overhauls require
explicit human approval before `implementation-ready`. Routine
behavior-preserving refactors that stay inside existing boundaries do not.
Record decisions in `.ai/project/decisions.md` or an ADR when added. See
`.ai/policies/autonomy-and-authorization.md` and
`.ai/quality/definition-of-ready.md`.

### No dependency additions without justification

New libraries, tools, or services need a stated reason tied to the task goal. Document trade-offs and get approval for significant additions.

## Enforcement

Canonical workflow instructions reference this policy from `.ai/instructions/workflow.md`.

Tool adapters (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules/`) should remain thin and point to `.ai/` instructions instead of restating this policy.

## When implementation may start

Implementation may start when:

- `implementation-ready` is satisfied (`.ai/quality/definition-of-ready.md`),
- the required brief, task packet, and plan exist for the change type,
- required human approvals are recorded before `implementation-ready` when
  applicable,
- immediate blockers, mandatory prior approvals, and issues necessary for safe
  implementation are resolved.

Non-blocking Decision queue items wait for the grouped decision checkpoint.
See `.ai/policies/autonomy-and-authorization.md`.

## Related documents

- `.ai/instructions/workflow.md`
- `.ai/policies/autonomy-and-authorization.md`
- `.ai/quality/definition-of-ready.md`
- `.ai/packets/task-packet.template.md`
- `.ai/conventions/ai-working-mode.md`
- `.ai/docs/full-workflow.md`
- `.ai/skills/execute-goal.md`
