# Test Writing Workflow

## When to use

Adding or updating tests for existing or new behavior.

## Required input

Follow the canonical preparation matrix in
`.ai/quality/definition-of-ready.md`.

At minimum provide:

- expected behavior to assert
- scope (which cases are in and out)
- a brief, task packet, or existing packet depending on scope

Small single-file test additions may use an explicit brief. Multi-file or
high-risk test work requires a task packet and plan.

## Steps

1. Read the behavior being tested (code, docs, or task packet).
2. Confirm required preparation for the test-only change type.
3. Create or complete a task packet when scope-dependent preparation requires it.
4. Confirm ready for planning when a packet or brief exists.
5. Create an implementation plan in `.ai/plans/` when required.
6. Confirm implementation-ready before changing files.
7. Identify test type: unit, integration, or documentation check as appropriate.
8. Plan test files and cases. Prefer focused examples over exhaustive lists.
9. Write tests that fail before the fix or feature when applicable.
10. Implement or verify production code only if in scope.
11. Complete via the canonical lifecycle (`.ai/docs/full-workflow.md`). Prefer
    independent review when available; otherwise self-review with
    `.ai/review/ai-review-checklist.md`. Prepare a review handoff noting
    coverage gaps intentionally left open. Agents never merge.

## Validation

- [ ] required preparation exists for the scope
- [ ] ready for planning and implementation-ready satisfied when required
- [ ] tests assert meaningful behavior, not implementation details only
- [ ] tests pass locally or CI status is documented
- [ ] no flaky or environment-dependent tests without note
- [ ] test changes match task scope
- [ ] unrelated production code not changed

## What to avoid

- snapshotting entire outputs without understanding failures
- deleting tests to make CI green
- testing unrelated modules in the same branch
- inventing test commands not defined in the project
- requiring a task packet for every trivial single-test edit when a brief suffices
