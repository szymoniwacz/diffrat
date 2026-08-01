# Project Executor — Cursor Automation Instructions

Project Executor is an event-driven orchestrator around the existing Goal
Executor. It selects at most one goal, invokes Goal Executor, and then waits
for human merge (default: after human CR; with self-correcting review mode:
after an eligible self-verified handoff, or human CR if escalated). It does not
copy the goal lifecycle or merge pull requests.

## Trigger events

Production trigger configuration:
`.ai/automation/project-executor-production-setup.md`.

### Issue comment

When this run was triggered by an owner comment on a **Project Execution**
issue:

- `/execute-project` authorizes the project (initially or after the most recent
  edit to its title or scope fields) and starts or resumes when state
  permits.
- `/execute-project self-correcting-review` is the same authorization and also
  opts eligible delegated goals into self-correcting review mode. Same mode
  rules as `/execute-goal self-correcting-review`:
  `.ai/policies/autonomy-and-authorization.md` and
  `.ai/review/self-correcting-review-loop.md`. Ineligible goals escalate to
  human CR.
- `/continue-project` is an optional manual nudge on an already authorized
  project: after material-decision answers, when applicable CI was pending, or
  when the owner wants to retry sooner. It does not authorize a project by
  itself and does not replace `/execute-project` after issue edits. If no valid
  authorization exists, stop as a no-op without writing.

Use the commented Project Execution issue as the active project.

### Pull request merged

When this run was triggered by a merged pull request:

1. Read the merged pull request number and body from the trigger event.
2. Extract exact `Closes #<goal-number>` from the body (same contract as Goal
   Executor).
3. Read the goal issue. If it lacks the trusted exact
   `<!-- project-executor:goal project=OWNER/REPOSITORY#PROJECT_NUMBER -->`
   marker from this automation identity, stop as a no-op without writing.
4. Resolve the Project Execution issue `#PROJECT_NUMBER` from that marker.
5. Verify `/execute-project` or `/execute-project self-correcting-review`
   authorization on that project issue after the most recent edit to its title
   or scope fields.
6. Run the same state resolution and actions as for a comment trigger on that
   project issue.

Fail closed without writing when: the body has no `Closes #<goal-number>`, the
goal is not a delegated Project Executor goal, authorization is missing or
invalid, or the merge cannot be linked to an active authorized project.

Merging a delegated pull request continues the project automatically when the
pull request merged trigger is configured. The owner does not need
`/continue-project` after merge unless state resolution enters `WAIT` (for
example applicable CI still pending on the default branch).

## Authorization

An active project is one open **Project Execution** issue that:

- starts with `[Project Execution]:`;
- contains Product outcome and Completion criteria;
- has an exact `/execute-project` or `/execute-project self-correcting-review`
  comment by the authorized repository owner posted after the most recent edit
  to its title or any **scope field** (Product outcome, Completion criteria,
  Constraints, Out of scope, Relevant context).

Edits to the **Commands** section alone do **not** invalidate authorization.
**Commands** is human reference only: ignore it for product boundary, goal
selection, planning, and implementation.

The `self-correcting-review` form also opts eligible delegated goals into
self-correcting review mode. Each goal still fails closed to human CR when
ineligible. See `.ai/policies/autonomy-and-authorization.md`.

The scope fields are the project boundary. If there is no active project, stop
as a no-op. If more than one exists, list them and stop without writing. Any
later title or scope-field edit invalidates the authorization until the owner
comments exactly `/execute-project` or `/execute-project self-correcting-review`
again. If edit ordering cannot be verified, treat the project as unauthorized
and make no write.

Before any write, verify that the live loader read this file and
`.ai/automation/goal-executor.md` from the current default branch. Otherwise
fail closed.

## Read current evidence

Read the active project issue and comments, the current default branch,
`.ai/project/`, `.ai/docs/project-requirements.md`,
`.ai/docs/architecture-direction.md`, every ADR linked from
`.ai/project/decisions.md`, and `.ai/automation/goal-executor.md`. Never resume
from chat history or a stale working branch.

**Ignore the issue `Commands` section entirely** for product boundary, goal
selection, planning, and implementation. It is human cheat-sheet text only.

Use this exact marker in every delegated Agent Goal issue:

```text
<!-- project-executor:goal project=OWNER/REPOSITORY#PROJECT_NUMBER -->
```

Resolve the exact GitHub login of the authenticated automation identity. The
marker is discovery evidence only: treat an issue as delegated only when its
author login exactly matches that identity. A marker-bearing issue with another
or unverifiable author is conflicting evidence; enter `CONFLICT` and make no
write. Never infer identity from a display name.

Trust a completed-without-PR or project completion marker only when its exact
remote comment has been read from GitHub, its author login exactly matches the
authenticated automation identity, and its repository and issue reference
matches the expected goal or project. Any other or unverifiable marker is
conflicting evidence; enter `CONFLICT` and make no write.

Resolve state before any repository mutation and again immediately before the
first remote write. Find every goal with that exact marker and its pull request
through the Goal Executor's required `Closes #<goal-number>` reference.

Apply the first matching state:

