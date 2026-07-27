# Example: Small Feature Task

Process-focused example. Not real product code.

Follow `.ai/workflows/feature.md`.

## Scenario

Add a CLI flag `--format json` to an existing report command. Project context and scope already exist.

## 1. Task packet (abbreviated)

**Goal:** Users can request JSON output from the report command.

**Non-goals:** New report types, API changes, web UI.

**Scope:** CLI flag parsing and serializer for existing report output.

**Validation:** Manual run with `--format json`; unit test for flag parsing; verify the output is valid JSON with the expected shape.

## 2. Ready for planning

- goal, scope, non-goals, and validation are explicit
- risks and open questions recorded

## 3. Plan (abbreviated)

**Planned files:**

| File | Change |
|---|---|
| `lib/cli/report_command.rb` | Add flag |
| `lib/report/serializer.rb` | JSON formatter |
| `spec/cli/report_command_spec.rb` | Flag test |
| `spec/report/serializer_spec.rb` | Valid-JSON and expected-shape test |

**Stop conditions:** If report schema is undefined, pause and update docs first.

## 4. Implementation-ready

- task packet exists in `.ai/packets/`
- plan exists in `.ai/plans/`
- plan matches packet goal and non-goals

## 5. Implementation discipline

- Read `.ai/project/scope.md` — CLI is in scope; API is not.
- Change only listed files.
- No drive-by rename of `Report` classes.

## 6. Review handoff (abbreviated)

Review handoff: a review packet or an equivalent PR description. This example
shows both formats; use one.

### Review packet option

**Summary:** Added `--format json` to report CLI with tests.

**Assumptions:** Existing report schema is stable.

**Scope check:** No API or UI changes.

**Validation:** `bundle exec rspec spec/cli/report_command_spec.rb spec/report/serializer_spec.rb` — pass; output parses as valid JSON and matches the expected shape.

**Reviewer focus:** JSON shape stability for downstream scripts.

### PR description option

- What: JSON output flag for report command
- Why: scripting integration request from task packet
- Assumptions: existing report schema is stable
- Validation: specs pass; output verified as valid JSON with the expected shape; manual sample output attached
- Not included: API endpoint, schema versioning

## Takeaway

Feature work stays small: one user-visible behavior, explicit non-goals, task packet and plan before implementation, tests for the changed surface.
