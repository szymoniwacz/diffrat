# AI Working System

This folder contains the reusable AI working system used by projects created from this template.

It is the main source of truth for AI-assisted project work.

This file is the canonical entry point for AI tools and for work inside `.ai/`.

## Start here

- Goal execution: `/execute-goal` (`.ai/skills/execute-goal.md`). Loading rules
  for that run live in the skill.
- Whole-project automation: create a **Project Execution** issue and authorize
  it with `/execute-project`. Merged delegated pull requests continue
  automatically; use `/continue-project` only when needed. Runtime:
  `.ai/automation/project-executor.md`.
- Project onboarding or human walkthrough: `.ai/docs/template-flow.md`.
- Operational workflow rules: `.ai/instructions/workflow.md`.
- Edits under `.ai/`: `.ai/instructions/docs.md`.

Canonical autonomy policy: `.ai/policies/autonomy-and-authorization.md`.
Full lifecycle order: `.ai/docs/full-workflow.md`.
Cursor Automation contract: `.ai/automation/README.md`.
Goal Executor production setup: `.ai/automation/goal-executor-production-setup.md`.
Multi-agent rules when parallel work may help:
`.ai/policies/multi-agent-orchestration.md`.

## Navigation

Use this reading order. Ignore advanced material until it becomes relevant.

### Core — start a project

| Document | Purpose |
|---|---|
| Root `README.md` | Human-facing front door |
| `.ai/docs/template-flow.md` | How to start and work in the template |
| `.ai/policies/autonomy-and-authorization.md` | Goal-to-PR autonomy and when to ask |
| `.ai/skills/execute-goal.md` | Primary goal entry point |
| `.ai/onboarding/bootstrap-checklist.md` | Bootstrap, customization, and project readiness |
| `.ai/contracts/project-definition-contract.md` | Decision areas, statuses, and readiness rules |

### Core — work on a task

| Document | Purpose |
|---|---|
| `.ai/project/` | Stable project context |
| `.ai/docs/project-requirements.md` | Explicit requirements and decision status |
| `.ai/packets/` or explicit brief | Scoped input for one unit of work |
| `.ai/plans/` | Implementation plan before coding |
| `.ai/quality/definition-of-ready.md` | Ready for planning and implementation-ready gates |
| `.ai/workflows/` | Task-type playbooks |
| `.ai/quality/quality-gates.md` | Required checks before review |
| `.ai/review/` | Independent review, self-review fallback, and handoff |

### Advanced — use when needed

| Document | Purpose |
|---|---|
| `.ai/architecture/` | Architecture decision records |
| `.ai/policies/dangerous-actions.md` | High-risk action controls |
| `.ai/policies/mcp-policy.md` | MCP usage rules |
| `.ai/observability/` | Session logging and traceability |
| `.ai/metrics/` | Workflow evaluation signals |
| `.ai/maintenance/` | Archive and handoff guidance |
| `.ai/stack-profiles/` | Stack-specific deep guidance |

### Tool adapters

| Adapter | Purpose |
|---|---|
| `AGENTS.md` | Root agent entrypoint |
| `CLAUDE.md` | Claude Code adapter |
| `.github/copilot-instructions.md` | GitHub Copilot adapter |
| `.cursor/rules/` | Cursor adapter rules |

## Purpose

The `.ai/` folder stores:

- project context
- design documents
- ideas and backlog
- implementation plans
- prompts
- reusable skills
- conventions
- templates
- review checklists
- task workflows

## Skill commands

Skills are reusable working procedures.

Each skill must define a slash command in its `Command` section.

Available commands:

| Command | Skill | Purpose |
|---|---|---|
| `/execute-goal` | `.ai/skills/execute-goal.md` | Carry one goal through to a review-ready PR |
| `/project-intake` | `.ai/skills/project-intake.md` | Active interview in short rounds; produces the full project context and requirements. |
| `/define-project` | `.ai/skills/define-project.md` | Organizes a supplied rough description and asks only blocking questions; produces the same project context and requirements. |
| `/add-idea` | `.ai/skills/add-idea.md` | Add a new project idea without starting implementation. |
| `/expand-idea` | `.ai/skills/expand-idea.md` | Turn a rough idea into a plan-ready idea. |
| `/plan-small-step` | `.ai/skills/plan-small-step.md` | Create or complete task packet when required, verify ready for planning, create plan, and verify implementation-ready. |

## Project documentation

Use `.ai/project/` for stable project context.

Use `.ai/docs/` for project-specific documents that guide implementation.

Use `.ai/plans/` for scoped implementation plans created before coding.

Use `.ai/architecture/` for architecture decision records (ADRs).
Link significant ADRs from `.ai/project/decisions.md`.

Use `.ai/review/` for independent review (preferred), self-review fallback,
diff-risk, and human review checklists.

Use `.ai/workflows/` for task-type playbooks (bugfix, refactor, test-writing, documentation-update, feature). Skills (`.ai/skills/`) remain slash-command procedures for specific actions.

For new projects, start with `/project-intake` to fill:

- `.ai/project/vision.md`
- `.ai/project/product-context.md`
- `.ai/project/scope.md`
- `.ai/project/roadmap.md`
- `.ai/project/glossary.md`
- `.ai/docs/project-requirements.md`

## Prompt vs skill rule

Prompts are user-facing task starters.

Skills are reusable procedures.

A prompt may call a skill command, but it should not duplicate the full skill procedure.

## Rule

Keep AI workflow materials here.

Keep `.cursor/` as a thin adapter for Cursor-specific rules.

Do not duplicate the same instructions across multiple places.
