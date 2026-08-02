# Project Executor — Production Setup

Configure one native Cursor Automation that runs
`.ai/automation/project-executor.md` on **Project Execution** issue comments,
on merged pull requests for delegated goals, and on applicable CI/workflow
completion for the **default branch** only. Goal Executor owns PR-head CI
resume (see `.ai/automation/goal-executor-production-setup.md`). The repository
does not configure or verify the live Cursor UI.

## Configuration parameters

| Parameter | Required value | Notes |
|---|---|---|
| Automation name | `Project Executor` | Display name in Cursor Automations. |
| Model | Choose a model capable of repository and GitHub tool use | |
| Trigger events | GitHub **issue comment**, **pull request merged**, and **CI/workflow completed** on the default branch | See **Comment filter**, **Pull request merged trigger**, and **CI/workflow completed trigger** below. |
| Repository scope | **This repository** | Configure the automation against the repository that contains this documentation. |
| Author filter | **Me** | Cursor UI value. Applies to the issue-comment trigger only. |
| Comment filter regex | Exact match; see **Comment filter** below | No leading or trailing text, whitespace, or punctuation. |
| Live automation prompt | See **Live automation prompt** below | Small stable loader. Loads `.ai/automation/project-executor.md` and `.ai/automation/goal-executor.md` from the repository default branch at the start of every run. |

Prefer one automation with all triggers and the same live prompt. If the UI
requires separate entries, duplicate the same configuration and prompt.

Authorization and resume meaning: `.ai/policies/autonomy-and-authorization.md`.

Start disabled and enable the automation only after this change is merged.

## Required live UI update after this change

Repository docs alone do not update Cursor Automations. After merging a change
to this loader or to the trigger table:

1. Open the live **Project Executor** automation for this repository.
2. Confirm triggers are issue comment, pull request merged, and **CI/workflow
   completed on the default branch only** (remove any PR-head CI trigger from
   Project Executor; Goal Executor owns that path).
3. Replace the saved prompt with the **Live automation prompt** block above
   (seven steps; no non-default CI step).
4. Save before the next `/execute-project` run.

## Comment filter

```text
^/(execute-project( self-correcting-review( auto-merge)?)?|continue-project)$
```

Accepts `/execute-project`, `/execute-project self-correcting-review`,
`/execute-project self-correcting-review auto-merge`, and `/continue-project`
only.
## Pull request merged trigger

GitHub **pull request merged** on this repository. Use the same automation name,
model, repository scope, and live automation prompt as the issue-comment
trigger.

## CI/workflow completed trigger

GitHub **CI/workflow completed** (or equivalent check-suite / workflow-run
completed event) for the **default branch** only. Fire on success and failure
so Project Executor can enter `NEXT`/`FINALIZE` when green or `REPAIR` when red
after merge. Ignore non-default / pull request head branches here — Goal
Executor owns that resume path.

Use the same automation name, model, repository scope, and live automation
prompt as the other Project Executor triggers.

## Live automation prompt

Paste this loader into the automation prompt:

```text
You are running the Project Executor automation.

Before any repository mutation or remote write:
1. Resolve the repository default branch.
2. Read .ai/automation/project-executor.md from that default branch.
3. Read .ai/automation/goal-executor.md from that default branch.
4. If the default branch or either file cannot be read, make no change or remote write and report the blocker.
5. Follow project-executor.md for orchestration and goal-executor.md for the delegated goal.
6. If this run was triggered by a merged pull request, resolve the parent Project Execution issue via Closes #<goal> and the project-executor:goal marker before state resolution. If resolution fails, no-op.
7. If this run was triggered by CI or workflow completion on the default branch, resolve the single active authorized Project Execution issue (prefer the project linked from the latest merged delegated goal on that tip). If resolution fails or is ambiguous, no-op.
```

Keep repository access limited to the issues, branches, commits, pull requests,
and workflow status required by those two runtimes. Store any required token as
a Cursor Runtime Secret; never commit or print it.

## Activate and verify

1. Create a **Project Execution** issue.
2. Fill its outcome, completion criteria, constraints, and context.
3. Comment exactly `/execute-project` as the authorized owner (or
   `/execute-project self-correcting-review` for self-correcting review without
   agent merge, or `/execute-project self-correcting-review auto-merge` for
   self-correcting review plus authorized squash merge on eligible delegated
   goals).
4. Verify that it creates at most one delegated goal and that Goal Executor
   opens a pull request, waits for applicable PR CI (or resumes via Goal
   Executor PR-head CI), and reaches review-ready (or an explicit blocker).
   Under `self-correcting-review auto-merge`, when eligible, Goal Executor also
   squash-merges that pull request.
5. Comment `/continue-project` while the pull request is still open on the
   human-merge path (default or self-correcting-review without auto-merge) and
   verify that it makes no change when state is already `WAIT` for human merge.
6. Default / self-correcting-review path: manually merge the pull request
   without commenting. Auto-merge path: after Goal Executor squash-merges.
   Verify that the pull request merged trigger runs Project Executor and, when
   applicable CI on the default branch is still pending, enters `WAIT`, posts
   one status comment on the Project Execution issue, and does not select the
   next product goal. For auto-merge, also verify the squash used an explicit
   clean title/body and the tip passes **Commits on `main`**.
7. When merge-time CI on the default branch turns green, verify that the
   CI/workflow completed trigger resumes Project Executor into `NEXT` or
   `FINALIZE` without requiring `/continue-project`.
8. When merge-time CI on the default branch turns red, verify that the
   CI/workflow completed trigger enters `REPAIR`, creates at most one CI-fix
   delegated goal, and does not advance unrelated product work until CI is
   green.
9. Force a `CONFLICT` or `BLOCKED` path in a disposable test and verify Project
   Executor posts exactly one status comment with state, evidence, and resume
   path before stopping.

Merge permissions: the Goal Executor / Project Executor automation identity must
be allowed to squash-merge into the protected default branch when using
`/execute-project self-correcting-review auto-merge`. Project Executor itself
never merges; Goal Executor performs authorized squash merges only with that
flag. Default `/execute-project` and `/execute-project self-correcting-review`
still require human merge.
