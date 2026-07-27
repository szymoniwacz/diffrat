# Dependency Policy

## Purpose

Prevent unnecessary or poorly justified dependencies from entering the project through AI-assisted changes.

## Rules

### Dependency justification

Every new dependency must have a stated reason tied to the current task goal. Prefer existing project libraries or standard library features when sufficient.

### Evaluate before adding

Consider:

- maintenance burden and license
- security track record
- overlap with existing dependencies
- whether the need is temporary or permanent

### Cross-layer risk

Dependencies that affect build, CI, deployment, or runtime need explicit human approval when impact is significant.

### No drive-by upgrades

Do not upgrade unrelated packages in the same branch as a feature or fix unless the task explicitly requires it.

### Document significant additions

Record meaningful dependency choices in `.ai/project/decisions.md` or an ADR when the choice affects architecture.

## Enforcement

Complements `.ai/policies/no-blind-coding.md`. Agents must not add dependencies without justification.

## Related documents

- `.ai/quality/quality-gates.md`
- `.ai/review/diff-risk-checklist.md`
- `.ai/architecture/README.md`
- `.ai/review/human-review-checklist.md`
