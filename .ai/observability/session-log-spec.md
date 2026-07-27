# Session Log Specification

## Purpose

Define a minimal log format so AI-assisted work is observable across sessions.

Logs preserve information that standard workflow artifacts do not capture, without
relying on chat history.

## When to create a log

Create or append a session log only when it preserves information not available
in standard workflow artifacts such as task packets, plans, review handoffs, or
pull requests.

Required:

- after a significant failed or corrected run, when error history, approach
  changes, or recovery steps are needed for review or continuation;
- when handing work off between sessions or agents and the current state is not
  sufficiently described in packets, plans, review handoffs, or PRs;
- when the project or user explicitly requires a session log.

Optional:

- for routine, successfully completed work — including multi-step work — when
  existing artifacts already capture scope, validation, and outcome.

## Required fields

| Field | Description |
|---|---|
| **task** | Task packet title or brief goal |
| **agent/tool** | Cursor, Claude Code, Copilot, or other |
| **files changed** | List of paths touched |
| **commands run** | Test, lint, build, or other commands executed |
| **failures** | Errors, gate failures, or blocked steps |
| **corrections** | What was fixed after a failure |
| **final result** | `completed`, `blocked`, `needs-review`, or `abandoned` |
| **follow-up** | Next tasks or open items |

## Recommended fields

| Field | Description |
|---|---|
| **iteration count** | Number of agent/user correction loops |
| **review surface** | Short summary of diff scope (file count, layers) |
| **quality gates** | Which gates passed, failed, or were skipped |
| **rework** | Whether work was redone and why |
| **drift signals** | Scope creep, doc drift, or unrelated edits detected |

## Log data safety

Session logs must not contain secrets, tokens, credentials, PII, or unapproved production data. Redact commands, failures, and outputs when necessary. Follow `.ai/policies/security-policy.md` for secret handling.

## Storage

Projects may store logs under `.ai/observability/sessions/` as markdown files:

```txt
.ai/observability/sessions/YYYY-MM-DD-task-slug.md
```

Use this specification as the format. Do not invent a parallel schema in tool adapters.

## Related documents

- `.ai/metrics/workflow-evaluation.md`
- `.ai/packets/review-packet.template.md`
- `.ai/policies/security-policy.md`
