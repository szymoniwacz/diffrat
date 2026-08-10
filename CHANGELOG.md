# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `--check` bandit false positives on Diffrat itself (`subprocess` import/run in
  `checks.py`; pillar id `"maintainable"` in `review_quality.py`)
- Track `.ai/ideas/implemented/` docs referenced by `decisions.md`

### Changed

- `mypy` excludes `build/` (avoids duplicate-module errors after `python -m build`)
- Maintainer setup notes CI Python 3.11 and that workflow validate needs
  `./scripts/setup-ai-workflow.sh` first
- CI runs `ruff format --check src tests`, `ruff check .`, and `mypy .` in
  addition to pytest (matches README / stack-profile quality gates)
- CI / `[dev]` include `bandit` on `--check` dogfood modules (`checks.py`,
  `review_quality.py`, `scoring.py`)
- One-shot `ruff format` on `src/` and `tests/`

## [1.1.1] - 2026-08-09

### Fixed

- `--check` bandit invocation uses a single `-r` with multiple paths (repeated
  `-r` flags broke bandit CLI)
- `--check` no longer maps package `__init__.py` to a non-existent
  `tests/test___init__.py`
- `possible_secret` high-entropy detection ignores code/prose string fragments
  (e.g. f-string message pieces with braces and operators)

### Changed

- `docs/feedback-checklist.md` updated for 1.1.1 (`--brief`, Review quality)

## [1.1.0] - 2026-08-08

### Added

- `diffrat review --brief` — triage-first text report (omits Changes hunks);
  JSON empties `changes.files` under `--brief`
- **Review quality** section in text reports and additive `review_quality` in
  `--json` — three pillars rolled up from Focus/Risk hints
  (`docs/review-quality.md`)
- Ruby debug leftover hints: `binding.pry`, `byebug`, call-like `puts(` in
  `.rb` files (`debug_leftover`)
- `docs/demo/` — sample brief report and 5-minute presenter runbook
- `docs/llm.md` — copy-paste OpenAI and Ollama setup, env table, troubleshooting,
  and JSON LLM field shapes
- Additive JSON `llm_status` / `llm_findings` on LLM success and
  `llm_status` / `llm_error` on LLM failure (`schema_version` unchanged)
- Actionable stderr for common LLM misconfiguration (missing base URL for
  Ollama, invalid API key, bad base URL, connection refused)

### Changed

- README repositioned as local **review triage** CLI with sample report
- README optional LLM section shortened with link to `docs/llm.md`
- `diffrat review --help` epilog references `docs/llm.md`
- Default CI/workflow Focus/Risk hints no longer embed dogfood validator commands;
  `ci_validator` runs only when configured in `[tool.diffrat.checks]`
- `--check` path mapping generalized for any `src/<package>/` layout (not
  hardcoded to this repository)
- PyPI classifier: Development Status Beta (was Production/Stable)

### Fixed

- Removed product-code hardcoding of `validate-workflow-contracts.py` filename;
  CI hints rely on `ci/` and `.github/workflows/` path patterns plus repo config

## [1.0.0] - 2026-07-31

First product release: v1 review CLI core plus optional Phase 3 LLM analysis.

Shipped initially as **Numbat**; rebranded to **Diffrat** (D-008) so the PyPI
project name, CLI command, and import package match (`diffrat`). PyPI held a
`0.0.1` name-reservation stub before the product `1.0.0` wheel.

### Added

- `diffrat review` — analyze local git diffs and print a human-readable report
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
- `diffrat review --check` — path-scoped local validators (pytest, ruff, mypy,
  bandit, pip-audit, CI workflow contract) with documented exit codes
- `--fail-on=<codes>` — scriptable gate on Focus/Risk hint codes (exit `4` when
  matched); JSON includes `fail_on.requested` and `fail_on.matched`
- Optional per-repository config in `pyproject.toml` / `.diffrat.toml`:
  `[tool.diffrat.checks]` (v1: `ci_validator` override) and
  `[tool.diffrat.content_rules]` (declarative regex on added hunk lines)
- Optional LLM-backed analysis when `DIFFRAT_LLM_PROVIDER` and `DIFFRAT_LLM_API_KEY`
  are set; optional `DIFFRAT_LLM_BASE_URL` for local OpenAI-compatible endpoints
  (ADR-0001, D-005). Heuristics-only report remains the default without API keys

### Changed

- Product rename Numbat → Diffrat (CLI, import, config keys, `DIFFRAT_LLM_*`)
- Install via `pip install diffrat` from PyPI (in addition to source install)

### Known limitations

- Phase 4 integrations (CI bots, PR annotations, GitHub App) are deferred
- Shared or remote rule packs beyond repo-local TOML are not supported
- LLM analysis requires explicit opt-in env vars; diff content leaves the machine
  only when configured
- Migration from Numbat dogfood: update CLI invocations, `[tool.diffrat]` /
  `.diffrat.toml`, and `DIFFRAT_LLM_*` (old `NUMBAT_*` / `[tool.numbat]` no
  longer read)

[Unreleased]: https://github.com/szymoniwacz/diffrat/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/szymoniwacz/diffrat/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/szymoniwacz/diffrat/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/szymoniwacz/diffrat/releases/tag/v1.0.0
