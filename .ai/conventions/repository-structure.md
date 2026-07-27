# Repository Structure

## Purpose

Define where project guidance belongs.

The goal is to make the repository predictable for both humans and coding assistants.

## Folder map

`.ai/docs/template-flow.md` owns the canonical complete folder map. This
convention stays focused on placement rules: which kind of guidance belongs where.

## Rules

### Root and adapters

- `README.md` — human-facing front door
- `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` — thin tool adapters
- `.cursor/rules/` — tool-specific Cursor wrappers
- `examples/` — process-focused examples, not canonical workflow rules

### `.ai/instructions/`

Use for operational workflow rules and documentation editing rules under `.ai/`.
Canonical AI entrypoint is `.ai/README.md`.

### `.ai/project/`

Use for stable project context:

- vision
- product context
- scope
- roadmap
- decisions
- glossary

### `.ai/docs/`

Use for project design documents and lifecycle references.

### `.ai/contracts/`

Use for cross-document contracts such as project definition and README rules.

### `.ai/onboarding/`

Use for bootstrap and template customization guidance.

### `.ai/ideas/`

Use for backlog and feature ideas when the backlog route is helpful.

Ideas are optional when work comes from accepted requirements, bug reports, or
direct scoped requests. See `.ai/quality/definition-of-ready.md`.

### `.ai/packets/`

Use for task and review packets.

### `.ai/plans/`

Use for implementation plans. Plans do not live in `.ai/packets/`.

### `.ai/workflows/`

Use for task-type playbooks.

### `.ai/prompts/`

Use for reusable prompts.

Prompts are user-facing task instructions.

### `.ai/skills/`

Use for reusable working procedures.

Skills describe how to perform a repeatable workflow.

### `.ai/quality/`, `.ai/review/`, `.ai/policies/`, `.ai/git/`

Use for readiness gates, review checklists, guardrails, and Git workflow rules.

### `.ai/automation/`

Use for Cursor Automation operational contracts, production setup guides, and
instruction payloads. Link to canonical lifecycle, policy, quality, review, and
Git documents instead of duplicating them.

### `.ai/conventions/`

Use for rules that should be followed across tasks.

### `.ai/stack-profiles/`, `.ai/templates/`, `.ai/architecture/`

Use for stack guidance, reusable templates, and ADRs.

### `.ai/observability/`, `.ai/metrics/`, `.ai/maintenance/`

Use for session logging, workflow evaluation, and long-term repository health.

### `.github/`

Use for GitHub-specific templates and Copilot instructions.

### `.cursor/`

Use only for Cursor-specific adapter rules.

Do not duplicate full prompts or skills inside `.cursor/`.
