# AI Project Template

A documentation-first GitHub template for building software with explicit
context, scoped changes, and human-controlled review.

Use this repository as a starting point, then replace template content with
your product documentation during bootstrap.

## Start here

Read [`.ai/docs/template-flow.md`](.ai/docs/template-flow.md) for the full
working guide and [canonical folder map](.ai/docs/template-flow.md#complete-folder-map).

## Who this is for

- developers starting a new product with assisted implementation
- teams that want project context, scope, and review rules in files instead of chat
- repositories that use AGENTS, Claude Code, Copilot, or Cursor adapters

## Core principle

```txt
Template defines the working system.
Project defines the product.
```

## Default operating model

Prefer `/execute-goal` for one meaningful outcome. Agents never merge.

Canonical rules:

- [`.ai/policies/autonomy-and-authorization.md`](.ai/policies/autonomy-and-authorization.md)
- Full lifecycle: [`.ai/docs/full-workflow.md`](.ai/docs/full-workflow.md)

## Define the project

Choose exactly one mode:

| Mode | Use when |
|---|---|
| `/project-intake` | You want guided questions in short rounds |
| `/define-project` | You already have a rough description to organize |

Both modes produce the same project context, requirements, and decision-status
table. See [`.ai/contracts/project-definition-contract.md`](.ai/contracts/project-definition-contract.md).

## Bootstrap flow

```txt
create repo
  -> choose intake mode
  -> complete definition coverage
  -> customize template for the product
  -> pass project readiness gate
  -> start first product task
```

Project readiness means no blockers remain, stack and real commands are
recorded, bootstrap markers are removed, and repository identity describes the
product. See [`.ai/onboarding/bootstrap-checklist.md`](.ai/onboarding/bootstrap-checklist.md).

## Feature and task flow

Prefer `/execute-goal` for one scoped outcome. Full lifecycle order:
[`.ai/docs/full-workflow.md`](.ai/docs/full-workflow.md). Autonomy and question
timing: [`.ai/policies/autonomy-and-authorization.md`](.ai/policies/autonomy-and-authorization.md).

Independent review is preferred; self-review is the fallback. Agents never merge.

## Task routes

| Task type | Primary workflow | Required preparation |
|---|---|---|
| Feature | [`.ai/workflows/feature.md`](.ai/workflows/feature.md) | Task packet and plan |
| Bugfix | [`.ai/workflows/bugfix.md`](.ai/workflows/bugfix.md) | Task packet and plan |
| Refactor | [`.ai/workflows/refactor.md`](.ai/workflows/refactor.md) | Task packet and plan; approval when high-risk or architectural |
| Tests | [`.ai/workflows/test-writing.md`](.ai/workflows/test-writing.md) | Brief or packet; plan when required |
| Documentation | [`.ai/workflows/documentation-update.md`](.ai/workflows/documentation-update.md) | Brief or packet; plan when required |

Preparation rules: [`.ai/quality/definition-of-ready.md`](.ai/quality/definition-of-ready.md)

## Supported adapters

| Adapter | Location |
|---|---|
| Root agents | [`AGENTS.md`](AGENTS.md) |
| Claude Code | [`CLAUDE.md`](CLAUDE.md) |
| GitHub Copilot | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Cursor | [`.cursor/rules/`](.cursor/rules/) |

Canonical workflow lives in [`.ai/`](.ai/). Adapters stay thin.

## Review and control boundaries

- meaningful work gets self-review and a review handoff
- human review is required before merge when using the GitHub PR workflow
- controlled or high-risk actions require explicit human approval first
- agents create branches and PRs; humans merge manually

## After bootstrap

Replace this README with product-facing documentation. Use
[`.ai/templates/project-readme.md`](.ai/templates/project-readme.md) as the
starting point for setup, run, tests, configuration, limitations, and license.

## Where details live

| Topic | Document |
|---|---|
| AI working system and canonical AI entrypoint | [`.ai/README.md`](.ai/README.md) |
| Goal Executor production setup | [`.ai/automation/goal-executor-production-setup.md`](.ai/automation/goal-executor-production-setup.md) |
| Bootstrap checklist | [`.ai/onboarding/bootstrap-checklist.md`](.ai/onboarding/bootstrap-checklist.md) |
| Root README contract | [`.ai/contracts/readme-contract.md`](.ai/contracts/readme-contract.md) |

## License

See [`LICENSE`](LICENSE). Confirm license and ownership for your project during
bootstrap.
