"""Review command: orchestrate git adapter, parser, and renderer."""

from __future__ import annotations

import sys

from numbat.analysis import analyze_diff
from numbat.diff_parser import DiffSummary, parse_numstat, parse_unified_diff
from numbat.git_adapter import (
    GitContext,
    GitError,
    get_diff_numstat,
    get_diff_numstat_vs_base,
    get_git_context,
)
from numbat.json_renderer import render_review_json
from numbat.report import render_review_report

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_EMPTY_DIFF = 2


def run_review(
    *,
    staged: bool = False,
    base: str | None = None,
    json_output: bool = False,
    cwd: str | None = None,
) -> int:
    """Analyze a git diff and print a review report to stdout."""
    if staged and base is not None:
        print("cannot use --staged with --base", file=sys.stderr)
        return EXIT_ERROR

    git_context: GitContext | None = None

    try:
        if base is not None:
            diff_result = get_diff_numstat_vs_base(base, cwd=cwd)
            git_context = get_git_context(base, cwd=cwd)
        else:
            diff_result = get_diff_numstat(staged=staged, cwd=cwd)
    except GitError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ERROR

    summary = parse_numstat(diff_result.numstat)
    if _is_empty_diff(summary):
        if base is not None:
            print(f"no changes on branch since {base}", file=sys.stderr)
        else:
            scope = "staged" if staged else "unstaged"
            print(f"no {scope} changes to review", file=sys.stderr)
        return EXIT_EMPTY_DIFF

    diff_content = parse_unified_diff(diff_result.patch)
    analysis = analyze_diff(summary)
    if json_output:
        mode = "branch" if base is not None else ("staged" if staged else "unstaged")
        output = render_review_json(
            summary,
            mode=mode,
            git_context=git_context,
            analysis=analysis,
            diff_content=diff_content,
        )
    else:
        output = render_review_report(
            summary,
            git_context=git_context,
            analysis=analysis,
            diff_content=diff_content,
        )

    sys.stdout.write(output)
    return EXIT_SUCCESS


def _is_empty_diff(summary: DiffSummary) -> bool:
    return summary.file_count == 0
