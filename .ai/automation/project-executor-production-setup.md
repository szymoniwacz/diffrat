# Project Executor — Production Setup

Configure one native Cursor Automation that runs
`.ai/automation/project-executor.md` when the authorized repository owner
comments on a **Project Execution** issue. The repository does not configure or
verify the live Cursor UI.

## Configuration parameters

| Parameter | Required value | Notes |
|---|---|---|
| Automation name | `Project Executor` | Display name in Cursor Automations. |
| Model | Choose a model capable of repository and GitHub tool use | |
| Trigger event | GitHub **issue comment** | Ordinary GitHub issues only. Pull request review threads and pull request comments are out of scope. |
| Repository scope | **This repository** | Configure the automation against the repository that contains this documentation. |
| Author filter | **Me** | Cursor UI value. Restricts execution to comments from the authorized repository owner. |
| Comment filter regex | Exact match; see **Comment filter** below | No leading or trailing text, whitespace, or punctuation. |
| Live automation prompt | See **Live automation prompt** below | Small stable loader. Loads `.ai/automation/project-executor.md` and `.ai/automation/goal-executor.md` from the repository default branch at the start of every run. |

Authorization and resume meaning: `.ai/policies/autonomy-and-authorization.md`.

Start disabled and enable the automation only after this change is merged.

## Comment filter

```text
^/(execute-project|continue-project)$
```

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
```

Keep repository access limited to the issues, branches, commits, pull requests,
and workflow status required by those two runtimes. Store any required token as
a Cursor Runtime Secret; never commit or print it.

## Activate and verify

1. Create a **Project Execution** issue.
2. Fill its outcome, completion criteria, constraints, and context.
3. Comment exactly `/execute-project` as the authorized owner.
4. Verify that it creates at most one delegated goal and one review-ready pull
   request (or an explicit blocker comment when review-ready criteria are not
   met).
5. Comment `/continue-project` while the pull request is open and verify that it
   makes no change.
6. Manually merge the pull request, then comment `/continue-project` and verify
   that a later run reads the new default branch before continuing.

Agents never merge.
