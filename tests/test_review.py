"""Tests for review command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from numbat.json_renderer import JSON_SCHEMA_VERSION
from numbat.review import (
    EXIT_CHECK_FAILED,
    EXIT_EMPTY_DIFF,
    EXIT_ERROR,
    EXIT_SUCCESS,
    run_review,
)


def test_run_review_unstaged(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, cwd=str(git_repo_with_changes))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Review Report" in captured.out
    assert "README.md" in captured.out
    assert "Changes" in captured.out
    assert "+extra line" in captured.out
    assert captured.err == ""


def test_run_review_staged(
    git_repo_with_staged_change: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, cwd=str(git_repo_with_staged_change))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "staged.txt  [other]  +1 -0" in captured.out
    assert "Focus / Risk" in captured.out


def test_run_review_empty_diff(git_repo_clean: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_review(staged=False, cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no unstaged changes to review" in captured.err


def test_run_review_not_a_repo(
    outside_git_directory: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, cwd=str(outside_git_directory))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert captured.out == ""
    assert "not a git repository" in captured.err


def test_run_review_base_main(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="main", cwd=str(git_repo_with_feature_branch))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Git context" in captured.out
    assert "Branch: feature" in captured.out
    assert "Base: main" in captured.out
    assert "Commits since base: 2" in captured.out
    assert "add feature file" in captured.out
    assert "feature.txt" in captured.out
    assert captured.err == ""


def test_run_review_base_invalid_ref(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="not-a-real-ref", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert captured.out == ""
    assert "Needed a single revision" in captured.err


def test_run_review_base_empty_diff(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no changes on branch since main" in captured.err


def test_run_review_staged_and_base_conflict(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, base="main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "cannot use --staged with --base" in captured.err


def test_run_review_range_main_feature(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(range_spec="main..feature", cwd=str(git_repo_with_feature_branch))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Range: main..feature" in captured.out
    assert "From: main" in captured.out
    assert "To: feature" in captured.out
    assert "Commits in range: 2" in captured.out
    assert "feature.txt" in captured.out
    assert captured.err == ""


def test_run_review_range_invalid_spec(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(range_spec="not-a-range", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "expected REV format A..B" in captured.err


def test_run_review_range_invalid_ref(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(range_spec="main..not-a-real-ref", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "Needed a single revision" in captured.err


def test_run_review_range_empty_diff(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(range_spec="main..main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no changes in range main..main" in captured.err


def test_run_review_staged_and_range_conflict(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, range_spec="main..main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "cannot use --staged with --range" in captured.err


def test_run_review_base_and_range_conflict(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="main", range_spec="main..main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "cannot use --base with --range" in captured.err


def test_run_review_json_range(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        range_spec="main..feature",
        json_output=True,
        cwd=str(git_repo_with_feature_branch),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["mode"] == "range"
    assert payload["git_context"]["range"] == "main..feature"
    assert payload["git_context"]["from_ref"] == "main"
    assert payload["git_context"]["to_ref"] == "feature"
    assert payload["git_context"]["commit_count"] == 2
    assert payload["git_context"]["commits"][0]["subject"] == "extend feature file"


def test_run_review_json_unstaged(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, json_output=True, cwd=str(git_repo_with_changes))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert captured.err == ""

    payload = json.loads(captured.out)
    assert payload["schema_version"] == JSON_SCHEMA_VERSION
    assert payload["mode"] == "unstaged"
    assert payload["summary"]["file_count"] == 1
    assert payload["files"][0]["path"] == "README.md"
    assert payload["files"][0]["category"] == "docs"
    assert "focus_risk" in payload
    assert "git_context" not in payload


def test_run_review_json_staged(
    git_repo_with_staged_change: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, json_output=True, cwd=str(git_repo_with_staged_change))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["mode"] == "staged"
    assert payload["files"] == [
        {
            "path": "staged.txt",
            "additions": 1,
            "deletions": 0,
            "category": "other",
        }
    ]
    assert payload["focus_risk"] == []


def test_run_review_json_base(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="main", json_output=True, cwd=str(git_repo_with_feature_branch))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["mode"] == "branch"
    assert payload["git_context"]["branch"] == "feature"
    assert payload["git_context"]["base"] == "main"
    assert payload["git_context"]["commit_count"] == 2
    assert payload["git_context"]["commits"][0]["subject"] == "extend feature file"
    assert any(file_entry["path"] == "feature.txt" for file_entry in payload["files"])


def test_run_review_json_empty_diff_no_stdout(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, json_output=True, cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no unstaged changes to review" in captured.err


def test_run_review_check_no_applicable_checks(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        run_checks_flag=True,
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Local checks" in captured.out
    assert "(none applicable)" in captured.out
    assert captured.err == ""


def test_run_review_check_reports_failure(
    git_repo_with_staged_change: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from numbat.checks import CheckResult, CheckSpec

    monkeypatch.setattr(
        "numbat.review.plan_checks",
        lambda summary: [
            CheckSpec(
                code="ci_validator",
                argv=("python",),
                display_command=(
                    "python ci/validate-workflow-contracts.py --mode project"
                ),
            )
        ],
    )
    monkeypatch.setattr(
        "numbat.review.run_checks",
        lambda specs, *, cwd=None: [
            CheckResult(
                code="ci_validator",
                command="python ci/validate-workflow-contracts.py --mode project",
                passed=False,
                output="validator failed",
            )
        ],
    )

    exit_code = run_review(staged=True, run_checks_flag=True, cwd=str(git_repo_with_staged_change))

    captured = capsys.readouterr()
    assert exit_code == EXIT_CHECK_FAILED
    assert "[ci_validator] failed" in captured.out
    assert "validator failed" in captured.out
    assert "check failed: ci_validator" in captured.err


def test_run_review_check_json_includes_checks(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from numbat.checks import CheckResult

    monkeypatch.setattr(
        "numbat.review.run_checks",
        lambda specs, *, cwd=None: [
            CheckResult(code="pytest", command="pytest", passed=True, output="")
        ],
    )

    exit_code = run_review(
        staged=False,
        json_output=True,
        run_checks_flag=True,
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["checks"] == [
        {
            "code": "pytest",
            "command": "pytest",
            "passed": True,
            "output": "",
        }
    ]
