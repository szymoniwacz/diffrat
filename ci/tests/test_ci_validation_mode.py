#!/usr/bin/env python3
"""Tests for CI validation mode transition after bootstrap."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = ROOT / ".github/workflows/validate-workflow-contracts.yml"

from test_project_validator import bootstrap_valid_project  # noqa: E402
from test_validator import run_validator  # noqa: E402


def test_bootstrapped_repository_ci_uses_project_mode() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "python ci/validate-workflow-contracts.py --mode project" in text
    assert "python ci/validate-workflow-contracts.py --mode template" not in text
    result = run_validator(ROOT, "project")
    assert result.returncode == 0, result.stderr


def test_bootstrapped_project_ci_uses_project_mode() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        workflow = root / ".github/workflows/validate-workflow-contracts.yml"
        text = workflow.read_text(encoding="utf-8")
        assert "python ci/validate-workflow-contracts.py --mode project" in text
        assert "python ci/validate-workflow-contracts.py --mode template" not in text
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_project_mode_accepts_typical_product_directories() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        for name in ("app", "config", "db", "public"):
            (root / name).mkdir()
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_project_mode_fails_when_ci_still_uses_template_mode() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        workflow = root / ".github/workflows/validate-workflow-contracts.yml"
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "python ci/validate-workflow-contracts.py --mode project",
                "python ci/validate-workflow-contracts.py --mode template",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "still runs validate-workflow-contracts.py with --mode template" in result.stderr


def test_project_mode_fails_when_ci_workflow_is_missing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / ".github/workflows/validate-workflow-contracts.yml").unlink()
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "CI workflow for contract validation is missing" in result.stderr


def test_project_mode_fails_when_ci_has_no_explicit_validation_mode() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        workflow = root / ".github/workflows/validate-workflow-contracts.yml"
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "python ci/validate-workflow-contracts.py --mode project",
                "python ci/validate-workflow-contracts.py",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "must run validate-workflow-contracts.py with --mode project" in result.stderr


def main() -> int:
    tests = [
        test_bootstrapped_repository_ci_uses_project_mode,
        test_bootstrapped_project_ci_uses_project_mode,
        test_project_mode_accepts_typical_product_directories,
        test_project_mode_fails_when_ci_still_uses_template_mode,
        test_project_mode_fails_when_ci_workflow_is_missing,
        test_project_mode_fails_when_ci_has_no_explicit_validation_mode,
    ]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {test.__name__}: {exc}", file=sys.stderr)
    if failures:
        print(f"{failures} CI validation mode test(s) failed", file=sys.stderr)
        return 1
    print("all CI validation mode tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
