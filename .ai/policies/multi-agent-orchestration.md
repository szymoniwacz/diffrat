# Multi-Agent Orchestration Policy

## Purpose

Define optional multi-agent execution under one authorized `/execute-goal` run.

`/execute-goal` remains the only primary entry point.

Autonomy and question timing: `.ai/policies/autonomy-and-authorization.md`.
Canonical lifecycle: `.ai/docs/full-workflow.md`.

## When to use

Use multiple agents only when independent workstreams exist, write scopes can be
isolated, and the gain outweighs coordination cost. Do not spawn agents for
trivial work. Otherwise stay single-agent.

## Roles

| Role | Responsibility |
|---|---|
| Lead / orchestrator | Owns the goal, task graph, integration branch, final PR, and stop decisions |
| Research agent | Read-only analysis or evidence gathering |
| Write agent | Implements one independent workstream in an isolated worktree and branch |
| Validation agent | Runs validation; does not redefine scope |
| Review agent | Independent review of the integrated result when available |

Exactly one lead/orchestrator owns the goal.

## Isolation and ownership

Parallel write agents must use separate Git worktrees and branches with
non-overlapping file ownership. Overlapping write scopes are forbidden.

Record workstream state only in the implementation plan. Omit that section for
single-agent work.

## Integration

The orchestrator owns one integration branch. After integrating workstream
commits, validate the combined result, review the integrated diff, resolve
in-scope findings, and rerun affected validation before finalization. Then
continue push and PR handoff per the canonical lifecycle.

## Fallback

Fall back to a single-agent `/execute-goal` run when additional agents are
unavailable, no independent workstreams exist, isolation costs too much, or
supervised mode requests a single-agent path.
