# Project Executor — Cursor Automation Instructions

Project Executor is an event-driven orchestrator around the existing Goal
Executor. It selects at most one goal, invokes Goal Executor, and then waits
for the delegated pull request to merge: human merge after human CR (default);
human merge after an eligible self-verified handoff
(`/execute-project self-correcting-review`); Goal Executor authorized squash
merge after an eligible self-verified handoff
(`/execute-project self-correcting-review auto-merge`); or human merge after
human CR if escalated. It does not copy the goal lifecycle or merge pull
requests itself.

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
  opts eligible delegated goals into self-correcting review mode (skip human CR
  when eligible; human still merges). Same mode rules as
  `/execute-goal self-correcting-review`:
  `.ai/policies/autonomy-and-authorization.md` and
  `.ai/review/self-correcting-review-loop.md`. Ineligible goals escalate to
  human CR (no agent merge).
- `/execute-project self-correcting-review auto-merge` is the same as
  `self-correcting-review` and also opts eligible delegated goals into
  authorized squash merge by Goal Executor (same as
  `/execute-goal self-correcting-review auto-merge`).
- `/continue-project` is an optional manual nudge on an already authorized
  project: after material-decision answers, or when the owner wants to retry
  sooner after an unexpected stop. It does not authorize a project by itself
  and does not replace `/execute-project` after issue edits. It is not required
  for ordinary post-merge CI pending or failed CI when the default-branch
  CI/workflow completed trigger is configured, or for draft / incomplete
  Goal Executor handoff when Goal Executor's PR-head CI resume is configured.
  If no valid authorization exists, stop as a no-op without writing.

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
5. Verify `/execute-project`, `/execute-project self-correcting-review`, or
   `/execute-project self-correcting-review auto-merge` authorization on that
   project issue after the most recent edit to its title or scope fields.
6. Run the same state resolution and actions as for a comment trigger on that
   project issue.

Fail closed without writing when: the body has no `Closes #<goal-number>`, the
goal is not a delegated Project Executor goal, authorization is missing or
invalid, or the merge cannot be linked to an active authorized project.

Merging a delegated pull request continues the project automatically when the
pull request merged trigger is configured. When applicable CI on the default
branch is still pending, enter `WAIT`, post one status comment, and stop; the
CI/workflow completed trigger resumes automatically. The owner does not need
`/continue-project` after merge for that ordinary pending-CI path.

### CI or workflow completed

When this run was triggered by applicable CI or workflow completion on the
**default branch** (post-merge tip):

1. Confirm the event is for the current default-branch tip (ignore other
   branches).
2. Resolve exactly one active authorized Project Execution issue: prefer the
   project linked from the latest merged delegated goal that produced this tip
   (`Closes #<goal>` + trusted `project-executor:goal` marker); otherwise the
   single open authorized Project Execution issue in the repository.
3. If none or more than one active authorized project resolves, stop as a no-op
   without writing.
4. Run the same state resolution and actions as for a comment trigger on that
   project issue.

Green applicable CI on the default branch permits `NEXT` or `FINALIZE`. Failed
applicable CI enters `REPAIR` (fix CI first) rather than advancing product
goals. Cancelled or uninspectable CI remains `BLOCKED`.

Do not handle PR-head (non-default) CI here. Goal Executor owns PR-head CI
resume through review-ready handoff and eligible auto-merge:
`.ai/automation/goal-executor.md`.

## Authorization

An active project is one open **Project Execution** issue that:

- starts with `[Project Execution]:`;
- contains Product outcome and Completion criteria;
- has an exact `/execute-project`, `/execute-project self-correcting-review`,
  or `/execute-project self-correcting-review auto-merge` comment by the
  authorized repository owner posted after the most recent edit to its title
  or any **scope field** (Product outcome, Completion criteria, Constraints,
  Out of scope, Relevant context).

Edits to the **Commands** section alone do **not** invalidate authorization.
**Commands** is human reference only: ignore it for product boundary, goal
selection, planning, and implementation.

The `self-correcting-review` form opts eligible delegated goals into
self-correcting review mode (human still merges). The
`self-correcting-review auto-merge` form also opts them into authorized squash
merge by Goal Executor when eligible. Each goal still fails closed to human CR
(no agent merge) when ineligible. See
`.ai/policies/autonomy-and-authorization.md`.

The scope fields are the project boundary. If there is no active project, stop
as a no-op. If more than one exists, list them and stop without writing. Any
later title or scope-field edit invalidates the authorization until the owner
comments exactly `/execute-project`, `/execute-project self-correcting-review`,
or `/execute-project self-correcting-review auto-merge` again. If edit ordering
cannot be verified, treat the project as unauthorized and make no write.

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
or unverifiable author is conflicting evidence; enter `CONFLICT`, post one
status comment, and make no other write. Never infer identity from a display
name.

Trust a completed-without-PR or project completion marker only when its exact
remote comment has been read from GitHub, its author login exactly matches the
authenticated automation identity, and its repository and issue reference
matches the expected goal or project. Any other or unverifiable marker is
conflicting evidence; enter `CONFLICT`, post one status comment, and make no
other write.

Resolve state before any repository mutation and again immediately before the
first remote write. Find every goal with that exact marker and its pull request
through the Goal Executor's required `Closes #<goal-number>` reference.

Apply the first matching state:

| State | Evidence | Action |
|---|---|---|
| `CONFLICT` | More than one delegated goal is non-terminal, completion evidence coexists with active work, or evidence is contradictory. | Post one status comment listing exact conflicts; make no other write. |
| `WAIT` | Applicable CI for the latest merged delegated pull request or current default-branch tip is pending; **or** one delegated pull request is open, ready for review, and merge is human-owned (`auto-merge` not authorized or the goal escalated / ineligible). | Post one status comment; stop. Do not select the next product goal. Resume automatically when the PR merges, when default-branch CI/workflow completed fires, or when Goal Executor finishes an auto-merge path. |
| `RESUME` | One delegated goal still needs Goal Executor: no pull request yet; open draft or not review-ready PR; open PR whose CI just completed and handoff/merge is incomplete; or review-ready PR with authorized eligible `auto-merge` not yet merged. | Invoke Goal Executor only for that issue. |
| `REPAIR` | All other non-terminal delegated work is absent, and applicable CI for the latest merged delegated pull request or current default-branch tip failed. | Select at most one CI-repair goal scoped to fixing that failure on the default-branch tip; create it if needed; invoke Goal Executor. Do not advance unrelated product goals while CI is red. |
| `BLOCKED` | The current pull request was closed without merge, its goal was closed without successful terminal evidence, applicable CI is cancelled or cannot be inspected, or a CI-repair path cannot proceed safely. | Post one status comment reporting the blocker; do not invent product work. |
| `FINALIZE` | The project issue has the trusted exact completion marker below. | Reverify all completion criteria, close the project as completed, and stop. |
| `NEXT` | All delegated goals are terminal, the project has no trusted completion marker, and applicable CI for the latest merged delegated pull request and current default-branch tip passed. | Re-read the default branch, check completion, then select at most one next goal. |

A delegated goal is terminal only when its pull request was merged or its issue
has Goal Executor's trusted exact completed-without-PR marker. Previous terminal
goals are normal history. A branch belonging to a pull request is not a second
goal. An open CI-repair goal counts as the sole `RESUME` goal.

Before `NEXT` or `FINALIZE` completion close, inspect applicable CI using
`.ai/git/branch-and-pr-workflow.md`. No configured applicable CI is not a
failure. Pending CI means `WAIT`; failed CI means `REPAIR`; cancelled or
unavailable CI status means `BLOCKED`. Only passed CI, or no applicable CI,
permits `NEXT`.

### Status comments before stop

After state resolution identifies an active authorized Project Execution issue,
do not stop silently on `CONFLICT`, `WAIT`, `BLOCKED`, or a failed `FINALIZE`
reverify. Post **exactly one** status comment on that project issue before
stopping.

