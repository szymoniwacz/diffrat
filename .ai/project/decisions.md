# Decisions

## Purpose

This file is a lightweight decision log and ADR index.

Record short decisions here directly.
For significant architecture decisions, create a full ADR in `.ai/architecture/` and link it below.

The goal is not bureaucracy.
The goal is memory.

## Decision log

### D-001 — Product direction (2026-07-27)

**Decision:** Numbat v1 is a local CLI that assists PR/diff review using git
context; terminal output by default with `--json` optional.

**Status:** confirmed (project intake round 1)

**Context:** Chosen over whole-project analysis, web UI, and CI-first delivery.

---

### D-002 — Stack (2026-07-27)

**Decision:** Python CLI using `.ai/stack-profiles/python-cli.md`.

**Status:** confirmed

**Context:** Fits local tooling, fast iteration, strong CLI test ecosystem.

---

### D-003 — Primary users (2026-07-27)

**Decision:** Both self-reviewing developers and reviewers assessing others' diffs.

**Status:** confirmed

---

### D-004 — License (2026-07-27)

**Decision:** MIT License; copyright Szymon Iwacz 2026 (see `LICENSE`).

**Status:** confirmed

---

### D-005 — LLM analysis layer (2026-07-27; updated 2026-07-28)

**Decision:** Skip Phase 3 LLM for this v1 project. Numbat v1 closes on the
Phase 2 static core (deterministic Focus/Risk hints and file categories). No
LLM provider, network client, or LLM-related env vars are in scope for v1.

**Status:** confirmed (skipped for v1)

**Context:** Owner reply on Project Execution issue #8 (2026-07-28): treat
Phase 2 as the v1 close bar; secrets N/A for v1; Phase 3 deferred.

**Return trigger:** A later Project Execution (or explicit owner goal) that
reopens optional LLM analysis and chooses a provider / data-handling policy.

---

### D-006 — Per-repository config format (2026-07-31)

**Decision:** Numbat v1 loads optional per-repository rules from TOML at the git
repository root (or `cwd` when not in a git repo):

1. `pyproject.toml` → `[tool.numbat]` (base)
2. `.numbat.toml` overrides duplicate keys when both exist

`[tool.numbat.checks]` maps check code → display command string; v1 allows
override for `ci_validator` only (pytest/ruff/mypy/bandit/pip-audit stay
built-in). `[tool.numbat.content_rules]` provides declarative regex rules on
added diff-hunk lines with shorthand (`pattern → expected`) or table form
(`pattern`, `expected`, optional `paths`). Invalid regex at load time: stderr
warning, skip rule. Parsing uses stdlib `tomllib` only; no new runtime
dependencies. Absent config preserves pre-config behavior.

**Status:** confirmed (Project Execution #33)

**Context:** Replaces numbat-specific hardcoding in `content_hints.py` and
`checks.py` with dogfood rules in this repo's `pyproject.toml`. Remote/shared
rule packs and `--config PATH` remain deferred.

> Reusable workflow rules (for example, documentation before implementation)
> live in the canonical workflow documents under `.ai/`, not in this product
> decision log.

## Architecture decision index

Link full ADRs here when they exist.

| ADR | File | Status |
|---|---|---|
| — | — | — |
