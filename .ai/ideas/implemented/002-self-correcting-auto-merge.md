# Self-correcting auto-merge

## Status

implemented

## Problem

Self-correcting review mode (idea 001) skipped human CR for eligible work but
still required a human to merge. Folding merge into the same
`self-correcting-review` comment mixed “skip CR” with “agent merges” and made
the safer opt-in harder to choose deliberately.

## Goal

Add an explicit optional suffix `auto-merge` so owners can authorize squash
merge separately:

- `/execute-goal self-correcting-review` — skip human CR when eligible; human
  merges
- `/execute-goal self-correcting-review auto-merge` — same + Goal Executor
  squash-merges when eligible
- `/execute-project self-correcting-review` — same CR-skip for delegated goals;
  human merges
- `/execute-project self-correcting-review auto-merge` — same + Goal Executor
  squash-merges eligible delegated PRs

Keep material-decision, dangerous-action, and high/security-sensitive stops.
Default `/execute-goal` / `/execute-project` still stop before merge.

## Scope

Documentation and policy only:

- Autonomy policy: separate self-correcting vs `auto-merge` authorization
- Self-correcting loop, Done, execute-goal, full workflow, git PR procedure
- Goal Executor / Project Executor runtimes, comment-filter regexes, production
  setup
- Issue templates, adapters, and idea/decision memory

## Non-goals

- GitHub auto-merge queue enablement
- Force push, history rewrite, or branch-protection bypass
- Relaxing material / dangerous / high-risk stops
- Changing default-mode behavior
- Making bare `self-correcting-review` merge by itself

## Supersedes

Idea 001 open question “Human merge still mandatory in v1; auto-merge out of
scope” — superseded by this optional `auto-merge` flag.

## Related

- `.ai/policies/autonomy-and-authorization.md`
- `.ai/git/branch-and-pr-workflow.md` (Authorized self-correcting merge)
- `.ai/review/self-correcting-review-loop.md`
- `.ai/automation/goal-executor.md`
- `.ai/automation/project-executor.md`
