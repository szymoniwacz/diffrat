# Task Packets

## Purpose

Task packets define scoped input for one unit of work: goal, boundaries,
validation, and done criteria.

In the default GitHub workflow, the **Agent Goal issue** is the task packet.
Its structured fields replace committed `.ai/packets/task-*.md` files.

## When to use

Use the canonical preparation matrix in
`.ai/quality/definition-of-ready.md` to decide when scoped input is required.

For feature, bugfix, and refactor work, create an **Agent Goal** issue (or
equivalent scoped issue) instead of committing a task packet file.

## Optional file template

`.ai/packets/task-packet.template.md` remains a preparation aid for
`/plan-small-step`, local drafting, or non-GitHub workflows. If you create a
file from it, treat it as scratch only. Do not commit `task-*.md` files to the
PR branch.

## Ready for planning

Scoped input is ready for planning when it includes:

- clear goal,
- bounded scope and explicit non-goals,
- validation plan,
- recorded risks and open questions,
- identified human decision points when needed.

Ready for planning does not require a separate implementation plan file.

## Relationship to other artifacts

| Artifact | Role |
|---|---|
| Agent Goal issue | Default durable scoped input for GitHub workflow |
| Idea (`.ai/ideas/`) | Backlog item; may seed a goal issue |
| Internal plan | Agent working state during the run; not committed |
| PR description | Durable review handoff after implementation |

## Review handoff

The pull request description is the durable review handoff.

Use `.ai/packets/review-packet.template.md` only when a separate review packet
file is helpful outside the PR. Reviewers verify scope against the triggering
issue or brief and the PR diff, not against committed packet or plan files.

## Rule

No blind implementation without the required preparation for the change type.

See `.ai/policies/no-blind-coding.md`.
