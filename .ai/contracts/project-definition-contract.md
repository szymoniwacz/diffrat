# Project Definition Contract

## Purpose

This contract defines the decision areas, status model, and completion gates
for project definition before implementation starts.

It is the canonical source for what must be considered, resolved, deferred,
or marked not applicable during `/project-intake` and `/define-project`.

Skills and onboarding documents should reference this contract instead of
duplicating the full decision-area list.

## When to use

Apply this contract during:

- `/project-intake`
- `/define-project`
- bootstrap definition-coverage checks
- bootstrap project-readiness checks

## Two gates

Project definition uses two separate gates. Do not merge them.

### Definition coverage

Definition coverage is complete when:

- every decision area has an explicit status,
- no area remains implicitly unset,
- each status includes the required data defined below,
- project context and requirements documents are filled honestly.

Definition coverage does not authorize product implementation by itself.

### Project readiness

Project readiness is complete when definition coverage is complete and all of
the following are true:

- no `blocking-question` remains anywhere in the decision-status table,
- every `deferred` item has a reason and return trigger or owner,
- every `default-accepted` item records the default and explicit human
  confirmation,
- template customization is complete,
- active stack profile is selected or marked `not-applicable`,
- real project commands are recorded,
- root README describes the product, not the template,
- `AGENTS.md` describes the actual repository role,
- required bootstrap markers are removed,
- license, ownership, CI, branch rules, and required approvals are decided
  or marked `not-applicable`.

Product implementation may start only after project readiness passes.

## Readiness check rows

The project readiness table in `.ai/docs/project-requirements.md` must include
exactly these checks:

| Check |
|---|
| Definition coverage complete |
| No `blocking-question` remains |
| All `deferred` items have reason and return trigger |
| Template customization complete |
| Stack profile selected or marked N/A |
| Real project commands recorded |
| Root README describes the product |
| `AGENTS.md` describes repository role |
| Bootstrap markers removed |
| License and ownership decided |
| CI, branch rules, and approvals decided |
| Project ready for first product task |

## Decision statuses

Every decision area must use exactly one status.

Unknown is acceptable only when explicitly classified. Do not leave areas
implicitly unset.

| Status | Meaning | Required data |
|---|---|---|
| `decided` | A confirmed choice is recorded | Concrete value and location or link to where it is recorded |
| `default-accepted` | A template or project default applies | Concrete default and explicit human confirmation, at least grouped |
| `deferred` | Explicitly postponed | Reason, return trigger or owner, and confirmation that it does not block the active first task |
| `not-applicable` | The area does not apply to this project | Short justification |
| `blocking-question` | Cannot proceed safely until a human answers | Open question that must be resolved before implementation |

Rules:

- `blocking-question` always blocks implementation. It cannot be accepted as a
  blocker and still allow work to start.
- `deferred` is valid only when the reason and return trigger are recorded.
- `default-accepted` is valid only when the default and human confirmation
  are recorded.

## Decision areas

| Area | What to establish |
|---|---|
| Product purpose | Why the project exists and what problem it solves |
| Users | Primary users, beneficiaries, and usage context |
| Outcomes | What should become easier, safer, clearer, or more repeatable |
| Success criteria | Measurable MVP result and acceptance criteria for the first version |
| First useful version | Smallest version that delivers real value |
| Non-goals | What is explicitly out of scope for now |
| Interfaces | CLI, API, UI, files, events, or other external surfaces |
| Inputs and outputs | Data, commands, files, or events in and out of the system |
| Architecture shape | Major components, boundaries, and interaction style |
| Boundaries | What the system owns versus what it delegates or integrates |
| Storage and data ownership | Where data lives and who owns it |
| Retention and migrations | How long data is kept and how schema or format changes are handled |
| Integrations and failure handling | External systems, retries, timeouts, and degraded behavior |
| Authentication and authorization | Who may access what and how access is enforced |
| Secrets, privacy, and sensitive data | Credentials, PII, and handling rules |
| Language, framework, and dependencies | Primary stack choices and dependency posture |
| Environments and deployment | Local, staging, production, and release targets |
| Configuration | Environment variables, config files, and secrets management |
| Logging, monitoring, and errors | Observability expectations and failure visibility |
| Tests, lint, typecheck, performance | Quality commands and minimum expectations |
| Scale, reliability, and cost | Expected volume, latency, budget, and acceptable data loss |
| Supported platforms and compatibility | Systems, runtimes, browsers, devices, formats, and versions supported at start |
| Accessibility and localization | Accessibility expectations and languages when relevant |
| Compliance, backup, and recovery | Legal or policy requirements, backup, restore, and disaster recovery when data persists |
| Branching, CI, release, and rollback | Git workflow, automation, and rollback approach |
| License, ownership, and documentation expectations | Legal posture, maintainership, and doc obligations |

## Recording decisions

Record confirmed meaningful choices in:

- `.ai/project/decisions.md` for lightweight decisions and ADR links
- `.ai/architecture/` ADRs when the choice needs fuller rationale

Record area statuses in `.ai/docs/project-requirements.md` using the
decision-status table defined there.

Record assumptions in `.ai/docs/project-requirements.md` separately from
confirmed requirements.

## Gate ownership

| Document | Responsibility |
|---|---|
| `project-definition-contract.md` | Decision areas, statuses, and gate rules |
| `project-requirements.md` | Project-specific statuses, values, assumptions, and links |
| `project-intake.md` / `define-project.md` | How information is collected |
| `bootstrap-checklist.md` | Customization execution and final readiness check |
| `template-customization-guide.md` | What to customize and what to leave intact |

## Related documents

- `.ai/skills/project-intake.md`
- `.ai/skills/define-project.md`
- `.ai/docs/project-requirements.md`
- `.ai/onboarding/bootstrap-checklist.md`
- `.ai/onboarding/template-customization-guide.md`
