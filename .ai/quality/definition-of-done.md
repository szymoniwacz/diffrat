# Definition of Done

## Purpose

A task is **done** when the scoped work is complete, validated, documented, and ready for human review. It is not done when code merely exists.

Independent review when available, otherwise self-review, and the review
handoff are required for all meaningful work. PR creation and diff-risk
assessment apply only when using the GitHub PR workflow. Local or
documentation-only work can reach Done without creating a PR. Agents never
merge PRs.

## Required for completion

### Scoped changes only

Implementation matches the brief, task packet, or plan. No unrelated edits.

### Quality gates considered

Applicable gates from `.ai/quality/quality-gates.md` were evaluated. Skipped gates are documented with reason.

### Documentation updated if needed

When behavior, scope, or decisions changed, relevant `.ai/` or project docs were updated.

### Review completed

Required for all meaningful work. Prefer an independent review agent when
available; otherwise self-review. Apply `.ai/review/ai-review-checklist.md` to
the full diff, with findings recorded in a review packet created from
`.ai/packets/review-packet.template.md`, a drafted PR description, or temporary
review notes.

### Review handoff prepared

Required for all meaningful work. A review packet created from `.ai/packets/review-packet.template.md`, or an equivalent drafted PR description, summarizes changes, validation, risks, and reviewer focus.

### Pull request created (when applicable)

When using the GitHub PR workflow, work is on a branch with a PR to `main`, one logical change per branch. Local or documentation-only work can reach Done without a PR.

### Applicable CI green (when applicable)

When using the GitHub PR workflow, applicable CI checks for the pull request
must pass before the task is Done or review-ready. Pending or failing
applicable CI means the task is not done. Local success on one platform is not
sufficient. Procedure: `.ai/git/branch-and-pr-workflow.md`. Gate checklist:
`.ai/quality/quality-gates.md`.

If CI cannot be inspected, document the limitation and do not claim full
validation or Done for the PR workflow path.

### Diff-risk assessment completed (when applicable)

When using the GitHub PR workflow, the created pull request was assessed before human review using `.ai/review/diff-risk-checklist.md`. The risk level, evidence, and required reviewer focus were recorded in the PR description or a top-level PR comment.

### No merge by agent

Agents never merge pull requests. Human review owns the final merge.

## Done checklist

- [ ] goal from brief, task packet, or plan is met
- [ ] non-goals respected
- [ ] validation plan executed or deviations explained
- [ ] applicable quality gates addressed
- [ ] documentation updated if needed
- [ ] independent review completed when available, otherwise self-review (`.ai/review/ai-review-checklist.md`)
- [ ] review handoff prepared: review packet or drafted PR description
- [ ] branch and PR created (when applicable)
- [ ] applicable CI checks pass after CI stabilization (when using the GitHub PR workflow)
- [ ] diff-risk assessed on the PR before human review, when applicable (`.ai/review/diff-risk-checklist.md`)
- [ ] agent did not merge the PR

## Not done

A task is not done when:

- validation was skipped without explanation,
- applicable CI is pending or failing on the pull request,
- CI could not be inspected but full validation was claimed,
- scope expanded beyond the brief, task packet, or plan without approval,
- docs contradict the implementation,
- the reviewer would need chat history to understand the change.

## Related documents

- `.ai/quality/definition-of-ready.md`
- `.ai/quality/quality-gates.md`
- `.ai/docs/full-workflow.md`
- `.ai/packets/task-packet.template.md`
- `.ai/packets/review-packet.template.md`
- `.ai/review/README.md`
