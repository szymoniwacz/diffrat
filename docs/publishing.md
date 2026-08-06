# Publishing Diffrat to PyPI

Maintainer runbook for releases after the Diffrat rebrand (D-008).

## Versioning

- Package version lives in `pyproject.toml` (`[project].version`) and
  `src/diffrat/__init__.py` (`__version__`). Keep them identical.
- Follow SemVer. Breaking CLI/JSON/`schema_version` changes bump major.
- PyPI already has `0.0.1` (name-reservation stub) and product `1.0.0`.

## Preconditions

1. `pytest`, `ruff check .`, and `mypy .` pass on the release commit.
2. `CHANGELOG.md` describes the release.
3. GitHub repository is named `diffrat` (Trusted Publisher is bound to
   owner/repo).
4. PyPI project `diffrat` has a Trusted Publisher for this repo’s
   `.github/workflows/publish.yml` and environment `pypi`.

## Release steps

1. Bump version in `pyproject.toml` and `src/diffrat/__init__.py`.
2. Update `CHANGELOG.md`; move notes out of Unreleased.
3. Merge to `main`.
4. Create and push an annotated tag: `git tag -a vX.Y.Z -m "Diffrat X.Y.Z"`
   then `git push origin vX.Y.Z`.
5. GitHub Actions workflow `Publish to PyPI` builds and uploads via Trusted
   Publishing.
6. Verify:

```bash
python3 -m venv /tmp/diffrat-verify && source /tmp/diffrat-verify/bin/activate
pip install diffrat==X.Y.Z
diffrat --version
diffrat review --help
```

7. Create a GitHub Release from the tag with CHANGELOG notes
   (`gh release create vX.Y.Z --notes-file ...` or the UI).

## Manual upload fallback

If Trusted Publishing is unavailable, build and upload with a short-lived
API token (never commit tokens):

```bash
python3 -m build
python3 -m twine check dist/*
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-... python3 -m twine upload dist/*
```

Revoke the token after use if it was exposed outside a secret store.

## TestPyPI

Optional dry-run against TestPyPI (separate account/token from production):

```bash
python3 -m twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ diffrat==X.Y.Z
```
