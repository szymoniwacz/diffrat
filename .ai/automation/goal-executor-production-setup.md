# Goal Executor — Production Setup

## Purpose

Configure the native Cursor Automation that executes authorized goals from
GitHub issues. Lifecycle, authorization, quality, review, and Git procedures
remain in their canonical files. Slice boundaries:
`.ai/automation/README.md`.

## Prerequisites

- Slice 2 contract present: `.ai/automation/README.md` and
  `.ai/automation/goal-executor.md`
- Maintainer access to Cursor Automations for this GitHub repository
- Repository connected to Cursor with permission to create branches and pull
  requests

## Configuration parameters

| Parameter | Required value | Notes |
|---|---|---|
| Automation name | `Goal Executor` | Display name in Cursor Automations. |
| Model | `Composer 2.5` | Model used for Goal Executor runs. |
| Trigger event | GitHub **issue comment** | Ordinary GitHub issues only. Pull request review threads and pull request comments are out of scope. |
| Repository scope | **This repository** | Configure the automation against the repository that contains this documentation. |
| Author filter | **Me** | Cursor UI value. Restricts execution to comments from the authorized repository owner. |
| Comment filter regex | `^/execute-goal( self-correcting-review)?$` | Exact match on the full comment body. Accepts `/execute-goal` and `/execute-goal self-correcting-review`. No leading or trailing text, whitespace, or punctuation. |
| Live automation prompt | See **Live automation prompt** below | Small stable loader. Loads `.ai/automation/goal-executor.md` from the repository default branch at the start of every run. |

Authorization meaning: `.ai/policies/autonomy-and-authorization.md`.

## Live automation prompt

Paste this block into the Cursor Automation prompt field. Do not paste the full
contents of `.ai/automation/goal-executor.md`.

```text
You are running the Goal Executor automation.

Before any repository mutation or remote write:
1. Resolve the repository default branch.
2. Read .ai/automation/goal-executor.md from that default branch.
3. If the default branch or canonical file cannot be resolved and read, fail closed: make no repository change and perform no remote write.
4. Follow the loaded file as the complete canonical Goal Executor instructions for this run.
```

Later edits to `.ai/automation/goal-executor.md` do not require editing the live
prompt. A change to the loader itself requires a deliberate live configuration
update.

The repository cannot inspect the live Cursor UI value. Verify the saved prompt
manually after any change.

## Setup

Apply the configuration table in Cursor Automations for this repository: create
or open the Goal Executor automation, set each required value, paste the live
automation prompt block above into the prompt field, then save and enable.

## Post-merge loader migration

When replacing a full-file live prompt with the loader:

```text
disable automation
-> human merges this change
-> replace the old full live prompt with the loader block
-> verify the saved prompt exactly
-> enable for one controlled test
-> verify the run loaded the canonical file from the default branch
```

## Private repository access

For private repositories, confirm the cloud agent can read the triggering
GitHub issue before relying on production execution.

1. Run a test authorization or inspect the agent run. The agent must resolve
   **Goal** and **Acceptance criteria** from the triggering issue.
2. When issue access fails, configure `GH_TOKEN` as a **Cursor Runtime Secret**
   scoped to this repository.
3. The token must be able to access the private repository and read Issues.
4. Never store, expose, or print the token in repository files, prompts, pull
   requests, comments, or logs. Follow `.ai/policies/security-policy.md`.

## Per-goal activation

1. Create an **Agent Goal** issue. Complete **Goal** and **Acceptance criteria**.
2. Comment exactly:

   ```txt
   /execute-goal
   ```

3. Expect a cloud agent run that opens a pull request and, when Slice 2
   criteria pass, marks it ready for review. Automation never merges.

Repeated `/execute-goal` comments must not create duplicate work. See
`.ai/automation/README.md`.

## Verification checklist

- [ ] Configuration table values match the live automation.
- [ ] Live automation prompt matches the loader block above exactly.
- [ ] For private repositories, issue read access works or `GH_TOKEN` is set.
- [ ] No secrets appear in repository files, prompts, PRs, comments, or logs.
- [ ] A test Agent Goal issue can be authorized with exact `/execute-goal`.
