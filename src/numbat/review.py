"""Review command: orchestrate git adapter, parser, and renderer."""

from __future__ import annotations

import sys

from numbat.analysis import analyze_diff
from numbat.checks import CheckResult, plan_checks, run_checks
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
EXIT_CHECK_FAILED = 3


def run_review(
    *,
    staged: bool = False,
    base: str | None = None,
    json_output: bool = False,
    run_checks_flag: bool = False,
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
    check_results: list[CheckResult] | None = None
    if run_checks_flag:
        check_results = run_checks(plan_checks(summary), cwd=cwd)
    if json_output:
        mode = "branch" if base is not None else ("staged" if staged else "unstaged")
        output = render_review_json(
            summary,
            mode=mode,
            git_context=git_context,
            analysis=analysis,
            diff_content=diff_content,
            check_results=check_results,
        )
    else:
        output = render_review_report(
            summary,
            git_context=git_context,
            analysis=analysis,
            diff_content=diff_content,
            check_results=check_results,
        )

    sys.stdout.write(output)
    if check_results is not None:
        _write_check_failures_to_stderr(check_results)
        if any(not result.passed for result in check_results):
            return EXIT_CHECK_FAILED
    return EXIT_SUCCESS


def _is_empty_diff(summary: DiffSummary) -> bool:
    return summary.file_count == 0


def _write_check_failures_to_stderr(check_results: list[CheckResult]) -> None:
    for result in check_results:
        if result.passed:
            continue
        print(f"check failed: {result.code}", file=sys.stderr)
        print(f"command: {result.command}", file=sys.stderr)
        if result.output:
            print(result.output, file=sys.stderr)
