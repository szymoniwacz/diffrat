# Validator Fixtures

This folder documents fixture scenarios exercised by `ci/tests/test_validator.py`.

Each test builds a temporary repository skeleton from the current template and
introduces one controlled failure. The validator must report that failure with a
file and reason.

Scenarios:

- missing mandatory file
- broken local Markdown link
- invalid Cursor frontmatter
- unresolved bootstrap marker in project mode
- blocking-question status in project mode

The current repository itself must pass template mode validation in CI.
