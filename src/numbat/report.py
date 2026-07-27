"""Report renderer: human-readable review output."""

from __future__ import annotations

from numbat.analysis import AnalysisResult, analyze_diff
from numbat.diff_parser import DiffSummary
from numbat.git_adapter import GitContext


def render_review_report(
    summary: DiffSummary,
    *,
    git_context: GitContext | None = None,
    analysis: AnalysisResult | None = None,
) -> str:
    """Render a review-oriented text report for stdout."""
    result = analysis if analysis is not None else analyze_diff(summary)

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

    lines.extend(["", "Focus / Risk", "------------"])
    if not result.hints:
        lines.append("(none)")
    else:
        for hint in result.hints:
            lines.append(f"- [{hint.code}] {hint.message}")

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
