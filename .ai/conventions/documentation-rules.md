# Documentation Rules

## Core rule

Documentation is part of the work.

## Update documentation when a change affects

- project purpose
- scope
- architecture
- inputs or outputs
- workflow
- quality gates
- assumptions
- decisions

## Rules

1. One document should have one clear purpose.
2. Keep important context in stable files, not only in prompts.
3. Keep documentation concise.
4. Prefer explicit rules over hidden assumptions.
5. If a decision changes, update `.ai/project/decisions.md`.
6. If scope changes, update `.ai/project/scope.md`.
7. If workflow changes, update `.ai/instructions/workflow.md` and/or
   `.ai/docs/full-workflow.md` depending on the kind of change. Update
   `.ai/conventions/ai-working-mode.md` only when working-mode conventions change.

## Definition of done

A task is complete only when the related documentation is still true.
