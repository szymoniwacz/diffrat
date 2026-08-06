# Glossary

## Purpose

Define project-specific terms so future work uses the same language.

## Terms

### Diffrat

The local CLI product defined in this repository. Formerly named Numbat
(rebrand D-008). PyPI name, CLI command, and import package are all `diffrat`.

### Diff scope

The set of file changes Diffrat analyzes — typically from `git diff` output or
equivalent (staged, unstaged, branch vs base, commit range). Not the entire
repository tree.

### Review report

Structured output describing changes, suggested review focus, and git context.
Default: human-readable terminal text. Optional: JSON via `--json`.

### Git context

Metadata accompanying a diff: branch names, commit messages, authors, files
touched, and coarse categorization (e.g. tests vs source vs config).

### Self-review

A developer running Diffrat on their own changes before push or PR creation.

### Reviewer triage

A reviewer running Diffrat on someone else's diff to prioritize manual review.

### Analysis backend

Component that turns parsed diff + git context into report content. Heuristic
logic always runs; optional LLM backend when `DIFFRAT_LLM_*` is set (D-005).

### Bootstrap

Template customization and project readiness work before the first product
feature goal. Distinct from `/project-intake` definition coverage.

### Agent Goal

A scoped GitHub issue (or equivalent) authorizing one `/execute-goal` lifecycle
to a review-ready PR.

### Working system

The reusable `.ai/` structure from `ai-project-template` that governs how AI
assisted work is planned, reviewed, and handed off.

## Workflow terms (from template)

### Idea

A raw or semi-structured potential change. Not yet an implementation task.

### Decision log entry

A lightweight record in `.ai/project/decisions.md` for confirmed project choices.

### Architecture decision record (ADR)

A fuller decision document in `.ai/architecture/` when the choice needs durable
rationale.

### Quality gate

A check that must pass before work is considered complete (tests, docs, scope,
review handoff).
