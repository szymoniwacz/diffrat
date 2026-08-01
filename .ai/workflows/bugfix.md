# Bugfix Workflow

## When to use

A known defect needs correction and the expected behavior is clear.

## Required input

- bug report or reproduction steps with expected behavior
- Agent Goal issue or scoped brief created from the bug report
- link to affected area (file, feature, or idea)
- scope and non-goals

A bug report seeds the scoped input. It does not replace structured goal and
acceptance criteria.

## Steps

1. Read project context (`.ai/project/scope.md`, relevant docs).
2. Confirm the bug and expected behavior. Record assumptions.
3. Create or complete an Agent Goal issue with goal, scope, non-goals, and
   validation.
4. Confirm ready for planning.
5. Plan internally before file changes.
6. Confirm implementation-ready.
7. Implement the fix only within scope. Supporting tests stay part of this workflow.
8. Add or update tests when the project has a test suite.
9. Complete via the canonical lifecycle (`.ai/docs/full-workflow.md`). Prefer
   independent review when available; otherwise self-review with
   `.ai/review/ai-review-checklist.md`. Prepare a review handoff highlighting
   the root cause and fix. Merge rules:
   `.ai/policies/autonomy-and-authorization.md`.

## Validation

- [ ] bug is reproduced or cause is understood
- [ ] scoped input exists (Agent Goal issue or approved brief)
- [ ] internal planning is complete when required
- [ ] ready for planning and implementation-ready are satisfied
- [ ] fix addresses root cause, not only symptoms
- [ ] no unrelated refactors bundled
- [ ] tests added or updated when applicable
- [ ] docs updated if behavior visible to users changed

## What to avoid

- broad cleanup while fixing
- behavior changes beyond the bug scope
- fixing without reproduction or clear expected behavior
- skipping review for "small" security or data-handling bugs
- implementing from a bug report alone without scoped input and planning
