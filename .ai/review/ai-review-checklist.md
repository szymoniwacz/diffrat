# AI Review Checklist

Agent self-review before handing work to a human.

Validation gates (scope, documentation, test, security, PR) are canonical in
`.ai/quality/quality-gates.md`. Do not repeat them here. This checklist covers
what the agent must do beyond running the gates: read the whole change, surface
what a reviewer cannot see, and prepare a clean handoff.

## Read the full diff

- [ ] every changed hunk was read, not only the files touched most
- [ ] generated, moved, or renamed files were inspected, not assumed
- [ ] nothing unexpected or unrelated is present in the diff

## Assumptions

- [ ] assumptions made during implementation are stated explicitly
- [ ] inputs or context taken on faith (not verified) are called out

## Limitations

- [ ] parts intentionally left incomplete or deferred are listed
- [ ] known weak spots or shortcuts are named, not hidden

## Scope deviations

- [ ] any change beyond the brief, task packet, or plan is flagged
- [ ] deviations are either justified or reverted before handoff

## Validation evidence

- [ ] what was actually checked is recorded (commands, manual steps, results)
- [ ] gates from `.ai/quality/quality-gates.md` that were skipped are noted with reason

## Handoff

- [ ] a reviewer can understand the change without reading the chat
- [ ] the reviewer's attention is pointed at the riskiest parts
- [ ] follow-up tasks are listed

## Where results go

Record self-review output in a review packet created from
`.ai/packets/review-packet.template.md`, a drafted PR description, or temporary
review notes used to prepare the handoff. Do not record results by editing this
or any other canonical checklist file, and do not edit the review-packet
template to store results.
