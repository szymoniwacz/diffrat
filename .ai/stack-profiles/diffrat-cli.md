# Diffrat CLI Stack Profile

Stack-specific guidance for the Diffrat product. Global workflow rules still apply.

## Layout

```txt
src/diffrat/
tests/
pyproject.toml
README.md
```

## Commands

```bash
pip install -e ".[dev]"
pytest
ruff format --check src tests
ruff check .
mypy .
bandit -r src/diffrat/checks.py src/diffrat/review_quality.py src/diffrat/scoring.py
python -m diffrat --help
diffrat --help
```

## Testing expectations

- Unit tests for changed modules under `tests/`
- CLI tests for new flags or subcommands
- Run full suite before opening a PR

## Documentation expectations

- Update CLI help text and README when commands change
- Record architecture changes in `.ai/docs/architecture-direction.md`

## AI-specific risks

- Packaging and entry-point misconfiguration
- Breaking stdout/stderr contracts used by scripts
- Adding dependencies without updating `pyproject.toml`
- Path and filesystem assumptions across OS environments

## References

- `.ai/stack-profiles/python-cli.md` — generic Python CLI guidance
- `.ai/docs/architecture-direction.md`
