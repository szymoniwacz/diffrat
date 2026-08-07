"""Tests for local review checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from diffrat.analysis import (
    is_ci_workflow_validator_path,
    is_pyproject_path,
    is_python_source_or_test_path,
)
from diffrat.checks import (
    CheckSpec,
    bandit_targets_for_paths,
    is_pip_audit_dependency_path,
    mypy_targets_for_paths,
    parse_check_argv,
    plan_checks,
    pytest_targets_for_paths,
    run_checks,
)
from diffrat.config import DiffratConfig
from diffrat.diff_parser import DiffSummary, FileChange


def test_parse_check_argv_maps_python_to_sys_executable() -> None:
    argv = parse_check_argv("python ci/validate-workflow-contracts.py --mode project")
    assert argv == (
        sys.executable,
        "ci/validate-workflow-contracts.py",
        "--mode",
        "project",
    )


def test_parse_check_argv_preserves_non_python_commands() -> None:
    assert parse_check_argv("pytest tests/test_review.py") == ("pytest", "tests/test_review.py")


def test_plan_checks_ci_validator_uses_config_override() -> None:
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
    config = DiffratConfig(
        checks={"ci_validator": "python ci/validate-workflow-contracts.py --mode strict"},
        content_rules=(),
    )

    specs = plan_checks(summary, config=config)

    assert specs[0].display_command == (
        "python ci/validate-workflow-contracts.py --mode strict"
    )
    assert specs[0].argv == (
        sys.executable,
        "ci/validate-workflow-contracts.py",
        "--mode",
        "strict",
    )


def test_plan_checks_ignores_non_ci_validator_config_overrides() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )
    config = DiffratConfig(
        checks={"pytest": "custom-pytest"},
        content_rules=(),
    )

    specs = plan_checks(summary, config=config)

    assert specs[0].display_command == "pytest tests/test_review.py"


def test_is_python_source_or_test_path() -> None:
    assert is_python_source_or_test_path("src/diffrat/review.py")
    assert is_python_source_or_test_path("tests/test_review.py")
    assert not is_python_source_or_test_path("README.md")
    assert not is_python_source_or_test_path("src/other/module.py")


def test_is_ci_workflow_validator_path() -> None:
    assert is_ci_workflow_validator_path("ci/validate-workflow-contracts.py")
    assert is_ci_workflow_validator_path(".github/workflows/validate.yml")
    assert not is_ci_workflow_validator_path("README.md")


def test_pytest_targets_maps_source_to_test_module() -> None:
    assert pytest_targets_for_paths(["src/diffrat/review.py"]) == ["tests/test_review.py"]


def test_pytest_targets_uses_test_module_directly() -> None:
    assert pytest_targets_for_paths(["tests/test_review.py"]) == ["tests/test_review.py"]


def test_pytest_targets_deduplicates_source_and_test_paths() -> None:
    paths = ["src/diffrat/review.py", "tests/test_review.py"]

    assert pytest_targets_for_paths(paths) == ["tests/test_review.py"]


def test_pytest_targets_supports_multiple_modules() -> None:
    paths = ["src/diffrat/review.py", "tests/test_checks.py"]

    assert pytest_targets_for_paths(paths) == [
        "tests/test_checks.py",
        "tests/test_review.py",
    ]


def test_pytest_targets_maps_conftest_to_tests_directory() -> None:
    assert pytest_targets_for_paths(["tests/conftest.py"]) == ["tests"]


def test_mypy_targets_maps_source_modules() -> None:
    assert mypy_targets_for_paths(["src/diffrat/review.py"]) == ["src/diffrat/review.py"]


def test_mypy_targets_skips_tests_and_other_paths() -> None:
    paths = ["tests/test_review.py", "README.md", "src/other/module.py"]
    assert mypy_targets_for_paths(paths) == []


def test_mypy_targets_deduplicates_and_sorts() -> None:
    paths = ["src/diffrat/checks.py", "src/diffrat/review.py", "src/diffrat/checks.py"]
    assert mypy_targets_for_paths(paths) == [
        "src/diffrat/checks.py",
        "src/diffrat/review.py",
    ]


def test_plan_checks_selects_mypy_for_source_paths() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest", "mypy", "bandit"]
    assert specs[1].argv == (
        sys.executable,
        "-m",
        "mypy",
        "src/diffrat/review.py",
    )
    assert specs[1].display_command == "mypy src/diffrat/review.py"


def test_plan_checks_mypy_deduplicates_multiple_modules() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
            FileChange(path="src/diffrat/checks.py", additions=1, deletions=0, binary=False),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest", "mypy", "bandit"]
    assert specs[1].argv[-2:] == ("src/diffrat/checks.py", "src/diffrat/review.py")


def test_is_pyproject_path() -> None:
    assert is_pyproject_path("pyproject.toml")
    assert is_pyproject_path("subdir/pyproject.toml")
    assert not is_pyproject_path("requirements.txt")
    assert not is_pyproject_path("README.md")


def test_plan_checks_omits_ci_validator_without_config() -> None:
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

    assert plan_checks(summary) == []


def test_plan_checks_selects_ci_validator_when_configured() -> None:
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
    config = DiffratConfig(
        checks={"ci_validator": "python ci/validate-workflow-contracts.py --mode project"},
        content_rules=(),
    )

    specs = plan_checks(summary, config=config)

    assert [spec.code for spec in specs] == ["ci_validator"]
    assert specs[0].display_command == (
        "python ci/validate-workflow-contracts.py --mode project"
    )


def test_plan_checks_selects_pytest_for_source_paths() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest", "mypy", "bandit"]
    assert specs[0].argv == (
        sys.executable,
        "-m",
        "pytest",
        "tests/test_review.py",
    )
    assert specs[0].display_command == "pytest tests/test_review.py"


def test_plan_checks_deduplicates_checks() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
            FileChange(path="tests/test_review.py", additions=1, deletions=0, binary=False),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest", "mypy", "bandit"]
    assert specs[0].argv[-1] == "tests/test_review.py"


def test_plan_checks_returns_empty_for_unrelated_paths() -> None:
    summary = DiffSummary(
        files=(FileChange(path="README.md", additions=1, deletions=0, binary=False),)
    )

    assert plan_checks(summary) == []


def test_plan_checks_ci_validator_with_python_paths_when_configured() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=1,
                deletions=0,
                binary=False,
            ),
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )
    config = DiffratConfig(
        checks={"ci_validator": "python ci/validate-workflow-contracts.py --mode project"},
        content_rules=(),
    )

    specs = plan_checks(summary, config=config)

    assert [spec.code for spec in specs] == ["ci_validator", "pytest", "mypy", "bandit"]
    assert specs[0].display_command == (
        "python ci/validate-workflow-contracts.py --mode project"
    )


def test_plan_checks_selects_ruff_for_pyproject() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["ruff", "pip-audit"]
    assert specs[0].display_command == "ruff check ."


def test_plan_checks_skips_ruff_for_other_config() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="requirements.txt", additions=1, deletions=0, binary=False),
        )
    )

    with patch("diffrat.checks.shutil.which", return_value=None):
        specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pip-audit"]
    assert specs[0].skip_reason == "pip-audit not found on PATH"


def test_plan_checks_pyproject_and_source() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )

    specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest", "mypy", "ruff", "bandit", "pip-audit"]


def test_run_checks_records_pass_and_fail() -> None:
    specs = [
        CheckSpec(code="pytest", argv=("pytest",), display_command="pytest"),
    ]
    success = MagicMock(returncode=0, stdout="ok\n", stderr="")
    failure = MagicMock(returncode=1, stdout="", stderr="boom\n")

    with patch("diffrat.checks.subprocess.run", side_effect=[success, failure]) as run_mock:
        passed = run_checks(specs, cwd="/tmp/repo")
        failed = run_checks(specs, cwd="/tmp/repo")

    assert run_mock.call_count == 2
    assert passed[0].passed is True
    assert passed[0].output == "ok"
    assert failed[0].passed is False
    assert failed[0].output == "boom"


def test_bandit_targets_match_mypy_targets() -> None:
    paths = ["src/diffrat/review.py", "tests/test_review.py"]
    assert bandit_targets_for_paths(paths) == ["src/diffrat/review.py"]


def test_is_pip_audit_dependency_path() -> None:
    assert is_pip_audit_dependency_path("pyproject.toml")
    assert is_pip_audit_dependency_path("poetry.lock")
    assert is_pip_audit_dependency_path("requirements.txt")
    assert not is_pip_audit_dependency_path("README.md")


def test_plan_checks_selects_bandit_when_on_path() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )

    with patch("diffrat.checks.shutil.which", return_value="/usr/bin/bandit"):
        specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest", "mypy", "bandit"]
    assert specs[2].display_command == "bandit -r src/diffrat/review.py"
    assert specs[2].argv == ("/usr/bin/bandit", "-r", "src/diffrat/review.py")
    assert specs[2].skip_reason is None


def test_plan_checks_skips_bandit_when_missing() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )

    with patch("diffrat.checks.shutil.which", return_value=None):
        specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pytest", "mypy", "bandit"]
    assert specs[2].skip_reason == "bandit not found on PATH"


def test_plan_checks_selects_pip_audit_for_pyproject() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    with patch("diffrat.checks.shutil.which", return_value="/usr/bin/pip-audit"):
        specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["ruff", "pip-audit"]
    assert specs[1].argv == ("/usr/bin/pip-audit",)


def test_plan_checks_skips_pip_audit_when_missing() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="requirements.txt", additions=1, deletions=0, binary=False),
        )
    )

    with patch("diffrat.checks.shutil.which", return_value=None):
        specs = plan_checks(summary)

    assert [spec.code for spec in specs] == ["pip-audit"]
    assert specs[0].skip_reason == "pip-audit not found on PATH"


def test_run_checks_records_skipped_without_subprocess() -> None:
    specs = [
        CheckSpec(
            code="bandit",
            argv=(),
            display_command="bandit -r src/diffrat/review.py",
            skip_reason="bandit not found on PATH",
        )
    ]

    with patch("diffrat.checks.subprocess.run") as run_mock:
        results = run_checks(specs, cwd="/tmp/repo")

    run_mock.assert_not_called()
    assert results[0].skipped is True
    assert results[0].passed is True
    assert results[0].output == "bandit not found on PATH"
