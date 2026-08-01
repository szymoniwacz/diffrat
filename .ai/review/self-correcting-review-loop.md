# Self-Correcting Review Loop

Closed **review → fix → revalidate → review** loop for **self-correcting review
mode**. Mode and eligibility: `.ai/policies/autonomy-and-authorization.md`.
Done boundary: `.ai/quality/definition-of-done.md`.

Use only when that mode is authorized and the change stays eligible. Otherwise
use the default path: handoff → human CR → human merge.

## Loop

Prefer an independent review agent; self-review is the fallback.

```txt
pass = 1
while pass <= 3:
  review with ai-review-checklist
  assess diff-risk (PR workflow)
  classify findings (fix now / material / accepted risk / out of scope)
  if no open actionable findings and still eligible: exit clean
  if ineligible: escalate to human CR
  apply fix-now findings only; rerun affected validation
  pass += 1
if still dirty after pass 3: escalate to human CR
```

Hard max: **3** passes. Do not expand scope or weaken validators.

## Escalate when

- max passes reached, findings oscillate, or no safe work remains
- diff-risk is **high**, or the change is security-sensitive /
  review-before-merge under dangerous-actions or security policy
- a dangerous action needs prior approval

Escalated work requires human CR. Do not agent-merge.

## Handoff

PR description or review packet must state: mode used, pass count, finding
summary, diff-risk/eligibility, residual risks, and whether human CR was
skipped or escalated.

## Authorized squash merge

Only when `self-correcting-review auto-merge` was authorized. After a clean
eligible exit, applicable CI green, and all merge preconditions in
`.ai/policies/autonomy-and-authorization.md`, Goal Executor performs the
authorized squash merge and verification in
`.ai/git/branch-and-pr-workflow.md`. Do not enable GitHub auto-merge queue.
If merge fails (permissions, branch protection, verification), stop with an
explicit blocker and do not claim Done via merge.

Without `auto-merge`, stop after the self-verified handoff; a human merges.
