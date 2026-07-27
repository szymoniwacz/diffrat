# Full Workflow

## Purpose

This document describes the complete AI-assisted development flow for projects built from this template.

It is the detailed workflow lifecycle reference. AI tools start from `.ai/README.md`. Concise operational rules live in `.ai/instructions/workflow.md`. Autonomy, authorization, and human decision boundaries live in `.ai/policies/autonomy-and-authorization.md`. This document expands the lifecycle stages, artifacts, gates, and handoff points.

## Relationship with other workflow documents

| Document | Role |
|---|---|
| `.ai/README.md` | Canonical AI instruction entrypoint |
| `.ai/instructions/workflow.md` | Concise operational workflow instructions for AI tools |
| `.ai/policies/autonomy-and-authorization.md` | Autonomous versus supervised mode and outcome authorization |
| `.ai/policies/multi-agent-orchestration.md` | Tool-agnostic multi-agent decomposition, isolation, and integration |
| `.ai/skills/execute-goal.md` | Primary goal-to-PR entry point |
| `.ai/docs/template-flow.md` | Short getting-started guide |
| `.ai/docs/full-workflow.md` | Detailed lifecycle/process reference with stages, inputs, outputs, and gates |
| `.ai/workflows/feature.md` | Feature playbook within this lifecycle |
| `.ai/workflows/README.md` | Task-type playbooks (bugfix, refactor, test-writing, documentation-update) that run within this lifecycle |

Use `template-flow.md` when onboarding or explaining the basics.

Use `full-workflow.md` when defining what must happen at each stage, what artifacts are required, and what gates apply.

Task workflows in `.ai/workflows/` operate within this canonical lifecycle. They guide task-type-specific steps but do not replace scoped input, internal planning, quality gates, or review artifacts.

## Workflow overview

```txt
authorized goal
  -> analyze and collect unresolved decisions
  -> prepare only what is required
  -> implement and integrate
  -> validate and review
  -> grouped human decision checkpoint when needed
  -> apply answers and rerun affected validation/review
  -> finalize commits
  -> push
  -> create or update PR
  -> CI stabilization
  -> diff-risk assessment
  -> human review
  -> manual human merge
```

This document owns the full lifecycle order. Other docs may summarize and link
here; they must not duplicate this block.

Implementation may use parallel independent workstreams when useful. See
`.ai/policies/multi-agent-orchestration.md`.

Task input may come from an optional idea, accepted requirements, a bug report,
or a direct scoped request. Idea capture is not required for every task.

Primary command: `/execute-goal`. Modes, authorization, and question timing:
`.ai/policies/autonomy-and-authorization.md`.

The pull request is normally the main human review boundary. CI stabilization,
diff-risk assessment, human review, and manual merge stages apply when using
the GitHub PR workflow. Otherwise, review handoff is the final required handoff
artifact.

A pull request is not review-ready while applicable CI is pending or failing.
Procedure: `.ai/git/branch-and-pr-workflow.md`.

Agents must never merge pull requests.

## Stages

### 1. Project context

**Goal:** Establish stable project identity and boundaries.

**Primary location:** `.ai/project/`

**Typical inputs:** rough product description, constraints, known decisions

**Typical outputs:** updated `vision.md`, `product-context.md`, `scope.md`, `roadmap.md`, `glossary.md`

**Gate:** context is readable without chat history before meaningful implementation starts

**Commands:** `/project-intake`, `/define-project`

---

### 2. Requirements

**Goal:** Turn context into explicit requirements for planning and implementation.

**Primary location:** `.ai/docs/project-requirements.md` and related design docs

**Typical inputs:** project context, stakeholder goals, constraints

**Typical outputs:** requirements document with goals, non-goals, assumptions, open questions

**Gate:** requirements are specific enough to scope an Agent Goal issue or brief

---

### 2b. Readiness-safe bootstrap

**Goal:** Complete remaining project-readiness work without implementing product behaviour.

**Typical inputs:** completed definition coverage, customization guide, stack decisions

**Typical outputs:** customized repository identity, stack profile, packaging-only scaffold when needed, real commands, readiness status updates, bootstrap pull request

