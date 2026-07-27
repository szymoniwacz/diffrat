# Project Executor — Production Setup

Configure one native Cursor Automation that runs
`.ai/automation/project-executor.md` on a regular schedule. The repository does
not configure or verify the live Cursor UI.

## Configuration

- Name: `Project Executor`
- Repository: this repository
- Trigger: schedule; hourly is a suitable default
- Model: choose a model capable of repository and GitHub tool use
- Start disabled and enable it only after this change is merged

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
4. Enable one controlled scheduled run.
5. Verify that it creates at most one delegated goal and one review-ready pull
   request (or an explicit blocker comment when review-ready criteria are not
   met).
6. Run it again while the pull request is open and verify that it makes no
   change.
7. Manually merge the pull request and verify that a later run reads the new
   default branch before continuing.

Agents never merge.
