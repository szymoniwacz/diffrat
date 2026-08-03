# Branch and Pull Request Workflow

## Purpose

Define git discipline for AI-assisted changes in this repository.

## Source of truth

This file owns the detailed Git and pull request procedure. Related canonical documents own their own concerns; reference them instead of duplicating their rules:

- `.ai/docs/full-workflow.md` owns lifecycle ordering across stages.
- `.ai/instructions/workflow.md` owns concise operational instructions.
- `.ai/policies/autonomy-and-authorization.md` owns autonomous versus supervised mode and outcome authorization.
- `.ai/quality/` owns quality gates and completion criteria.
- `.ai/review/` owns the review checklists (AI self-review, diff-risk, human review).

## Outcome authorization

Invoking `/execute-goal` authorizes branch or worktree creation, commits, push,
and pull request creation or update by default. Supervised mode may override
that default. See `.ai/policies/autonomy-and-authorization.md`.

When the user authorizes a review-ready pull request outcome, or invokes
`/execute-goal`, the agent may:

- create or switch to an appropriate non-protected branch,
- create separate worktrees and branches for parallel write agents,
- create intentional commits,
- push the branch,
- create or update the pull request,
- complete CI stabilization and in-scope CI fixes after PR creation,
- record the initial diff-risk assessment.

That authorization does not include merge, force push, published-history
rewrite, bypassing branch protection, disabling required validation, secret
disclosure, or destructive changes outside scope. Published branch history is
append-only after the first push; see **Append-only published history** below.

## Parallel write isolation

When multiple write agents work on one goal, each write agent uses a separate
Git worktree and branch with non-overlapping file ownership. The lead
orchestrator owns the integration branch and the final PR. See
`.ai/policies/multi-agent-orchestration.md`.

## Branch naming

Use descriptive branch names:

```txt
NN-phase-short-slug
feature-short-slug
fix-short-slug
```

For template maintenance, follow the roadmap format when applicable (e.g. `10-p1-architecture-pack`).

Goal Executor automation branches:

- every new Goal Executor branch must include the literal `issue-<issue-number>`
  token;
- `cursor/issue-123-short-slug` is the canonical example;
- a generic native `cursor/...` name without the exact issue token remains
  acceptable only outside Goal Executor;
- a branch without an exact issue token and without an already-linked pull
  request must not be treated as resumable Goal Executor evidence.

State resolution: `.ai/automation/README.md`.

Cloud agents may use native non-protected `cursor/...` branch names outside Goal
Executor. Before creating another branch or pull request for the same issue,
search for an existing open pull request or resumable branch linked to that
issue. See `.ai/automation/README.md`.

## One logical change per branch

Each branch should contain one coherent change:

- one feature slice,
- one bugfix,
- one doc update,
- one template improvement,
- one authorized goal that may include multiple intentional commits.

Do not bundle unrelated work.

## Working tree safety

Inspect the working tree before changes. Never discard or overwrite unrelated
user changes. Stop only when proceeding would put unrelated work at risk.

## One PR per branch

Open one pull request per branch targeting `main`.

## No direct push to main

Agents and automated workflows must not push directly to `main`. Use a branch and pull request.

## No merge by agent except auto-merge

Agents may create branches, commits, and pull requests. Agents must never merge
pull requests except under authorized eligible
`self-correcting-review auto-merge`. Default, self-correcting-without-auto-merge,
and escalated paths: only humans merge after review. Mode and preconditions:
`.ai/policies/autonomy-and-authorization.md`.

## Authorized self-correcting merge

Use only when all merge preconditions in
`.ai/policies/autonomy-and-authorization.md` are met
(`self-correcting-review auto-merge` authorization; loop clean; eligible
low/medium; applicable CI green or none; no open material, dangerous, or
immediate blockers).

Procedure (Goal Executor):

1. Confirm the pull request is ready for review, applicable CI is green (or no
   applicable CI is configured), attribution and PR metadata are clean, and the
   self-correcting handoff records eligibility.
2. Squash-merge only (for example `gh pr merge --squash`). Do not use merge
   commit or rebase merge. Do not enable GitHub auto-merge queue.
3. When squash-merging, pass an explicit **clean commit title** and **clean
   commit body** (subject + optional body only). Do not include AI badges,
   generation footers, or any `Co-authored-by` / `Signed-off-by` trailers in
   the message the agent supplies. Prefer the GitHub API / `gh` flags that set
   `commit_title` and `commit_message` (or equivalent) so the default squash
   text from PR commits is not used as-is.
