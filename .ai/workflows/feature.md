# Feature Workflow

## When to use

Adding or extending product capability when requirements and scope are known
or can be confirmed before implementation.

Use this workflow for normal feature development. For defects, refactors,
tests-only work, or documentation-only updates, use the matching workflow in
`.ai/workflows/` instead.

## Required input

One of:

- expanded idea linked to accepted requirements,
- Agent Goal issue derived from accepted requirements,
- accepted requirement or direct scoped request recorded in an issue or brief.

Also read:

- `.ai/project/scope.md`
- `.ai/docs/project-requirements.md`
- relevant decisions in `.ai/project/decisions.md`

Follow the canonical preparation matrix in
`.ai/quality/definition-of-ready.md`. Feature work requires scoped input
(typically an Agent Goal issue) and internal planning. An idea file is optional
when the work already comes from accepted requirements.

## Requirement and scope check

Before planning:

1. Confirm the feature aligns with current scope and requirements.
2. Identify affected interfaces, data, and integrations.
3. Record non-goals so implementation does not expand silently.
4. Resolve or defer open questions that would change the design.

## Scoped input

Create an **Agent Goal** issue for every feature task. Use the issue template
fields for goal, acceptance criteria, constraints, and out of scope.

`.ai/packets/task-packet.template.md` is an optional drafting aid only. Do not
commit `task-*.md` files to the PR branch.

Do not substitute a brief-only route for feature work.

## Ready for planning

Confirm ready for planning using `.ai/quality/definition-of-ready.md`:

- goal is clear,
- scope and non-goals are bounded,
- validation plan exists,
- risks and open questions are recorded or accepted.

## Implementation plan

Plan internally before coding. You may use `/plan-small-step` or
`.ai/plans/implementation-plan.template.md` as structure, but do not commit
`plan-*.md` files to the PR branch.

The plan must match the issue goal and non-goals.

## Implementation-ready

Confirm implementation-ready before changing files. Obtain human approval first
when the change is high-risk per the preparation matrix.

## Implementation discipline

- Read relevant project context and the plan before changing files.
- Change only what the plan covers.
- Do not bundle unrelated cleanup or refactors.
- Record meaningful trade-offs in `.ai/project/decisions.md` or an ADR when
  needed.

## Tests and docs

- Add or update tests when the project has a test suite and behavior changed.
- Update user-facing or operator-facing docs when behavior or setup changed.
- Update `.ai/` context when project facts changed.

## Quality gates

Complete applicable items from `.ai/quality/quality-gates.md` before review.

## Review

Prefer independent review when available; otherwise self-review with
`.ai/review/ai-review-checklist.md`. Feed unresolved material questions into the
Decision queue.

Complete the remaining stages in canonical order via
`.ai/docs/full-workflow.md`: grouped decision checkpoint when needed, apply
answers and rerun affected validation and review, prepare the review handoff,
then commit, push, and create or update the pull request.

Agents never merge.

## Idea lifecycle update

After merge or completion:

- move related idea files to `.ai/ideas/implemented/` or
  `.ai/ideas/archived/` when an idea drove the work,
- update `.ai/ideas/README.md`,
- update project docs if capabilities or scope changed.

Loose backlog ideas use the idea lifecycle. Work from accepted requirements may
start at the task-packet stage without a new idea file.

## Validation

- [ ] requirements and scope confirmed before planning
- [ ] scoped input exists (Agent Goal issue or approved brief)
- [ ] ready for planning satisfied
- [ ] internal planning is complete when required
- [ ] implementation-ready satisfied before file changes
- [ ] changes stay within scope
- [ ] tests and docs updated when applicable
- [ ] quality gates addressed
- [ ] independent review completed when available, otherwise self-review
- [ ] review handoff prepared
- [ ] idea status updated when an idea drove the work

## What to avoid

- starting from a vague prompt without scope boundaries
- skipping task packets for feature work
- combining unrelated features in one branch
- architecture changes without an explicit decision
- treating backlog ideas as approved requirements without scope check
