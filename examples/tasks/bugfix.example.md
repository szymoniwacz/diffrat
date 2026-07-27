# Example: Bugfix Task

Process-focused example. Not real product code.

Follow `.ai/workflows/bugfix.md`.

## Scenario

Report command crashes when input file is empty. Expected: clear error message, exit code 1.

## 1. Task packet (abbreviated)

**Goal:** Empty input produces a readable error instead of a stack trace.

**Non-goals:** New validation framework, changes to successful path output.

**Scope:** Input validation in report command only.

**Validation:** Reproduce with empty file; add regression test.

## 2. Ready for planning

- reproduction steps and expected behavior are explicit
- scope and non-goals are bounded

## 3. Plan (abbreviated)

**Planned files:**

| File | Change |
|---|---|
| `lib/cli/report_command.rb` | Add empty-input guard |
| `spec/cli/report_command_spec.rb` | Regression test |

## 4. Implementation-ready

- task packet and plan exist
- ready for planning is satisfied

## 5. Implementation discipline

- One file primary change: `lib/cli/report_command.rb`
- Test: `spec/cli/report_command_spec.rb`
- No formatting sweep across `lib/`

## 6. Review handoff (abbreviated)

Review handoff: a review packet or an equivalent PR description. This example
shows both formats; use one.

### Review packet option

**Root cause:** Missing guard for zero-byte input before parser call.

**Assumptions:** Empty file means zero bytes, not whitespace-only content.

**Scope check:** Only error path changed.

**Validation:** New spec `exits 1 with message when input empty` — pass.

**Risks:** None identified; behavior change is intentional for empty input only.

### PR description option

- What: Handle empty input file in report command
- Why: Bug report #42 — crash on empty file
- Assumptions: empty file means zero bytes
- Validation: regression test + manual reproduce steps in PR
- Not included: Broader input validation redesign

## Takeaway

Bugfixes require a task packet and plan, reproduce the failure, fix the smallest cause, and ship a regression test.
