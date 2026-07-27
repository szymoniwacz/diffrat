# Prompt — Review Output

Use this prompt after an assistant or tool changes files, to run independent
review when available or self-review before handoff.

## Prompt

Review, in order:

- the relevant brief, task packet, or plan
- relevant project context and conventions
- the complete diff of the current change
- applicable gates in `.ai/quality/quality-gates.md`
- `.ai/review/ai-review-checklist.md` (apply, do not edit)

Record the results in a review packet created from
`.ai/packets/review-packet.template.md`, a drafted PR description, or temporary
review notes used to prepare the handoff — not in the checklist files, and not
by editing the review-packet template itself.

Diff-risk assessment and human review happen later on the created pull request. See `.ai/review/README.md`.

## Output

```text
Pass/fail summary:
Issues found:
Assumptions:
Limitations:
Scope deviations:
Validation evidence:
Required reviewer focus:
Recommended fixes:
Follow-up tasks:
Next safe step:
```
