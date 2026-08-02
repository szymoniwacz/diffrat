# Goal Executor — Cursor Automation Instructions

Cursor Automation loads this file from the repository default branch through the
live loader defined in `.ai/automation/goal-executor-production-setup.md`.

Manual `/execute-goal` usage outside Cursor Automation reads this file directly
from the working tree and is unaffected by the live loader.

## Trigger

Run in any of these cases:

1. an authorized repository owner comments exactly `/execute-goal`,
   `/execute-goal self-correcting-review`, or
   `/execute-goal self-correcting-review auto-merge` on an ordinary GitHub
   issue in this repository;
2. Project Executor invokes one delegated Agent Goal under an active,
   in-scope `/execute-project`, `/execute-project self-correcting-review`, or
   `/execute-project self-correcting-review auto-merge` authorization;
3. applicable CI or workflow completion on a **non-default** branch that is the
   head of an open pull request whose body contains exact `Closes #<issue>` for
   an Agent Goal that this automation may continue (standalone prior
   `/execute-goal…` authorization still valid, or delegated Project Executor
   goal with trusted marker and valid parent authorization).

For case 2, require the exact project marker and reverify the parent issue and
authorization before every write. When the parent authorization is
`/execute-project self-correcting-review` or
`/execute-project self-correcting-review auto-merge`, treat the delegated run as
self-correcting review mode (same as the matching `/execute-goal` form). When
the parent form includes `auto-merge`, inherit authorized squash merge as well.

For case 3, resolve the pull request from the CI head branch or SHA, read
`Closes #<issue>`, reverify authorization, then continue from **CI
stabilization and review-ready handoff** (or authorized merge) for that issue
only. If resolution or authorization fails, stop as a no-op without writing.
Do not start a new unrelated goal from a PR CI event.

## Live loader precondition (automation only)

An automated Goal Executor run may execute this runtime only after its standalone
loader, or the Project Executor loader for a delegated goal, loaded this file
from the repository default branch.

This runtime does not load itself. If that precondition cannot be established,
fail closed before every repository mutation or remote write:

- make no repository file changes;
- perform no agent-created branch or branch switch;
- create no commit;
- perform no push;
- perform no remote branch publication;
- create or update no pull request;
- perform no merge;
- report an explicit live-loader precondition blocker;
- point to `.ai/automation/goal-executor-production-setup.md`.

Manual `/execute-goal` usage outside Cursor Automation is unaffected.

## Always read first

1. The triggering issue and its structured fields (Goal, Acceptance criteria,
   Constraints, Out of scope, Relevant context). For delegated work, also read
   the parent Project Execution issue (Product outcome, Completion criteria,
   Constraints, Out of scope, Relevant context only).
2. `.ai/README.md` and follow `/execute-goal` through canonical documents.
3. `.ai/policies/autonomy-and-authorization.md` for authorization and question
   timing.
4. `.ai/automation/README.md` for automation-specific boundaries.

**Ignore the issue `Commands` section entirely** for scope, planning,
implementation, validation, and Done. It is human cheat-sheet text only. Do not
treat it as a goal, constraint, acceptance criterion, or relevant context.

## Preconditions

- Confirm a valid standalone trigger or delegated Project Executor
  authorization.
- Confirm Goal and Acceptance criteria are present and bounded.
- Refuse execution when authorization, repository access, or required context is
  missing.

## Idempotency

Apply the complete execution-state contract from `.ai/automation/README.md`:

- before the first agent-initiated repository mutation, branch creation or
  switch, implementation, or commit; and
- immediately before the first remote write of every run, including resumed work.

Remote writes include push, pull request creation or metadata update, issue or
pull request comment creation or edit, and authorized squash merge.

## Execution

Follow `.ai/skills/execute-goal.md` and canonical lifecycle documents. Do not
duplicate lifecycle or quality-gate content here.

1. Prepare only required artifacts per `.ai/quality/definition-of-ready.md`.
2. Implement only the authorized scope.
3. Run applicable validation per `.ai/quality/quality-gates.md`.
4. Prefer independent review when available; otherwise perform explicit
   self-review per `.ai/review/ai-review-checklist.md`. When self-correcting
   review mode is active (direct opt-in or inherited from Project Executor),
   follow `.ai/review/self-correcting-review-loop.md`.
5. Limit implementation, review, and fix iterations to three. Stop when the limit
   is reached. The self-correcting review loop uses the same hard max of three
   review passes.
6. Stop for an immediate blocker or unresolved material decision per
   `.ai/policies/autonomy-and-authorization.md`.

