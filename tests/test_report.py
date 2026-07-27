"""Tests for report renderer."""

from __future__ import annotations

from numbat.diff_parser import DiffSummary, FileChange
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
    assert "src/a.py  +4 -1" in report
    assert "bin.dat  (binary)" in report
