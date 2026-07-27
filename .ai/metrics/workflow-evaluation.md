# Workflow Evaluation

## Purpose

Define how to evaluate whether the AI workflow is working for a project.

Use this for retrospectives, template improvement, and spotting drift—not for punishing individuals.

## Data source

Evaluate workflow health from durable artifacts first:

- Agent Goal issue, explicit brief, or accepted requirement
- pull request description and diff
- review comments on the pull request

Use session logs as a supplemental source for exceptional execution history
(failures, corrections, handoffs) when required by
`.ai/observability/session-log-spec.md`. `.ai/observability/session-log-spec.md`
owns individual log fields; this document defines evaluation signals and does
not restate the field schema.

## Evaluation signals

Derive these signals from available durable artifacts. Use session-log fields
only when a log exists for the task:

| Signal | Derived from | What it indicates |
|---|---|---|
| **task readiness** | issue, brief, or requirement scope | Was the task defined clearly enough to start? |
| **scoped input requirement** | task type, workflow, issue or brief presence | Was scoped input required and present before planning? |
| **scoped input result** | issue or brief quality | Did the scoped input satisfy ready for planning? |
| **plan requirement** | task type, workflow | Was internal planning required before implementation? |
| **plan result** | issue comments, PR description, agent notes when present | Was planning evident and aligned with scope before file changes? |
| **blocker count** | open questions, blocking-question statuses, stop conditions | How many unresolved blockers remained before implementation? |
| **readiness result** | ready for planning and implementation-ready checks | Did the task pass both readiness gates before file changes? |
| **scope proportionality** | PR diff, files changed, review surface | Was the diff proportional to scope? |
| **validation coverage** | review handoff, PR description, commands run in session log when present | Were applicable validation commands and gates executed, or explicitly skipped with a documented reason? |
| **skipped gates** | review handoff, PR description, session log when present | Which gates were intentionally skipped and why? |
| **failures** | session log, PR comments, review handoff when failures occurred | What errors, gate failures, or blocked steps occurred? |
| **corrections** | session log, PR comments, review handoff when corrections occurred | What failures, review findings, or other issues required correction? |
| **iteration count** | session log when present | Loops per task (lower is often better if quality holds) |
| **outcome** | review handoff, PR state, session log when present | `completed`, `blocked`, `needs-review`, or `abandoned` |
| **rework** | PR history, review comments, session log when present | Tasks reopened or redone after review |
| **follow-up** | review handoff, PR description, session log when present | How much follow-up work remained |
| **review surface** | PR diff, session log when present | File count and cross-layer spread |
| **tool adherence** | agent/tool in session log when present; adapter behavior | Which tool was used; did it follow `.ai/`? |
| **drift** | review handoff, PR diff, session log when present | Unrelated edits, doc contradictions, scope creep |

## Evaluation questions

After a meaningful task, ask:

1. Did the required scoped input (issue, brief, or requirement) exist before implementation?
2. Were preparation requirements satisfied for the task type per the preparation matrix?
3. Did the task pass ready for planning and implementation-ready before file changes?
4. Was the change reviewable without chat context?
5. Were quality gates considered and documented, including skipped gates?
6. For controlled actions, did the agent get explicit approval before executing approval-before-execution actions and flag review-before-merge changes for human review (`.ai/policies/dangerous-actions.md`)?
7. Was there measurable rework or drift?

## Healthy signals

- small PRs with clear descriptions
- scoped input, internal planning, and readiness signals evident before implementation
- review handoff or PR description sufficient to understand scope and validation
- session logs are present when required and otherwise used only when they add non-duplicative execution history
- documentation stays aligned with code
- failures and corrections recorded in durable artifacts when they occurred

## Unhealthy signals

- large unexplained diffs
- repeated scope corrections mid-task
- skipped validation without reason
- unresolved blockers ignored at implementation start
- duplicate rules appearing in tool adapters
- increasing iteration count without quality gain
- a session log required by `.ai/observability/session-log-spec.md` is missing

## Related documents

- `.ai/observability/session-log-spec.md`
- `.ai/quality/definition-of-ready.md`
- `.ai/quality/quality-gates.md`
- `.ai/review/diff-risk-checklist.md`
- `.ai/policies/dangerous-actions.md`

## Rule

Measure to improve the workflow. Do not add heavy process unless the project needs it.
