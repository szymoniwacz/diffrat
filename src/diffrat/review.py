"""Review command: orchestrate git adapter, parser, and renderer."""

from __future__ import annotations

import sys
from pathlib import Path

from diffrat.analysis_backend import run_analysis
from diffrat.checks import CheckResult, plan_checks, run_checks
from diffrat.config import load_config
from diffrat.diff_parser import (
    HUNKS_FOR_MAX_LINES_PER_FILE,
    DiffSummary,
    parse_numstat,
    parse_unified_diff,
)
from diffrat.git_adapter import (
    GitContext,
    GitError,
    get_diff_numstat,
    get_diff_numstat_for_range,
    get_diff_numstat_vs_base,
    get_git_context,
    get_git_context_for_range,
    parse_range_spec,
)
from diffrat.json_renderer import render_review_json
from diffrat.report import render_review_report

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_EMPTY_DIFF = 2
EXIT_CHECK_FAILED = 3
EXIT_FAIL_ON_MATCH = 4


def parse_fail_on_codes(raw: str) -> tuple[list[str] | None, str | None]:
    """Parse comma-separated hint codes for --fail-on.

    Returns (codes, error_message). On error, codes is None.
    """
    if not raw:
        return None, "invalid --fail-on: expected comma-separated hint codes"

    codes: list[str] = []
    for token in raw.split(","):
        if not token or token != token.strip() or any(char.isspace() for char in token):
            return None, f"invalid --fail-on token: {token!r}"
        codes.append(token)

    return codes, None


def matched_fail_on_codes(
    requested: list[str],
    hint_codes: set[str],
) -> list[str]:
    """Return requested codes that appear in the report hints, in request order."""
    return [code for code in requested if code in hint_codes]


def run_review(
    *,
    staged: bool = False,
    base: str | None = None,
    range_spec: str | None = None,
    brief: bool = False,
    json_output: bool = False,
    run_checks_flag: bool = False,
    fail_on: str | None = None,
    hunks_for: str | None = None,
    cwd: str | None = None,
) -> int:
    """Analyze a git diff and print a review report to stdout."""
    if staged and base is not None:
        print("cannot use --staged with --base", file=sys.stderr)
        return EXIT_ERROR
    if staged and range_spec is not None:
        print("cannot use --staged with --range", file=sys.stderr)
        return EXIT_ERROR
    if base is not None and range_spec is not None:
        print("cannot use --base with --range", file=sys.stderr)
        return EXIT_ERROR
    if brief and hunks_for is not None:
        print("cannot use --brief with --hunks-for", file=sys.stderr)
        return EXIT_ERROR

    fail_on_codes: list[str] | None = None
    if fail_on is not None:
        fail_on_codes, fail_on_error = parse_fail_on_codes(fail_on)
        if fail_on_error is not None:
            print(fail_on_error, file=sys.stderr)
            return EXIT_ERROR

    git_context: GitContext | None = None

    try:
        if range_spec is not None:
            from_ref, to_ref = parse_range_spec(range_spec)
            diff_result = get_diff_numstat_for_range(from_ref, to_ref, cwd=cwd)
            git_context = get_git_context_for_range(from_ref, to_ref, cwd=cwd)
        elif base is not None:
            diff_result = get_diff_numstat_vs_base(base, cwd=cwd)
            git_context = get_git_context(base, cwd=cwd)
        else:
            diff_result = get_diff_numstat(staged=staged, cwd=cwd)
    except GitError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_ERROR

    summary = parse_numstat(diff_result.numstat, name_status=diff_result.name_status)
    if _is_empty_diff(summary):
        if range_spec is not None:
            print(f"no changes in range {range_spec}", file=sys.stderr)
        elif base is not None:
            print(f"no changes on branch since {base}", file=sys.stderr)
        else:
            scope = "staged" if staged else "unstaged"
            print(f"no {scope} changes to review", file=sys.stderr)
        return EXIT_EMPTY_DIFF

    diff_content = parse_unified_diff(diff_result.patch)
    changes_diff_content = diff_content
    if hunks_for is not None:
        changed_paths = {file_change.path for file_change in summary.files}
        if hunks_for not in changed_paths:
            print(f"path not in diff: {hunks_for}", file=sys.stderr)
            return EXIT_ERROR
        changes_diff_content = parse_unified_diff(
            diff_result.patch,
            only_paths=frozenset({hunks_for}),
            max_lines_per_file_by_path={hunks_for: HUNKS_FOR_MAX_LINES_PER_FILE},
        )
    config_cwd = cwd if cwd is not None else str(Path.cwd())
    diffrat_config = load_config(config_cwd)
    analysis = run_analysis(
        summary,
        diff_content=diff_content,
        cwd=cwd,
        git_context=git_context,
        config=diffrat_config,
    )
    check_results: list[CheckResult] | None = None
    if run_checks_flag:
        check_results = run_checks(
            plan_checks(summary, config=diffrat_config),
            cwd=cwd,
        )

    matched_codes: list[str] | None = None
    if fail_on_codes is not None:
        matched_codes = matched_fail_on_codes(
            fail_on_codes,
            {hint.code for hint in analysis.hints},
        )

    if json_output:
        if range_spec is not None:
            mode = "range"
        elif base is not None:
            mode = "branch"
        else:
            mode = "staged" if staged else "unstaged"
        output = render_review_json(
            summary,
            mode=mode,
            git_context=git_context,
            analysis=analysis,
            diff_content=None if brief else changes_diff_content,
            changes_limits_max_lines_per_file=(
                HUNKS_FOR_MAX_LINES_PER_FILE if hunks_for is not None else None
            ),
            check_results=check_results,
            fail_on_requested=fail_on_codes,
            fail_on_matched=matched_codes,
            brief=brief,
        )
    else:
        output = render_review_report(
            summary,
            git_context=git_context,
            analysis=analysis,
            diff_content=changes_diff_content,
            check_results=check_results,
            brief=brief,
        )

    sys.stdout.write(output)
    if check_results is not None:
        _write_check_failures_to_stderr(check_results)
        if any(not result.passed for result in check_results):
            return EXIT_CHECK_FAILED
    if matched_codes:
        return EXIT_FAIL_ON_MATCH
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
