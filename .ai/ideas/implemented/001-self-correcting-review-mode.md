# Self-correcting review mode

## Status

implemented

## Problem

The default lifecycle always ends at human code review before merge. That is
the right default for most work, but it blocks a future path where the human
authorizes an outcome and expects the agent to substitute a rigorous
review-and-fix loop for human CR — not a weaker handoff.

Today the template already prefers independent review and allows fixing
in-scope findings, but:

- review is still a one-pass (or lightly repeated) gate before human CR,
- “Done” means ready for human review, not self-verified completion,
- agents never merge, and human review remains mandatory in the PR workflow,
- there is no explicit operating mode, exit criteria, or stop rules for a
  closed review→fix→revalidate loop that replaces human CR.

Without a named mode, any attempt at “no human review” would either weaken
quality or silently violate current invariants.

## Goal

Define an explicit, opt-in **self-correcting review mode** for this template
where:

1. the human authorizes the mode (and risk class) up front,
2. the agent implements the scoped goal as usual,
3. an independent review agent is preferred (self-review only as fallback),
4. every actionable in-scope finding is fixed,
5. validation and review are rerun until the exit criteria pass,
6. human code review is not required for that authorized run,
7. material decisions, dangerous actions, and out-of-scope risk still stop for
   a human.

The default autonomous mode (review-ready PR + human CR + human merge) stays
unchanged.

## Why it matters

- Enables higher-autonomy template evolution without replacing the safe
  default.
- Makes “AI reviews and fixes until clean” a controlled policy, not an ad-hoc
  habit.
- Keeps human attention for product/architecture/security decisions instead of
  routine CR when the human explicitly opts out of CR for eligible work.

## Scope

Documentation and workflow design only for the first implementation of this
idea. Include:

- New operating mode next to autonomous / supervised in
  `.ai/policies/autonomy-and-authorization.md` (name TBD; working name:
  **self-correcting review mode**).
- Lifecycle variant in `.ai/docs/full-workflow.md`: after CI stabilization,
  run a closed **review → fix → revalidate → review** loop instead of
  “hand off for human CR”.
- Exit criteria in `.ai/quality/definition-of-done.md` and
  `.ai/review/README.md` for when human CR may be skipped.
- A review-loop procedure (new doc under `.ai/review/` or a section owned by
  review README) covering:
  - prefer independent review agent,
  - apply `.ai/review/ai-review-checklist.md` and
    `.ai/review/diff-risk-checklist.md` each pass,
  - classify findings: fix now / material decision / accepted risk /
    out of scope,
  - max iterations and escalation when the loop does not converge,
  - evidence to record in the PR handoff (passes, findings closed, residual
    risk).
- Authorization rules: exact opt-in trigger; what the mode does and does not
  authorize; interaction with `/execute-goal` and Project Executor.
- Eligibility rules by risk class (at least: security-sensitive and
  high diff-risk remain human-CR-required unless separately decided).
- Thin adapter pointers only if needed (do not duplicate policy in
  `.cursor/`).
- Updates to related summaries: `.ai/conventions/ai-working-mode.md`,
  `.ai/docs/template-flow.md`, `.ai/skills/execute-goal.md`, root README /
  AGENTS only as cross-references.

## Non-goals

- Changing the default mode (human CR before merge remains default).
- Implementing auto-merge, branch-protection bypass, or force push.
- Removing the “agents never merge” rule in the first cut unless a later
  explicit decision authorizes a separate merge policy.
- Weakening `.ai/policies/dangerous-actions.md` or security review-before-merge
  for sensitive changes.
- Replacing the grouped material-decision checkpoint; that stays.
- Building new automation infrastructure beyond documenting how Goal Executor /
  Project Executor would opt into the mode later.
- Application/product code (this repository is the working-system template).

## Proposed design (for planning)

```txt
authorize goal + opt into self-correcting review mode
  -> normal prepare / implement / validate
  -> independent review (preferred) or self-review
  -> fix actionable in-scope findings
  -> rerun affected validation
  -> repeat review until exit criteria pass or escalate
  -> grouped material-decision checkpoint if needed
  -> finalize commits / push / PR / CI green
  -> record self-verified handoff (no human CR required)
  -> stop: human merge still required unless a later decision says otherwise
```

### Exit criteria (draft)

Mode may claim self-verified completion only when all of:

- scoped goal and non-goals respected,
- applicable quality gates addressed,
- applicable CI green (PR workflow),
- latest review pass reports no open actionable findings,
- diff-risk assessed; if high or security-sensitive, escalate to human CR
  unless a stricter authorization explicitly covers that class,
- material questions answered, deferred, or accepted as risk,
- PR handoff states that self-correcting review mode was used, iteration
  count, residual risks, and that human CR was intentionally skipped.

### Stop / escalate conditions (draft)

Stop the loop and require a human when:

- max review iterations reached without a clean pass,
- findings conflict or oscillate,
- a dangerous action or security-sensitive change needs prior approval or
  human CR,
- no safe independent work remains,
- the change is no longer eligible for the mode.

## Risks

- False confidence: a clean AI review pass is not equivalent to human judgment.
- Scope creep inside the fix loop.
- Infinite or oscillating fix loops without a hard iteration cap.
- Accidental use as default, undermining the template’s human-controlled model.
- Ambiguity between “skip human CR” and “auto-merge”.
- Project Executor chaining could multiply unverified merges if merge policy
  is relaxed later without tight eligibility rules.

## Assumptions

- First delivery is policy and docs only; runtime automation follows later.
- Independent review agent remains preferred over same-agent self-review.
- Default repository posture stays human-controlled; this mode is explicit
  opt-in per goal or project authorization.

## Open questions

Resolved 2026-07-31 / 2026-08-01 (see `.ai/project/decisions.md`):

- [x] Mode name: **self-correcting review mode**; triggers documented in autonomy policy
- [x] Human merge still mandatory in v1; auto-merge out of scope
  *(superseded 2026-08-01 by idea 002 — optional
  `self-correcting-review auto-merge` may squash-merge when eligible)*
- [x] v1 eligibility: low + medium; high and security-sensitive require human CR
- [x] Hard max iterations: 3
- [x] Project Executor: `/execute-project self-correcting-review` opts eligible delegated goals into the same mode
- [x] Solo-author: merge of self-verified head records Approve without separate CR

## Possible next step

Answer the open questions (especially merge vs CR-only, and v1 eligibility),
then run `/plan-small-step` or `/execute-goal` to implement the documentation
changes under Scope without altering default behavior.
