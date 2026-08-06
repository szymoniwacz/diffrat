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
- Minimal installable package via `pip install -e ".[dev]"` (then named Numbat;
  rebranded to Diffrat per D-008)

## Phase 2 — Diff ingestion and static report (v1 core)

**Status:** complete (v1 close bar)

Evidence: `main` includes merged PR #10 (`7c8711b`) — review modes,
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
Make `diffrat review` useful for pre-merge self-review beyond file counts —
show what changed, flag CI/workflow edits, and optionally run local checks.

Evidence: Project Execution #13 closed; merged PRs #15, #17, #19 on `main`.

Outputs:

- Bounded diff hunks in text report and `--json` `changes`
- `ci_workflow_paths` Focus/Risk hint with suggested validator command
- `diffrat review --check` with path-mapped validators, documented exit codes

## Phase 3 — Analysis depth (optional LLM layer)

**Status:** complete

Evidence: Project Execution #71; merged PRs #73 (ADR/D-005), #75 (analysis
backend), #77 (OpenAI-compatible client), #79 (report/JSON `llm_findings`).

Goal:
Add optional intelligent analysis when configured; keep deterministic fallback
without API keys.

Outputs:

- ADR-0001 and updated D-005 (OpenAI-compatible client; env vars now
  `DIFFRAT_LLM_*` after D-008)
- Pluggable analysis backend (heuristics default, optional LLM via env/config)
- Documented secrets handling and offline behavior in README
- LLM findings in text report and additive `--json` `llm_findings` when enabled
- Mocked LLM HTTP tests; no live integration required in CI

## Rebrand and PyPI publication

**Status:** in progress (D-008)

Goal:
Ship under the Diffrat name with matching PyPI / CLI / import (`diffrat`), and
publish the real `1.0.0` wheel (after `0.0.1` name-reservation stub).

Outputs:

- Full rebrand (code, config, env, docs)
- Trusted Publishing + tag-driven release workflow
- `pip install diffrat` installs the product CLI

## Phase 4 — Integrations (deferred)

Goal:
Extend beyond local CLI — CI hooks, PR annotations, team workflows.

Outputs:

- TBD after v1 usage feedback
- Owner: project maintainer

## Later phases

- Config profiles per repository — **partially delivered** (v1 repo-local
  `[tool.diffrat]` in `pyproject.toml` / `.diffrat.toml`; see D-006 and README
  Configuration)
- Custom rule packs for domain-specific review focus — **partially delivered**
  (v1 `content_rules` declarative regex on added hunk lines; shared/remote
  packs still deferred)
