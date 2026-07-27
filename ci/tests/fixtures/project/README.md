# Project validator fixtures

These tests build temporary repository trees to verify project mode behavior.

Scenarios covered:

- valid bootstrapped project passes
- instructional bootstrap marker references allowed
- product-owned bootstrap markers rejected
- missing, duplicate, and invalid decision areas
- missing status metadata
- placeholder or missing stack profiles
- incomplete readiness rows
- template README and AGENTS identity rejection
- commands row without evidence location

Run with:

```bash
python ci/tests/test_project_validator.py
```