**Gate:** project readiness passes before product behaviour starts

**Rule:** after definition coverage, `/execute-goal` may autonomously complete all remaining readiness-safe work when that outcome is authorized. Do not require a separate prompt for each readiness artifact.

---

### 3. Idea (optional)

**Goal:** Capture a candidate piece of work without starting implementation.

**Primary location:** `.ai/ideas/active/`

**Typical inputs:** feature request, improvement note

**Typical outputs:** idea file with problem, rough goal, and initial scope notes

**Gate:** idea is recorded and linked to project context when this route is used

**Command:** `/add-idea`

**Rule:** skip this stage when work comes from accepted requirements, a bug
report, or a direct scoped request.

---

### 3b. Bug report or direct task input (optional)

**Goal:** Start scoped work without creating a backlog idea first.

**Typical inputs:** bug report, accepted requirement, explicit scoped request

**Typical outputs:** Agent Goal issue or explicit brief according to the preparation matrix

**Gate:** input is bounded enough to satisfy ready for planning when required

---

### 4. Scoped input

**Goal:** Define one scoped unit of AI-assisted work with explicit boundaries.

**Primary location:** Agent Goal issue fields, or an explicit brief when the
preparation matrix allows it

**Typical inputs:** expanded idea, accepted requirement, bug report, or explicit user request

**Typical outputs:** goal, non-goals, scope, validation plan, and done criteria recorded in the issue or brief

**Gate:** ready for planning is satisfied (see `.ai/quality/definition-of-ready.md`)

**Rule:** required preparation depends on change type. See
`.ai/quality/definition-of-ready.md`. Trivial unambiguous edits may use an
explicit brief. Feature, bugfix, and multi-file work require scoped input
(typically an Agent Goal issue) before planning. Under `/execute-goal`, the
agent creates or uses the required scoped input as part of the same authorized
goal.

---

### 5. Implementation plan

**Goal:** Break scoped input into a concrete, reviewable set of steps.

**Primary location:** internal agent working state during the run; optional
structure from `.ai/plans/implementation-plan.template.md`

**Typical inputs:** brief or Agent Goal issue

**Typical outputs:** planned files, steps, validation, rollback notes, and stop conditions

**Gate:** plan scope matches the issue or brief; non-goals are explicit

**Commands:** `/execute-goal`, `/plan-small-step`

**Rule:** plan creation does not automatically require human approval. In
autonomous mode, defer unresolved material decisions to the grouped human
decision checkpoint. Ask earlier only for immediate blockers defined in
`.ai/policies/autonomy-and-authorization.md` or when the preparation matrix
requires prior approval for the risk class. Supervised mode follows the
user-requested stop points.

---

### 5b. Implementation-ready gate

**Goal:** Confirm the task may start changing files.

**Typical inputs:** scoped input, internal plan when required, recorded approvals when required

**Typical outputs:** confirmation that implementation-ready is satisfied

**Gate:** implementation-ready is satisfied (see `.ai/quality/definition-of-ready.md`)

---

### 6. Scoped implementation

**Goal:** Make only the changes described in the plan or authorized goal.

**Typical inputs:** internal plan and relevant context files

**Typical outputs:** code, configuration, or documentation changes within scope

**Gate:** no unrelated changes; no blind coding (see `.ai/policies/no-blind-coding.md`)

**Rule:** one logical change per branch when using git. In autonomous mode,
continue through all in-scope steps for the goal rather than stopping after the
first file change.

---

### 7. Quality gates

**Goal:** Verify the change meets project expectations before review.

**Primary location:** `.ai/quality/quality-gates.md`

**Typical inputs:** changed files, validation plan from scoped input

**Typical outputs:** evidence that applicable gates were considered or executed

**Gate:** applicable universal, documentation, code, test, security, and PR gates are addressed

**Rule:** automatically fix in-scope failures caused by this work and rerun
validation. Do not stop after the first failing test merely to ask whether to
fix it.

---

### 8. Independent review when available, otherwise self-review

**Goal:** Review the integrated result before the grouped decision checkpoint or
finalization.

**Primary location:** `.ai/review/ai-review-checklist.md`

