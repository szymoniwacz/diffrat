# Diffrat

**Diffrat** is a local **review triage** CLI. Point it at a git diff and it
tells you what to look at first — offline by default, with an optional LLM
layer only when you configure it.

Use it before opening a PR, or when reviewing a branch, to get a ranked file
list, Focus/Risk hints, and bounded hunks without leaving the terminal.

## Sample report

Example of `diffrat review --base main` on a small feature branch (sections and
formatting match shipped 1.0.0 text output):

```text
Review Report
=============

Git context
-----------
Branch: feature/risk-score-tweak
Base: main
Commits since base: 2
Recent commits:
  a1b2c3d Tune risk weights for config paths
  e4f5a6b Cover scoring edge cases in tests

Summary
-------
Files changed: 4
Lines added: 83
Lines deleted: 15
Total lines changed: 98

Files
-----
source
  src/diffrat/scoring.py  [source]  risk=17  +28 -6
  src/diffrat/cli.py  [source]  risk=7  +12 -3
tests
  tests/test_scoring.py  [tests]  risk=19  +35 -4
docs
  README.md  [docs]  risk=5  +8 -2

Review order
------------
1. tests/test_scoring.py  [tests]  (+35 -4 lines)
2. src/diffrat/scoring.py  [source]  (+28 -6 lines)
3. src/diffrat/cli.py  [source]  (+12 -3 lines)
4. README.md  [docs]  (+8 -2 lines)

Changes
-------
tests/test_scoring.py
@@ -10,0 +11,8 @@
+def test_config_boost_for_toml() -> None:
+    assert _config_boost('pyproject.toml') > 0

src/diffrat/scoring.py
@@ -40,7 +40,10 @@
 RISK_WEIGHT_CONFIG_CATEGORY = 10
+
+def _config_boost(path: str) -> int:
+    return RISK_WEIGHT_CONFIG_CATEGORY if path.endswith('.toml') else 0

src/diffrat/cli.py
@@ -88,6 +88,9 @@
     parser.add_argument("--json", action="store_true")
+    parser.add_argument(
+        "--fail-on",
+        help="comma-separated hint codes that fail the review",
+    )

README.md
@@ -1,3 +1,5 @@
 # Diffrat
+
+Local review triage for git diffs.


Focus / Risk
------------
- [warn] [tests_touched] Tests touched — confirm coverage matches behavior changes
```

## Setup

Requires Python 3.11+ and git on PATH.

```bash
pip install diffrat
diffrat --version
diffrat review --base main
```

`diffrat review` needs a **real diff**. On a clean `main` with no local changes,
`--base main` returns exit code `2` (`no changes on branch since main`) — that
is expected. Use unstaged/staged edits or a feature branch, then rerun.

From source (development):

```bash
git clone https://github.com/szymoniwacz/diffrat.git
cd diffrat
pip install -e .
diffrat --version
```

For local tests, lint, typecheck, and `diffrat review --check`, install extras:

```bash
pip install -e ".[dev]"
```

External dogfood sessions: [`docs/feedback-checklist.md`](docs/feedback-checklist.md).

## Common commands

Run from inside a git repository:

```bash
# Unstaged changes (working tree vs index) — default
diffrat review

# Staged changes
diffrat review --staged

# Branch vs base (merge-base through HEAD; default base is main)
diffrat review --base main

# Two-dot range
diffrat review --range main..feature

# Structured JSON for scripting
diffrat review --base main --json

# Triage-first report (omit Changes / hunk payloads)
diffrat review --base main --brief
diffrat review --base main --brief --json

# Path-scoped local validators/tests for touched files
diffrat review --base main --check

diffrat review --help
```

`--json` writes a structured document to stdout (`schema_version` identifies the
format). When LLM analysis is enabled and succeeds, JSON includes additive
`llm_findings`; the key is omitted when LLM is disabled or the request fails.
Errors and empty-diff messages go to stderr with the same exit codes as the
text report.

