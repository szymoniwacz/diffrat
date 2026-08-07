"""Report renderer: human-readable review output."""

from __future__ import annotations

from diffrat.analysis import AnalysisResult, sort_hints
from diffrat.analysis_backend import run_analysis
from diffrat.checks import CheckResult
from diffrat.diff_parser import DiffContent, DiffSummary, FileChange
from diffrat.git_adapter import GitContext
from diffrat.scoring import (
    group_entries_by_category,
    review_order_entries,
    sort_file_entries,
)


def render_review_report(
    summary: DiffSummary,
    *,
    git_context: GitContext | None = None,
    analysis: AnalysisResult | None = None,
    diff_content: DiffContent | None = None,
    check_results: list[CheckResult] | None = None,
    brief: bool = False,
) -> str:
    """Render a review-oriented text report for stdout."""
    result = (
        analysis
        if analysis is not None
        else run_analysis(summary, diff_content=diff_content)
    )

    lines = [
        "Review Report",
        "=============",
        "",
    ]

    if git_context is not None:
        lines.extend(_render_git_context(git_context))
        lines.append("")

    lines.extend(
        [
            "Summary",
            "-------",
            f"Files changed: {summary.file_count}",
            f"Lines added: {summary.total_additions}",
            f"Lines deleted: {summary.total_deletions}",
            f"Total lines changed: {summary.total_lines_changed}",
            "",
            "Files",
            "-----",
        ]
    )

    sorted_entries = (
        sort_file_entries(summary.files, result.categories, result.risk_scores)
        if summary.files
        else []
    )

    if not sorted_entries:
        lines.append("(no files changed)")
    else:
        for category, entries in group_entries_by_category(sorted_entries):
            lines.append(category)
            for file_change, entry_category, risk_score in entries:
                lines.append(_format_file_line(file_change, entry_category, risk_score))

    lines.extend(["", "Review order", "------------"])
    if not sorted_entries:
        lines.append("(no files changed)")
    else:
        for rank, (file_change, category, _risk_score) in enumerate(
            review_order_entries(sorted_entries), start=1
        ):
            if file_change.binary:
                lines.append(
                    f"{rank}. {file_change.path}  [{category}]  (binary)"
                )
            else:
                lines.append(
                    f"{rank}. {file_change.path}  [{category}]  "
                    f"(+{file_change.additions} -{file_change.deletions} lines)"
                )

    if not brief:
        lines.extend(["", "Changes", "-------"])
        sorted_paths = [entry[0].path for entry in sorted_entries]
        lines.extend(_render_changes(diff_content, sort_paths=sorted_paths))

    lines.extend(["", "Focus / Risk", "------------"])
    sorted_hints = sort_hints(list(result.hints))
    if not sorted_hints:
        lines.append("(none)")
    else:
        for hint in sorted_hints:
            lines.append(f"- [{hint.severity}] [{hint.code}] {hint.message}")

    if result.llm_findings is not None:
        lines.extend(["", "LLM analysis", "-------------"])
        lines.extend(result.llm_findings.splitlines())

    if check_results is not None:
        lines.extend(["", "Local checks", "------------"])
        if not check_results:
            lines.append("(none applicable)")
        else:
            for check in check_results:
                if check.skipped:
                    status = "skipped"
                elif check.passed:
                    status = "passed"
                else:
                    status = "failed"
                lines.append(f"- [{check.code}] {status}: {check.command}")
                if check.skipped and check.output:
                    lines.append(f"  {check.output}")
                elif not check.passed and check.output:
                    for output_line in check.output.splitlines():
                        lines.append(f"  {output_line}")

    return "\n".join(lines) + "\n"


def _format_file_line(
    file_change: FileChange,
    category: str,
    risk_score: int,
) -> str:
    if file_change.binary:
        return (
            f"  {file_change.path}  [{category}]  risk={risk_score}  (binary)"
        )
    return (
        f"  {file_change.path}  [{category}]  risk={risk_score}  "
        f"+{file_change.additions} -{file_change.deletions}"
    )


def _render_git_context(git_context: GitContext) -> list[str]:
    lines = [
        "Git context",
        "-----------",
    ]

    if git_context.range_spec is not None:
        lines.extend(
            [
                f"Range: {git_context.range_spec}",
                f"From: {git_context.from_ref}",
                f"To: {git_context.to_ref}",
                f"Commits in range: {git_context.commit_count}",
            ]
        )
    else:
        lines.extend(
            [
                f"Branch: {git_context.branch}",
                f"Base: {git_context.base_ref}",
                f"Commits since base: {git_context.commit_count}",
            ]
        )

    if git_context.commits:
        lines.append("Recent commits:")
        for commit in git_context.commits:
            lines.append(f"  {commit.short_hash} {commit.subject}")
    else:
        lines.append("Recent commits: (none)")

    return lines


def _render_changes(
    diff_content: DiffContent | None,
    *,
    sort_paths: list[str] | None = None,
) -> list[str]:
    if diff_content is None or not diff_content.files:
        return ["(no change content)"]

    file_diffs_by_path = {file_diff.path: file_diff for file_diff in diff_content.files}
    if sort_paths is not None:
        ordered_paths = [path for path in sort_paths if path in file_diffs_by_path]
        remaining = [
            file_diff.path
            for file_diff in diff_content.files
            if file_diff.path not in set(ordered_paths)
        ]
        path_order = ordered_paths + remaining
    else:
        path_order = [file_diff.path for file_diff in diff_content.files]

    lines: list[str] = []
    for path in path_order:
        file_diff = file_diffs_by_path[path]
        lines.append(file_diff.path)
        if file_diff.binary:
            lines.append("(binary)")
        else:
            for hunk in file_diff.hunks:
                lines.append(hunk.header)
                lines.extend(hunk.lines)
            if file_diff.truncated:
                lines.append("(truncated — diff lines limit reached for this file)")
        lines.append("")

    if diff_content.truncated_files:
        lines.append("(truncated — file limit reached; not all changed files shown)")

    return lines
