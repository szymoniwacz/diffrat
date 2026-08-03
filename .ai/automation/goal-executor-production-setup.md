# Goal Executor — Production Setup

## Purpose

Configure the native Cursor Automation that executes authorized goals from
GitHub issues. Lifecycle, authorization, quality, review, and Git procedures
remain in their canonical files. Slice boundaries:
`.ai/automation/README.md`.

## Prerequisites

- Goal Executor contract present: `.ai/automation/README.md` and
  `.ai/automation/goal-executor.md`
- Maintainer access to Cursor Automations for this GitHub repository
- Repository connected to Cursor with permission to create branches and pull
  requests
- For `/execute-goal self-correcting-review auto-merge` squash merge: automation
  identity allowed to squash-merge into the protected default branch
  (branch-protection allowlist / required-review rules must permit that identity
  when no human review is required for eligible self-verified PRs)

## Configuration parameters

| Parameter | Required value | Notes |
|---|---|---|
| Automation name | `Goal Executor` | Display name in Cursor Automations. |
| Model | `Composer 2.5` | Model used for Goal Executor runs. |
| Trigger events | GitHub **issue comment** and **CI/workflow completed** on non-default (pull request head) branches | See **Comment filter** and **CI/workflow completed trigger** below. Issue comments authorize and start work; PR-head CI completion resumes review-ready handoff / merge when a prior run stopped early. |
| Repository scope | **This repository** | Configure the automation against the repository that contains this documentation. |
| Author filter | **Me** | Cursor UI value. Restricts issue-comment execution to the authorized repository owner. |
| Comment filter regex | Exact match; see **Comment filter** below | No leading or trailing text, whitespace, or punctuation. Prefer one filter or split exact filters per command. |
| Live automation prompt | See **Live automation prompt** below | Small stable loader. Loads `.ai/automation/goal-executor.md` from the repository default branch at the start of every run. |

Prefer one automation with both triggers and the same live prompt. If the UI
requires separate entries, duplicate the same configuration and prompt.

Authorization meaning: `.ai/policies/autonomy-and-authorization.md`.

## Comment filter

```text
^/execute-goal( self-correcting-review( auto-merge)?)?$
```

Accepts `/execute-goal`, `/execute-goal self-correcting-review`, and
`/execute-goal self-correcting-review auto-merge`. Exact match on the full
comment body.

## CI/workflow completed trigger

GitHub **CI/workflow completed** (or equivalent check-suite / workflow-run
completed event) for **non-default branches** that are open pull request heads
in this repository. Fire on both success and failure so Goal Executor can
finish review-ready handoff, fix in-scope CI failures, or stop with a blocker.
Ignore the default branch here (Project Executor owns default-branch CI resume).
Use the same automation name, model, repository scope, and live automation
prompt as the issue-comment trigger.

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
5. If this run was triggered by CI or workflow completion on a non-default branch, resolve the open pull request for that head branch, read Closes #<issue>, reverify authorization, and resume that goal only. If resolution fails, no-op.
6. Never treat "draft PR created" as success. If the authorized PR is still draft, finish CI stabilization through ready-for-review (and auto-merge when eligible) in this run, or stop only with an explicit blocker.
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

## Required live UI update after this change

Repository docs alone do not update Cursor Automations. After merging a change
to this loader or to the trigger table:

1. Open the live **Goal Executor** automation for this repository.
2. Confirm **CI/workflow completed** is enabled for non-default / PR head
   branches (success and failure), in addition to issue comment.
3. Replace the saved prompt with the **Live automation prompt** block above
   (including step 6).
4. Save and run one draft-handoff smoke test before relying on production.

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

3. Expect a cloud agent run that opens a pull request, **waits for applicable
   PR CI**, and when review-ready criteria pass, marks it ready for review. Default
   `/execute-goal` and `/execute-goal self-correcting-review` never merge. With
   `/execute-goal self-correcting-review auto-merge`, when eligible, Goal
   Executor squash-merges after that handoff. If a run still ends while the PR
   is draft and CI later completes, the PR-head CI/workflow completed trigger
   must resume Goal Executor without a human comment.
4. For an auto-merge smoke test: authorize with
   `/execute-goal self-correcting-review auto-merge` on a low-risk docs-only
   goal, confirm the PR merges with an explicit clean squash title/body from
   Goal Executor, and confirm the default-branch tip passes **Commits on
   `main`** in `.ai/git/branch-and-pr-workflow.md` (platform-injected
   `Co-authored-by: Cursor Agent` / user `Co-authored-by` alone are allowed).
   Also confirm that ending a run at draft is not treated as success when CI is
   still pending, and that PR-head CI completion resumes handoff/merge.

Repeated `/execute-goal` comments must not create duplicate work. See
`.ai/automation/README.md`.

## Verification checklist

- [ ] Configuration table values match the live automation.
- [ ] Live automation prompt matches the loader block above exactly.
- [ ] For private repositories, issue read access works or `GH_TOKEN` is set.
- [ ] No secrets appear in repository files, prompts, PRs, comments, or logs.
- [ ] A test Agent Goal issue can be authorized with exact `/execute-goal`.
- [ ] For auto-merge: automation identity can squash-merge to the protected
      default branch; a `/execute-goal self-correcting-review auto-merge` smoke
      test merges with an explicit clean squash message and tip attribution
      that passes **Commits on `main`** (platform-injected Cursor Agent / user
      `Co-authored-by` alone allowed).
- [ ] CI/workflow completed trigger is configured for non-default PR head
      branches (success and failure) with the loader step that resumes via
      `Closes #<issue>`.
- [ ] A draft PR whose first run ends early is resumed by PR-head CI completion
      through ready-for-review (and squash when auto-merge eligible) without
      `/continue-project` or a second `/execute-goal`.
