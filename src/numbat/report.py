"""Report renderer: human-readable review output."""

from __future__ import annotations

from numbat.analysis import AnalysisResult, analyze_diff
from numbat.checks import CheckResult
from numbat.diff_parser import DiffContent, DiffSummary
from numbat.git_adapter import GitContext


def render_review_report(
    summary: DiffSummary,
    *,
    git_context: GitContext | None = None,
    analysis: AnalysisResult | None = None,
    diff_content: DiffContent | None = None,
    check_results: list[CheckResult] | None = None,
) -> str:
    """Render a review-oriented text report for stdout."""
    result = (
        analysis
        if analysis is not None
        else analyze_diff(summary, diff_content=diff_content)
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

    if not summary.files:
        lines.append("(no files changed)")
    else:
        for file_change, category in zip(summary.files, result.categories, strict=True):
            if file_change.binary:
                lines.append(f"{file_change.path}  [{category}]  (binary)")
            else:
                lines.append(
                    f"{file_change.path}  [{category}]  "
                    f"+{file_change.additions} -{file_change.deletions}"
                )

    lines.extend(["", "Changes", "-------"])
    lines.extend(_render_changes(diff_content))

    lines.extend(["", "Focus / Risk", "------------"])
    if not result.hints:
        lines.append("(none)")
    else:
        for hint in result.hints:
            lines.append(f"- [{hint.code}] {hint.message}")

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


def _render_git_context(git_context: GitContext) -> list[str]:
    lines = [
        "Git context",
        "-----------",
        f"Branch: {git_context.branch}",
        f"Base: {git_context.base_ref}",
        f"Commits since base: {git_context.commit_count}",
    ]

    if git_context.commits:
        lines.append("Recent commits:")
        for commit in git_context.commits:
            lines.append(f"  {commit.short_hash} {commit.subject}")
    else:
        lines.append("Recent commits: (none)")

    return lines


def _render_changes(diff_content: DiffContent | None) -> list[str]:
    if diff_content is None or not diff_content.files:
        return ["(no change content)"]

    lines: list[str] = []
    for file_diff in diff_content.files:
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
