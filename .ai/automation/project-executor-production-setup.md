# Project Executor — Production Setup

Configure one native Cursor Automation that runs
`.ai/automation/project-executor.md` on **Project Execution** issue comments and
on merged pull requests for delegated goals. The repository does not configure
or verify the live Cursor UI.

## Configuration parameters

| Parameter | Required value | Notes |
|---|---|---|
| Automation name | `Project Executor` | Display name in Cursor Automations. |
| Model | Choose a model capable of repository and GitHub tool use | |
| Trigger events | GitHub **issue comment** and **pull request merged** | See **Comment filter** and **Pull request merged trigger** below. |
| Repository scope | **This repository** | Configure the automation against the repository that contains this documentation. |
| Author filter | **Me** | Cursor UI value. Applies to the issue-comment trigger only. |
| Comment filter regex | Exact match; see **Comment filter** below | No leading or trailing text, whitespace, or punctuation. |
| Live automation prompt | See **Live automation prompt** below | Small stable loader. Loads `.ai/automation/project-executor.md` and `.ai/automation/goal-executor.md` from the repository default branch at the start of every run. |

Prefer one automation with both triggers and the same live prompt. If the UI
requires two entries, duplicate the same configuration and prompt.

Authorization and resume meaning: `.ai/policies/autonomy-and-authorization.md`.

Start disabled and enable the automation only after this change is merged.

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
4. Verify that it creates at most one delegated goal and one review-ready pull
   request (or an explicit blocker comment when review-ready criteria are not
   met). Under `self-correcting-review auto-merge`, when eligible, Goal Executor
   also squash-merges that pull request.
5. Comment `/continue-project` while the pull request is still open (default or
   self-correcting-review path, or auto-merge before merge completes) and verify
   that it makes no change.
6. Default / self-correcting-review path: manually merge the pull request
   without commenting and verify that Project Executor continues (or enters
   `WAIT` when applicable CI is still pending). Auto-merge path: after Goal
   Executor squash-merges, verify that the pull request merged trigger continues
   Project Executor (or enters `WAIT` when applicable CI is still pending on the
   default branch).
7. When merge-time CI is pending, verify that `/continue-project` resumes after
   CI passes.

Merge permissions: the Goal Executor / Project Executor automation identity must
be allowed to squash-merge into the protected default branch when using
`/execute-project self-correcting-review auto-merge`. Project Executor itself
never merges; Goal Executor performs authorized squash merges only with that
flag. Default `/execute-project` and `/execute-project self-correcting-review`
still require human merge.
