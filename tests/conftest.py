"""Shared pytest fixtures."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _run_git(args: list[str], *, cwd: Path) -> None:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise RuntimeError(message)


@pytest.fixture
def git_repo_clean(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(["init"], cwd=repo)
    _run_git(["config", "user.email", "test@example.com"], cwd=repo)
    _run_git(["config", "user.name", "Test User"], cwd=repo)
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _run_git(["add", "README.md"], cwd=repo)
    _run_git(["commit", "-m", "initial"], cwd=repo)
    return repo


@pytest.fixture
def git_repo_with_changes(git_repo_clean: Path) -> Path:
    readme = git_repo_clean / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "extra line\n", encoding="utf-8")
    return git_repo_clean


@pytest.fixture
def git_repo_with_staged_change(git_repo_clean: Path) -> Path:
    (git_repo_clean / "staged.txt").write_text("staged\n", encoding="utf-8")
    _run_git(["add", "staged.txt"], cwd=git_repo_clean)
    return git_repo_clean
