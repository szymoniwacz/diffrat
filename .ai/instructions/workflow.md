# Workflow Instructions

Canonical workflow instructions for AI-assisted work in this repository.

## Default operating model

Work is **goal-oriented**. Prefer `/execute-goal`. Autonomous mode is the
default; supervised mode is an explicit override. Agents never merge except
under authorized eligible `self-correcting-review auto-merge`
(`.ai/policies/autonomy-and-authorization.md`).

Canonical rules:

- `.ai/policies/autonomy-and-authorization.md`
- `.ai/policies/multi-agent-orchestration.md` when parallel work may help
- Full lifecycle order: `.ai/docs/full-workflow.md`

## Loading context

For `/execute-goal`, follow the skill's conditional loading rules.
Otherwise read only the context, policy, workflow, and quality files relevant
to the current task.

Confirm required preparation for the change type per
`.ai/quality/definition-of-ready.md`, including ready for planning and
implementation-ready when applicable. Follow the matching workflow in
`.ai/workflows/` for the change type.

## Working rules

- Start with context, not implementation.
- Collect non-blocking questions and improvement suggestions while working.
  Ask them as one grouped batch after independent work and review are complete.
  Ask earlier only when no safe work can continue or prior approval is
  mandatory. See `.ai/policies/autonomy-and-authorization.md`.
- Make one logical, scoped change at a time.
- Do not add unrelated features, refactors, or cleanup.
- Update documentation when behavior, scope, or decisions change.
- After changes, verify scope, docs, and quality gates before starting the next task.
- Prepare changes that a human can review without chat history.
- Under `/execute-goal`, continue through commit, push, PR, and CI
  stabilization without extra confirmation. Merge only when
  `self-correcting-review auto-merge` is authorized and eligible; otherwise do
  not merge.
- Put workstream execution state in the agent's internal plan during the run.
  Do not commit `.ai/plans/plan-*.md` or `.ai/packets/task-*.md` to the PR
  branch.

## Quality

Follow `.ai/quality/quality-gates.md` for applicable quality gates.

Follow `.ai/conventions/ai-working-mode.md` for AI working mode conventions.

Follow applicable policies in `.ai/policies/`.

## Session logs

Session logs are a supplemental artifact, not a default requirement for every
task. Create or append one only when required by
`.ai/observability/session-log-spec.md`. The triggering issue or brief, pull
request description, and canonical project documentation remain the primary
durable record.

## Review

Follow the canonical review stages in `.ai/docs/full-workflow.md`.

When using the GitHub branch and pull request workflow, follow
`.ai/git/branch-and-pr-workflow.md`.
