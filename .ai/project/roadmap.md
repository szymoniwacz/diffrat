# Roadmap

## Purpose

Keep the project direction visible without turning the roadmap into a task dump.

## Phase 1 — Bootstrap and CLI skeleton

Goal:
Complete project definition, template customization, and a runnable Python CLI
with `--help` and documented dev commands.

Outputs:

- Filled `.ai/project/*` and `.ai/docs/project-requirements.md`
- Product README and updated `AGENTS.md`
- CI validator in `--mode project`
- Minimal `numbat` package installable via `pip install -e ".[dev]"`

## Phase 2 — Diff ingestion and static report (v1 core)

Goal:
Deliver the first useful version: read git diff context locally and emit a
structured review-oriented report.

Outputs:

- Commands for diff targets (e.g. unstaged, staged, branch range)
- Terminal report and `--json` output
- Tests covering CLI and diff parsing paths
- Git-context section (commits, files touched, coarse change categories)

## Phase 3 — Analysis depth (optional LLM layer)

Goal:
Add optional intelligent analysis when configured; keep deterministic fallback
without API keys.

Outputs:

- Pluggable analysis backend (heuristics default, optional LLM via env/config)
- Documented secrets handling and offline behavior
- Decision record for provider choice

Return trigger: first Agent Goal after Phase 2 ships.

## Phase 4 — Integrations (deferred)

Goal:
Extend beyond local CLI — CI hooks, PR annotations, team workflows.

Outputs:

- TBD after v1 usage feedback
- Owner: project maintainer

## Later phases

- PyPI publication
- Config profiles per repository
- Custom rule packs for domain-specific review focus
