# README Contract

## Purpose

Define responsibilities for the root `README.md` so it stays useful without duplicating `.ai/` workflow content.

## README responsibilities

The root README should explain:

- **what the project is** — product or repo purpose
- **who it is for** — audience or users
- **current status** — planning, prototype, MVP, maintenance
- **how to start** — pointer to `.ai/docs/template-flow.md`, not a full workflow copy
- **where context lives** — `.ai/project/`, `.ai/docs/`, ideas backlog
- **license and contact** — when applicable

## When to update root README

Update when:

- project purpose or status changes materially
- onboarding steps for new contributors change
- the repo is no longer a generic template instance (after bootstrap)
- user-facing install or run instructions change

Do not update root README for every internal `.ai/` tweak—only when human-facing project description changes.

## What README must not become

- A duplicate of `.ai/docs/full-workflow.md`
- A second copy of quality gates, policies, or review checklists
- A dump of AI prompts or skills
- Chat history or session notes

## Template vs project README

| Phase | README content |
|---|---|
| Fresh from template | Generic template description (shipped default) |
| After bootstrap | Project-specific description using `.ai/templates/project-readme.md` as a starting point |

## Relationship to other docs

| Document | Role |
|---|---|
| Root `README.md` | Human-facing front door |
| `.ai/README.md` | AI working system overview |
| `.ai/docs/template-flow.md` | How to work in the repo |
| `.ai/onboarding/template-customization-guide.md` | What to customize |

## Rule

If workflow detail is needed, link to `.ai/`—do not paste it into root README.