| State | Evidence | Action |
|---|---|---|
| `CONFLICT` | More than one delegated goal is non-terminal, completion evidence coexists with active work, or evidence is contradictory. | List exact conflicts and make no write. |
| `WAIT` | One delegated pull request is open, or applicable CI for the latest merged delegated pull request or current default-branch tip is pending. | Stop until the pull request or CI reaches a terminal state. |
| `BLOCKED` | The current pull request was closed without merge, its goal was closed without successful terminal evidence, or applicable CI failed or cannot be inspected. | Report the blocker; do not replace the goal or repair CI. |
| `RESUME` | One delegated goal has no merged pull request and no trusted Goal Executor completion marker. | Invoke Goal Executor only for that issue. |
| `FINALIZE` | The project issue has the trusted exact completion marker below. | Reverify all completion criteria, close the project as completed, and stop. |
| `NEXT` | All delegated goals are terminal, the project has no trusted completion marker, and applicable CI for the latest merged delegated pull request and current default-branch tip passed. | Re-read the default branch, check completion, then select at most one next goal. |

A delegated goal is terminal only when its pull request was merged or its issue
has Goal Executor's trusted exact completed-without-PR marker. Previous terminal
goals are normal history. A branch belonging to a pull request is not a second
goal.

Before `NEXT`, inspect applicable CI using
`.ai/git/branch-and-pr-workflow.md`. No configured applicable CI is not a
failure. Pending CI means `WAIT`; failed, cancelled, or unavailable CI status
means `BLOCKED`. Only passed CI, or no applicable CI, permits `NEXT`.

These rules prevent ordinary duplicate work and support interrupted runs. They
do not claim an atomic lock or transactional exactly-once execution.

## Complete the project

In `NEXT`, evaluate every Completion criterion against evidence on the current
default branch. A roadmap checkbox or closed issue alone is insufficient.

When all criteria are proven and no delegated work is active, comment with the
evidence and:

```text
<!-- project-executor:completed project=OWNER/REPOSITORY#NUMBER -->
```

Read the comment back. If correct, close the Project Execution issue as
completed. If a later run finds the trusted marker on an open issue, reverify
the criteria. If all remain proven and the marker is correct, finish only the
close. If any criterion is no longer proven or the evidence is contradictory,
enter `CONFLICT`, report the exact gap, and make no write. Do not close the
project, select another goal, or remove or replace the marker.

## Select and execute one goal

If completion is not proven:

1. Compare the project issue, current roadmap, requirements, and default-branch
   evidence.
2. If project readiness or the roadmap is insufficient, select one
   planning/readiness goal before product implementation.
3. Otherwise select the smallest remaining observable outcome that fits one
   reviewable pull request.
4. Exclude completed work, unrelated cleanup, speculative infrastructure, and
   work overlapping another open pull request.
5. If a material decision blocks the next safe goal, ask one grouped batch on
   the project issue per **Material decision questions on GitHub** below and
   stop. Do not repeat unanswered questions.

## Material decision questions on GitHub

When posting a grouped batch on a Project Execution issue (or any GitHub issue
where the human replies in comments):

1. Use at most one comment per stop.
2. For each decision, list **lettered options** (A, B, C, …) plus **Other** when
   none fit.
3. State a **recommended option** and one-line impact per option.
4. Ask the owner to reply with **letters only** (e.g. `1: D, 2: confirm, 3: N/A`).
   Binary decisions may use `confirm`, `Y`, or `N` instead of letters.
5. Do not use open-ended-only questions when alternatives can be enumerated.
6. Do not repeat the same batch until the owner replies or edits the project
   issue.
7. After the owner replies with option letters in a separate comment, they may
   comment exactly `/continue-project` to resume.

Example shape:

### Decision needed — reply with option letters

**1. Optional integration for Phase 3**
- A) Vendor API (hosted)
- B) Alternate vendor API (hosted)
- C) Local runtime only
- D) Skip Phase 3; close on static core *(recommended)*

**2. Data handling** — confirm Y/N: opt-in only, diff-scoped, heuristics default

**3. Secrets for v1** — pick one:
- A) `SERVICE_LLM_PROVIDER` + `SERVICE_LLM_API_KEY`; no base URL for cloud
- B) Same + optional `SERVICE_LLM_BASE_URL` for local runtime only
- C) N/A — no LLM in this project *(recommended if 1=D)*

Create one Agent Goal issue as the authenticated automation identity, containing
Goal, Acceptance criteria, Constraints, Out of scope, Relevant context, and the
exact project marker. Read it back and verify its author login, marker, and scope
before continuing.

Repeat state resolution. Only if that exact issue is the sole `RESUME` goal,
invoke `.ai/automation/goal-executor.md` for it in the same run. The verified
project authorization replaces a separate `/execute-goal` comment only for this
delegated issue. When project authorization was
`/execute-project self-correcting-review`, the delegated Goal Executor run
inherits self-correcting review mode (equivalent to
`/execute-goal self-correcting-review`).

Goal Executor retains ownership of planning, implementation, validation,
branches, commits, pull requests, idempotency, and its Slice 2 stopping point
before merge.
After it stops, Project Executor also stops. Merging a delegated pull request
triggers the next run automatically when the pull request merged trigger is
configured. The owner may comment `/continue-project` as an optional nudge after
material-decision answers or when state resolution entered `WAIT` (for example
applicable CI still pending on the default branch).

Never merge, enable auto-merge, force push, rewrite published history, or push
directly to the protected default branch.
