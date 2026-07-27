# Python CLI Stack Profile

Stack-specific guidance for AI-assisted work. Global workflow rules still apply.

## Common structure

```txt
src/<package_name>/
tests/
pyproject.toml or setup.cfg
README.md
```

Document entry points and CLI layout in `.ai/docs/` if non-standard.

## Common commands (placeholders)

Replace with project-defined commands:

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy .
python -m <package> --help
```

Do not invent commands that are not set up in the project.

## Testing expectations

- Unit tests for changed modules
- CLI tests for new flags or commands (e.g. `pytest` with runner helpers)
- Snapshot tests only when stable output is intentional

## Documentation expectations

- Update CLI help text and README when commands change
- Document config files and environment variables in `.ai/docs/` or project README

## AI-specific risks

- Packaging and entry-point misconfiguration
- Silent exception swallowing in CLI paths
- Breaking stdout/stderr contracts used by scripts
- Adding dependencies without lockfile update
- Path and filesystem assumptions across OS environments

## What agents should avoid

- Broad `ruff format` on unrelated modules
- Changing `pyproject.toml` optional deps without justification
- Executing arbitrary shell from CLI without sandbox review
- Bundling library API changes with CLI-only tasks
- Committing virtualenvs or local `.env` files

## References

- `.ai/workflows/test-writing.md`
- `.ai/policies/security-policy.md`
