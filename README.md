# Numbat

Local CLI for developers and reviewers who want structured assistance when
assessing pull-request diffs using git context.

## Purpose

Numbat reads a bounded git diff (not the whole repository) and produces a
review-oriented report: change summary, focus areas, and git metadata. It runs
locally without a web UI. Terminal output is the default; use `--json` when
scripting (planned for the first feature goal after bootstrap).

## Status

documentation first — bootstrap complete; product commands are scaffold-only

## Current capabilities

- Installable Python package with `numbat` CLI entry point
- `--help` and `--version`
- Dev tooling: pytest, ruff, mypy

Diff ingestion and review reports are not implemented yet.

## Setup

Requires Python 3.11+ and git on PATH (for future diff commands).

```bash
pip install -e ".[dev]"
```

## Run

```bash
numbat --help
python -m numbat --help
```

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

- No diff analysis commands yet
- No CI integration or GitHub App
- Optional LLM analysis deferred to a later phase

## License

MIT — see [`LICENSE`](LICENSE).

## Contact and contributions

Maintained by Szymon Iwacz. Contributions via pull request; agents never merge.
