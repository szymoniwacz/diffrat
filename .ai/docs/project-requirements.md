# Project Requirements

## Purpose

This document describes what should be built and why.

It is the main requirements document for AI-assisted planning and implementation.

## Project summary

Numbat is a local Python CLI that helps developers and reviewers assess pull-request
diffs using git context. It targets the repeated pain of inconsistent, slow manual
diff review by producing a structured report: what changed, what deserves attention,
and supporting metadata from git.

The first useful version runs locally in a git repository, analyzes a bounded diff
(not the whole project), and prints a human-readable report to the terminal with an
optional `--json` flag for scripting. There is no web UI and no CI integration in v1.

## Users

| User | Needs | Notes |
|---|---|---|
| Developer (author) | Fast self-review signal before push/PR | Runs locally on own branch |
| Reviewer | Triage and focus areas for manual review | Same CLI; may use branch/range args |
| Maintainer | Small PRs, documented commands, MIT license | Uses `.ai/` workflow for delivery |

## Problems to solve

- Reviewers miss risky or subtle changes in large diffs
- Authors lack a consistent pre-push review checklist grounded in actual changes
- Git context (commits, files, categories) is underused during review
- Review quality varies with time pressure and experience

## Goals

- One-command local diff review assistance with git context
- Actionable, scannable report for humans; machine-readable JSON when needed
- Deterministic core that works offline without API keys in v1
- Small, reviewable increments delivered via Agent Goals

## Non-goals

- Hosted review platform or web dashboard
- CI bots, PR comments, or GitHub App integration (v1)
- Full-repository static analysis
- Automatic merge/approval decisions
- PyPI publication before v1 is usable from source

## Core workflows

### Workflow 1 — Self-review before PR

1. Developer completes changes on a feature branch
2. Runs Numbat against diff vs base branch (or staged/unstaged)
3. Reads summary, focus areas, and git context in terminal
4. Fixes issues and re-runs until satisfied
5. Opens PR manually (outside Numbat)

### Workflow 2 — Reviewer triage

1. Reviewer checks out branch locally or specifies commit range
2. Runs Numbat with appropriate diff target
3. Uses report to prioritize files and risk areas
4. Performs manual code review; Numbat does not approve

## Functional requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| FR-001 | CLI installable from repo via editable install | must | Phase 1 bootstrap scaffold |
| FR-002 | Accept diff targets: unstaged, staged, branch vs base, commit range (`--range A..B`) | must | Phase 2; `--range` uses two-dot `A..B` semantics |
| FR-003 | Emit human-readable review report to stdout | must | Default output |
| FR-004 | Support `--json` for structured output | must | Confirmed intake |
| FR-005 | Include git metadata (commits, files touched) in report | must | Phase 2 |
| FR-006 | Non-zero exit on invalid repo, bad refs, or empty diff when inappropriate | must | Clear errors |
| FR-007 | Heuristic risk/focus hints without LLM | should | v1 static analysis; includes git-context hints (`many_commits`, `wip_commits`, `mixed_concerns`) |
| FR-008 | Optional LLM-backed analysis when configured | could | Phase 3; D-005 / ADR-0001 |

## Data and inputs

| Input | Source | Format | Notes |
|---|---|---|---|
| Git diff | Local `git` | Unified diff text | Primary input v1 |
| Branch/ref names | CLI args | Strings | e.g. `--base main` |
| Commit metadata | Local `git log` | Parsed text | Authors, messages, dates |
| Optional LLM credentials | Environment | API key string | Phase 3 only |

## Outputs

| Output | Consumer | Format | Notes |
|---|---|---|---|
| Review report | Human in terminal | Plain text (structured sections) | Default |
| Review report | Scripts/CI (future) | JSON | `--json` flag |
| Errors | User | stderr + exit code | Non-zero on failure |

## Integrations

| Integration | Purpose | Required now? | Notes |
|---|---|---|---|
| Local git | Diff and metadata | yes | subprocess or GitPython TBD at scaffold |
| LLM API | Deeper analysis | no | Phase 3; provider TBD |
| GitHub API | PR context | no | Deferred |
| CI systems | Automated review | no | Deferred post-v1 |

## Constraints

- Local-first; no network required for v1 core path
- Diff-scoped only; no whole-repo scan in v1
- Agents never merge PRs; humans merge manually
- Small PRs; one bounded Agent Goal at a time
- Python 3.11+ (confirmed in `pyproject.toml`)

## Technical preferences

- Python CLI per `.ai/stack-profiles/numbat-cli.md`
- `pyproject.toml` packaging with `src/numbat/` layout
- pytest, ruff, mypy for quality (commands recorded at scaffold)
- Prefer stdlib + minimal dependencies for v1 git interaction

## Active stack profile

| Active profile | Applies to | Notes |
|---|---|---|
| .ai/stack-profiles/numbat-cli.md | CLI, tests, packaging | Project-specific profile; bootstrap 2026-07-27 |

## Quality requirements

- Unit tests for diff parsing and report building
- CLI integration tests for commands and exit codes
- ruff + mypy clean on changed code
- README and `--help` updated when CLI surface changes

## Security and privacy requirements

- v1 must not exfiltrate repository content by default
- Optional LLM (Phase 3) requires explicit opt-in via env/config and documented data handling
- No secrets in repo; API keys via environment only
- Fail safely on path traversal or unexpected git output (validate inputs)

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| LLM provider undecided | Delays Phase 3 | Ship heuristic v1 first; defer provider ADR |
| Git edge cases (merge commits, renames) | Incorrect reports | Test fixtures; document limitations |
| Over-scoping v1 | Delayed value | Strict scope.md; diff-only |
| JSON schema churn | Breaks scripts | Version field in JSON; semver policy |
| False confidence in heuristics | Bad review outcomes | Frame output as assistance; document limits |

