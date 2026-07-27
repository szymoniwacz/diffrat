# Scope

## Purpose

Define what is currently allowed and what is intentionally deferred.

This file protects the project from uncontrolled expansion.

## In scope now

> REPLACE DURING BOOTSTRAP: list what this project is currently allowed to work on.

- [in-scope area]
- [in-scope area]

## Out of scope by default

- work that does not satisfy the required preparation for its change type
- large rewrites without explicit approval
- new frameworks without a decision record
- hidden architecture changes
- undocumented generated files

Required preparation by change type lives in
`.ai/quality/definition-of-ready.md` and `.ai/policies/no-blind-coding.md`.

## Scope levels

| Level | Meaning |
|---|---|
| Idea | rough concept only |
| Expanded idea | clear problem, goal, scope, risks |
| Ready for planning | packet or brief complete enough to plan |
| Planned | implementation plan exists in `.ai/plans/` |
| Implementation-ready | full gate passed; work may change files |
| Implemented | code exists and docs were updated |
| Archived | intentionally rejected or deferred |

## Rule

If a task changes scope, update this file or add a decision record before continuing.
