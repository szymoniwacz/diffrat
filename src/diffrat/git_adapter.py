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
    name_status: str
    patch: str


@dataclass(frozen=True)
class GitCommitInfo:
    """Short commit metadata for review context."""

    short_hash: str
    subject: str


@dataclass(frozen=True)
class GitContext:
    """Git metadata for branch-vs-base or commit-range review."""

    commit_count: int
    commits: tuple[GitCommitInfo, ...]
    branch: str | None = None
    base_ref: str | None = None
    range_spec: str | None = None
    from_ref: str | None = None
    to_ref: str | None = None


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


def _get_diff_outputs(
    diff_args: list[str],
    *,
    cwd: str | None = None,
) -> GitDiffResult:
    numstat_result = _run_git(["diff", "--numstat", *diff_args], cwd=cwd)
    if numstat_result.returncode != 0:
        message = numstat_result.stderr.strip() or "git diff failed"
        raise GitError(message)

    name_status_result = _run_git(["diff", "--name-status", *diff_args], cwd=cwd)
    if name_status_result.returncode != 0:
        message = name_status_result.stderr.strip() or "git diff failed"
        raise GitError(message)

    patch_result = _run_git(["diff", *diff_args], cwd=cwd)
    if patch_result.returncode != 0:
        message = patch_result.stderr.strip() or "git diff failed"
        raise GitError(message)

    return GitDiffResult(
        numstat=numstat_result.stdout,
        name_status=name_status_result.stdout,
        patch=patch_result.stdout,
    )


def get_diff_numstat(*, staged: bool, cwd: str | None = None) -> GitDiffResult:
    """Return numstat and unified diff for unstaged or staged changes."""
    ensure_git_repository(cwd=cwd)

    diff_args: list[str] = []
    if staged:
        diff_args.append("--cached")

    return _get_diff_outputs(diff_args, cwd=cwd)


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
    """Return numstat and unified diff for changes on HEAD since merge-base with ``base_ref``."""
    merge_base = get_merge_base(base_ref, cwd=cwd)
    return _get_diff_outputs([f"{merge_base}..HEAD"], cwd=cwd)


def parse_range_spec(range_spec: str) -> tuple[str, str]:
    """Parse a two-dot range ``A..B`` into ``(from_ref, to_ref)``."""
    if ".." not in range_spec:
        raise GitError("invalid range: expected REV format A..B")
    from_ref, separator, to_ref = range_spec.partition("..")
    if not separator or not from_ref or not to_ref:
        raise GitError("invalid range: expected REV format A..B with two refs")
    return from_ref, to_ref


def get_diff_numstat_for_range(
    from_ref: str,
    to_ref: str,
    *,
    cwd: str | None = None,
) -> GitDiffResult:
    """Return numstat and unified diff for the two-dot range ``from_ref..to_ref``."""
    verify_ref(from_ref, cwd=cwd)
    verify_ref(to_ref, cwd=cwd)
    return _get_diff_outputs([f"{from_ref}..{to_ref}"], cwd=cwd)


def _collect_commits_in_range(
    range_revision: str,
    *,
    cwd: str | None = None,
) -> tuple[int, tuple[GitCommitInfo, ...]]:
    count_result = _run_git(["rev-list", "--count", range_revision], cwd=cwd)
    if count_result.returncode != 0:
        message = count_result.stderr.strip() or "git rev-list failed"
        raise GitError(message)
    commit_count = int(count_result.stdout.strip() or "0")

    log_result = _run_git(
        ["log", "--format=%h %s", "-n", "10", range_revision],
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

    return commit_count, tuple(commits)


def get_git_context_for_range(
    from_ref: str,
    to_ref: str,
    *,
    cwd: str | None = None,
) -> GitContext:
    """Collect commit metadata for a two-dot range review."""
    verify_ref(from_ref, cwd=cwd)
    verify_ref(to_ref, cwd=cwd)
    range_spec = f"{from_ref}..{to_ref}"
    commit_count, commits = _collect_commits_in_range(
        range_spec,
        cwd=cwd,
    )
    return GitContext(
        commit_count=commit_count,
        commits=commits,
        range_spec=range_spec,
        from_ref=from_ref,
        to_ref=to_ref,
    )


def get_git_context(base_ref: str, *, cwd: str | None = None) -> GitContext:
    """Collect branch and commit metadata for branch-vs-base review."""
    merge_base = get_merge_base(base_ref, cwd=cwd)

    branch_result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if branch_result.returncode != 0:
        message = branch_result.stderr.strip() or "git rev-parse failed"
        raise GitError(message)
    branch = branch_result.stdout.strip() or "HEAD"

    commit_count, commits = _collect_commits_in_range(
        f"{merge_base}..HEAD",
        cwd=cwd,
    )

    return GitContext(
        commit_count=commit_count,
        commits=commits,
        branch=branch,
        base_ref=base_ref,
    )
