"""Tests for report renderer."""

from __future__ import annotations

from numbat.diff_parser import DiffSummary, FileChange
from numbat.git_adapter import GitCommitInfo, GitContext
from numbat.report import render_review_report


def test_render_review_report_includes_summary_and_files() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/a.py", additions=4, deletions=1, binary=False),
            FileChange(path="bin.dat", additions=0, deletions=0, binary=True),
        )
    )

    report = render_review_report(summary)

    assert "Review Report" in report
    assert "Files changed: 2" in report
    assert "Lines added: 4" in report
    assert "Lines deleted: 1" in report
    assert "Total lines changed: 5" in report
    assert "src/a.py  [source]  +4 -1" in report
    assert "bin.dat  [other]  (binary)" in report
    assert "Focus / Risk" in report
    assert "(none)" in report


def test_render_review_report_includes_categories_and_hints() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    report = render_review_report(summary)

    assert "tests/test_a.py  [tests]  +2 -0" in report
    assert "pyproject.toml  [config]  +1 -0" in report
    assert "[tests_touched]" in report
    assert "[config_or_deps]" in report


def test_render_review_report_includes_git_context() -> None:
    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=1, deletions=0, binary=False),)
    )
    git_context = GitContext(
        branch="feature",
        base_ref="main",
        commit_count=2,
        commits=(
            GitCommitInfo(short_hash="abc1234", subject="second commit"),
            GitCommitInfo(short_hash="def5678", subject="first commit"),
        ),
    )

    report = render_review_report(summary, git_context=git_context)

    assert "Git context" in report
    assert "Branch: feature" in report
    assert "Base: main" in report
    assert "Commits since base: 2" in report
    assert "abc1234 second commit" in report
