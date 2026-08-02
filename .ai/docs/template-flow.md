# Template Flow

## Purpose

This document explains how to start a project from this template.

Keep it simple.
Use it as the first human-readable guide before asking AI to implement anything.

## Default operating model

Prefer `/execute-goal` for one meaningful outcome, or whole-project
automation via a **Project Execution** issue and `/execute-project`. Agents
never merge except under authorized eligible `self-correcting-review auto-merge`.

Canonical rules:

- [`.ai/policies/autonomy-and-authorization.md`](../policies/autonomy-and-authorization.md)
- Full lifecycle order: [`.ai/docs/full-workflow.md`](full-workflow.md)

## Complete walkthrough

This section follows one generic example from zero to merged PR.
Details for gates, checklists, and task types live in linked documents — not here.

**Example:** a local CLI that reviews code diffs, starting with one language.

### At a glance

```txt
new project
  -> questions
  -> context and requirements
  -> project readiness
  -> first task via /execute-goal

new task
  -> /execute-goal with one scoped outcome
  -> agent completes preparation through review-ready PR when authorized
  -> human review and merge (default)
  -> or self-correcting-review: eligible self-verified handoff, human merges
  -> or self-correcting-review auto-merge: eligible self-verified squash merge

whole product (comment- and merge-triggered automation)
  -> Project Execution issue + /execute-project
  -> or /execute-project self-correcting-review (skip CR; you merge)
  -> or /execute-project self-correcting-review auto-merge (skip CR; agent squash-merges when eligible)
  -> Project Executor selects one goal at a time
  -> Goal Executor completes each delegated goal per the automation contract
  -> human review and merge each PR (default / self-correcting-review), or Goal Executor squash-merges when auto-merge eligible
  -> merged PR triggers Project Executor for the next goal until completion criteria pass
```

This walkthrough describes the complete canonical `/execute-goal` lifecycle.
Direct or interactive execution continues through CI stabilization to a
review-ready pull request. Cursor Automation uses a bounded prefix of that
lifecycle; see [`.ai/automation/README.md`](../automation/README.md) for the
current stopping point. Goal Executor Cursor Automation implements Slice 2
through review-ready handoff per
[`.ai/automation/README.md`](../automation/README.md).
Project Executor Cursor Automation selects at most one delegated goal per run
(issue comment or merged delegated pull request) and stops after Goal
Executor review-ready handoff for human merge per
[`.ai/automation/project-executor.md`](../automation/project-executor.md).

### 1. Start a new project

| | |
|---|---|
| **You** | Create a repo from this template. Open it in your AI tool. Run `/project-intake` with a rough description. |
| **AI** | Asks short clarifying rounds (at most 5 questions at once). Skips what you already answered. |
| **AI may ask** | “What is out of scope for v1?” “Local only or CI later?” “Which language first?” |
| **Result** | Updated `.ai/project/*` and `.ai/docs/project-requirements.md`. No application code yet. |
| **You next** | Answer questions. Repeat until definition coverage is complete. |

```txt
/project-intake

I want to build a local CLI that reviews code changes in a repository.
It should analyze diffs, not the whole project at first.
It should work locally first.
Later it may run in CI.
Start with one language. No web UI. No auto-fixes for now.
```

Setup checklist: [`.ai/onboarding/bootstrap-checklist.md`](../onboarding/bootstrap-checklist.md)

### 2. Clarify missing details

| | |
|---|---|
| **You** | Answer only what you know. Say when something is undecided. |
| **AI** | Records facts in project docs. Marks unknowns as assumptions or open questions. |
| **AI may say** | “I will record ‘GitHub Actions later’ as an assumption.” “Open question: rule pack format?” |
| **Result** | Requirements doc lists assumptions and open questions separately from decided facts. |
| **You next** | Resolve blockers before project readiness, or accept documented open questions. |

### 3. Save context and requirements

| | |
|---|---|
| **You** | Confirm the written context matches your intent. Customize template placeholders for the product. |
| **AI** | Updates vision, scope, roadmap, glossary, and requirements. Does not start product code. |
| **Result** | `.ai/project/vision.md`, `product-context.md`, `scope.md`, `roadmap.md`, `glossary.md`, and `.ai/docs/project-requirements.md`. |
| **You next** | Finish definition coverage for every decision area. |

