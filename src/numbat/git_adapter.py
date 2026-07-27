"""Git adapter: invoke local git for diff data."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


class GitError(Exception):
    """Raised when git cannot satisfy a request."""


@dataclass(frozen=True)
class GitDiffResult:
    """Raw diff output from git."""

    numstat: str


def _run_git(args: list[str], *, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found on PATH") from exc


def ensure_git_repository(*, cwd: str | None = None) -> None:
    """Verify the working directory is inside a git repository."""
    result = _run_git(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
    if result.returncode != 0:
        message = result.stderr.strip() or "not a git repository"
        raise GitError(message)
    if result.stdout.strip() != "true":
        raise GitError("not a git repository")


def get_diff_numstat(*, staged: bool, cwd: str | None = None) -> GitDiffResult:
    """Return numstat output for unstaged or staged changes."""
    ensure_git_repository(cwd=cwd)

    args = ["diff", "--numstat"]
    if staged:
        args.insert(1, "--cached")

    result = _run_git(args, cwd=cwd)
    if result.returncode != 0:
        message = result.stderr.strip() or "git diff failed"
        raise GitError(message)

    return GitDiffResult(numstat=result.stdout)
