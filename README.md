# Numbat

Local CLI for developers and reviewers who want structured assistance when
assessing pull-request diffs using git context.

## Purpose

Numbat reads a bounded git diff (not the whole repository) and produces a
review-oriented report: change summary, focus areas, and git metadata. It runs
locally without a web UI. Terminal output is the default; use `--json` when
scripting.

## Status

v1 complete on `main` — local diff review CLI without LLM (D-005):

- `numbat review` with unstaged, `--staged`, `--base`, and `--range` modes; optional `--json`
- Bounded diff hunks, git context, file categories, deterministic Focus/Risk hints
  (including CI/workflow path hints with suggested commands, and content-based typo
  hints for known CI validator patterns)
- Optional `--check` for path-scoped local validators and tests

Phase 3 (optional LLM) and Phase 4 (integrations) are deferred. See
`.ai/project/roadmap.md`.

## Current capabilities

- Installable Python package with `numbat` CLI entry point
- `--help` and `--version`
- `numbat review` — analyze unstaged or staged local git diffs and print a
  human-readable report (file list with coarse categories, per-file +/- counts,
  bounded diff hunks, summary, deterministic Focus/Risk hints)
- `numbat review --json` — same analysis as structured JSON on stdout for scripting
- `numbat review --check` — run applicable local validators/tests for touched paths
- `numbat review --base <ref>` — compare the current branch to a base ref and
  include git context (branch, base, commits since base)
- `numbat review --range <A..B>` — compare two git refs using two-dot range
  semantics (e.g. `main..feature`) and include range git context
- Dev tooling: pytest, ruff, mypy

## Setup

Requires Python 3.11+ and git on PATH.

```bash
pip install -e ".[dev]"
```

## Run

```bash
numbat --help
python -m numbat --help
```

### Review a local diff

Run from inside a git repository:

```bash
# Unstaged changes (working tree vs index) — default
numbat review

# Staged changes (index vs HEAD)
numbat review --staged

# Branch vs base (merge-base with ref through HEAD; default base is main)
numbat review --base main
numbat review --base

# Two-dot commit range (changes reachable from B not from A)
numbat review --range main..feature

numbat review --help
```

### JSON output for scripting

Use `--json` to write a structured document to stdout instead of the
human-readable report. The `schema_version` field identifies the output format;
breaking changes require bumping that version.

```bash
# Unstaged diff as JSON
numbat review --json

# Staged or branch-vs-base JSON
numbat review --staged --json
numbat review --base main --json

# Example: file count from a branch review
numbat review --base main --json | python -c "import sys,json; print(json.load(sys.stdin)['summary']['file_count'])"
```

Errors and empty-diff messages still go to stderr with the same exit codes as
the default report.

### Focus / Risk hints and file categories

Every successful review assigns each changed file a coarse category:

`source`, `tests`, `config`, `docs`, `ci`, or `other`.

The report also includes deterministic Focus/Risk hints derived from paths and
diff size (for example large diffs, tests touched, config/dependency changes,
docs-only changes, CI/workflow path changes with suggested validator commands,
security-sensitive path names, rename/copy detection (`rename_or_move`),
category-composition signals (`source_without_tests`, `tests_only`,
`ci_without_tests`, `workflow_without_ci_validator`), size and deletion signals
(`large_single_file`, `deletions_heavy`), generated-artifact detection
(`generated_file_touched`), missing mapped test files for changed
`src/numbat` modules, lockfile/manifest consistency hints (`lockfile_without_manifest`,
`manifest_without_lockfile`), git-context hints on branch/range reviews
(`many_commits`, `wip_commits`) and cross-area diffs (`mixed_concerns`), and
content-based hints from added hunk lines on
`source` and `ci` paths). Content-based codes include `possible_secret`,
`debug_leftover`, `dangerous_call`, `broad_exception`, and `hardcoded_url_or_ip`,
plus validator-specific typo hints for known CI patterns such as
`PROJECT_EXECUTOR_COMMENT_FILTER`. No network or API key is
required. JSON
output includes additive `category` fields on each file and a top-level
`focus_risk` array while keeping `schema_version` at `"1"`. Each hint carries a
`severity` (`risk`, `warn`, or `info`) from the central registry in
`src/numbat/scoring.py`; unknown codes default to `info`. Hints are sorted by
severity (risk first), then by code, in both text and JSON reports.

### File risk scores and ordering

Each changed file receives a deterministic non-negative integer `risk_score`
computed in `src/numbat/scoring.py`. Files in the text **Files** list and JSON
`files[]` array are sorted by descending `risk_score`; ties break by path name.
The **Changes** section follows the same order.

Text reports show `risk=<score>` on each file line (for example
`src/a.py  [source]  risk=42  +4 -1`). Binary files use a fixed score of `5`.

