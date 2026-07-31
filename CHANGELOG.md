# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-07-31

First product release: v1 review CLI core plus optional Phase 3 LLM analysis.

### Added

- `numbat review` — analyze local git diffs and print a human-readable report
- Review modes: unstaged (default), `--staged`, `--base <ref>` (merge-base through
  HEAD), and `--range <A..B>` (two-dot commit range)
- `--json` — structured stdout output with `schema_version`; additive `llm_findings`
  when LLM analysis succeeds
- Git context on branch and range reviews (branch, base, commits since base)
- File categories (`source`, `tests`, `config`, `docs`, `ci`, `other`) and
  deterministic Focus/Risk hints (path, size, git-context, and content-based
  signals)
- Per-file `risk_score`, risk-sorted file listings, category groups, and
  **Review order** (top five paths)
- Bounded **Changes** diff hunks in text and JSON; `--hunks-for=<path>` for
  single-file deep view
- `numbat review --check` — path-scoped local validators (pytest, ruff, mypy,
  bandit, pip-audit, CI workflow contract) with documented exit codes
- `--fail-on=<codes>` — scriptable gate on Focus/Risk hint codes (exit `4` when
  matched); JSON includes `fail_on.requested` and `fail_on.matched`
- Optional per-repository config in `pyproject.toml` / `.numbat.toml`:
  `[tool.numbat.checks]` (v1: `ci_validator` override) and
  `[tool.numbat.content_rules]` (declarative regex on added hunk lines)
- Optional LLM-backed analysis when `NUMBAT_LLM_PROVIDER` and `NUMBAT_LLM_API_KEY`
  are set; optional `NUMBAT_LLM_BASE_URL` for local OpenAI-compatible endpoints
  (ADR-0001, D-005). Heuristics-only report remains the default without API keys

### Known limitations

- Phase 4 integrations (CI bots, PR annotations, GitHub App) are deferred
- No PyPI publication in this release (`pip install -e` from source)
- Shared or remote rule packs beyond repo-local TOML are not supported
- LLM analysis requires explicit opt-in env vars; diff content leaves the machine
  only when configured

[Unreleased]: https://github.com/szymoniwacz/numbat/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/szymoniwacz/numbat/releases/tag/v1.0.0
