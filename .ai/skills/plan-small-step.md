# Skill — Plan Small Step

## Command

`/plan-small-step`

## Purpose

Prepare one small implementation step before any code is written.

Use this skill after requirements and scope are clear. It decides whether scoped
input is required, creates or completes it when needed, verifies ready for
planning, prepares internal planning, and then verifies implementation-ready
status.

## Trigger

Run this skill when the user writes:

`/plan-small-step`

Also use it when the user clearly asks to:

- plan the next implementation step
- turn work into a small plan before coding
- prepare constraints and quality gates before coding

## Input

Accept one of:

- an expanded idea file or clear idea reference,
- an Agent Goal issue or other scoped input,
- an optional scratch file from `.ai/packets/` for local drafting,
- an explicit brief when the preparation matrix marks brief as `required` or
  `scope-dependent` and the actual scope allows it.

Optional:

- target milestone
- implementation constraints
- preferred technology choices
- known risks
- files that should or should not change

## Preparation by change type

Use the canonical preparation matrix in
`.ai/quality/definition-of-ready.md`. Allowed values are `required`,
`optional`, `not used`, and `scope-dependent`.

When in doubt, create scoped input (typically an Agent Goal issue).

This skill always prepares internal planning when invoked. That does not mean
every task globally requires a plan outside an explicit `/plan-small-step` call.

## Related files

Read:

- selected idea from `.ai/ideas/expanded/` when provided
- triggering Agent Goal issue, brief, or optional scratch packet file when
  provided
- `.ai/plans/implementation-plan.template.md`
- `.ai/packets/task-packet.template.md`
- `.ai/project/product-context.md`
- `.ai/project/scope.md`
- `.ai/project/decisions.md`
- `.ai/quality/definition-of-ready.md`
- `.ai/quality/quality-gates.md`
- `.ai/conventions/ai-working-mode.md`

Create or update:

- Agent Goal issue or equivalent scoped input when required
- internal plan structure (use `.ai/plans/implementation-plan.template.md` as a
  guide; keep it in working state during the run)
- `.ai/project/decisions.md` only when a meaningful decision is made

Do not commit `.ai/packets/task-*.md` or `.ai/plans/plan-*.md` to the PR
branch. Scratch files, if created, are local preparation aids only.

## Steps

1. Identify the input type: expanded idea, scoped input, scratch packet, or
   explicit brief.
2. Determine whether scoped input is required using the preparation table.
3. Create or complete scoped input when required (typically an Agent Goal
   issue).
4. Verify ready for planning (`.ai/quality/definition-of-ready.md`).
5. Identify the smallest useful implementation step.
6. Prepare one internal plan that matches the scoped input goal and non-goals.
7. Define goal, likely changed files, constraints, non-goals, quality gates,
   risks, and open questions in the plan.
8. Record required human approvals before verifying implementation-ready when
   the preparation matrix requires them.
9. If required human approval is missing after planning is complete, report
   `planned, awaiting human approval`, stop before changing files, and wait for
   explicit human approval. Otherwise verify implementation-ready status.
10. Record a decision only if the plan introduces a meaningful trade-off.
11. Stop before writing code.

## Output

Report exactly one readiness outcome:

- `implementation-ready` — all requirements in
  `.ai/quality/definition-of-ready.md` are satisfied.
- `planned, awaiting human approval` — internal planning is complete but
  required human approval is not yet recorded. Stop before changing files and
  wait for explicit human approval.

Also include when applicable:

- scoped input reference (issue, brief, or requirement)
- internal plan summary (goal, planned files, constraints, non-goals)
- confirmation that ready for planning is satisfied
- clear list of likely changed files
- constraints and non-goals
- quality gates
- risks and open questions
- short summary of the next safe action

## Stop conditions

When required human approval is missing after planning is complete, do not ask
for clarification. Report `planned, awaiting human approval`, stop before
changing files, and wait for explicit human approval.

Stop and ask for clarification only if:

- no valid input can be identified
- required scoped input cannot be drafted without missing scope
- ready for planning cannot be satisfied
- the requested plan is too broad to fit one small step
- required context is missing or unclear
- the plan would violate current scope or accepted decisions

Do not write application code as part of this skill.