| Signal | Weight constant | Points |
|---|---|---|
| Line share of non-binary diff | `RISK_WEIGHT_LINE_SHARE_MAX` (50) | scaled by file lines ÷ total |
| Security-sensitive path | `RISK_WEIGHT_SECURITY_SENSITIVE` | 40 |
| `source` without tests in diff | `RISK_WEIGHT_SOURCE_WITHOUT_TESTS` | 25 |
| `ci` category | `RISK_WEIGHT_CI_CATEGORY` | 20 |
| `config` category | `RISK_WEIGHT_CONFIG_CATEGORY` | 10 |
| Binary file | `RISK_WEIGHT_BINARY` | 5 (fixed) |

JSON output includes additive `risk_score` on each file entry while keeping
`schema_version` at `"1"`.

### Changes section (diff hunks)

Text reports include a **Changes** section with unified-diff hunks for each
changed file (after the file list). JSON output includes a top-level `changes`
object with the same bounded content per file (`path`, `hunks` with `header`
and `lines`, plus `binary` / `truncated` flags).

Output is bounded to keep reports readable:

| Limit | Value |
|---|---|
| Max files shown in Changes | 20 |
| Max diff lines per file | 100 |

When limits apply, the report notes truncation. Limits are documented in
`numbat review --help` and echoed in JSON under `changes.limits`.

### Optional local checks (`--check`)

Use `--check` to run applicable repo validators/tests for touched paths and
include results in the report:

| Touched path pattern | Command run |
|---|---|
| `ci/`, `.github/workflows/`, or `validate-workflow-contracts.py` | `python ci/validate-workflow-contracts.py --mode project` |
| `src/numbat/<module>.py` | `pytest tests/test_<module>.py`, `mypy src/numbat/<module>.py`, and `bandit -r src/numbat/<module>.py` when `bandit` is on PATH |
| `tests/test_<name>.py` | `pytest tests/test_<name>.py` |
| other `tests/` files (e.g. `conftest.py`) | `pytest tests` |
| `pyproject.toml` | `ruff check .` and `pip-audit` when `pip-audit` is on PATH |
| lockfile or dependency manifest paths (e.g. `poetry.lock`, `requirements.txt`) | `pip-audit` when `pip-audit` is on PATH |

Multiple touched modules are deduplicated into one `pytest`, one `mypy`, and one
`bandit` invocation with all target paths. Source and test changes that map to the
same module run that test file once.

`bandit` and `pip-audit` are optional host tools. When a check applies by path
but the executable is not on PATH, the report records a **skipped** result and
the review run does not fail solely because the tool is missing.

Text reports add a **Local checks** section. JSON output includes an additive
top-level `checks` array with `code`, `command`, `passed`, `output`, and
optional `skipped` fields.

Failed checks are echoed to stderr with the command and output. Exit code `3`
means at least one check failed (distinct from git errors and empty diffs).

```bash
numbat review --check
numbat review --staged --check
numbat review --base main --check --json
```

### Scriptable gate (`--fail-on`)

Use `--fail-on` with comma-separated hint codes (no spaces) to fail the review
when any requested code appears in Focus/Risk hints. This is an advisory gate on
hint presence only — it does not run extra subprocesses beyond `--check`.

| Exit code | Meaning |
|---|---|
| `0` | Success (no requested codes matched) |
| `1` | Git error, usage error, or invalid `--fail-on` token |
| `2` | Empty diff (evaluated before `--fail-on`) |
| `3` | `--check` subprocess failure (takes precedence over exit `4`) |
| `4` | At least one requested hint code matched |

```bash
# Fail when typo or secret hints appear (human report)
numbat review --base main --fail-on=regex_typo,possible_secret

# Pre-push hook: JSON + gate
numbat review --base main --json --fail-on=regex_typo,possible_secret
```

When `--json` and `--fail-on` are both used, JSON output includes a top-level
`fail_on` object with `requested` and `matched` arrays so scripts can read
matches without parsing stderr.

## Tests and quality

```bash
pytest
ruff check .
mypy .
```

## Configuration and environment variables

No configuration or API keys required. v1 is offline and deterministic. Optional
LLM credentials are out of scope for this project (Phase 3 deferred; D-005).

## Architecture and context

- `.ai/project/product-context.md` — product identity and workflows
- `.ai/project/scope.md` — in-scope and deferred work
- `.ai/docs/architecture-direction.md` — CLI component boundaries

## Working system

This repository uses `.ai/` as its AI working system. See
[`.ai/docs/template-flow.md`](.ai/docs/template-flow.md) for workflow rules.

## Limitations

- No CI integration or GitHub App
- Optional LLM analysis is out of v1 (deferred; D-005)

## License

MIT — see [`LICENSE`](LICENSE).

## Contact and contributions

Maintained by Szymon Iwacz. Contributions via pull request; agents never merge.
