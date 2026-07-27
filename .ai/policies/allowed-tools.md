# Allowed Tools Policy

## Purpose

Define what tools and actions AI agents may use by default in this repository.

## Default posture

- **Read-only by default** — prefer reading context before modifying files.
- **Least privilege** — use the minimum tool access needed for the scoped task.
- **Safe commands** — prefer reversible, well-understood operations.

## Generally allowed

- Reading project files and documentation
- Searching the codebase
- Running project-defined test, lint, and build commands when they exist
- Running existing project-defined migrations locally or in tests when the approved task requires it

## Controlled actions

These actions are not generally allowed without additional controls. Follow the linked canonical policy to determine the required justification, approval, review, or other safeguards:

- Installing or upgrading dependencies — see `.ai/policies/dependency-policy.md`
- Changing authentication, authorization, or security configuration — see `.ai/policies/security-policy.md` and `.ai/policies/dangerous-actions.md`
- Accessing production data or using external services with credentials — see `.ai/policies/security-policy.md`
- Creating or modifying migrations, or applying any migration to a shared, staging, or production environment — see `.ai/policies/dangerous-actions.md`
- Modifying CI/CD permissions or workflows — see `.ai/policies/dangerous-actions.md`
- Deleting files, large-scale renames, mass formatting, or whole-repository rewrites — see `.ai/policies/dangerous-actions.md`
- Force push or published-history rewrite — permanently prohibited for agents;
  see `.ai/git/branch-and-pr-workflow.md`

## Branch, commit, push, and PR creation

Agents may create branches, commits, push the feature branch, or open pull
requests when:

- the user explicitly requested those actions, or
- the authorized outcome is a review-ready pull request.

A request such as "implement this and prepare a PR" authorizes the routine
branch, commit, push, and PR actions needed for that outcome. It does not
authorize merge or other dangerous actions.

Agents must never push directly to `main` and must never merge a pull request.

See `.ai/git/branch-and-pr-workflow.md` and
`.ai/policies/autonomy-and-authorization.md`.

## Related documents

- `.ai/policies/autonomy-and-authorization.md`
- `.ai/policies/dangerous-actions.md`
- `.ai/policies/mcp-policy.md`
- `.ai/policies/no-blind-coding.md`
- `.ai/git/branch-and-pr-workflow.md`
