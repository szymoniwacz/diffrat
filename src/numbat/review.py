"""Review command: orchestrate git adapter, parser, and renderer."""

from __future__ import annotations

import sys

from numbat.diff_parser import DiffSummary, parse_numstat
from numbat.git_adapter import GitError, get_diff_numstat
from numbat.report import render_review_report

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_EMPTY_DIFF = 2


def run_review(*, staged: bool, cwd: str | None = None) -> int:
    """Analyze a git diff and print a review report to stdout."""
    try:
        diff_result = get_diff_numstat(staged=staged, cwd=cwd)
    except GitError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ERROR

    summary = parse_numstat(diff_result.numstat)
    if _is_empty_diff(summary):
        scope = "staged" if staged else "unstaged"
        print(f"no {scope} changes to review", file=sys.stderr)
        return EXIT_EMPTY_DIFF

    sys.stdout.write(render_review_report(summary))
    return EXIT_SUCCESS


def _is_empty_diff(summary: DiffSummary) -> bool:
    return summary.file_count == 0
