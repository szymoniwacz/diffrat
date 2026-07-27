# Implementation Plan

## Source task packet

Link to task packet or brief:

## Goal

What should this step achieve?

## Non-goals

What is explicitly out of scope for this plan?

## Decision queue

Point to the task packet Decision queue, or list only plan-local items here.
Non-blocking questions wait for the grouped decision checkpoint after
validation and review. See `.ai/policies/autonomy-and-authorization.md`.

## Risks

What could go wrong or expand scope?

## Planned files

| File | Planned change |
|---|---|
|  |  |

## Steps

1. First step.
2. Second step.
3. Third step.

## Workstream dependencies

Canonical owner of workstream execution state for this goal. Use when the goal
decomposes into multiple workstreams. Omit this section for single-agent work.

| Workstream | Depends on | Owns | Role | Branch and worktree | Status |
|---|---|---|---|---|---|
|  |  |  | lead / research / write / validation / review |  |  |

Write workstreams record both branch and worktree. Read-only research,
validation, or review workstreams may use `not applicable`.

The orchestrator owns final integrated validation unless a validation agent is
explicitly assigned through the role column.

See `.ai/policies/multi-agent-orchestration.md`.

## Validation

How will this plan be verified when complete?

- [ ] scope matches brief or task packet
- [ ] docs updated if needed
- [ ] tests or lint when code exists
- [ ] integrated result validated when multiple workstreams were used
- [ ] review handoff prepared: a review packet or an equivalent PR description

## Rollback notes

How to undo or revert if this step goes wrong?

## Review focus

What should the reviewer pay closest attention to?

## Stop conditions

Pause only for immediate blockers or actions that require prior approval.
Non-blocking Decision queue items do not stop implementation.

- scope expansion needed
- architecture decision required before safe progress
- changing security posture or trust boundaries
- destructive migration or shared-environment apply
- other immediate blocker or mandatory prior approval:
