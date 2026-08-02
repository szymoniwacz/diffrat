# Cursor Automation Contract

## Purpose

Define automation-specific rules for native Cursor Automations and cloud agents
executing the existing `.ai/` goal-to-PR workflow.

This folder does not replace canonical lifecycle, authorization, quality, review,
or Git rules. Link to those owners instead of copying them.

## Execution plane

Native Cursor Automations and cloud agents are the execution plane.

Do not add a custom GitHub Actions orchestrator, GitHub App, PAT, webhook
bridge, or signing-key management in this repository unless a verified platform
limitation requires it.

## Authorization trigger

Production authorization is an exact `/execute-goal` comment on an ordinary
GitHub issue by the authorized repository owner.

That comment authorizes the canonical `/execute-goal` lifecycle in
`.ai/skills/execute-goal.md`. Goal Executor automation implements Slice 2
through review-ready handoff as a bounded prefix of that lifecycle, and under
`/execute-goal self-correcting-review auto-merge` continues through authorized
squash merge when eligible. It is not an alternative command.

Authorization meaning and question timing:
`.ai/policies/autonomy-and-authorization.md`.

Instruction payload: `.ai/automation/goal-executor.md`.

Production setup: `.ai/automation/goal-executor-production-setup.md`.

Delegated goals may instead inherit one active `/execute-project`
authorization. Merging a delegated pull request with `Closes #<goal-number>`
may trigger Project Executor when that trigger is configured; post-merge
default-branch CI completion resumes it (green → next/finalize; red → CI
repair first). Project-level state and setup live in
`.ai/automation/project-executor.md` and
`.ai/automation/project-executor-production-setup.md`.

## Execution-state resolution

Use only the exact repository and triggering issue number. Never use title,
similar goal text, packet title, plan title, or fuzzy matching as identity.

### Timing

Run the complete state-resolution procedure twice during every run:

1. once before any agent-initiated repository mutation, branch creation or
   switch, implementation, commit, or remote write;
2. again immediately before the first remote write of that run.

The second check is mandatory for new work, an existing branch, an existing PR,
and a completed-without-PR result. A remote write includes:

- push or remote branch publication;
- pull request creation or metadata update;
- issue or pull request comment creation or edit;
- authorized squash merge of a pull request.

### Durable evidence

- A Goal Executor pull request is linked by the exact mandatory closing
  reference `Closes #<issue-number>` in its body.
- A Goal Executor branch created without a pull request is linked by the literal
  token `issue-<issue-number>` in its remote branch name. Example:
  `cursor/issue-123-short-slug`.
- A completed-without-PR outcome is linked by the exact hidden marker below.
- A task packet or plan, when one happens to exist, may provide supporting
  evidence but is never required and is never the sole identity mechanism.

A pull request head branch is part of that pull request. Do not count it again as
a separate orphan or resumable branch.

### Normalize evidence

Inspect issue state and state reason, linked pull requests in every state,
linked remote branches, commits, and the completed-without-PR marker. Apply the
priority order below. First matching state wins. The normalized result must be
exactly one state.

Treat evidence as `CONFLICT` when any of these is true:

- more than one linked open pull request exists;
- more than one linked orphan branch exists;
- one linked open pull request and a different linked orphan branch coexist;
- terminal completion evidence coexists with an open pull request, orphan branch,
  or closed-unmerged pull request;
- more than one closed-unmerged pull request exists;
- a closed-unmerged pull request coexists with an open pull request or orphan
  branch;
- available evidence cannot be mapped to exactly one normalized state.

Multiple completion signals that all describe the same completed execution are
not a conflict by themselves.

| Priority | Normalized state | Exact condition | Required action |
|---|---|---|---|
| 1 | `CANCELLED` | Issue is closed with state reason `not_planned`. | Stop as a cancelled no-op. Do not resume, create, update, commit, push, open a pull request, or write a comment. Report any existing linked artifacts for human cleanup. |
| 2 | `UNKNOWN_CLOSED` | Issue is closed but its state reason is missing, unreadable, or neither `completed` nor `not_planned`. | Stop with an explicit state-resolution blocker and make no write. |
| 3 | `CONFLICT` | Evidence is contradictory or ambiguous under the conflict rules above. | Stop with an explicit ambiguity blocker. List the exact conflicting pull requests and branches. Do not choose or mutate one. |
| 4 | `COMPLETED` | No conflict exists, and at least one terminal completion signal exists: issue closed as `completed`, a linked merged pull request, or the exact completed-without-PR marker. | Stop as an already-completed no-op. Make no branch, commit, push, pull request, or comment. |
| 5 | `CLOSED_UNMERGED` | No terminal or conflicting evidence exists, and exactly one linked pull request is closed without merge. | Stop with an explicit blocker. Do not create replacement work. |
| 6 | `RESUME_PR` | Issue is open, no terminal, closed-unmerged, or conflicting evidence exists, and exactly one linked open pull request exists. | Resume only that pull request's head branch and update only that pull request. |
| 7 | `RESUME_BRANCH` | Issue is open, no linked pull request or terminal, closed-unmerged, or conflicting evidence exists, and exactly one linked remote branch without a pull request exists. | Resume only that branch and create at most one pull request for it. |
| 8 | `NEW` | Issue is open and no linked pull request, linked remote branch, terminal marker, or other prior execution evidence exists. | Start exactly one new execution. |

This is deterministic duplicate prevention and safe resumption. Do not claim
transactional exactly-once execution or an atomic lock that the repository does
not implement.

### Required creation rules

Every newly created Goal Executor branch must include the exact
`issue-<issue-number>` token.

Every Goal Executor implementation pull request must contain
`Closes #<issue-number>` for its triggering issue.

Any task packet or plan created by ordinary future runs must carry the exact
issue URL or `owner/repository#number`, not only a prose title.

Do not add labels, a database, a state directory, or a new repository artifact
for idempotency.

### Completed without a PR

When the goal is already satisfied and no repository change or pull request is
needed, write one concise issue comment containing this hidden marker:

```text
<!-- goal-executor:completed-without-pr issue=OWNER/REPOSITORY#NUMBER -->
```

The visible comment must state why no change was required and cite the evidence.
After writing it, read the remote comment back and verify the marker and visible
text. A later run treats the marker as terminal evidence.

Do not use this marker for failures or blockers.

## Resume evidence

Resume from repository evidence, not chat history: issue body, branch, commits,
and pull request state. See `.ai/policies/autonomy-and-authorization.md`.

## Bounded iteration

Default limits for one authorized goal run:

- local implementation, review, and fix loop: maximum 3 iterations,
- repeated handling of the same review finding: maximum 2 attempts.

When a limit is reached, preserve evidence, explain the blocker, and stop.

Remote CI repair loops are in scope for the current Goal Executor automation
(Slice 2). Stop when bounded iteration limits are reached.

## Attribution verification

Remote commit messages, pull request titles and bodies, and generated GitHub
comments must not contain prohibited attribution. After pull request creation or
update, inspect the actual remote pull request body and remove prohibited
platform-added footer markup when possible. Procedure:
`.ai/git/branch-and-pr-workflow.md`.

When signed cloud commits are expected, any commit in the pull request range
that is not GitHub Verified is an immediate blocker.

After authorized `self-correcting-review auto-merge` squash, Goal Executor must
supply a clean squash title/body and verify the default-branch tip per
**Commits on `main`** (platform-injected `Co-authored-by: Cursor Agent` and
platform-added user `Co-authored-by` on that tip are allowed).

## Slice boundaries

**Slice 1 (superseded):** stopped after a validated draft pull request.

**Slice 2 (current default):** continues through remote CI stabilization,
diff-risk recording, and marking the pull request ready for review. Default and
escalated paths stop before merge.

**Self-correcting extension:** when `self-correcting-review auto-merge` is
authorized and eligible, Goal Executor continues from Slice 2 through authorized
squash merge per `.ai/git/branch-and-pr-workflow.md`.

Report the stopping point when blocked. Claim merge authorization only for that
`auto-merge` eligible path.

## Merge policy

Agents and automations must never merge pull requests except under authorized
eligible `self-correcting-review auto-merge` (Goal Executor squash merge).
Default, self-correcting-without-auto-merge, and escalated paths: only humans
merge after review. Do not enable GitHub auto-merge queue. Project Executor
never merges.

