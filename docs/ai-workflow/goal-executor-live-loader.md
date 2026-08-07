# Diffrat Goal Executor — default-branch live loader

This file is the **public** Goal Executor entrypoint on the Diffrat default
branch. It exists because the full Goal Executor runtime is **not** committed
under `.ai/automation/` on `main` (private `ai-project-template` via
`.ai-template/`; see [../ai-workflow-setup.md](../ai-workflow-setup.md)).

Cursor Automations for this repository must load **this** file from the default
branch (not `origin/main:.ai/automation/goal-executor.md`). Paste the live
prompt from [../ai-workflow-setup.md](../ai-workflow-setup.md).

## Resolve canonical Goal Executor instructions

Before any repository mutation or remote write:

1. Resolve the repository default branch and confirm this loader was read from
   that branch (or from an equivalent trusted default-branch checkout).
2. Resolve the **full** Goal Executor runtime using the first readable path:

   | Priority | Path |
   |---|---|
   | 1 | `.ai/automation/goal-executor.md` (after `./scripts/setup-ai-workflow.sh`) |
   | 2 | `.ai-template/.ai/automation/goal-executor.md` (initialized submodule) |

3. If neither path is readable:
   - initialize/update the `.ai-template` submodule when credentials allow
     (`git submodule update --init --recursive .ai-template`; CI uses
     `SUBMODULE_DEPLOY_KEY`);
   - optionally run `./scripts/setup-ai-workflow.sh` to materialize `.ai/`;
   - retry step 2.
4. If the full runtime still cannot be read, **fail closed**:
   - make no repository file changes;
   - create no branch, commit, push, pull request, or merge;
   - perform no remote write;
   - report that Diffrat keeps Goal Executor privately in `.ai-template/` /
     materialized `.ai/`, and point to `docs/ai-workflow-setup.md`.
5. Follow the resolved full file as the complete Goal Executor instructions for
   this run. Do not treat this short loader as a substitute for that runtime.
6. If this run was triggered by CI or workflow completion on a non-default
   branch, resolve the open pull request for that head branch, read
   `Closes #<issue>`, reverify authorization, and resume that goal only. If
   resolution fails, no-op.
7. Never treat "draft PR created" as success. If the authorized PR is still
   draft, finish CI stabilization through ready-for-review (and auto-merge when
   eligible) in this run, or stop only with an explicit blocker.

## Manual `/execute-goal` (chat)

Outside Cursor Automation, after local setup, read
`.ai/automation/goal-executor.md` (or `.ai-template/.ai/automation/goal-executor.md`)
directly from the working tree. This loader file is for the automation gate.
