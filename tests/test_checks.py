"""Tests for local review checks."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from numbat.analysis import is_ci_workflow_validator_path, is_python_source_or_test_path
from numbat.checks import CheckSpec, plan_checks, run_checks
from numbat.diff_parser import DiffSummary, FileChange


def test_is_python_source_or_test_path() -> None:
    assert is_python_source_or_test_path("src/numbat/review.py")
    assert is_python_source_or_test_path("tests/test_review.py")
    assert not is_python_source_or_test_path("README.md")
    assert not is_python_source_or_test_path("src/other/module.py")


def test_is_ci_workflow_validator_path() -> None:
    assert is_ci_workflow_validator_path("ci/validate-workflow-contracts.py")
    assert is_ci_workflow_validator_path(".github/workflows/validate.yml")
    assert not is_ci_workflow_validator_path("README.md")


def test_plan_checks_selects_ci_validator() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=1,
                deletions=0,
                binary=False,
            ),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["ci_validator"]
    assert specs[0].display_command == (
        "python ci/validate-workflow-contracts.py --mode project"
    )


def test_plan_checks_selects_pytest_for_source_paths() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/review.py", additions=1, deletions=0, binary=False),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest"]


def test_plan_checks_deduplicates_checks() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/review.py", additions=1, deletions=0, binary=False),
            FileChange(path="tests/test_review.py", additions=1, deletions=0, binary=False),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest"]


def test_plan_checks_returns_empty_for_unrelated_paths() -> None:
    summary = DiffSummary(
        files=(FileChange(path="README.md", additions=1, deletions=0, binary=False),)
    )

    assert plan_checks(summary) == []


def test_run_checks_records_pass_and_fail() -> None:
    specs = [
        CheckSpec(code="pytest", argv=("pytest",), display_command="pytest"),
    ]
    success = MagicMock(returncode=0, stdout="ok\n", stderr="")
    failure = MagicMock(returncode=1, stdout="", stderr="boom\n")

    with patch("numbat.checks.subprocess.run", side_effect=[success, failure]) as run_mock:
        passed = run_checks(specs, cwd="/tmp/repo")
        failed = run_checks(specs, cwd="/tmp/repo")

    assert run_mock.call_count == 2
    assert passed[0].passed is True
    assert passed[0].output == "ok"
    assert failed[0].passed is False
    assert failed[0].output == "boom"
