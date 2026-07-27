# MCP Policy

## Purpose

Model Context Protocol (MCP) servers extend agent capabilities. This policy sets expectations for MCP use in AI-assisted work.

## Default posture

- **Least privilege** — enable only MCP servers needed for the task.
- **Read-only by default** — prefer read access until write access is justified.
- **No credential exposure** — MCP tools must not leak secrets into logs, commits, or PRs; follow `.ai/policies/security-policy.md` for secret handling.

## Allowed use

- Reading from approved documentation or issue trackers when configured by the project
- Running read-only queries against development or staging systems when explicitly set up
- Fetching external references needed for the scoped task

## Requires explicit approval

- MCP tools that write to production systems
- MCP tools that modify repository settings, permissions, or deployments
- MCP tools that access sensitive personal or customer data
- Adding new MCP servers or expanding server permissions mid-task

## Safe commands

When MCP exposes shell or API execution:

- scope commands to the task
- avoid destructive flags
- document commands in the review handoff (a review packet or equivalent PR
  description) or session log

## Branch and PR creation

MCP does not change git policy. Agents still must not merge PRs or push to `main`. See `.ai/git/branch-and-pr-workflow.md`.

## Related documents

- `.ai/policies/allowed-tools.md`
- `.ai/policies/dangerous-actions.md`
- `.ai/policies/security-policy.md`
