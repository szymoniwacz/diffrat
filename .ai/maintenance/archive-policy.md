# Archive Policy

## Purpose

Keep the repository maintainable by archiving stale ideas, docs, and decisions without losing history.

## Ideas

Follow `.ai/ideas/README.md` lifecycle:

```txt
active -> expanded -> implemented
        -> archived
```

### Archive an idea when

- rejected after review
- postponed with no planned horizon
- superseded by another idea
- implemented elsewhere and the backlog item is obsolete

### Stale ideas

Review `active/` periodically. If an idea has had no activity for a defined project period (e.g. one quarter), either expand, archive, or explicitly refresh it.

Record reason in the idea file before moving to `archived/`.

## Documents

- Deprecate obsolete docs with a short note at the top pointing to the canonical replacement
- For duplicate docs, identify the canonical source and deprecate the duplicate before removal
- Remove a document only when deletion is explicitly included in the approved task and follows `.ai/policies/dangerous-actions.md`
- Keep ADRs in `.ai/architecture/`; mark obsolete records as `Deprecated` or `Superseded` and link to the replacement when applicable

## Sessions and handoff artifacts

Old session logs under `.ai/observability/sessions/` may be archived according to a documented project retention policy after handoff is complete and related PRs are merged.

Deleting session logs requires explicit approval and must follow `.ai/policies/dangerous-actions.md`.

## What not to archive casually

- `.ai/project/` context still true for the product
- Active conventions and policies in use
- Open task packets for in-progress work

## Related documents

- `.ai/maintenance/ai-handoff-note.template.md`
- `.ai/ideas/README.md`
- `.ai/observability/session-log-spec.md`
- `.ai/policies/dangerous-actions.md`
- `.ai/architecture/README.md`
