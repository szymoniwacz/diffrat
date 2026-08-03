# Human Review Checklist

For a human independently reviewing an existing pull request. The review packet is supporting input; the reviewer must read the actual PR diff, and the review packet is not a substitute for it.

Validation gates (scope, documentation, test, security, PR) are canonical in
`.ai/quality/quality-gates.md`. Do not repeat them here. This checklist covers
the human's distinct job: verify independently rather than trust the summary.

## Independent diff verification

- [ ] the diff was read directly, not only the summary or review packet
- [ ] the actual changes match what the PR description or review packet claims
- [ ] the initial diff-risk assessment was independently verified against the actual PR diff

## Approved scope verification

The PR description and review packet can repeat the same incorrect assumptions. Verify against the source, not against another summary.

- [ ] the triggering issue, explicit brief, or accepted requirement was read directly
- [ ] the actual diff was compared against the approved goal from that source, not the PR's description of it
- [ ] the actual diff was compared against the approved scope from that source, not the PR's description of it
- [ ] non-goals were respected; any violation is flagged
- [ ] changes present in the diff but not justified by the issue, brief, or PR description are identified
- [ ] discrepancies between the approved scope, PR description or review packet, and actual diff are challenged, not assumed consistent

## Claims verification

- [ ] stated goal is genuinely achieved by the code, not just described
- [ ] validation evidence was spot-checked, not accepted at face value

## Architecture impact

- [ ] change fits project direction (`.ai/project/`, `.ai/docs/`)
- [ ] structural or boundary changes have a decision record
- [ ] no undocumented shift in how components fit together

## Maintainability

- [ ] a future reader can follow the change without this context
- [ ] complexity is justified by the problem, not incidental

## Hidden coupling

- [ ] no implicit dependency introduced between unrelated modules
- [ ] shared state, ordering, or timing assumptions are safe

## Edge cases

- [ ] boundary, empty, and error conditions are handled or explicitly out of scope
- [ ] failure modes were considered, not only the happy path

## Validation credibility

- [ ] the described validation is plausible for this change
- [ ] gaps between claimed and actual validation are challenged

## Decision

Conclude the review with exactly one:

- **Approve** — the change may proceed to manual human merge.
- **Request changes** — leave the pull request open and record actionable findings.
- **Reject** — record the reason; a human closes the pull request without merging.

`APPROVE` allows only a later manual human merge. It does not authorize an agent
to merge.

## Where to record the decision

| Situation | Where to record the decision |
|---|---|
| Reviewer is not the PR author and GitHub permits the selected review state | GitHub PR review |
| Reviewer is the PR author and the decision is Approve | Manual human merge of the reviewed remote head. No separate `Human review: APPROVE` comment is required. |
| Reviewer is the PR author, or native review state is unavailable, and the decision is Request changes or Reject | Top-level PR comment |

For a top-level comment recording Request changes or Reject, require:

```text
Human review: REQUEST CHANGES | REJECT
Reviewed commit: <full PR head SHA>
Findings: <actionable findings or rejection reason>
```

A solo PR author's Approve decision is recorded by the human merge itself after
independent review of the current remote head. Merge rules:
`.ai/policies/autonomy-and-authorization.md`.

Immediately before merge, the human must read the current remote pull request
head SHA and confirm it is the revision they reviewed. Any later commit
invalidates the prior review and requires reviewing the new head.

For Request changes, Reject, or a non-author Approve recorded in a GitHub PR
review, the recorded head SHA must match the reviewed revision. A missing
decision, missing reviewed SHA where required, or SHA mismatch blocks merge.

Do not edit an old comment to make a prior decision appear current. After a new
commit, record a new Request changes or Reject decision tied to the new head,
or review the new head again before merge.

Do not record results in the repository review packet, the PR description, or
generic review notes. Do not record results by editing this or any other
canonical checklist file.
