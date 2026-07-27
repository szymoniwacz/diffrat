# Diff Risk Checklist

Assess risk from the change surface of the created pull request before human review.

Read and apply this checklist; do not edit it to store results. The PR author
performs the initial assessment after PR creation; if an AI agent created the
PR, that agent performs the initial assessment. The human reviewer independently
verifies the assessment before deciding.

Record the completed result in the PR description or a top-level PR comment. Do
not write the result into a repository review-packet file.

## How to score

- Evaluate every risk signal below.
- Mark every risk signal **Yes**, **No**, or **N/A** internally.
- **Yes always means the risk is present**, regardless of whether it is acceptable.
- Put concrete evidence (paths, hunks, counts) in `Evidence`.
- State the follow-up in `Required action`.

## Risk signals

| Risk signal | Present? (Yes / No / N/A) | Evidence | Required action |
|---|---|---|---|
| Scope expansion beyond the brief, task packet, or plan | | | |
| Architecture boundary, API, or shared-module change | | | |
| Migration or data-model change | | | |
| Cross-layer change (app + infra + docs in one PR) | | | |
| Behavior change without matching test change | | | |
| Documentation drift (behavior/doc mismatch) | | | |
| Security-sensitive change (auth, crypto, permissions, secrets, PII, external calls) | | | |
| Dependency added, removed, or upgraded | | | |
| CI or workflow permission change | | | |
| Rollback is difficult or irreversible | | | |
| High review complexity (hard to follow, mixed concerns) | | | |

## Changed file count (heuristic only)

File count is a signal, not a verdict. It suggests where to look; it does not set
the risk level on its own.

| Files changed | Heuristic |
|---|---|
| 1–5 | usually normal for small tasks |
| 6–15 | verify a single logical change |
| 16+ | expect justification or a split |

**File count alone does not determine risk.** A one-line change to auth can be
High; a large mechanical rename can be Low.

## Risk classification

Classify the change as **Low**, **Medium**, or **High** by weighing:

- impact (blast radius if it goes wrong),
- reversibility (how hard rollback is),
- security exposure,
- data or migration effects,
- architecture boundaries crossed,
- strength of validation evidence.

Guidance:

- **Low** — contained impact, easily reversible, no security or data effects, evidence sufficient.
- **Medium** — behavior change with real impact but bounded and reversible, evidence present.
- **High** — security, data, migration, boundary, or irreversible impact, or weak/missing validation evidence.

## Required output

Record this concise format in the PR description or a top-level PR comment. Only
signals marked present need to appear in `Signals`.

```text
Diff-risk: Low | Medium | High
Signals: None | <comma-separated signals that are present>
Evidence: <specific paths, hunks, or counts>
Reviewer focus: <specific review target>
Required action: None | <human decision, split, or follow-up>
```

Do not include the eleven-row risk signals table in the recorded result; do not
write the result into a repository review-packet file.
