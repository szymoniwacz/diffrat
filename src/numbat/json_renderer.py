"""JSON report renderer for machine-readable review output."""

from __future__ import annotations

import json

from numbat.analysis import AnalysisResult, analyze_diff
from numbat.checks import CheckResult
from numbat.diff_parser import (
    MAX_CHANGE_FILES,
    MAX_LINES_PER_FILE,
    DiffContent,
    DiffSummary,
)
from numbat.git_adapter import GitContext

JSON_SCHEMA_VERSION = "1"


def render_review_json(
    summary: DiffSummary,
    *,
    mode: str,
    git_context: GitContext | None = None,
    analysis: AnalysisResult | None = None,
    diff_content: DiffContent | None = None,
    check_results: list[CheckResult] | None = None,
) -> str:
    """Render a review report as a JSON document for stdout."""
    result = (
        analysis
        if analysis is not None
        else analyze_diff(summary, diff_content=diff_content)
    )

    payload: dict[str, object] = {
        "schema_version": JSON_SCHEMA_VERSION,
        "mode": mode,
        "summary": {
            "file_count": summary.file_count,
            "total_additions": summary.total_additions,
            "total_deletions": summary.total_deletions,
        },
        "files": [
            {
                "path": file_change.path,
                "additions": file_change.additions,
                "deletions": file_change.deletions,
                "category": category,
            }
            for file_change, category in zip(summary.files, result.categories, strict=True)
        ],
        "focus_risk": [
            {"code": hint.code, "message": hint.message} for hint in result.hints
        ],
        "changes": _serialize_changes(diff_content),
    }

    if check_results is not None:
        payload["checks"] = [
            {
                "code": check.code,
                "command": check.command,
                "passed": check.passed,
                "output": check.output,
                **({"skipped": True} if check.skipped else {}),
            }
            for check in check_results
        ]

    if git_context is not None:
        if git_context.range_spec is not None:
            payload["git_context"] = {
                "range": git_context.range_spec,
                "from_ref": git_context.from_ref,
                "to_ref": git_context.to_ref,
                "commit_count": git_context.commit_count,
                "commits": [
                    {"hash": commit.short_hash, "subject": commit.subject}
                    for commit in git_context.commits
                ],
            }
        else:
            payload["git_context"] = {
                "branch": git_context.branch,
                "base": git_context.base_ref,
                "commit_count": git_context.commit_count,
                "commits": [
                    {"hash": commit.short_hash, "subject": commit.subject}
                    for commit in git_context.commits
                ],
            }

    return json.dumps(payload, indent=2) + "\n"


def _serialize_changes(diff_content: DiffContent | None) -> dict[str, object]:
    limits = {
        "max_files": MAX_CHANGE_FILES,
        "max_lines_per_file": MAX_LINES_PER_FILE,
    }
    if diff_content is None:
        return {"limits": limits, "truncated_files": False, "files": []}

    files_payload: list[dict[str, object]] = []
    for file_diff in diff_content.files:
        entry: dict[str, object] = {
            "path": file_diff.path,
            "binary": file_diff.binary,
            "truncated": file_diff.truncated,
        }
        if not file_diff.binary:
            entry["hunks"] = [
                {
                    "header": hunk.header,
                    "lines": list(hunk.lines),
                }
                for hunk in file_diff.hunks
            ]
        files_payload.append(entry)

    return {
        "limits": limits,
        "truncated_files": diff_content.truncated_files,
        "files": files_payload,
    }
