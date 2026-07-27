"""Tests for git adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from numbat.git_adapter import GitError, ensure_git_repository, get_diff_numstat


def test_ensure_git_repository_rejects_non_repo(tmp_path: Path) -> None:
    with pytest.raises(GitError, match="not a git repository"):
        ensure_git_repository(cwd=str(tmp_path))


def test_get_diff_numstat_unstaged(git_repo_with_changes: Path) -> None:
    result = get_diff_numstat(staged=False, cwd=str(git_repo_with_changes))

    assert "README.md" in result.numstat


def test_get_diff_numstat_staged(git_repo_with_staged_change: Path) -> None:
    result = get_diff_numstat(staged=True, cwd=str(git_repo_with_staged_change))

    assert "staged.txt" in result.numstat
    assert "1\t0\tstaged.txt" in result.numstat


def test_get_diff_numstat_git_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import numbat.git_adapter as git_adapter

    def fake_run_git(args: list[str], *, cwd: str | None = None) -> object:
        class Result:
            returncode = 0
            stdout = "true\n"
            stderr = ""

        if args[:2] == ["rev-parse", "--is-inside-work-tree"]:
            return Result()
        failure = Result()
        failure.returncode = 1
        failure.stderr = "fatal: bad revision"
        return failure

    monkeypatch.setattr(git_adapter, "_run_git", fake_run_git)

    with pytest.raises(GitError, match="fatal: bad revision"):
        get_diff_numstat(staged=False, cwd=str(tmp_path))
