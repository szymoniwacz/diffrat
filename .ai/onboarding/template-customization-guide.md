# Template Customization Guide

What to customize when creating a project from this template—and what to leave alone.

Template customization is part of project readiness, not an optional extra.
Complete it after definition coverage and before the first product task.

## Customize for your product

### Root `README.md`

Replace template description with your project: purpose, status, setup, run,
tests, configuration, limitations, and license.

See `.ai/contracts/readme-contract.md`.

### `AGENTS.md`

Update the repository role so it describes your product repository after
bootstrap. It must not keep the template-only statement that the repo is not
an application.

### `.ai/project/`

Fill with your product identity: vision, scope, roadmap, decisions, glossary.

Remove or replace all `REPLACE DURING BOOTSTRAP` markers in:

- `.ai/project/product-context.md`
- `.ai/project/scope.md`
- `.ai/project/roadmap.md`

### `.ai/docs/`

Add project-specific design docs: requirements, architecture direction, quality
model.

Fill the decision-status table, assumptions, and project readiness sections in
`.ai/docs/project-requirements.md`.

### `.ai/ideas/`

Use for your backlog. Remove or replace template placeholder content.

### Prompts and skills

Adjust examples in `.ai/prompts/` to match your domain. Extend `.ai/skills/`
when you have repeatable procedures.

### Stack profile

Select one or more active profiles from `.ai/stack-profiles/` and record the
selection in `.ai/docs/project-requirements.md`. Mark stack guidance
`not-applicable` when no profile applies.

Unselected profiles remain reusable examples; do not delete them
automatically.

Record real project commands in the selected profile or project README.

### License and ownership

Confirm license, copyright, and ownership for the new project. Do not keep
template maintainer defaults unless they are intentionally reused.

### CI, branch rules, and approvals

Record the project's CI, branch, release, rollback, and approval expectations
in requirements or project docs.

After bootstrap, change contract validation in
`.github/workflows/validate-workflow-contracts.yml` from:

```bash
python ci/validate-workflow-contracts.py --mode template
```

to:

```bash
python ci/validate-workflow-contracts.py --mode project
```

The template repository keeps `--mode template` until a project is created.

### Conventions

Update `.ai/conventions/` when your project has rules beyond the template defaults.

## Customize lightly

### `.cursor/rules/`

Keep as thin adapters. Add only Cursor-specific behavior; point to `.ai/` for workflow rules.

### Other tool adapters

Update `CLAUDE.md` or `.github/copilot-instructions.md` only to point at your project's `.ai/` layout.

## Do not customize (keep template workflow intact)

- The principle: **template defines the working system; project defines the product**
- Do not copy full workflow into root README or tool adapters
- Do not delete `.ai/` folder structure without replacing its responsibilities
- Do not merge unrelated workflow rules into application code
- Do not remove quality, review, or policy docs without an explicit decision

## What not to do on day one

- Implement features before definition coverage and project readiness pass
- Rewrite the entire `.ai/` tree to match another repo
- Duplicate workflow docs in multiple places
- Let AI merge PRs or push directly to `main`

## First-week goal

A new teammate—or a new AI session—should understand the project from files in `.ai/project/` and `.ai/docs/` without reading old chat logs.

## References

- `.ai/contracts/project-definition-contract.md`
- `.ai/onboarding/bootstrap-checklist.md`
- `.ai/docs/template-flow.md`