**Typical inputs:** full diff, validation evidence, triggering issue, brief, or internal plan notes

**Typical outputs:** stated assumptions, limitations, scope deviations,
validation evidence, and unresolved material items for the decision queue

**Gate:** the integrated diff was reviewed and the handoff is understandable without chat history

**Rules:**

- Prefer an independent review agent when available; otherwise self-review.
- Resolve in-scope review findings, rerun affected validation, and repeat review
  when necessary.
- Feed unresolved material questions, architecture choices, correctness concerns,
  and best-practice suggestions into the grouped decision checkpoint. See
  `.ai/policies/autonomy-and-authorization.md`.
- Read and apply the checklist; do not edit the checklist file to record results.

---

### 9. Grouped human decision checkpoint

**Goal:** Ask one concise batch of remaining non-blocking material questions
after independent implementation, validation, and review are complete.

**Primary location:** issue comments, internal plan notes, temporary review notes,
or PR handoff draft

**Typical inputs:** deferred decisions collected during analysis, implementation,
validation, and review

**Typical outputs:** user answers, recorded deferred follow-ups or accepted risks

**Gate:** remaining material questions are answered, deferred, or accepted as risk

**Rule:** skip this stage when no unresolved material questions remain. Ask
earlier only for immediate blockers per the autonomy policy.

---

### 10. Apply answers and rerun

**Goal:** Incorporate human answers before finalization.

**Typical outputs:** updated scoped input notes, code, tests, and docs; rerun
validation; repeated review when needed

**Gate:** affected validation passes and review is current

---

### 11. Review handoff

**Goal:** Summarize what changed and what a human reviewer should focus on, as either a review packet or a drafted PR description carrying equivalent information.

**Primary location:** `.ai/packets/` (use `review-packet.template.md`), or a drafted PR description with equivalent structure

**Typical inputs:** implementation result, validation notes, review findings, decision outcomes

**Typical outputs:** a review packet or a drafted PR description with summary, scope check, risks, limitations, follow-ups; a separate review-packet file is optional

**Gate:** reviewer can understand the change without reading the full chat

**Rule:** The durable scoped input is the triggering GitHub issue, an explicit
brief, or an accepted requirement reference. An implementation plan is agent
working state during the run, not a committed repository artifact. The pull
request description is the durable review handoff. Do not commit
`.ai/packets/task-*.md` or `.ai/plans/plan-*.md` files to the PR branch.
Record lasting decisions only in canonical project documentation or ADRs.
Optional templates in `.ai/packets/` and `.ai/plans/` may help preparation but
are not review sources of truth.

---

### 12. Commit, push, and pull request

**Goal:** Present the change for human review in version control.

**Detailed procedure:** `.ai/git/branch-and-pr-workflow.md`

**Typical inputs:** branch with scoped commits, plus the review handoff (a review packet or drafted PR description)

**Typical outputs:** intentional commits, pushed branch, pull request with description of what changed, why, and how it was validated

**Gate:** PR exists; description includes validation and dependency notes

**Rule:** when the authorized outcome is a review-ready pull request, commit,
push, and PR creation are allowed without additional confirmation. Agents may
create branches and PRs; agents must not merge PRs. Creating the PR alone does
not make the task review-ready; CI stabilization must still pass.

---

### 13. CI stabilization

**Goal:** Make the remote pull request attribution-clean and CI-green before
claiming it is ready for human review.

**Detailed procedure:** `.ai/git/branch-and-pr-workflow.md`

**Typical inputs:** pushed branch, open pull request, configured CI checks

**Typical outputs:** attribution-clean remote commits and PR metadata; passing
applicable CI; or an explicit inspectability or published-history blocker

**Gate:** all applicable CI checks pass; pending or failing applicable CI means
the PR is not review-ready

---

### 14. Diff-risk assessment

**Goal:** Assess the risk of the change from its diff before human review.

**Primary location:** `.ai/review/diff-risk-checklist.md`

**Typical inputs:** PR diff, changed file count, affected layers

**Typical outputs:** a low/medium/high risk note recorded in the PR description or a PR comment

**Gate:** risk level and its drivers are explicit for the reviewer

