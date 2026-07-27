# Architecture Decisions

## Purpose

This folder is the home for architecture decision records (ADRs) in projects built from this template.

ADRs capture significant technical choices, alternatives considered, and consequences so future work does not depend on chat history.

## When to write a full ADR

Create an ADR when a decision:

- affects system structure or boundaries,
- is hard to reverse,
- involves meaningful trade-offs,
- should guide future AI-assisted implementation.

Save it as `.ai/architecture/adr-NNNN-short-slug.md`.

## When `.ai/project/decisions.md` is enough

Use `.ai/project/decisions.md` for lightweight notes when a decision:

- is low-risk and easy to reverse,
- does not affect system structure,
- can be described in a few lines without alternatives on record.

## Linking decisions

When a full ADR exists, add a reference to it from `.ai/project/decisions.md`.
This keeps the decision log complete without duplicating the full record.

## How to create an ADR

1. Copy `.ai/architecture/adr.template.md`.
2. Save as `.ai/architecture/adr-NNNN-short-slug.md` (increment number).
3. Fill every section before treating the decision as `Accepted`.
4. A decision must not move to `Accepted` without explicit human approval.

## Relationship to other documents

| Document | Role |
|---|---|
| `.ai/project/decisions.md` | Lightweight decision log and ADR index |
| `.ai/architecture/adr-*.md` | Full architecture decision records |
| `.ai/architecture/adr.template.md` | Canonical ADR template |
| `.ai/docs/architecture-direction.md` | High-level architecture guidance for the project |

## Rule

Architecture changes without an explicit decision should not be implemented.
See `.ai/policies/no-blind-coding.md`.
