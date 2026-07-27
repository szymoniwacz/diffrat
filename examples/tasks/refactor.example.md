# Example: Refactor Task

Process-focused example. Not real product code.

Follow `.ai/workflows/refactor.md`.

## Scenario

Extract report formatting from `ReportCommand` into a dedicated serializer class. Behavior must not change.

## 1. Task packet (abbreviated)

**Goal:** Move formatting logic out of CLI command for maintainability.

**Non-goals:** Behavior changes, new output formats, renaming public API.

**Scope:** `lib/cli/report_command.rb` and new `lib/report/serializer.rb`.

**Validation:** Existing test suite must pass unchanged; compare sample output before/after.

## 2. Ready for planning

- goal, scope, non-goals, and validation are explicit

## 3. Plan (abbreviated)

**Steps:**

1. Create `Report::Serializer` with same output as inline code.
2. Delegate from command to serializer.
3. Run full spec suite.
4. Compare golden sample output file.

**Rollback:** Revert single commit if output differs.

**Stop conditions:** If tests need behavior changes, stop—split into bugfix task.

## 4. Approval decision

Approval not required: behavior is preserved, scope is bounded, equivalence checks exist, no important architecture boundary changes, and no destructive operation is involved.

## 5. Implementation-ready

- task packet exists in `.ai/packets/`
- plan exists in `.ai/plans/`
- scope-dependent approval resolved before this gate

## 6. Implementation discipline

- Mechanical move only
- No "while I'm here" cleanup in other commands
- One logical commit on branch `refactor-extract-report-serializer`

## 7. Review handoff (abbreviated)

Review handoff: a review packet or an equivalent PR description. This example
shows both formats; use one.

### Review packet option

**Summary:** Extracted serializer; CLI delegates formatting.

**Scope check:** Output byte-identical on sample fixtures.

**Approval:** Not required for this bounded refactor; scope-dependent approval resolved before implementation-ready.

**Validation:** `bundle exec rspec` — all pass; diff on `fixtures/sample.out` — none.

**Reviewer focus:** Confirm no hidden behavior change in edge cases.

### PR description option

- What: Extract `Report::Serializer` from command
- Why: Reduce command class size (task packet link)
- Validation: full suite green; output comparison noted
- Not included: JSON format work (separate feature task)

## Takeaway

Refactors resolve scope-dependent approval before implementation-ready and record approval only when the scope makes it required. Keep behavior identical and resist mixing feature work.
