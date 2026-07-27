# Bootstrap Checklist

Use when creating a new project from this template.

After definition coverage and required human decisions are resolved,
`/execute-goal` may complete the remaining readiness-safe bootstrap work and
prepare the bootstrap PR. Product behaviour remains blocked until project
readiness passes.

See `.ai/policies/autonomy-and-authorization.md`.

## 1. Create repository from template

- [ ] Use GitHub **Use this template** to create the new repo
- [ ] Clone locally and open in your AI coding tool
- [ ] Confirm `.ai/` and the relevant AI tool adapter files are present

## 2. Complete definition coverage

Run exactly one project-definition mode:

- [ ] Run `/project-intake` or `/define-project`
- [ ] Update `.ai/project/vision.md`
- [ ] Update `.ai/project/product-context.md`
- [ ] Update `.ai/project/scope.md` with in-scope and out-of-scope items
- [ ] Update `.ai/project/roadmap.md` and `.ai/project/glossary.md` as needed
- [ ] Create or update `.ai/docs/project-requirements.md`
- [ ] Fill every decision area in the project decision status table
- [ ] Record assumptions separately from confirmed requirements
- [ ] Confirm no decision area is silently omitted

Definition coverage is complete when every contract area has an explicit
status and required metadata. See
`.ai/contracts/project-definition-contract.md`.

Resolve material product and architecture decisions here.

## 3. Customize the template for the product

Follow `.ai/onboarding/template-customization-guide.md`.

- [ ] Replace root `README.md` with product-facing content
- [ ] Update `AGENTS.md` so it describes the actual repository role
- [ ] Update tool adapters only as needed to point at this project's `.ai/`
- [ ] Select an active stack profile or mark stack guidance `not-applicable`
- [ ] Create packaging-only scaffold when needed by the selected stack
- [ ] Record real setup, run, test, lint, typecheck, and build commands
- [ ] Confirm license, ownership, and copyright for the new project
- [ ] Decide CI, branch rules, and required approvals
- [ ] Change workflow contract validation in
  `.github/workflows/validate-workflow-contracts.yml` from:

  ```bash
  python ci/validate-workflow-contracts.py --mode template
  ```

  to:

  ```bash
  python ci/validate-workflow-contracts.py --mode project
  ```

- [ ] Remove or replace all `REPLACE DURING BOOTSTRAP` markers
- [ ] Validate, review according to `.ai/docs/full-workflow.md`, commit, push,
  open the bootstrap PR, and complete CI stabilization before review-ready
  (`.ai/git/branch-and-pr-workflow.md`)

## 4. Pass the project readiness gate

Record the result in `.ai/docs/project-requirements.md` under **Project
readiness**.

- [ ] No `blocking-question` remains in the decision-status table
- [ ] Every `deferred` item has a reason and return trigger or owner
- [ ] Every `default-accepted` item records the default and human confirmation
- [ ] Goal, user, core workflow, first useful version, scope, and non-goals are
  concrete
- [ ] Stack and real project commands are recorded
- [ ] Data, security, deployment, CI, rollback, and license decisions are
  decided or marked `not-applicable`
- [ ] Root README describes the product, not the template
- [ ] `AGENTS.md` no longer describes the repo as template-only
- [ ] Bootstrap markers are removed
- [ ] Project ready for first product task is confirmed
- [ ] Bootstrap pull request is review-ready when using GitHub (applicable CI
  green)

Product implementation may start only after this gate passes.

Bootstrap ends here.

## First product task

Prefer `/execute-goal` for the first product outcome. Full lifecycle order:
`.ai/docs/full-workflow.md`. Preparation rules:
`.ai/quality/definition-of-ready.md`.

## Done when

Two separate outcomes are complete:

### Definition coverage complete

- [ ] Project context exists in files, not only in chat
- [ ] Every contract decision area has an explicit status and required metadata

### Bootstrap complete

- [ ] Project readiness gate passed and recorded
- [ ] Root `README.md` describes the actual project (see
  `.ai/contracts/readme-contract.md`)
- [ ] Readiness-safe bootstrap work has been reviewed by a human when using the
  GitHub PR workflow

The first implemented product task is optional during bootstrap. Track it with
`/execute-goal` when ready.

## References

- `.ai/docs/template-flow.md`
- `.ai/docs/full-workflow.md`
- `.ai/policies/autonomy-and-authorization.md`
- `.ai/skills/execute-goal.md`
- `.ai/contracts/project-definition-contract.md`
- `.ai/onboarding/template-customization-guide.md`