## Branch and pull request

- Use a non-protected branch whose name includes the exact `issue-<issue-number>`
  token for the triggering issue.
- Create or update a **draft** pull request only after local validation and
  review are current.
- The pull request body must contain exact `Closes #<issue-number>` for the
  triggering issue. When Project Executor's pull request merged and CI/workflow
  completed triggers are configured, merging that pull request continues the
  parent project (after post-merge CI is green, or via CI repair when red).

## CI stabilization and review-ready handoff

After the draft pull request exists, complete Slice 2 through review-ready
handoff per `.ai/git/branch-and-pr-workflow.md` **in the same automation run**
whenever the run can still observe CI. Do not treat "draft PR created" as a
successful terminal stop.

1. Verify remote commit attribution and PR metadata.
2. Wait for applicable CI on the pull request to reach a terminal state (poll
   or re-check until green, failed, cancelled, or uninspectable). Do not end
   the run while applicable CI is still pending.
3. Fix clear in-scope CI failures caused by this branch; push forward commits
   only; then wait for CI again.
4. Rerun affected local validation and review when fixes change behavior.
5. Record the initial diff-risk assessment in the PR description or a top-level
   PR comment per `.ai/review/diff-risk-checklist.md`.
6. Mark the pull request **ready for review** only when applicable CI passes,
   attribution is clean, and the handoff is complete.

If the automation platform ends the run before CI finishes despite the rule
above, the CI/workflow completed trigger on that PR head branch must resume
Goal Executor (case 3 in **Trigger**) so handoff and merge still complete
without a human comment.

If applicable CI cannot be inspected, or attribution cannot be fixed without
rewriting published history, stop with an explicit blocker. Do not claim
review-ready status.

### Run completion boundary

A Goal Executor automation run may stop only when one of these is true:

- the pull request is **ready for review** and merge is human-owned (no
  `auto-merge`, or escalated / ineligible);
- authorized `self-correcting-review auto-merge` squash completed and tip
  verification passed;
- an explicit blocker or unresolved material decision was reported;
- bounded iteration limits were reached and reported.

Stopping after opening or updating a **draft** while applicable CI is pending,
or before review-ready handoff when CI is already green, is a contract
violation. Do not report automation success for that outcome.

## Authorized self-correcting merge

When `self-correcting-review auto-merge` is active (direct opt-in or inherited
from Project Executor) and all merge preconditions in
`.ai/policies/autonomy-and-authorization.md` are met after the handoff above,
perform the authorized squash merge and verification in
`.ai/git/branch-and-pr-workflow.md`. Report the merge SHA and pull request URL.

Required for that squash:

1. Pass an explicit clean commit title and clean commit body (no AI badges and
   no trailers in the message the agent supplies).
2. Read back the merged PR and the default-branch tip.
3. Treat only agent-added / non-platform prohibited attribution as a tip
   blocker. Platform-injected `Co-authored-by: Cursor Agent` and platform-added
   user `Co-authored-by` on that tip after an authorized auto-merge squash are
   allowed per `.ai/git/branch-and-pr-workflow.md`.

When `auto-merge` was not authorized, the run escalated to human CR, or any
merge precondition fails, stop before merge. Do not enable GitHub auto-merge
queue.

## Remote verification

Before stopping:

1. Inspect every commit in the pull request range for GitHub-verified
   signatures. Platform-managed `Cursor Agent` author and user `Co-authored-by`
   on verified native cloud agent commits are not blockers. Procedure:
   `.ai/git/branch-and-pr-workflow.md`. When signed cloud commits are expected,
   any commit that is not GitHub Verified is an immediate blocker. Do not claim
   review-ready status while such a commit remains.
2. Execute the canonical read-after-write procedure in
   `.ai/git/branch-and-pr-workflow.md` for pull request metadata and for every
   issue or pull request comment created or edited during the current run.
3. Read the remote pull request back and confirm it is marked ready for review
   when review-ready criteria are met.
4. When an authorized self-correcting merge ran, confirm the pull request is
   merged and the default-branch tip attribution passes **Commits on `main`**
   in `.ai/git/branch-and-pr-workflow.md` (including the authorized-squash
   platform-injected trailer exception).

## Prohibited actions

Never enable GitHub auto-merge queue, force push, or rewrite published branch
history after the first push. Never merge except under authorized eligible
`self-correcting-review auto-merge`. Human authorization cannot override the
append-only published-history rule. Do not bypass branch protection, disable
required validation, or make unrelated cleanup changes.

