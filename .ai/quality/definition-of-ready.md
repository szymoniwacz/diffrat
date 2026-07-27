# Definition of Ready

## Purpose

A task is **ready** when an AI agent or human can start the next allowed step
without guessing scope, goals, validation, or required approvals.

Readiness has two gates:

- **Ready for planning** — authorizes plan creation.
- **Implementation-ready** — authorizes file changes.

Only immediate blockers, required human approvals, and issues necessary for
safe implementation must be resolved before implementation. Non-blocking items
in the Decision queue do not block implementation. See
`.ai/policies/autonomy-and-authorization.md`.

## Canonical preparation matrix

This matrix is the single source of truth for required preparation by change
type. Other documents must link here or restate these values exactly.

Allowed cell values: `required`, `optional`, `not used`, `scope-dependent`.

| Change type | Idea | Brief | Task packet | Plan | Human approval |
|---|---|---|---|---|---|
| Trivial unambiguous edit | not used | required | not used | not used | not used |
| Small meaningful change | optional | scope-dependent | scope-dependent | scope-dependent | not used |
| Feature | optional | not used | required | required | scope-dependent |
| Bugfix | not used | not used | required | required | scope-dependent |
| Refactor | not used | not used | required | required | scope-dependent |
| Test-only change | not used | scope-dependent | scope-dependent | scope-dependent | not used |
| Documentation change | not used | scope-dependent | scope-dependent | scope-dependent | scope-dependent |
| Architecture overhaul, security-posture change, destructive migration, or other high-risk change | not used | not used | required | required | required |

### Matrix notes

- **Idea** is optional when work comes from accepted requirements, a bug report,
  or a direct scoped request.
- **Feature** and **bugfix** always require scoped input (typically an Agent
  Goal issue) and internal planning before implementation.
- **Task packet** means scoped input: an Agent Goal issue, explicit brief, or
  accepted requirement reference. It does not require a committed
  `.ai/packets/task-*.md` file.
- **Plan** means the agent must plan before implementation when the matrix
  requires it. The plan is internal working state; do not commit
  `.ai/plans/plan-*.md` to the PR branch.
- **Brief** may satisfy preparation only where the matrix marks it
  `required` or `scope-dependent`.
- **Plan** is required only where the matrix marks it `required` or where
  `scope-dependent` resolves to required for the actual scope.
- In the **Human approval** column, `required` means recorded human approval
  before `implementation-ready`.
- Approval never substitutes for missing scoped input or internal planning when
  those are required.

### Resolving scope-dependent

- A single obvious one-file change may use a brief instead of a full task packet.
- Multi-file or cross-layer work requires scoped input (typically an Agent Goal
  issue) and internal planning before implementation.
- Routine behavior-preserving refactors and bounded structural cleanup inside
  existing boundaries may proceed without human approval when scope is bounded,
  tests or equivalence checks exist, no important architecture boundary changes,
  and no destructive operation is involved.
- An ordinary feature may include a non-destructive migration when the
  data-model decision is already authorized by that feature.
- Implementing an already approved security design may proceed without a new
  approval.

### Always-required human approval

Recorded human approval before `implementation-ready` is always required for:

- architecture overhauls and large cross-boundary restructuring,
- high-risk, destructive, or irreversible work,
- destructive or irreversible migrations, data-loss risk, applying migrations to
  shared, staging, or production environments, and material data-model decisions
  not already approved,
- changing security or privacy posture, authentication or authorization model,
  secret access, trust boundaries, encryption strategy, or externally visible
  security behaviour.

Security-sensitive changes still require human review before merge. See
`.ai/policies/security-policy.md` and `.ai/policies/dangerous-actions.md`.

## Task input routes

| Route | Typical input | Idea step |
|---|---|---|
| Backlog idea | expanded idea in `.ai/ideas/expanded/` | optional capture step |
| Accepted requirement | requirement ID or accepted scope from `.ai/docs/project-requirements.md` | not used |
| Bug report | reproduction steps and expected behavior | not used |
| Direct scoped request | explicit user brief for a bounded change | not used |

All routes still follow the preparation matrix for the resulting change type.

## Ready for planning

A task input is ready for planning when the active Agent Goal issue, explicit
brief, or accepted requirement includes a clear goal, bounded scope and
non-goals, a validation plan, recorded risks, and a Decision queue for
remaining questions. Non-blocking Decision queue items may remain open.

Ready for planning does **not** require an implementation plan.

### Ready for planning checklist

- [ ] goal is clear
- [ ] context is linked or summarized
- [ ] scope is bounded
- [ ] non-goals are listed
- [ ] validation plan exists
- [ ] risks are noted
- [ ] Decision queue records remaining questions
- [ ] required scoped input exists for the change type (issue, brief, or requirement)

## Implementation-ready

A task is implementation-ready when ready for planning is satisfied, internal
planning is complete when the matrix requires it, required human approvals are
recorded when the Human approval column applies, and stop conditions and
rollback notes exist for multi-step or high-risk work.

When internal planning is complete but required human approval is not yet
recorded, status is `planned, awaiting human approval`. Do not start file
changes until `implementation-ready` is satisfied.

### Implementation-ready checklist

- [ ] ready for planning is satisfied
- [ ] internal planning is complete when the matrix requires it
- [ ] required human approval is recorded before this gate when applicable
- [ ] planned scope matches scoped input goal and non-goals when planning is
  required
- [ ] immediate blockers and issues necessary for safe implementation are resolved

## Not ready

Do not create a plan when ready for planning is not satisfied.

Do not start implementation when the goal is vague, scope is unbounded,
validation is undefined, required scoped input or internal planning is missing
when the matrix requires it, required human approval is missing, or an
immediate blocker or issue necessary for safe implementation remains unresolved.

## Related documents

- `.ai/packets/task-packet.template.md`
- `.ai/policies/no-blind-coding.md`
- `.ai/policies/autonomy-and-authorization.md`
- `.ai/docs/full-workflow.md`
- `.ai/skills/execute-goal.md`
- `.ai/skills/plan-small-step.md`
