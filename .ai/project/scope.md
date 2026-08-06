# Scope

## Purpose

Define what is currently allowed and what is intentionally deferred.

This file protects the project from uncontrolled expansion.

## In scope now

- Bootstrap and project definition (vision, requirements, readiness)
- Python CLI packaging scaffold (`pyproject.toml`, `src/diffrat/`, dev tooling)
- Local git diff ingestion (working tree, staged, branch vs base, commit range)
- Structured review report: change summary, risk/focus hints, git metadata context
- Human-readable terminal output with optional `--json` flag
- Optional LLM analysis when `DIFFRAT_LLM_*` is configured (D-005 / ADR-0001);
  heuristics-only remains the default without API keys
- Unit and CLI tests for new commands and flags
- Documentation updates alongside behavior changes

## Out of scope by default

- Web UI, GitHub App, or hosted review service
- CI/CD integration and PR comment bots (deferred to Phase 4)
- Full-repository or cross-repo analysis
- Automatic merge, approval, or policy enforcement
- Shared or remote rule packs beyond repo-local TOML (D-006 partial)
- Large rewrites without explicit approval
- New frameworks without a decision record
- Hidden architecture changes
- Undocumented generated files

Required preparation by change type lives in
`.ai/quality/definition-of-ready.md` and `.ai/policies/no-blind-coding.md`.

## Scope levels

| Level | Meaning |
|---|---|
| Idea | rough concept only |
| Expanded idea | clear problem, goal, scope, risks |
| Ready for planning | packet or brief complete enough to plan |
| Planned | implementation plan exists in `.ai/plans/` |
| Implementation-ready | full gate passed; work may change files |
| Implemented | code exists and docs were updated |
| Archived | intentionally rejected or deferred |

## Rule

If a task changes scope, update this file or add a decision record before continuing.
