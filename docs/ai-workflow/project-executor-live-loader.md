# Diffrat Project Executor — default-branch live loader

This file is the **public** Project Executor entrypoint on the Diffrat default
branch. Full Project Executor and Goal Executor runtimes are **not** committed
under `.ai/automation/` on `main` (private submodule `.ai-template/`; see
[../ai-workflow-setup.md](../ai-workflow-setup.md)).

Cursor Automations for this repository must load **this** file from the default
branch. Paste the live prompt from [../ai-workflow-setup.md](../ai-workflow-setup.md).

## Resolve canonical Project + Goal Executor instructions

Before any repository mutation or remote write:

1. Resolve the repository default branch and confirm this loader was read from
   that branch (or from an equivalent trusted default-branch checkout).
2. Resolve the **full** runtimes using the first readable path for each file:

   | Runtime | Priority 1 (materialized) | Priority 2 (submodule) |
   |---|---|---|
   | Project Executor | `.ai/automation/project-executor.md` | `.ai-template/.ai/automation/project-executor.md` |
   | Goal Executor | `.ai/automation/goal-executor.md` | `.ai-template/.ai/automation/goal-executor.md` |

3. If either file is missing, initialize/update `.ai-template` when credentials
   allow (`git submodule update --init --recursive .ai-template`; CI uses
   `SUBMODULE_DEPLOY_KEY`), optionally run `./scripts/setup-ai-workflow.sh`,
   and retry step 2.
4. If either full runtime still cannot be read, **fail closed** (no repo
   mutation, no remote write) and point to `docs/ai-workflow-setup.md`.
5. Follow `project-executor.md` for orchestration and `goal-executor.md` for any
   delegated goal.
6. If this run was triggered by a merged pull request, resolve the parent
   Project Execution issue via `Closes #<goal>` and the
   `project-executor:goal` marker before state resolution. If resolution fails,
   no-op.
7. If this run was triggered by CI or workflow completion on the default
   branch, resolve the single active authorized Project Execution issue
   (prefer the project linked from the latest merged delegated goal on that
   tip). If resolution fails or is ambiguous, no-op.
