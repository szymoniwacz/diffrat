# Dangerous Actions Policy

## Purpose

Some actions can cause irreversible harm, security exposure, or repository drift. This policy distinguishes two categories so a general rule never conflicts with the detailed sections:

- **Approval before execution** — get explicit human approval before performing the action.
- **Review before merge** — the change may be prepared on a branch, but requires human review before it is merged.

Align material-decision nuance with
`.ai/policies/autonomy-and-authorization.md` and
`.ai/quality/definition-of-ready.md`.

## Requires approval before execution

### Force push or history rewrite

Agents must never force push or rewrite published branch history on any branch.
Published history is append-only after the first push. Human authorization
cannot override this prohibition for agents. Procedure:
`.ai/git/branch-and-pr-workflow.md`.

### Deleting files or large-scale renames

Do not delete files outside the current task scope. Prefer deprecation and follow-up tasks for large removals. See `.ai/policies/repo-drift-policy.md`.

### Creating, modifying, or applying migrations

Creating a non-destructive migration required by an already authorized feature
may be prepared autonomously on a branch.

Explicit approval and an appropriate rollback plan remain required for:

- destructive or irreversible migrations,
- migrations that risk data loss,
- material data-model decisions not already approved,
- applying any migration to shared, staging, or production environments.

Running existing project-defined migrations locally or in tests may be allowed
when required by the authorized task.

### Mass formatting or broad rewrites

Do not reformat entire directories or the whole repository, or perform multi-module
architecture overhauls, renaming sweeps across unrelated modules, or other
high-risk rewrites, unless that is the explicit, approved scoped task. Routine
bounded behavior-preserving refactors do not require this approval class. See
`.ai/policies/repo-drift-policy.md` and `.ai/workflows/refactor.md`.

### Auth and security changes

Changing authentication or authorization model, encryption strategy, secret
access, trust boundaries, privacy posture, or other externally visible
security behaviour requires explicit human approval before
`implementation-ready`.

Implementing an already approved security design may proceed without a new
approval. See `.ai/policies/security-policy.md`.

## Requires human review before merge

### Auth and security changes

Changes to authentication, authorization, encryption, secrets handling, or other
security-sensitive behavior also require human review before merge. See
`.ai/policies/security-policy.md`.

### CI permission changes

Workflow files that broaden tokens, secrets access, or deployment permissions require human review before merge.

## Before proceeding

1. Confirm the action is in the task packet or plan.
2. State the risk in the review handoff or PR description.
3. Get explicit user approval before executing approval-required actions.

## Related documents

- `.ai/policies/allowed-tools.md`
- `.ai/policies/security-policy.md`
- `.ai/policies/autonomy-and-authorization.md`
- `.ai/policies/repo-drift-policy.md`
- `.ai/git/branch-and-pr-workflow.md`
- `.ai/review/diff-risk-checklist.md`