## Assumptions

Record assumptions separately from confirmed requirements.

| Assumption | Why it matters | Confirm by |
|---|---|---|
| Python 3.11+ acceptable for developers | Toolchain choice | Confirmed in `pyproject.toml` |
| `git` available on PATH | Core input source | Documented in README |
| Users run CLI inside a git repo | Diff resolution | FR-006 error handling |
| Heuristic analysis sufficient for v1 value | Scope Phase 2 vs 3 | User feedback after v1 |
| MIT license matches distribution intent | Legal | `LICENSE` |
| macOS and Linux primary; Windows best-effort | Platform support | Confirmed at bootstrap |

## Open questions

- [x] CLI entry point and `--help` (bootstrap scaffold)
- [ ] GitPython vs subprocess for git interaction (resolve at diff-ingestion goal)
- [ ] LLM provider and data-handling policy (Phase 3 goal)
- [ ] stdin/patch-file diff input needed in v1? (likely no — confirm if requested)

## First useful version

Smallest useful v1 (Phase 2 after bootstrap):

- Installable CLI from repo
- Command to analyze a git diff (branch vs base minimum)
- Report with: change summary, files touched, git context, basic heuristic focus hints
- Terminal output + `--json`
- Tests and documented dev commands

## Later versions

- Optional LLM analysis backend (Phase 3)
- CI integration and PR annotations (Phase 4)
- PyPI publish, config profiles, custom rule packs

## Project decision status

Record the status of every area from
`.ai/contracts/project-definition-contract.md`.

| Area | Status | Value / notes | Link / location / return trigger |
|---|---|---|---|
| Product purpose | decided | Local CLI for diff/PR review assistance | `.ai/project/vision.md` |
| Users | decided | Developers (self-review) and reviewers | Intake round 1; D-003 |
| Outcomes | decided | Faster, more consistent diff review with git context | `.ai/project/vision.md` |
| Success criteria | decided | One-command local report; terminal + `--json`; tests pass | FR-001–FR-007; Phase 2 done |
| First useful version | decided | Diff ingestion + structured report (heuristic) | Roadmap Phase 2 |
| Non-goals | decided | No web UI, CI, whole-repo scan, auto-merge | `.ai/project/scope.md` |
| Interfaces | decided | CLI only in v1 | `.ai/docs/architecture-direction.md` |
| Inputs and outputs | decided | Git diff + metadata in; text/JSON report out | FR-002–FR-004 |
| Architecture shape | decided | Layered CLI: git → parser → analysis → renderer | `.ai/docs/architecture-direction.md` |
| Boundaries | decided | Local git only; no server; LLM optional later | Architecture doc |
| Storage and data ownership | not-applicable | No persistent storage; ephemeral stdout | v1 CLI |
| Retention and migrations | not-applicable | No stored user data | v1 CLI |
| Integrations and failure handling | decided | Local git required; clear errors; LLM deferred | FR-006; Phase 3 |
| Authentication and authorization | not-applicable | Local CLI; no multi-user access control | v1 |
| Secrets, privacy, and sensitive data | decided | No default network; Phase 3 keys via env only | Security section |
| Language, framework, and dependencies | decided | Python CLI; pytest/ruff/mypy | D-002; `.ai/stack-profiles/numbat-cli.md` |
| Environments and deployment | decided | Local dev install only; PyPI deferred | Roadmap Phase 4 |
| Configuration | decided | CLI flags + env for future LLM | Architecture doc |
| Logging, monitoring, and errors | decided | stderr + exit codes; no remote telemetry v1 | FR-006 |
| Tests, lint, typecheck, performance | default-accepted | pytest, ruff, mypy per numbat-cli profile | Confirmed at bootstrap 2026-07-27 |
| Scale, reliability, and cost | decided | Single-user local; no SLA; offline OK | v1 scope |
| Supported platforms and compatibility | default-accepted | macOS/Linux primary; Windows best-effort | Confirmed at bootstrap 2026-07-27 |
| Accessibility and localization | not-applicable | Terminal CLI; English output v1 | — |
| Compliance, backup, and recovery | not-applicable | No persistent data | v1 |
| Branching, CI, release, and rollback | default-accepted | `main` + PR; CI `--mode project`; manual merge | Confirmed at bootstrap 2026-07-27 |
| License, ownership, and documentation expectations | decided | MIT; Szymon Iwacz 2026; README + `.ai/` docs | D-004; `LICENSE` |

## Project readiness

Project readiness is a separate gate from definition coverage.

Record the result after completing `.ai/onboarding/bootstrap-checklist.md`.

| Check | Result | Notes |
|---|---|---|
| Definition coverage complete | yes | Intake 2026-07-27 |
| No `blocking-question` remains | yes | LLM deferred, not blocking |
| All `deferred` items have reason and return trigger | yes | LLM → Phase 3 goal |
| Template customization complete | yes | README, AGENTS, CI, scaffold |
| Stack profile selected or marked N/A | yes | `.ai/stack-profiles/numbat-cli.md` |
| Real project commands recorded | yes | `README.md` and `.ai/stack-profiles/numbat-cli.md` |
| Root README describes the product | yes | Product README replaces template |
| `AGENTS.md` describes repository role | yes | Describes Numbat CLI repository |
| Bootstrap markers removed | yes | Removed from `.ai/project/*` during intake |
| License and ownership decided | yes | MIT; Szymon Iwacz 2026 |
| CI, branch rules, and approvals decided | yes | `--mode project`; manual merge on `main` |
| Project ready for first product task | yes | Bootstrap PR; next goal: diff ingestion |

Product implementation may start only when the final row is confirmed.
