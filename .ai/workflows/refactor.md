# Refactor Workflow

## When to use

Code or docs need structural improvement without intentional behavior change.

## Required input

- Agent Goal issue or scoped brief with explicit refactor goal
- non-goals (what behavior must not change)
- validation plan (how equivalence will be checked)

Follow the canonical preparation matrix in
`.ai/quality/definition-of-ready.md`.

Human approval is **scope-dependent**, not required for every refactor.

Routine behavior-preserving refactors may proceed autonomously when:

- scope is bounded,
- tests or equivalence checks exist,
- no important architecture boundary changes,
- no destructive operation is involved.

Human approval remains required for architecture overhauls, large
cross-boundary restructuring, destructive changes, high-risk changes, and
material decisions not already approved.

## Steps

1. Read context and confirm the refactor is in scope.
2. Create or complete the scoped input (typically an Agent Goal issue).
3. Confirm ready for planning.
4. Plan internally with planned files and rollback notes before file changes.
5. Obtain explicit human approval only when scope-dependent approval resolves to
   required. Record the decision in `.ai/project/decisions.md` or an ADR when
   appropriate.
6. Confirm implementation-ready.
7. Make mechanical changes only; behavior must remain unchanged. Route any intended behavior change to a separate task.
8. Run existing tests or manual checks to confirm behavior is unchanged.
9. Update docs only if structure names or boundaries changed.
10. Complete through the canonical lifecycle in `.ai/docs/full-workflow.md`.
    Merge rules: `.ai/policies/autonomy-and-authorization.md`.

## Validation

- [ ] behavior unchanged
- [ ] scoped input exists and internal planning is complete when required
- [ ] ready for planning and implementation-ready are satisfied
- [ ] human approval recorded before implementation-ready when required by scope
- [ ] diff is reviewable (not a whole-repo rewrite)
- [ ] tests pass or manual equivalence checks documented
- [ ] no new dependencies without justification

## What to avoid

- mixing refactor with feature work in one branch
- renaming or reformatting unrelated files
- large refactors without a plan or stop conditions
- file changes before implementation-ready
- treating every refactor as an architecture overhaul
- "improve everything" prompts