The comment must include:

1. the resolved state name (`CONFLICT`, `WAIT`, `BLOCKED`, or why `FINALIZE`
   cannot complete);
2. concrete evidence (pull request number, CI conclusion or pending checks,
   conflicting goal numbers, or the missing/contradictory completion criterion);
3. what resumes the run (pull request merged trigger, default-branch
   CI/workflow completed, Goal Executor PR-head CI resume for draft handoff,
   owner `/continue-project` after a material-decision reply, or an owner
   action for a hard blocker).

That status comment is the only allowed write for those stops. Do not create
goals, edit scope fields, remove or replace markers, or close the project in
the same stop.

Still make **no write** (true no-ops) when: no active authorized project
resolves; `/continue-project` without valid authorization; a merge or CI
trigger cannot link to exactly one project; or the live-loader precondition
fails before a project is resolved.

`RESUME`, `REPAIR`, and `NEXT` that proceed do not need a separate status
comment before their goal-creation or Goal Executor writes. A material-decision
stop uses the decision-batch comment (that counts as the required status).
Successful `FINALIZE` uses the completion-marker comment.

### CI-repair goals

In `REPAIR`:

1. Scope the goal strictly to restoring green applicable CI on the current
   default-branch tip (fix the failing checks; no product-feature expansion).
2. Keep one reviewable pull request; inherit the project's self-correcting /
   auto-merge authorization the same way as other delegated goals.
3. After that repair PR merges, wait for CI again (`WAIT` while pending;
   `REPAIR` again if still red; `NEXT`/`FINALIZE` only when green).

These rules prevent ordinary duplicate work and support interrupted runs. They
do not claim an atomic lock or transactional exactly-once execution.

## Complete the project

In `NEXT`, evaluate every Completion criterion against evidence on the current
default branch. A roadmap checkbox or closed issue alone is insufficient.

When evaluating Constraints that mention commit attribution on the default
branch, apply **Attribution by surface** / **Commits on `main`** in
`.ai/git/branch-and-pr-workflow.md`. Do not fail completion solely because of
platform-injected `Co-authored-by: Cursor Agent` or platform-added user
`Co-authored-by` trailers on a tip produced by authorized
`self-correcting-review auto-merge` squash.

When all criteria are proven and no delegated work is active, comment with the
evidence and:

```text
<!-- project-executor:completed project=OWNER/REPOSITORY#NUMBER -->
```

Read the comment back. If correct, close the Project Execution issue as
completed. If a later run finds the trusted marker on an open issue, reverify
the criteria. If all remain proven and the marker is correct, finish only the
close. If any criterion is no longer proven or the evidence is contradictory,
enter `CONFLICT`, post one status comment with the exact gap, and make no other
write. Do not close the project, select another goal, or remove or replace the
marker.

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
`/execute-goal self-correcting-review`). When project authorization was
`/execute-project self-correcting-review auto-merge`, the delegated run also
inherits authorized squash merge (equivalent to
`/execute-goal self-correcting-review auto-merge`).

Goal Executor retains ownership of planning, implementation, validation,
branches, commits, pull requests, idempotency, review-ready handoff, PR-head
CI resume, and — when `self-correcting-review auto-merge` is active and
eligible — authorized squash merge. After Goal Executor stops (review-ready
without merge, escalated, blocked, or after a successful auto-merge), Project
Executor also stops. When Goal Executor leaves a draft or incomplete handoff,
Goal Executor's PR-head CI/workflow completed trigger must resume that handoff
without `/continue-project`. Merging a delegated pull request (human or Goal
Executor) triggers the next Project Executor run when the pull request merged
trigger is configured. When that run enters `WAIT` because applicable
default-branch CI is pending, the default-branch CI/workflow completed trigger
resumes Project Executor automatically. The owner may comment
`/continue-project` as an optional nudge after material-decision answers or
after an unexpected stop.

Project Executor never merges, never enables GitHub auto-merge queue, never
force pushes, never rewrites published history, and never pushes directly to the
protected default branch.
