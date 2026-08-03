# AI Working Mode

## Purpose

Define how assisted project work should happen in this repository.

## Working principles

- context first
- small steps
- documentation first
- self-review and review handoff for meaningful work
- human review before merge when using the PR workflow, unless self-correcting
  review mode is authorized and eligible
- explicit approval before controlled or structural changes
- no blind generation
- no large hidden rewrites

## Before starting a task

Read:

1. `.ai/project/product-context.md`
2. `.ai/project/scope.md`
3. relevant files in `.ai/conventions/`
4. relevant idea or plan file

## During work

- keep changes small
- explain trade-offs in the relevant document
- do not introduce new structure without updating conventions
- do not assume missing requirements
- follow question timing in `.ai/policies/autonomy-and-authorization.md`;
  defer non-blocking items and ask earlier only for immediate blockers or
  mandatory prior approval

## After work

Check:

- documentation is updated
- decisions are recorded
- scope is still correct
- self-review and review handoff are complete
- human review happens before merge when using the PR workflow, unless
  self-correcting review mode is authorized and eligible
- a session log is created or appended when required by `.ai/observability/session-log-spec.md`
- next step is clear

## Related documents

- `.ai/quality/definition-of-done.md`
- `.ai/review/README.md`
- `.ai/policies/dangerous-actions.md`
