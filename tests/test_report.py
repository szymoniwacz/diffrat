"""Tests for report renderer."""

from __future__ import annotations

from numbat.diff_parser import DiffSummary, FileChange
from numbat.git_adapter import GitCommitInfo, GitContext
from numbat.report import render_review_report


def test_render_review_report_includes_summary_and_files() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/a.py", additions=4, deletions=1, binary=False),
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
            FileChange(path="bin.dat", additions=0, deletions=0, binary=True),
        )
    )

    report = render_review_report(summary)

    assert "Review Report" in report
    assert "Files changed: 3" in report
    assert "Lines added: 6" in report
    assert "Lines deleted: 1" in report
    assert "Total lines changed: 7" in report
    assert "src/a.py  [source]  +4 -1" in report
    assert "tests/test_a.py  [tests]  +2 -0" in report
    assert "bin.dat  [other]  (binary)" in report
    assert "Focus / Risk" in report
    assert "[tests_touched]" in report
    assert "Changes" in report


def test_render_review_report_includes_changes_section() -> None:
    from numbat.diff_parser import DiffContent, DiffHunk, FileDiffContent

    summary = DiffSummary(
        files=(FileChange(path="README.md", additions=1, deletions=0, binary=False),)
    )
    diff_content = DiffContent(
        files=(
            FileDiffContent(
                path="README.md",
                hunks=(DiffHunk(header="@@ -1 +1 @@", lines=("+extra line",)),),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    report = render_review_report(summary, diff_content=diff_content)

    assert "Changes" in report
    assert "README.md" in report
    assert "+extra line" in report
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
