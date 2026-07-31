# Roadmap

## Purpose

Keep the project direction visible without turning the roadmap into a task dump.

## Phase 1 — Bootstrap and CLI skeleton

**Status:** complete

Goal:
Complete project definition, template customization, and a runnable Python CLI
with `--help` and documented dev commands.

Outputs:

- Filled `.ai/project/*` and `.ai/docs/project-requirements.md`
- Product README and updated `AGENTS.md`
- CI validator in `--mode project`
- Minimal `numbat` package installable via `pip install -e ".[dev]"`

## Phase 2 — Diff ingestion and static report (v1 core)

**Status:** complete (v1 close bar)

Evidence: `main` includes merged PR #10 (`7c8711b`) — `numbat review` modes,
`--json` schema v1, git context, coarse file categories, and deterministic
Focus/Risk hints; validated with pytest / ruff / mypy.

Goal:
Deliver the first useful version: read git diff context locally and emit a
structured review-oriented report.

Outputs:

- Commands for diff targets (e.g. unstaged, staged, branch range)
- Terminal report and `--json` output
- Tests covering CLI and diff parsing paths
- Git-context section (commits, files touched, coarse change categories)
- Deterministic Focus/Risk hints (no LLM)

## Review depth — hunks, CI hints, local checks

**Status:** complete

Goal:
Make `numbat review` useful for pre-merge self-review beyond file counts — show
what changed, flag CI/workflow edits, and optionally run local checks.

Evidence: Project Execution #13 closed; merged PRs #15, #17, #19 on `main`.

Outputs:

- Bounded diff hunks in text report and `--json` `changes`
- `ci_workflow_paths` Focus/Risk hint with suggested validator command
- `numbat review --check` with path-mapped validators, documented exit codes

## Phase 3 — Analysis depth (optional LLM layer)

**Status:** deferred / out of v1 (D-005)

Goal:
Add optional intelligent analysis when configured; keep deterministic fallback
without API keys.

Outputs:

- Pluggable analysis backend (heuristics default, optional LLM via env/config)
- Documented secrets handling and offline behavior
- Decision record for provider choice

Not implemented for this v1 project. Return trigger: a later project or owner
goal that reopens LLM work after provider and data-handling choices.

## Phase 4 — Integrations (deferred)

Goal:
Extend beyond local CLI — CI hooks, PR annotations, team workflows.

Outputs:

- TBD after v1 usage feedback
- Owner: project maintainer

## Later phases

- PyPI publication
- Config profiles per repository — **partially delivered** (v1 repo-local
  `[tool.numbat]` in `pyproject.toml` / `.numbat.toml`; see D-006 and README
  Configuration)
- Custom rule packs for domain-specific review focus — **partially delivered**
  (v1 `content_rules` declarative regex on added hunk lines; shared/remote
  packs still deferred)
