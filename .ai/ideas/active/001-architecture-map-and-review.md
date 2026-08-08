# Architecture map and review

## Status

active

## Problem

Diff-only review does not answer architectural questions: whether a change
belongs in the right module or layer, whether it breaks boundaries, or whether
it duplicates responsibility that already exists elsewhere in the codebase.

## Goal

Diffrat can evaluate a diff in the context of a repository architecture map
(files, modules, layers, dependencies) and surface what makes the most sense
architecturally — for the whole application or for specific modules.

## Why it matters

Reviewers often catch syntax and local logic issues but miss structural fit.
A lightweight architecture index would let Diffrat compare changes against
known boundaries and dependencies instead of treating each diff in isolation.

## Scope

### Mapping command (fast path)

A dedicated command (e.g. `diffrat map` or `diffrat index` — name TBD) builds
a local index of repository structure:

- File and directory layout
- Module boundaries and package structure
- Import / dependency graph (language-dependent)
- Layer heuristics where applicable (e.g. `src/`, `tests/`, adapters)

The index is stored as a local artifact (e.g. under `.diffrat/` — format TBD)
and can be refreshed on demand (`map --force`) or when the repo changes.

### Review with cached map

`diffrat review` gains a flag or mode that uses the pre-built index to add
architecture-focused hints: misplaced code, boundary violations, suspicious
dependencies, or suggestions to reuse existing modules.

Subsequent reviews are faster because mapping is not repeated.

### Review without prior mapping (slow path)

The same architectural analysis is available without a prior `map` step.
Diffrat builds the index on the fly during review. Output contract matches the
cached path; the user is warned that the run may be slower.

### Output

- Deterministic architecture hints in the text report and `--json` output
- Optional LLM augmentation with architecture context when `DIFFRAT_LLM_*` is
  configured (consistent with ADR-0001)

## Non-goals

- Cross-repository analysis
- Automatic refactoring or directory restructuring
- Replacing dedicated architecture linters (e.g. import-linter) — complement
  review, do not duplicate enforcement tooling
- Changing v1 diff-scoped default behavior (D-001); this is a future phase

## Risks

- Index staleness if cache invalidation is wrong or users forget to refresh
- On-the-fly mapping may be too slow on large repositories without clear UX
- Over-broad heuristics could produce noisy or misleading architecture hints
- Language-specific mapping logic increases maintenance surface

## Open questions

- [ ] What goes into the map: file tree only, import graph, layer heuristics,
      AST summaries, or a combination?
- [ ] Cache format and invalidation strategy (commit SHA, mtime, manual
      `--force`)?
- [ ] Default behavior: require `map` first, or always fall back to on-the-fly
      mapping when no index exists?
- [ ] Integrate with existing Focus/Risk hints vs a separate report section /
      JSON field?
- [ ] Which languages to support first (Python only vs pluggable adapters)?

## Possible next step

Spike: minimal `diffrat map` that writes a file tree plus Python import graph
for one test repository; `diffrat review` reads the cache and emits one
architecture hint (e.g. new code in a layer that imports from a forbidden
direction).
