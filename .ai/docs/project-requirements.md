# Project Requirements

## Purpose

This document describes what should be built and why.

It is the main requirements document for AI-assisted planning and implementation.

## Project summary

Describe the project in a few short paragraphs.

Include:

- what the project is
- who it is for
- what problem it solves
- what the first useful version should do

## Users

| User | Needs | Notes |
|---|---|---|
|  |  |  |

## Problems to solve

- 

## Goals

- 

## Non-goals

- 

## Core workflows

Describe the main flows the user should be able to complete.

### Workflow 1 — [Name]

1. 
2. 
3. 

## Functional requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| FR-001 |  | must |  |

## Data and inputs

| Input | Source | Format | Notes |
|---|---|---|---|
|  |  |  |  |

## Outputs

| Output | Consumer | Format | Notes |
|---|---|---|---|
|  |  |  |  |

## Integrations

| Integration | Purpose | Required now? | Notes |
|---|---|---|---|
|  |  |  |  |

## Constraints

- 

## Technical preferences

- 

## Active stack profile

Select one or more active stack profiles for this project and record them here.
Unselected profiles in `.ai/stack-profiles/` remain reusable examples, not active
project rules, and must not be deleted automatically.

| Active profile | Applies to | Notes |
|---|---|---|
| `.ai/stack-profiles/[profile].md` |  |  |

Project-specific commands (build, run, test, lint, typecheck) live in the
selected profile or in the project README. Do not invent commands.

## Quality requirements

- 

## Security and privacy requirements

- 

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
|  |  |  |

## Assumptions

Record assumptions separately from confirmed requirements.

| Assumption | Why it matters | Confirm by |
|---|---|---|
|  |  |  |

## Open questions

- [ ] 

## First useful version

Define the smallest useful version of the project.

## Later versions

Describe what should be deferred.

## Project decision status

Record the status of every area from
`.ai/contracts/project-definition-contract.md`.

Use one status per area: `decided`, `default-accepted`, `deferred`,
`not-applicable`, or `blocking-question`.

Each row must include the required data for that status:

- `decided` — concrete value and link or location
- `default-accepted` — default and explicit human confirmation
- `deferred` — reason and return trigger or owner
- `not-applicable` — short justification
- `blocking-question` — open question that blocks implementation

| Area | Status | Value / notes | Link / location / return trigger |
|---|---|---|---|
| Product purpose |  |  |  |
| Users |  |  |  |
| Outcomes |  |  |  |
| Success criteria |  |  |  |
| First useful version |  |  |  |
| Non-goals |  |  |  |
| Interfaces |  |  |  |
| Inputs and outputs |  |  |  |
| Architecture shape |  |  |  |
| Boundaries |  |  |  |
| Storage and data ownership |  |  |  |
| Retention and migrations |  |  |  |
| Integrations and failure handling |  |  |  |
| Authentication and authorization |  |  |  |
| Secrets, privacy, and sensitive data |  |  |  |
| Language, framework, and dependencies |  |  |  |
| Environments and deployment |  |  |  |
| Configuration |  |  |  |
| Logging, monitoring, and errors |  |  |  |
| Tests, lint, typecheck, performance |  |  |  |
| Scale, reliability, and cost |  |  |  |
| Supported platforms and compatibility |  |  |  |
| Accessibility and localization |  |  |  |
| Compliance, backup, and recovery |  |  |  |
| Branching, CI, release, and rollback |  |  |  |
| License, ownership, and documentation expectations |  |  |  |

## Project readiness

Project readiness is a separate gate from definition coverage.

Record the result after completing `.ai/onboarding/bootstrap-checklist.md`.

| Check | Result | Notes |
|---|---|---|
| Definition coverage complete |  |  |
| No `blocking-question` remains |  |  |
| All `deferred` items have reason and return trigger |  |  |
| Template customization complete |  |  |
| Stack profile selected or marked N/A |  |  |
| Real project commands recorded |  |  |
| Root README describes the product |  |  |
| `AGENTS.md` describes repository role |  |  |
| Bootstrap markers removed |  |  |
| License and ownership decided |  |  |
| CI, branch rules, and approvals decided |  |  |
| Project ready for first product task |  |  |

Product implementation may start only when the final row is confirmed.