Decision areas and statuses: [`.ai/contracts/project-definition-contract.md`](../contracts/project-definition-contract.md)

### 4. Reach project readiness

| | |
|---|---|
| **You** | Remove bootstrap markers, record real stack and commands, confirm no blockers remain. |
| **AI** | Helps verify checklist items. Stops product implementation until the gate passes. |
| **AI may say** | “The stack profile is not selected yet, and the real test command is still missing.” |
| **Result** | Project readiness gate passed. Repository identity describes the product. |
| **You next** | Start the first product task. |

Gate details: [`.ai/onboarding/bootstrap-checklist.md`](../onboarding/bootstrap-checklist.md)

### 5. Start a task

| | |
|---|---|
| **You** | Pick a task route: backlog idea, accepted requirement, bug report, or direct scoped request. |
| **AI** | Confirms the project is ready. Routes to the right preparation for the change type. |
| **AI may ask** | “Is this from the backlog or an accepted requirement?” “Bug report or small feature?” |
| **Result** | A clear task input. Idea capture is optional when work already comes from requirements, a bug, or a direct request. |
| **You next** | Create required preparation (brief, task packet, and/or plan). |

Task routes and required preparation: [`.ai/quality/definition-of-ready.md`](../quality/definition-of-ready.md)

**Example — backlog idea:**

```txt
/add-idea

Add idea: first language pack for code review rules.
Documentation-only first version. No parser yet.
```

### 6. Choose brief, task packet, and plan

| | |
|---|---|
| **You** | Prefer `/execute-goal` for the full outcome. Use `/plan-small-step` only when you want preparation without implementation. |
| **AI** | Creates a task packet and/or accepts an explicit brief. Produces a plan in `.ai/plans/` when required. Under `/execute-goal`, continues through routine phases without a new prompt between them. |
| **AI may say** | “This feature needs a task packet and plan before coding.” “Trivial doc fix — brief is enough.” |
| **Result** | Ready for planning, then implementation-ready when gates and any required approvals are satisfied. |
| **You next** | For supervised stops, approve the plan scope. Otherwise let `/execute-goal` continue. |

Preparation matrix: [`.ai/quality/definition-of-ready.md`](../quality/definition-of-ready.md)
Primary command: `/execute-goal`
Planning-only command: `/plan-small-step`

```txt
/execute-goal

Create the folder structure and first rule document for the language pack.
Do not implement analysis logic yet.
```

### 7. Questions, assumptions, blockers, and approvals

Question timing belongs to
[`.ai/policies/autonomy-and-authorization.md`](../policies/autonomy-and-authorization.md).
This guide does not own lifecycle order.

| Situation | What happens |
|---|---|
| **Missing detail** | If safe work can continue, AI records it for the Decision queue and keeps going. |
| **Reasonable guess** | AI records an assumption in the packet or plan and states it in the handoff. |
| **Undecided design** | Non-blocking design choices go to the Decision queue; work continues where safe. |
| **Hard blocker** | AI stops only when no safe work remains or prior approval is mandatory. |
| **Risky change** | AI requests explicit approval when the preparation matrix or dangerous-actions policy requires it. See [`.ai/quality/definition-of-ready.md`](../quality/definition-of-ready.md) and [`.ai/policies/dangerous-actions.md`](../policies/dangerous-actions.md). |
| **Incomplete plan** | AI extends or narrows the plan before coding that part. |

### 8. Implement, validate, review, decide, then PR

