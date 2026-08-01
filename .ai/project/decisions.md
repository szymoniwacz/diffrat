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

### D-005 — LLM analysis layer (2026-07-27; updated 2026-07-31)

**Decision:** Phase 3 adds an optional LLM analysis layer when explicitly
configured. Default path remains heuristics-only (offline, no API keys). When
opt-in env/config is set, a single OpenAI-compatible HTTP client augments the
report with LLM findings; prompts are diff-scoped only.

**Env contract:** `NUMBAT_LLM_PROVIDER`, `NUMBAT_LLM_API_KEY`, optional
`NUMBAT_LLM_BASE_URL` for local/custom endpoints.

**Status:** confirmed (Phase 3 — Project Execution #71)

**Context:** v1 closed on Phase 2 static core (issue #8, 2026-07-28). Reopened
via Project Execution #71 (2026-07-31). Owner choices: single OpenAI-compatible
client (1:A); explicit opt-in, diff-scoped prompts, heuristics additive
(2:Y,Y,Y); unified `NUMBAT_LLM_*` env vars with optional base URL (3:B).

**ADR:** [ADR-0001 — Phase 3 optional LLM analysis layer](../architecture/adr-0001-llm-analysis-layer.md)

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

---

### D-007 — Self-correcting `auto-merge` option (2026-08-01)

**Decision:** Squash merge by Goal Executor requires an explicit
`auto-merge` suffix on top of self-correcting review:

- `/execute-goal self-correcting-review auto-merge`
- `/execute-project self-correcting-review auto-merge`

Bare `self-correcting-review` still skips human CR when eligible but leaves
merge to a human.

**Kept:** material-decision, dangerous-action, and high/security-sensitive stops;
default modes still never agent-merge; no GitHub auto-merge queue; no
force-push or protection bypass.

**Status:** confirmed (synced from ai-project-template #115)

**Context:** See `.ai/ideas/implemented/002-self-correcting-auto-merge.md`.

> Reusable workflow rules (for example, documentation before implementation)
> live in the canonical workflow documents under `.ai/`, not in this product
> decision log.

## Architecture decision index

Link full ADRs here when they exist.

| ADR | File | Status |
|---|---|---|
| ADR-0001 | [adr-0001-llm-analysis-layer.md](../architecture/adr-0001-llm-analysis-layer.md) | Accepted |