---

### 15. Human review

**Goal:** A human independently verifies scope, quality, risk, and fit with project direction.

**Primary location:** `.ai/review/human-review-checklist.md`

**Typical inputs:** PR diff, PR description or review packet, diff-risk note,
triggering issue or explicit brief, related canonical docs

**Typical outputs:** an explicit decision — Approve, Request changes, or Reject — per `.ai/review/human-review-checklist.md`: non-authors may record through a GitHub PR review; solo authors record Approve by manually merging the reviewed remote head; Request changes or Reject require a top-level PR comment with the reviewed head SHA

**Gate:** reviewer confirms scope, documentation, and applicable quality gates

**Rule:** read and apply the checklist; do not edit the checklist file to record results

---

### 16. Manual merge

**Goal:** Integrate approved work into the main line under human control.

**Typical inputs:** approved PR

**Typical outputs:** merged commit on `main`

**Rule:** only humans merge. No direct push to `main` by agents.

## Artifact map

The "Checklist or procedure" column is the reusable input applied at a stage. The "Recorded result" column is where that stage's actual output is stored. Checklist files are procedures, never recorded results.

| Stage | Checklist or procedure | Recorded result |
|---|---|---|
| Context | `/project-intake`, `/define-project` | `.ai/project/*` |
| Requirements | — | `.ai/docs/project-requirements.md` |
| Readiness-safe bootstrap | `/execute-goal`, bootstrap checklist | customized docs, stack profile, readiness table, bootstrap PR |
| Idea | `/add-idea` | `.ai/ideas/active/*` |
| Scoped input | Agent Goal issue, explicit brief, or accepted requirement | issue fields, brief text, or requirement reference |
| Plan | internal agent working state during the run | not committed; optional scratch from `.ai/plans/implementation-plan.template.md` |
| Implementation | `/execute-goal` or task workflow | code/docs changes on a branch |
| Quality gates | `.ai/quality/quality-gates.md` | validation notes, test/lint results |
| Independent review when available, otherwise self-review | `.ai/review/ai-review-checklist.md` | review notes, decision-queue items, and handoff inputs |
| Grouped decision checkpoint | autonomy policy | answers, deferred follow-ups, accepted risks |
| Apply answers and rerun | autonomy policy | updated artifacts and validation evidence |
| Review handoff | PR description or `.ai/packets/review-packet.template.md` structure | drafted PR description; separate review-packet file optional |
| Commit / push / PR | `.ai/git/branch-and-pr-workflow.md` | commits, remote branch, GitHub pull request |
| CI stabilization | `.ai/git/branch-and-pr-workflow.md` | green applicable CI, clean remote attribution, or documented inspectability limit |
| Diff-risk assessment | `.ai/review/diff-risk-checklist.md` | PR description or top-level PR comment |
| Human review | `.ai/review/human-review-checklist.md` | GitHub PR review, solo-author merge for Approve, or top-level PR comment for Request changes or Reject |
| Merge | — | human-approved merge to `main` |

## Resumability

Resume from repository evidence, not chat history:

- project phase from definition coverage and project readiness,
- active task from the triggering issue, brief, or branch and PR state,
- planning completeness from agent working state or issue comments,
- branch, commit, and PR state from git and GitHub.

See `.ai/policies/autonomy-and-authorization.md`.

## Lifecycle invariants

These invariants summarize constraints that span the lifecycle. Operational instructions for AI tools live in `.ai/instructions/workflow.md`.

1. `.ai/` is the source of truth.
2. Start with context, not code.
3. Required preparation for the task type must exist before planning or implementation.
4. Autonomous mode continues through routine phases; deferred decisions wait for
   the grouped checkpoint; immediate blockers still stop early.
5. Preserve context in files, not only in conversations.
6. The pull request is the normal review boundary; humans merge.

## What this document does not cover

- Tool-specific adapter configuration (see root adapters and `.cursor/`, `.github/`)
- Stack-specific commands (add via stack profiles when needed)
- Detailed review checklists (see `.ai/review/`)
- Detailed autonomy and authorization rules (see `.ai/policies/autonomy-and-authorization.md`)