Under `/execute-goal`, one authorized goal continues through preparation,
implementation, validation, review, the grouped decision checkpoint when needed,
then commits, push, PR, and CI stabilization. Full stage order:
[`.ai/docs/full-workflow.md`](full-workflow.md). Automation completion
boundary: see [At a glance](#at-a-glance) and
[`.ai/automation/README.md`](../automation/README.md).

| | |
|---|---|
| **You** | Prefer `/execute-goal` for the full outcome. Answer the grouped decision batch when asked. |
| **AI** | Changes files within scope. Fixes clear in-scope failures. Prefers independent review; self-review is the fallback. Asks one grouped decision batch after validation and review when material questions remain. Completion boundary: see [At a glance](#at-a-glance). Merges only under authorized eligible `self-correcting-review auto-merge`. |
| **AI may say** | “That request is outside the scope — should I add it as a follow-up idea?” |
| **Result** | PR outcome per [At a glance](#at-a-glance) and the automation contract. |
| **You next** | Human review and merge after review-ready handoff (default / self-correcting-review), or confirm auto-merge when that form was used. |

```txt
/execute-goal

Implement the implementation-ready scope for this task only.
```

Operational rules: [`.ai/instructions/workflow.md`](../instructions/workflow.md)
Quality gates: [`.ai/quality/quality-gates.md`](../quality/quality-gates.md)
Review checklist: [`.ai/review/ai-review-checklist.md`](../review/ai-review-checklist.md)
PR workflow: [`.ai/git/branch-and-pr-workflow.md`](../git/branch-and-pr-workflow.md)

### 8b. Whole-project automation (optional)

Use this when you want to describe the product once and let automation select
goals sequentially. Default and `self-correcting-review` wait for your manual
merges; with `/execute-project self-correcting-review auto-merge`, eligible
delegated PRs are squash-merged by Goal Executor.

| | |
|---|---|
| **You** | Create a **Project Execution** issue. Fill product outcome and completion criteria. Comment exactly `/execute-project`, `/execute-project self-correcting-review`, or `/execute-project self-correcting-review auto-merge`. Configure Project Executor per [`.ai/automation/project-executor-production-setup.md`](../automation/project-executor-production-setup.md). |
| **AI** | Project Executor reads the project issue and repository state, selects at most one next goal, and delegates to Goal Executor. Goal Executor must wait for PR CI (or resume via PR-head CI completion) through review-ready and eligible auto-merge. After merge, PE waits only for default-branch CI; green continues, red repairs first. Project Executor never merges; Goal Executor may squash-merge only under `self-correcting-review auto-merge` when eligible. |
| **Result** | A sequence of pull requests, one scoped goal at a time. Goal Executor stopping point: [`.ai/automation/README.md`](../automation/README.md). |
| **You next** | Default / self-correcting-review: review and merge each PR. Auto-merge eligible: answer material decisions only; draft→ready→merge and green post-merge CI continue automatically. Use `/continue-project` only after material decisions or an unexpected stop. |

Runtime: [`.ai/automation/project-executor.md`](../automation/project-executor.md)

### 9. Human review and merge

| | |
|---|---|
| **You** | Default / self-correcting-review / escalated: review diff, diff-risk note, and checklists; approve, request changes, or reject; merge. `auto-merge` eligible: no CR or merge required. |
| **AI** | Default / self-correcting-review / escalated: does not merge. `self-correcting-review auto-merge` eligible: Goal Executor squash-merges per [`.ai/git/branch-and-pr-workflow.md`](../git/branch-and-pr-workflow.md). |
| **Result** | Work on `main` via human squash merge or authorized `auto-merge` squash merge. |
| **You next** | Start the next scoped task (or let Project Executor continue after merge). |

Checklists: [`.ai/review/human-review-checklist.md`](../review/human-review-checklist.md), [`.ai/review/diff-risk-checklist.md`](../review/diff-risk-checklist.md)

---

**Side paths during task work**

- **Out-of-scope idea mid-task:** AI captures it in `.ai/ideas/` or notes a follow-up; does not expand scope silently.
- **Tests fail:** fix within scope or revise the plan before continuing.
- **No GitHub PR workflow:** review handoff is still required; PR stages are skipped.

More process examples: [`examples/golden-flow/README.md`](../../examples/golden-flow/README.md)

## Main rule

Do not start with code.

Start with project context and readiness.

## Complete folder map

This is the canonical folder map. Other documents should link here instead of
keeping incomplete copies.

### Root and adapters

| Path | Purpose |
|---|---|
| `README.md` | Human-facing front door |
| `AGENTS.md` | Root agent adapter |
| `CLAUDE.md` | Claude Code adapter |
| `LICENSE` | License for the repository |
| `.cursorrules` | Commit-message compatibility layer |
| `.github/` | GitHub templates and Copilot instructions |
| `.github/copilot-instructions.md` | Copilot adapter |
| `.github/pull_request_template.md` | Default product PR template |
| `.github/PULL_REQUEST_TEMPLATE/` | Specialized PR templates |
| `.cursor/rules/` | Cursor adapter rules |
| `examples/` | Process-focused workflow examples |
| `ci/` | Workflow contract validation and fixture tests |

### Product code (Numbat)

| Path | Purpose |
|---|---|
| `pyproject.toml` | Python packaging and tool configuration |
| `src/` | Application source (`src/numbat/`) |
| `tests/` | Product test suite |

### `.ai/` working system

| Path | Purpose |
|---|---|
| `.ai/README.md` | AI working system overview and navigation |
| `.ai/instructions/` | Canonical operational and documentation rules for AI tools |
| `.ai/docs/` | Project-specific and lifecycle documents |
| `.ai/contracts/` | Cross-document contracts |
| `.ai/project/` | Stable project context |
| `.ai/onboarding/` | Bootstrap and customization guidance |
| `.ai/architecture/` | Architecture decision records |
| `.ai/ideas/` | Backlog and idea lifecycle |
| `.ai/packets/` | Task and review packets |
| `.ai/plans/` | Implementation plans |
| `.ai/skills/` | Slash-command procedures |
| `.ai/workflows/` | Task-type playbooks |
| `.ai/prompts/` | Prompt wrappers |
| `.ai/conventions/` | Shared working rules |
| `.ai/stack-profiles/` | Stack-specific guidance |
| `.ai/templates/` | Reusable document templates |
| `.ai/quality/` | Definition of ready, done, and quality gates |
| `.ai/review/` | Self-review, diff-risk, and human review checklists |
| `.ai/policies/` | Guardrail policies |
| `.ai/git/` | Branch and pull request workflow |
| `.ai/automation/` | Cursor Automation contract, Goal Executor and Project Executor setup, and instruction payloads |
| `.ai/observability/` | Session logging specifications |
| `.ai/metrics/` | Workflow evaluation guidance |
| `.ai/maintenance/` | Archive and handoff guidance |

## Commands

| Command | Use when |
|---|---|
| `/execute-goal` | You want one outcome carried through the canonical goal-to-PR lifecycle. See [At a glance](#at-a-glance) for the automation boundary. |
| `/execute-goal self-correcting-review` | Same as `/execute-goal`, plus eligible self-verified handoff (you still merge). |
| `/execute-goal self-correcting-review auto-merge` | Same as self-correcting-review, plus eligible Goal Executor squash merge. |
| `/execute-project` | GitHub comment on a **Project Execution** issue authorizing whole-project automation and starting the first step. Setup: [`.ai/automation/project-executor-production-setup.md`](../automation/project-executor-production-setup.md). |
| `/execute-project self-correcting-review` | Same as `/execute-project`, plus self-correcting mode on delegated goals (you still merge). |
| `/execute-project self-correcting-review auto-merge` | Same as self-correcting-review, plus eligible Goal Executor squash merge on delegated goals. |
| `/continue-project` | Optional GitHub comment on an authorized **Project Execution** issue after material-decision answers or an unexpected stop. Ordinary PR-head CI and post-merge default-branch CI resume via CI/workflow completed triggers. |
| `/project-intake` | Starting a new project and you want AI to ask questions. |
| `/define-project` | You already have a rough description and want AI to organize it. |
| `/add-idea` | You want to add a new idea to the backlog. |
| `/expand-idea` | You want to refine an idea before planning. |
| `/plan-small-step` | You want a task packet and plan prepared without implementing. |

Alternative intake mode: `/define-project` produces the same project artifacts as `/project-intake`.

## Task routes

After project readiness, work may start from:

| Route | When to use |
|---|---|
| Backlog idea | New candidate work that needs refinement in `.ai/ideas/` |
| Accepted requirement | Scoped work already recorded in requirements |
| Bug report | Defect with reproduction and expected behavior |
| Direct scoped request | Small bounded change with explicit brief when allowed |

Required preparation for each route is defined in
[`.ai/quality/definition-of-ready.md`](../quality/definition-of-ready.md).
Task-type playbooks live in [`.ai/workflows/`](../workflows/).
