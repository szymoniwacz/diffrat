"""Tests for review command."""

from __future__ import annotations

from pathlib import Path

import pytest

from numbat.review import EXIT_EMPTY_DIFF, EXIT_ERROR, EXIT_SUCCESS, run_review


def test_run_review_unstaged(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, cwd=str(git_repo_with_changes))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Review Report" in captured.out
    assert "README.md" in captured.out
    assert captured.err == ""


def test_run_review_staged(
    git_repo_with_staged_change: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, cwd=str(git_repo_with_staged_change))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "staged.txt  +1 -0" in captured.out


def test_run_review_empty_diff(git_repo_clean: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_review(staged=False, cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no unstaged changes to review" in captured.err


def test_run_review_not_a_repo(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_review(staged=False, cwd=str(tmp_path))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert captured.out == ""
    assert "not a git repository" in captured.err
