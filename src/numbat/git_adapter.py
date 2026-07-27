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


@dataclass(frozen=True)
class GitCommitInfo:
    """Short commit metadata for review context."""

    short_hash: str
    subject: str


@dataclass(frozen=True)
class GitContext:
    """Git metadata for branch-vs-base review."""

    branch: str
    base_ref: str
    commit_count: int
    commits: tuple[GitCommitInfo, ...]


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


def verify_ref(ref: str, *, cwd: str | None = None) -> None:
    """Verify that a git ref exists."""
    ensure_git_repository(cwd=cwd)
    result = _run_git(["rev-parse", "--verify", ref], cwd=cwd)
    if result.returncode != 0:
        message = result.stderr.strip() or f"invalid git ref: {ref}"
        raise GitError(message)


def get_merge_base(base_ref: str, *, cwd: str | None = None) -> str:
    """Return the merge-base between HEAD and ``base_ref``."""
    verify_ref(base_ref, cwd=cwd)
    result = _run_git(["merge-base", "HEAD", base_ref], cwd=cwd)
    if result.returncode != 0:
        message = result.stderr.strip() or "git merge-base failed"
        raise GitError(message)
    merge_base = result.stdout.strip()
    if not merge_base:
        raise GitError("git merge-base returned no result")
    return merge_base


def get_diff_numstat_vs_base(base_ref: str, *, cwd: str | None = None) -> GitDiffResult:
    """Return numstat output for changes on HEAD since merge-base with ``base_ref``."""
    merge_base = get_merge_base(base_ref, cwd=cwd)
    result = _run_git(["diff", "--numstat", f"{merge_base}..HEAD"], cwd=cwd)
    if result.returncode != 0:
        message = result.stderr.strip() or "git diff failed"
        raise GitError(message)
    return GitDiffResult(numstat=result.stdout)


def get_git_context(base_ref: str, *, cwd: str | None = None) -> GitContext:
    """Collect branch and commit metadata for branch-vs-base review."""
    merge_base = get_merge_base(base_ref, cwd=cwd)

    branch_result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if branch_result.returncode != 0:
        message = branch_result.stderr.strip() or "git rev-parse failed"
        raise GitError(message)
    branch = branch_result.stdout.strip() or "HEAD"

    count_result = _run_git(["rev-list", "--count", f"{merge_base}..HEAD"], cwd=cwd)
    if count_result.returncode != 0:
        message = count_result.stderr.strip() or "git rev-list failed"
        raise GitError(message)
    commit_count = int(count_result.stdout.strip() or "0")

    log_result = _run_git(
        ["log", "--format=%h %s", "-n", "10", f"{merge_base}..HEAD"],
        cwd=cwd,
    )
    if log_result.returncode != 0:
        message = log_result.stderr.strip() or "git log failed"
        raise GitError(message)

    commits: list[GitCommitInfo] = []
    for line in log_result.stdout.splitlines():
        if not line.strip():
            continue
        short_hash, _, subject = line.partition(" ")
        commits.append(GitCommitInfo(short_hash=short_hash, subject=subject))

    return GitContext(
        branch=branch,
        base_ref=base_ref,
        commit_count=commit_count,
        commits=tuple(commits),
    )
