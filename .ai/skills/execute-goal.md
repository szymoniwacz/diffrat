# Skill — Execute Goal

## Command

`/execute-goal`

## Purpose

Carry one authorized goal from analysis through a review-ready pull request.

Invoking `/execute-goal` authorizes branch or worktree creation, scoped changes,
tests, validation, commits, push, final PR creation or update, CI
stabilization, and clear in-scope CI fixes after PR creation.

Autonomous mode is the default. Supervised mode applies only when explicitly
requested. Question timing and authorization details:
`.ai/policies/autonomy-and-authorization.md`.

Canonical lifecycle: `.ai/docs/full-workflow.md`.

## Completion by execution surface

`/execute-goal` names one canonical goal-to-PR lifecycle (Steps below). Direct
or interactive execution targets a review-ready PR through CI stabilization. A
bounded automation slice may stop earlier at an explicit prefix of the same
lifecycle; the current Goal Executor automation implements Slice 2 through
review-ready handoff. Details: `.ai/automation/README.md`.

## Trigger

Run when the user writes `/execute-goal`, or clearly asks for an end-to-end
outcome ready for human review.

## Always read

- `.ai/policies/autonomy-and-authorization.md`
- `.ai/instructions/workflow.md`
- relevant project context and scope
- triggering issue, explicit brief, or accepted requirement

## Read when applicable

- `.ai/policies/multi-agent-orchestration.md` when parallel work may help
- `.ai/onboarding/bootstrap-checklist.md` during bootstrap
- the matching task workflow for the actual change type
- security and dangerous-action policies when relevant
- `.ai/git/branch-and-pr-workflow.md` before commit, push, or PR operations
- `.ai/quality/quality-gates.md` before validation
- `.ai/quality/definition-of-ready.md` when preparing a packet or plan

## Steps

```txt
resolve state
  -> analyze and collect unresolved decisions
  -> prepare only required artifacts
  -> implement and integrate
  -> validate and review
  -> grouped human decision checkpoint when needed
  -> apply answers and rerun affected validation/review
  -> finalize commits
  -> push
  -> create or update PR
  -> CI stabilization
  -> stop before merge
```

Rules:

- clear in-scope fixes are automatic,
- non-blocking questions are deferred into one grouped batch,
- do not finalize the commit set before answers are applied when questions were
  asked,
- continue directly to finalize when no unresolved material questions remain,
- after PR creation, complete CI stabilization per
  `.ai/git/branch-and-pr-workflow.md`; pending or failing applicable CI means
  not review-ready,
- if CI cannot be inspected, report the limitation and do not claim full
  validation.

## Output

Report phase, decisions asked or deferred, validation, commits, PR URL,
CI stabilization result, remaining follow-ups, and confirmation that nothing
was merged.

## Stop conditions

Stop for immediate blockers, dangerous actions requiring prior approval,
unrelated dirty working-tree risk, readiness blocking product behaviour,
supervised early stops, or out-of-scope blockers.
