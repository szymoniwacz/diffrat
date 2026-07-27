# Quality Model

## Purpose

Define what quality means for this project.

Quality is not only passing checks.
It also includes maintainability, clarity, reviewability, and consistency.

## Default quality dimensions

| Dimension | Meaning |
|---|---|
| Correctness | The change does what it should do |
| Reviewability | The change is small and understandable |
| Consistency | The change follows existing structure |
| Documentation | The related context stays true |
| Maintainability | The future cost is acceptable |
| Safety | Risky behavior is visible and controlled |

## Project-specific quality gates

Add project-specific checks here.

Examples:

- tests pass
- linting passes
- output format is stable
- generated report is readable
- no unrelated files changed

## Rule

A change can be technically correct and still fail the quality model.
