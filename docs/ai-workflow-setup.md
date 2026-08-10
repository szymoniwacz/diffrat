# Private AI workflow setup

Owner/maintainer runbook. The reusable AI workflow lives in the private
submodule `.ai-template/` (`szymoniwacz/ai-project-template`) and is not
shared. Product users install and run Diffrat via the Setup section in
`README.md` only — they do not need this document or submodule access.

## Local setup

```bash
git clone --recurse-submodules git@github.com:szymoniwacz/diffrat.git
cd diffrat
./scripts/setup-ai-workflow.sh
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive .ai-template
./scripts/setup-ai-workflow.sh
```

After setup, `.ai/` is a local merge of the private template plus committed
diffrat product files under `.ai/project/`, `.ai/docs/project-requirements.md`,
and related paths. Tracked `.ai/ideas/` overlays product entries; template
`implemented/` wins on rematerialize.

CI runs on **Python 3.11**. Local development needs **Python ≥ 3.11** (3.12+ is
fine). Before `./scripts/validate-ai-workflow.sh` or
`python ci/validate-workflow-contracts.py --mode project`, run
`./scripts/setup-ai-workflow.sh` so materialized `.ai/` path references resolve.

## Full workflow validation (local)

```bash
./scripts/validate-ai-workflow.sh
```

## GitHub Actions

CI reads the private submodule via deploy key secret `SUBMODULE_DEPLOY_KEY`
(read-only key on `ai-project-template`). Repository maintainers configure this
once in diffrat Settings → Secrets and variables → Actions.

## Cursor Automations — Diffrat live loaders (required)

Template production setup
(`.ai-template/.ai/automation/goal-executor-production-setup.md`) assumes
`.ai/automation/goal-executor.md` is committed on the default branch. **Diffrat
does not do that** (D-009): full automation stays private in `.ai-template/` /
materialized `.ai/`.

Public default-branch entrypoints:

| Automation | Load from default branch |
|---|---|
| Goal Executor | [`docs/ai-workflow/goal-executor-live-loader.md`](ai-workflow/goal-executor-live-loader.md) |
| Project Executor | [`docs/ai-workflow/project-executor-live-loader.md`](ai-workflow/project-executor-live-loader.md) |

Canonical full runtimes (after submodule init and/or setup), in order:

1. `.ai/automation/goal-executor.md` / `.ai/automation/project-executor.md`
2. `.ai-template/.ai/automation/goal-executor.md` /
   `.ai-template/.ai/automation/project-executor.md`

If neither path is readable, fail closed (no mutations, no remote writes).

### Goal Executor — live automation prompt

Paste this block into the Cursor **Goal Executor** automation prompt (replace any
template prompt that reads `.ai/automation/goal-executor.md` from the default
branch alone):

```text
You are running the Goal Executor automation for Diffrat.

Before any repository mutation or remote write:
1. Resolve the repository default branch.
2. Read docs/ai-workflow/goal-executor-live-loader.md from that default branch.
3. If the default branch or that loader cannot be resolved and read, fail closed: make no repository change and perform no remote write.
4. Follow that loader to resolve the full Goal Executor runtime from .ai/automation/goal-executor.md (after setup-ai-workflow.sh) or .ai-template/.ai/automation/goal-executor.md (initialized submodule; use SUBMODULE_DEPLOY_KEY / submodule access when required). If neither full runtime is readable, fail closed.
5. Follow the resolved full goal-executor.md as the complete canonical Goal Executor instructions for this run.
6. If this run was triggered by CI or workflow completion on a non-default branch, resolve the open pull request for that head branch, read Closes #<issue>, reverify authorization, and resume that goal only. If resolution fails, no-op.
7. Never treat "draft PR created" as success. If the authorized PR is still draft, finish CI stabilization through ready-for-review (and auto-merge when eligible) in this run, or stop only with an explicit blocker.
```

### Project Executor — live automation prompt

```text
You are running the Project Executor automation for Diffrat.

Before any repository mutation or remote write:
1. Resolve the repository default branch.
2. Read docs/ai-workflow/project-executor-live-loader.md from that default branch.
3. If the default branch or that loader cannot be resolved and read, fail closed: make no repository change and perform no remote write.
4. Follow that loader to resolve full project-executor.md and goal-executor.md from materialized .ai/automation/ (after setup) or .ai-template/.ai/automation/ (initialized submodule). If either full runtime is unreadable, fail closed.
5. Follow project-executor.md for orchestration and goal-executor.md for the delegated goal.
6. If this run was triggered by a merged pull request, resolve the parent Project Execution issue via Closes #<goal> and the project-executor:goal marker before state resolution. If resolution fails, no-op.
7. If this run was triggered by CI or workflow completion on the default branch, resolve the single active authorized Project Execution issue (prefer the project linked from the latest merged delegated goal on that tip). If resolution fails or is ambiguous, no-op.
```

### Required live UI update after merging this loader change

Repository docs alone do not update Cursor Automations. After merge to `main`:

1. Open the live **Goal Executor** (and **Project Executor**, if used) automation
   for `szymoniwacz/diffrat`.
2. Replace the saved prompt with the Diffrat block above.
3. Confirm cloud agents can read the private submodule (same access model as CI
   `SUBMODULE_DEPLOY_KEY` / template clone credentials).
4. Save and run one controlled `/execute-goal` smoke test.

## What stays public in diffrat

- `src/diffrat/`, `tests/`, product `README.md`
- Diffrat product context: `.ai/project/`, `diffrat-cli.md`, product ADR/docs
- Thin adapters: `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`
- Public automation **loaders** under `docs/ai-workflow/` (not the private
  runtime)

## What is private

Everything else under `.ai/` and template-owned paths (`ci/`, `examples/`,
selected `.github/` adapters including issue/PR templates) are symlinked from
`.ai-template/` by the setup script and are not committed to the public
repository.
