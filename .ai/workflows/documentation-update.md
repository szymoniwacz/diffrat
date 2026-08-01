# Documentation Update Workflow

## When to use

Updating project context, design docs, `.ai/` materials, or user-facing documentation.

## Required input

Follow the canonical preparation matrix in
`.ai/quality/definition-of-ready.md`.

Provide at minimum:

- a brief, task packet, or explicit doc change request depending on scope
- list of files that must stay consistent
- reason the doc change is needed

## Steps

1. Confirm required preparation for the documentation change type.
2. Read existing docs to avoid duplicating content elsewhere.
3. Confirm ready for planning when a packet or brief exists.
4. Create an implementation plan in `.ai/plans/` when required.
5. Confirm implementation-ready before changing files.
6. Identify the single source of truth for each concept being updated.
7. Update primary doc first; fix cross-references second.
8. Keep changes scoped to the stated doc set.
9. Check for documentation drift against implementation when code exists.
10. Complete via the canonical lifecycle (`.ai/docs/full-workflow.md`). Prefer
    independent review when available; otherwise self-review with
    `.ai/review/ai-review-checklist.md`. Prepare a review handoff listing what
    readers should re-check. Merge rules:
    `.ai/policies/autonomy-and-authorization.md`.

## Validation

- [ ] required preparation exists for the scope
- [ ] ready for planning and implementation-ready satisfied when required
- [ ] one clear source of truth per concept
- [ ] cross-references still valid
- [ ] no duplicate rules added to tool adapters
- [ ] wording is concise and actionable
- [ ] decisions recorded when trade-offs were made

## What to avoid

- copying full workflow into README or tool adapter files
- updating docs without stating why
- broad rewrites without a scoped task
- contradicting `.ai/project/scope.md` or requirements docs
