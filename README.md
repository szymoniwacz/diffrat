# Numbat

Local CLI for developers and reviewers who want structured assistance when
assessing pull-request diffs using git context.

## Purpose

Numbat reads a bounded git diff (not the whole repository) and produces a
review-oriented report: change summary, focus areas, and git metadata. It runs
locally without a web UI. Terminal output is the default; use `--json` when
scripting.

## Status

Phase 2 complete — v1 static core: `numbat review` with modes, JSON, git
context, categories, and deterministic Focus/Risk hints. Optional LLM (Phase 3)
is deferred / out of v1 (D-005).

## Current capabilities

- Installable Python package with `numbat` CLI entry point
- `--help` and `--version`
- `numbat review` — analyze unstaged or staged local git diffs and print a
  human-readable report (file list with coarse categories, per-file +/- counts,
  summary, deterministic Focus/Risk hints)
- `numbat review --json` — same analysis as structured JSON on stdout for scripting
- `numbat review --base <ref>` — compare the current branch to a base ref and
  include git context (branch, base, commits since base)
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

`source`, `tests`, `config`, `docs`, or `other`.

The report also includes deterministic Focus/Risk hints derived from paths and
diff size (for example large diffs, tests touched, config/dependency changes,
and security-sensitive path names). No network or API key is required. JSON
output includes additive `category` fields on each file and a top-level
`focus_risk` array while keeping `schema_version` at `"1"`.

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
