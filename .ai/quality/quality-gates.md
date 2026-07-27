# Quality Gates

## Purpose

Quality gates define what must be checked before AI-assisted work is considered complete.

Gates apply based on the type of change. Not every gate applies to every task. Skipped gates must be documented with reason.

## Universal gates

Apply to all meaningful work:

- [ ] change aligns with project scope (`.ai/project/scope.md`)
- [ ] change matches brief, task packet, or plan scope
- [ ] non-goals were not violated
- [ ] review surface is small enough for a human to understand
- [ ] context is preserved in files, not only in chat

## Documentation gates

Apply when docs, `.ai/` files, or project context change:

- [ ] relevant files were updated
- [ ] wording is clear and concise
- [ ] no duplicate source of truth introduced
- [ ] cross-references remain valid
- [ ] decisions recorded when trade-offs were made

## Code gates

Apply when application or script code changes:

- [ ] implementation follows existing structure and conventions
- [ ] no unrelated refactors or cleanup bundled in
- [ ] error handling is appropriate for the change scope
- [ ] no secrets, credentials, or production data introduced

Run project-specific commands when they exist (tests, lint, typecheck). Do not invent stack-specific commands that are not already defined in the project.

## Test gates

Apply when code behavior changes or bugs are fixed:

- [ ] tests added or updated when the project has a test suite
- [ ] existing tests pass
- [ ] test changes relate to the scoped behavior change

If the project has no test suite yet, note that in the review handoff and describe manual validation instead.

## Security gates

Apply when auth, permissions, data handling, or external integrations are touched:

- [ ] secrets are not committed or logged
- [ ] input validation considered for new surfaces
- [ ] least privilege respected for permissions
- [ ] security-sensitive changes called out for human review

## PR gates

Apply when submitting a pull request:

- [ ] one logical change per branch
- [ ] commit messages are clear; attribution follows **Attribution by surface**
  in `.ai/git/branch-and-pr-workflow.md`
- [ ] PR description explains what, why, validation, and dependencies
- [ ] every commit in the PR range was inspected for attribution and signature
  rules in `.ai/git/branch-and-pr-workflow.md`, not only the tip
- [ ] pre-push metadata gate passed before every push
- [ ] applicable CI checks pass after CI stabilization; pending or failing
  applicable CI means the PR is not review-ready
- [ ] if CI cannot be inspected, the limitation is reported and full validation
  is not claimed
- [ ] agent did not merge the PR
- [ ] agent did not force push or rewrite published branch history after the
  first push (append-only rule; no exceptions)

Attribution, remote PR metadata verification, append-only published history,
and CI stabilization procedure: `.ai/git/branch-and-pr-workflow.md`.

## Compatibility gates

Apply when the change touches CI matrices, runtimes, dependency manifests,
lockfiles, or package-manager configuration:

- [ ] configured CI environments were considered, not only the local platform
- [ ] local success on one platform is not treated as proof that all configured
  CI environments will pass
- [ ] lockfiles, manifests, and package-manager settings remain compatible with
  the CI matrix and runtimes declared for the project
- [ ] clear in-scope CI failures caused by this branch were fixed before
  handoff

Keep this gate stack-neutral. Do not invent language-specific rules here.

## Skipped gate rules

A gate may be skipped only when:

- it does not apply to this change type (document why),
- the project lacks the tooling (document manual alternative),
- an explicit human decision accepts the risk.

Record skipped gates in the review packet or PR description.

Pending or failing applicable CI is not a skippable gate for review-ready
handoff when using the GitHub PR workflow. See
`.ai/git/branch-and-pr-workflow.md`.

## Relationship to other documents

| Document | Role |
|---|---|
| `.ai/docs/quality-model.md` | Quality dimensions for the project |
| `.ai/quality/definition-of-done.md` | When work is complete |
| `.ai/git/branch-and-pr-workflow.md` | Remote verification and CI stabilization procedure |

This file is the canonical gate checklist for the AI workflow. Do not duplicate full gate lists in tool adapters.

## Rule

A task can be small. A task cannot skip accountability for applicable gates without explanation.
