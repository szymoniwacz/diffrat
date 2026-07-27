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
    _run_git(["init", "-b", "main"], cwd=repo)
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


@pytest.fixture
def git_repo_with_feature_branch(git_repo_clean: Path) -> Path:
    _run_git(["checkout", "-b", "feature"], cwd=git_repo_clean)
    (git_repo_clean / "feature.txt").write_text("feature work\n", encoding="utf-8")
    _run_git(["add", "feature.txt"], cwd=git_repo_clean)
    _run_git(["commit", "-m", "add feature file"], cwd=git_repo_clean)
    (git_repo_clean / "feature.txt").write_text("feature work\nmore\n", encoding="utf-8")
    _run_git(["add", "feature.txt"], cwd=git_repo_clean)
    _run_git(["commit", "-m", "extend feature file"], cwd=git_repo_clean)
    return git_repo_clean