`--brief` keeps Git context (when applicable), Summary, Files, Review order, and
Focus/Risk, but omits the text **Changes** section. With `--json`, `changes.files`
is empty while `changes.limits` remains. `--brief` works with `--staged`,
`--base`, and `--range`. It is mutually exclusive with `--hunks-for`.

## Status

**1.0.0** is the first product release on PyPI as
[`diffrat`](https://pypi.org/project/diffrat/) (formerly developed as Numbat;
see D-008):

- `diffrat review` with unstaged, `--staged`, `--base`, and `--range`; optional
  `--json` and `--brief` (triage without hunks)
- Bounded hunks, git context, file categories, deterministic Focus/Risk hints
- Optional `--check` for path-scoped local validators and tests
- Optional LLM analysis when `DIFFRAT_LLM_*` is set (ADR-0001 / D-005);
  heuristics-only remains the default without API keys

Phase 4 (CI bots / GitHub App) is deferred. See `.ai/project/roadmap.md`.

## Focus / Risk, categories, and ordering

Each changed file gets a coarse category: `source`, `tests`, `config`, `docs`,
`ci`, or `other`.

Focus/Risk hints are deterministic (paths, diff size, content on `source` /
`ci` hunks). No network or API key is required for the heuristic report. JSON
adds `category` on each file and a top-level `focus_risk` array
(`schema_version` stays `"1"`). Each hint has `code`, `message`, and
`severity` (`risk`, `warn`, or `info`) from `src/diffrat/scoring.py`. Content
hints may include optional `path` and `line`. Hints sort by severity, then code.

Each file also gets a non-negative integer `risk_score`. The text **Files** list
and JSON `files[]` sort by descending score (ties by path). **Files** groups by
category (`source`, `tests`, `ci`, `config`, `docs`, `other`). **Review order**
lists up to five highest-priority paths. Text lines show `risk=<score>` (binary
files use fixed score `5`).

| Signal | Weight constant | Points |
|---|---|---|
| Line share of non-binary diff | `RISK_WEIGHT_LINE_SHARE_MAX` (50) | scaled by file lines ÷ total |
| Security-sensitive path | `RISK_WEIGHT_SECURITY_SENSITIVE` | 40 |
| `source` without tests in diff | `RISK_WEIGHT_SOURCE_WITHOUT_TESTS` | 25 |
| `ci` category | `RISK_WEIGHT_CI_CATEGORY` | 20 |
| `config` category | `RISK_WEIGHT_CONFIG_CATEGORY` | 10 |
| Binary file | `RISK_WEIGHT_BINARY` | 5 (fixed) |

Common hint themes include large diffs, tests/config/CI touched, security-sensitive
paths, rename/copy, category composition, generated artifacts, lockfile/manifest
consistency, git-context signals on branch/range reviews, and content codes such
as `possible_secret`, `debug_leftover`, `dangerous_call`, `broad_exception`,
`hardcoded_url_or_ip`, plus validator typo patterns (e.g.
`PROJECT_EXECUTOR_COMMENT_FILTER`). Full code list: `src/diffrat/scoring.py`.

## Changes section (diff hunks)

Text reports include a **Changes** section with unified-diff hunks unless
`--brief` is set. JSON has a top-level `changes` object (`changes.files` is empty
under `--brief`). Output is bounded:

| Limit | Value |
|---|---|
| Max files in Changes | 20 |
| Max diff lines per file | 100 |

Limits appear in `diffrat review --help` and JSON `changes.limits`.

### Single-file deep diff (`--hunks-for`)

`--hunks-for=<path>` shows **Changes** for one repository-relative path only
(500-line budget). **Files**, **Review order**, and **Focus / Risk** still
cover the full diff. Missing path → exit `1`. Cannot combine with `--brief`.

```bash
diffrat review --staged --hunks-for=src/foo.py
diffrat review --base main --hunks-for=src/foo.py --json
```

## Optional local checks (`--check`)

