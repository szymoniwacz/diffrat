# Review

## Purpose

Review checklists make independent review and human review focus explicit.

They fit into the canonical lifecycle in `.ai/docs/full-workflow.md` after
quality gates and before the grouped decision checkpoint and PR handoff.

Prefer an independent review agent when available. Self-review is the fallback.

Review handoff means a review packet created from
`.ai/packets/review-packet.template.md`, or an equivalent drafted PR description.

## Checklists

| Checklist | Audience | Use when |
|---|---|---|
| [ai-review-checklist.md](ai-review-checklist.md) | Independent review agent or self-review | After quality gates, before the decision checkpoint or handoff |
| [diff-risk-checklist.md](diff-risk-checklist.md) | Both | Assessing change risk from the diff before human review |
| [self-correcting-review-loop.md](self-correcting-review-loop.md) | Agent | Opt-in self-correcting review mode only |
| [human-review-checklist.md](human-review-checklist.md) | Human reviewer | Reviewing an existing pull request |

## How to use

1. Complete implementation and address applicable quality gates.
2. Prefer an independent review agent; otherwise self-review with
   `.ai/review/ai-review-checklist.md` on the full diff.
3. Feed unresolved material questions into the Decision queue for the grouped
   checkpoint. See `.ai/policies/autonomy-and-authorization.md`.
4. Record findings in a review packet, drafted PR description, or temporary
   review notes used to prepare the handoff.
5. When using the GitHub PR workflow, create or update the pull request after
   answers are applied and affected validation and review are current.
6. When using the GitHub PR workflow, assess risk with
   `.ai/review/diff-risk-checklist.md` and record the result in the PR
   description or a top-level PR comment.
7. When using the GitHub PR workflow, the human reviewer applies
   `.ai/review/human-review-checklist.md` and concludes with Approve, Request
   changes, or Reject.
8. When using the GitHub PR workflow, a human merges the approved PR. Agents
   never merge.

The review packet is supporting input for human review, not an alternative
review surface. Post-PR review results are not written back into the repository
review packet.

Checklists are read and applied, not edited. Do not record results by editing
the checklist files or the review-packet template.

## Relationship to other documents

| Document | Role |
|---|---|
| `.ai/quality/quality-gates.md` | Canonical validation gates (not repeated here) |
| `.ai/packets/review-packet.template.md` | Structured summary of the change |
| `.ai/prompts/04-review-output.md` | Thin prompt wrapper for review output |
| `.ai/docs/full-workflow.md` | Where review fits in the lifecycle |
| `.ai/policies/autonomy-and-authorization.md` | Question timing and decision checkpoint |

## Terminology

- **Independent review** — preferred review of the integrated diff by a separate agent when available
- **Self-review** — fallback when no independent review agent is available
- **Review handoff** — review packet or equivalent PR description
- **Human review** — independent human review before merge when using the PR workflow
- **Approval** — explicit human authorization before controlled or structural changes

## Rule

Independent review when available, otherwise self-review, and review handoff are
required before continuing to the next task. Human review is required before
merge when using the GitHub PR workflow, unless self-correcting review mode is
authorized and eligible. See `.ai/docs/full-workflow.md`. Agents never merge.
