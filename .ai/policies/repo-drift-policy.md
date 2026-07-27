# Repository Drift Policy

## Purpose

Protect the repository from AI-generated drift: unrelated changes, scope creep, and gradual loss of structure.

## Rules

### Unrelated changes

Do not include fixes, refactors, formatting, or renames outside the current task scope. Record them as follow-up tasks instead.

### Cross-layer risk

Changes that span multiple layers (application, configuration, CI, documentation) require explicit justification in the task packet or plan. Reviewers should use `.ai/review/diff-risk-checklist.md`.

### Structure preservation

`.ai/docs/template-flow.md` owns the current complete folder map, including
`.ai/instructions/`, `.github/`, `examples/`, and adapter directories;
`.ai/conventions/repository-structure.md` provides placement rules. Do not
introduce new top-level folders or move concepts without updating the applicable
folder map or placement rules and recording a decision when significant.

### Documentation drift

When documented behavior, structure, commands, configuration, or decisions change, update the documentation that describes them; when docs change, verify implementation still matches. Do not require documentation updates for internals that are not documented, and do not maintain parallel rules in tool adapters.

### Idea and scope alignment

Check `.ai/project/scope.md` before expanding work. Scope expansion requires human approval.

## Enforcement

Canonical workflow instructions (`.ai/instructions/workflow.md`) reference this policy. Tool adapters must not duplicate it. This file owns drift-specific rules.

## Related documents

- `.ai/review/diff-risk-checklist.md`
- `.ai/conventions/repository-structure.md`
- `.ai/conventions/ai-working-mode.md`