| Touched path pattern | Command run |
|---|---|
| `ci/`, `.github/workflows/`, or `validate-workflow-contracts.py` | `python ci/validate-workflow-contracts.py --mode project` |
| `src/diffrat/<module>.py` | `pytest tests/test_<module>.py`, `mypy src/diffrat/<module>.py`, and `bandit -r …` when `bandit` is on PATH |
| `tests/test_<name>.py` | `pytest tests/test_<name>.py` |
| other `tests/` files | `pytest tests` |
| `pyproject.toml` | `ruff check .` and `pip-audit` when available |
| lockfile / dependency manifests | `pip-audit` when available |

Failed checks → stderr + exit `3`. Missing optional tools are recorded as
**skipped** and do not fail the run alone.

## Scriptable gate (`--fail-on`)

Fail when requested hint codes appear (comma-separated, no spaces):

| Exit code | Meaning |
|---|---|
| `0` | Success (no requested codes matched) |
| `1` | Git error, usage error, or invalid `--fail-on` token |
| `2` | Empty diff (evaluated before `--fail-on`) |
| `3` | `--check` failure (takes precedence over exit `4`) |
| `4` | At least one requested hint code matched |

```bash
diffrat review --base main --fail-on=regex_typo,possible_secret
diffrat review --base main --json --fail-on=regex_typo,possible_secret
```

With `--json`, output includes top-level `fail_on.requested` / `fail_on.matched`.

## Configuration

Offline and deterministic by default (D-005). No API keys required for the
heuristic report.

### Optional LLM analysis (Phase 3)

Opt-in only. With no `DIFFRAT_LLM_*` variables, Diffrat makes no network
requests. When provider and API key are set, it sends **diff-scoped** prompts
to an OpenAI-compatible endpoint. Success adds an **LLM analysis** section /
`llm_findings` in JSON.

| Variable | Required | Purpose |
|---|---|---|
| `DIFFRAT_LLM_PROVIDER` | When LLM enabled | Provider id (e.g. `openai`, `ollama`) |
| `DIFFRAT_LLM_API_KEY` | When LLM enabled | API key or token |
| `DIFFRAT_LLM_BASE_URL` | Optional | Custom / local OpenAI-compatible base URL |

**Privacy:** diff content leaves the machine only when you set these variables.
Never commit keys. See ADR-0001 and D-005 in `.ai/project/decisions.md`.

Optional per-repo TOML at the git root (or `cwd`):

1. `pyproject.toml` → `[tool.diffrat]` (base)
2. `.diffrat.toml` overrides duplicate keys

Invalid content-rule regex → stderr warning and skip; review continues.

### `[tool.diffrat.checks]`

Map check code → command string (no `shell=True`). In v1, only `ci_validator`
may be overridden.

```toml
[tool.diffrat.checks]
ci_validator = "python ci/validate-workflow-contracts.py --mode project"
```

### `[tool.diffrat.content_rules]`

Regex rules on **added** hunk lines. Shorthand or table form with optional
`paths`. See D-006 and this repo’s `pyproject.toml` for dogfood examples.

## Tests and quality

```bash
pytest
ruff check .
mypy .
```

## Architecture and context

- `.ai/project/product-context.md` — product identity and workflows
- `.ai/project/scope.md` — in-scope and deferred work
- `.ai/docs/architecture-direction.md` — CLI component boundaries

## How this project is built

Developed with a documentation-first AI delivery workflow. That system is
private and not part of the installable CLI — Setup above is enough to run
`diffrat`. Maintainer setup: [`docs/ai-workflow-setup.md`](docs/ai-workflow-setup.md).

## Limitations

- No CI integration or GitHub App (Phase 4 deferred)
- LLM analysis needs explicit env configuration; non-OpenAI-shaped APIs need a
  compatibility layer or future adapter (ADR-0001)
- The PyPI name `numbat` was already taken; this product uses `diffrat` (D-008)

## License

MIT — see [`LICENSE`](LICENSE).

## Contact and contributions

Maintained by Szymon Iwacz. Contributions via pull request; agents never merge
except under authorized eligible `self-correcting-review auto-merge`.