4. Read back the remote pull request and confirm it is merged.
5. Read the resulting default-branch tip commit. Confirm the title and body
   follow **Commits on `main`** below (including the authorized-squash
   platform-injected trailer exception).
6. If merge is denied (permissions, branch protection, required reviews) or
   verification fails, stop with an explicit blocker. Do not bypass protection,
   force push, or retry with a different merge strategy.
7. Report the merge SHA and pull request URL. On success under Project Executor,
   the existing pull request merged trigger continues the project; when
   applicable CI on the default branch is still pending, the CI/workflow
   completed trigger resumes after that CI finishes (green → next/finalize;
   red → CI repair first).

## Attribution by surface

Use the author identity from local Git configuration and respect existing
signing requirements.

**Prohibited attribution** means tool, model, agent, or AI attribution —
including "Made with Cursor", "generated by" / "created by", agent-added
`Co-authored-by`, invented `Signed-off-by`, and similar markers.

### Temporary PR branch commits

Native Cursor Cloud Agent commits on temporary pull-request branches may use
`Cursor Agent` as the commit author and may include the platform-added user
`Co-authored-by` trailer. This platform-managed attribution is **not** a
blocker when the commit is **GitHub Verified**.

Agents must not manually add `Co-authored-by` or other prohibited attribution
to commit messages.

### Pull request metadata

PR titles and PR bodies must not contain prohibited attribution. Remove
platform-added operational footer markup such as `Open in Web` or `View
Automation` from the final PR body intended for human review.

After every create or update operation affecting a pull request title or body:

1. Read the actual remote title and body.
2. Check both for prohibited attribution and platform footer markup.
3. If cleanup is needed, update the remote metadata.
4. Read the actual remote title and body again after that update.
5. Confirm the server-side result is clean.

A successful write response is not verification. If the platform restores
prohibited content and a clean read-back cannot be obtained, stop with an
immediate blocker.

### Generated GitHub comments

Apply the same rule to every issue or pull request comment created or edited by
the automation:

1. Write the comment.
2. Read that exact remote comment back.
3. Check the returned content for prohibited attribution.
4. Clean it when possible.
5. Read it again after cleanup.

Do not edit human-authored comments. Final status is based on remote state, not
the locally prepared text or write response.

### Commits on `main`

Final commits on `main` must not contain agent-added prohibited attribution.
Squash merge onto `main` is performed by a human (default, self-correcting
without `auto-merge`, or escalated) or by Goal Executor under authorized
eligible `self-correcting-review auto-merge`. Agents must not merge outside
that authorized path.

The merger verifies the resulting default-branch tip:

1. Clean title and an empty or clean body (no AI badges or generation footers).
2. No agent-supplied AI attribution trailers in the squash message the merger
   sent.
3. **Authorized-squash tip exception:** after Goal Executor squash-merges under
   eligible `self-correcting-review auto-merge`, GitHub may still append
   platform-injected `Co-authored-by: Cursor Agent <…>` and the platform-added
   user `Co-authored-by` trailer on the tip (derived from verified native cloud
   agent PR commits). Those platform-injected trailers alone are **not**
   blockers and are **not** a Project Executor FINALIZE failure. Same rationale
   as **Temporary PR branch commits**: the platform owns that metadata.
4. Any other prohibited attribution on the tip (for example "Made with Cursor",
   agent-invented trailers, or generation badges) remains an immediate blocker.

Human squash merges should still supply a clean squash message in the UI when
possible. Agents must not rewrite published history to strip platform-injected
trailers.

## Pre-push metadata gate

Before every push:

1. Inspect **every local commit that is not yet present on the remote branch**
   (the exclusive range `upstream..HEAD` or `base..HEAD`, equivalently
   merge-base-to-HEAD), not only the tip.
2. Remove prohibited attribution from local commits **before** pushing when the
   commit is not a native cloud agent commit covered by **Temporary PR branch
   commits** above. Platform-added user `Co-authored-by` on verified cloud agent
   commits is allowed and need not be stripped. Local history may be amended,
   rebased, or squashed only while those commits remain unpublished (before the
   first push).
3. When creating the PR, or when updating PR title or body metadata, prepare and
   verify the planned title and body:
   - no prohibited attribution or generation badges,
   - required PR description sections are present,
   - the text is ready to submit without further metadata cleanup.

Do not push commits that still contain prohibited attribution, except
platform-managed cloud agent attribution allowed under **Temporary PR branch
commits** above.

## Append-only published history

Once any commit from a branch exists on the remote (published), that branch's
history is **append-only**.

Rules:

- Every correction after the first push must be added as a **new signed commit**.
- Agents must never force push or otherwise rewrite published history
  (amend, rebase, filter-branch, or equivalent) on any branch — **without
  exception**.
- Human authorization cannot override this prohibition for agents. If published
  history must be rewritten, a human performs that action outside agent
  workflow.
- Before the first push, local unpublished commits may still be amended,
  rebased, or squashed to meet the pre-push metadata gate.
- After publication, PR title and body attribution may be removed automatically.
  If prohibited attribution remains in published commits (other than
  platform-managed cloud agent attribution allowed under **Temporary PR branch
  commits**) and the only fix is rewriting published history, treat that as an
  **immediate blocker**. Report and stop.

## CI stabilization

This section owns the remote verification and CI procedure used after pull
request creation and before human-review handoff. Lifecycle order:
`.ai/docs/full-workflow.md`. Quality-gate ownership:
`.ai/quality/quality-gates.md`. Completion criteria:
`.ai/quality/definition-of-done.md`.

A pull request is **not review-ready** while any applicable CI check is pending
or failing. Local success on one platform is not proof that all configured CI
environments will pass.

### After push and PR creation

1. Inspect **every commit in the pull request range** (`base..HEAD` or
   merge-base-to-HEAD), not only the tip:
   - remote commits are GitHub-verified when this workflow expects signed cloud
     commits,
   - temporary PR branch commits follow **Attribution by surface**,
   - tip commit SHA matches what was intentionally pushed.
2. Verify PR metadata per **Attribution by surface** (including remote body
   inspection after creation or update).
3. If published commit messages contain prohibited attribution (other than
   allowed platform-managed cloud agent attribution) and fixing them requires
   rewriting published history, stop as an immediate blocker.
4. Identify applicable CI checks for the PR (required and otherwise configured
   checks that this change triggers).
5. Wait until those checks complete. Prefer `gh pr checks <n> --watch` (or
   equivalent status polling) until every applicable check is terminal. Pending
   applicable CI means not review-ready.
6. If any applicable check fails:
   - inspect the failure logs,
   - fix clear in-scope failures caused by this branch,
   - push the fix as a new forward commit,
   - repeat from remote verification until applicable CI is green.
7. If CI cannot be inspected (missing permissions, unavailable logs, or no
   usable status API), report that limitation explicitly and do not claim full
   validation or review-ready status.

### Compatibility expectations

When the change touches CI matrices, runtimes, dependency manifests, lockfiles,
or package-manager configuration, treat cross-environment compatibility as
in-scope. Do not treat a single local platform pass as sufficient evidence for
all configured CI environments. The gate checklist lives in
`.ai/quality/quality-gates.md`.

### Stop condition

Claim review-ready only when:

- PR metadata is attribution-clean per **Attribution by surface**,
- every commit in the PR range meets attribution rules for its surface,
- all applicable CI checks pass.

If prohibited commit attribution (other than allowed platform-managed cloud
agent attribution) can only be removed by rewriting published history, report an
immediate blocker. If CI cannot be inspected, report the limitation and do not
claim full validation or review-ready status.

### Goal Executor automation

Goal Executor automation creates a draft pull request, completes remote CI
stabilization, records diff-risk, and marks the pull request ready for review
when criteria pass. A draft without terminal applicable CI (or without
review-ready handoff when CI is already green) is an incomplete run, not a
successful stop. Default and escalated paths still stop before merge; eligible
`self-correcting-review auto-merge` continues through squash merge. Contract:
`.ai/automation/goal-executor.md`.

## Review handoff

A PR description may act as the review handoff when it contains information
equivalent to the review packet (`.ai/packets/review-packet.template.md`).
When it does not, link to a separate review packet instead of duplicating it.

Use the applicable GitHub template:

- product PRs: `.github/pull_request_template.md`
- template-maintenance PRs: `.github/PULL_REQUEST_TEMPLATE/template-maintenance.md`
  (append `?template=template-maintenance.md` to the PR URL)

After creating the PR and completing CI stabilization, record the initial
diff-risk assessment from `.ai/review/diff-risk-checklist.md` in the PR
description or a top-level PR comment. If an AI agent created the PR, that
agent performs the initial assessment; the human reviewer independently
verifies it. Pending or failing applicable CI means not yet ready for that
human-review handoff.

Record validation results in the PR body; skipped checks need a reason. State
related PR or merge-order dependencies explicitly. Prefer small, independent
PRs.

Related canonical documents: `.ai/packets/review-packet.template.md`,
`.ai/review/diff-risk-checklist.md`, `.ai/review/human-review-checklist.md`,
`.ai/quality/definition-of-done.md`.
