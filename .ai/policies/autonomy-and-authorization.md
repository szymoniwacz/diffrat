# Autonomy and Authorization Policy

## Purpose

Define the default operating model for AI-assisted work in this repository.

The default is **goal-oriented autonomous work** from an authorized goal through
a review-ready pull request. Supervised step-by-step prompting is an explicit
override, not the default.

This policy owns:

- autonomous versus supervised mode,
- `/execute-goal` authorization,
- `/execute-project` authorization,
- when to ask the human,
- routine versus material decisions,
- failure recovery,
- resumability,
- human-only merge.

Canonical lifecycle order: `.ai/docs/full-workflow.md`.

Multi-agent parallelism: `.ai/policies/multi-agent-orchestration.md`.

Agents must never merge a pull request.

## Operating modes

### Autonomous mode (default)

After the user authorizes a goal, continue through routine phases without asking
for approval between them. That includes preparation, implementation,
validation, review, commits, push, final PR creation or update, CI
stabilization, and in-scope CI fixes after PR creation when using the GitHub PR
workflow.

### Supervised mode (explicit request only)

Use only when the user explicitly requests an earlier stop. Supervised mode may
override default goal-to-PR authorization. When the requested stop is before
commit or push, do not commit and do not push until authorized.

## `/execute-goal` authorization

Invoking `/execute-goal`, or an equivalent request to carry a goal through to
human review, authorizes branch or worktree creation, scoped changes, tests,
validation, commits, push, final PR creation or update, CI stabilization, and
in-scope CI fixes after PR creation.

For a configured trusted automation, an exact `/execute-goal` comment by the
authorized repository owner on an ordinary GitHub issue is equivalent to
invoking `/execute-goal`. Automation-specific trigger and boundary details live
in `.ai/automation/README.md`.

The user does not need to repeat the words "open a PR".

Exceptions: supervised mode, no PR workflow, an unresolved immediate blocker, a
dangerous action requiring prior approval, or another genuine external blocker.

Never authorized: merge, force push, rewriting published branch history after
the first push, out-of-scope destructive changes, secret disclosure, bypassing
branch protection, disabling required validation, or unrelated cleanup. Human
authorization cannot override the append-only published-history rule for agents.
See `.ai/git/branch-and-pr-workflow.md`.

## `/execute-project` authorization

An exact `/execute-project` comment by the authorized repository owner on one
open **Project Execution** issue authorizes Project Executor to select and run
one small goal at a time inside that issue's stated outcome and constraints.
A separate `/execute-goal` comment is not required for those delegated goals.

It does not authorize concurrent goals, scope expansion, undefined material
decisions, dangerous actions, force push, direct push to the protected default
branch, auto-merge, or merge. Runtime details live in
`.ai/automation/project-executor.md`.

## Question timing

This policy is the sole owner of when to ask.

### Automatic fixes

Apply automatically when the fix is clearly correct, inside scope,
non-destructive, and does not introduce an unapproved material product,
architecture, security, privacy, data, or externally visible decision.

Do not ask about routine naming, obvious file placement, documented validation,
existing repository conventions, or other low-risk details when repository
evidence gives a clear answer. Record those assumptions in the packet, plan, or
PR handoff.

### Deferred decisions

Collect unresolved material questions, architecture choices, correctness
concerns, and best-practice suggestions during analysis, implementation,
validation, and review.

Do not interrupt while safe independent work remains.

Ask one grouped batch after independent implementation, validation, and review
are complete, but before final commits, push, and PR handoff.

For every question include evidence or reason, a recommended answer, meaningful
alternatives when they exist, and the impact of each option.

When the human replies on a GitHub issue, present enumerated lettered options
(plus **Other** when needed) and ask for letter-only replies. Project Executor
format on project issues: `.ai/automation/project-executor.md`.

If the user rejects a material suggestion, record it concisely as a deferred
follow-up or accepted risk in the PR handoff.

### Immediate blockers

Ask earlier only when:

- no safe independent work remains,
- the next necessary action requires prior human approval,
- continuing would probably create incorrect, destructive, or insecure work.

### After answers

Apply the answers, update affected packet, plan, code, tests, and documentation,
rerun affected validation, repeat review when needed, then finalize commits,
push, and PR handoff.

## Planning and approvals

Create a plan or task graph when required by
`.ai/quality/definition-of-ready.md`. Plan creation is not automatically a
blocking approval gate.

Approval classes for refactors, migrations, and security follow
`.ai/quality/definition-of-ready.md`, `.ai/policies/dangerous-actions.md`, and
`.ai/policies/security-policy.md`.

## Bootstrap and readiness

After definition coverage and required human decisions are resolved,
readiness-safe bootstrap may proceed under `/execute-goal`. Product behaviour
remains blocked until project readiness passes.

## Failure handling

Automatically fix in-scope failures caused by this work, update directly
affected docs, and rerun validation. Do not hide failures or weaken validators.

## Resumability

Resume from repository evidence, not chat history: readiness docs, triggering
issue or brief, branch, commits, and PR.

## Git safety

Work on a non-protected branch, never discard unrelated user changes, use the
local Git author identity, never merge, never force push or rewrite published
branch history after the first push, and never bypass protection rules. See
`.ai/git/branch-and-pr-workflow.md`.

## Related documents

- `.ai/skills/execute-goal.md`
- `.ai/docs/full-workflow.md`
- `.ai/policies/multi-agent-orchestration.md`
- `.ai/quality/definition-of-ready.md`
- `.ai/git/branch-and-pr-workflow.md`

