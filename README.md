# Numbat

Local CLI for developers and reviewers who want structured assistance when
assessing pull-request diffs using git context.

## Purpose

Numbat reads a bounded git diff (not the whole repository) and produces a
review-oriented report: change summary, focus areas, and git metadata. It runs
locally without a web UI. Terminal output is the default; use `--json` when
scripting.

## Status

Phase 2 in progress — `numbat review` for unstaged/staged and branch-vs-base diffs

## Current capabilities

- Installable Python package with `numbat` CLI entry point
- `--help` and `--version`
- `numbat review` — analyze unstaged or staged local git diffs and print a
  human-readable report (file list, per-file +/- counts, summary)
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

## Tests and quality

```bash
pytest
ruff check .
mypy .
```

## Configuration and environment variables

No configuration required for the bootstrap scaffold. Optional LLM credentials
will be documented when that layer is added (Phase 3).

## Architecture and context

- `.ai/project/product-context.md` — product identity and workflows
- `.ai/project/scope.md` — in-scope and deferred work
- `.ai/docs/architecture-direction.md` — CLI component boundaries

## Working system

This repository uses `.ai/` as its AI working system. See
[`.ai/docs/template-flow.md`](.ai/docs/template-flow.md) for workflow rules.

## Limitations

- No CI integration or GitHub App
- Optional LLM analysis deferred to a later phase

## License

MIT — see [`LICENSE`](LICENSE).

## Contact and contributions

Maintained by Szymon Iwacz. Contributions via pull request; agents never merge.
