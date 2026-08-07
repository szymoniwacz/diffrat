"""JSON report renderer for machine-readable review output."""

from __future__ import annotations

import json

from diffrat.analysis import AnalysisResult, FocusRiskHint, sort_hints
from diffrat.analysis_backend import run_analysis
from diffrat.checks import CheckResult
from diffrat.diff_parser import (
    MAX_CHANGE_FILES,
    MAX_LINES_PER_FILE,
    DiffContent,
    DiffSummary,
)
from diffrat.git_adapter import GitContext
from diffrat.scoring import (
    files_by_category_mapping,
    review_order_entries,
    sort_file_entries,
)

JSON_SCHEMA_VERSION = "1"


def _serialize_focus_risk_hint(hint: FocusRiskHint) -> dict[str, object]:
    entry: dict[str, object] = {
        "code": hint.code,
        "message": hint.message,
        "severity": hint.severity,
    }
    if hint.path is not None:
        entry["path"] = hint.path
    if hint.line is not None:
        entry["line"] = hint.line
    return entry


def render_review_json(
    summary: DiffSummary,
    *,
    mode: str,
    git_context: GitContext | None = None,
    analysis: AnalysisResult | None = None,
    diff_content: DiffContent | None = None,
    changes_limits_max_lines_per_file: int | None = None,
    check_results: list[CheckResult] | None = None,
    fail_on_requested: list[str] | None = None,
    fail_on_matched: list[str] | None = None,
    brief: bool = False,
) -> str:
    """Render a review report as a JSON document for stdout."""
    result = (
        analysis
        if analysis is not None
        else run_analysis(summary, diff_content=diff_content)
    )

    sorted_entries = sort_file_entries(
        summary.files, result.categories, result.risk_scores
    )
    sorted_paths = [entry[0].path for entry in sorted_entries]
    review_order = [entry[0].path for entry in review_order_entries(sorted_entries)]

    if brief:
        changes_payload: dict[str, object] = {
            "limits": {
                "max_files": MAX_CHANGE_FILES,
                "max_lines_per_file": (
                    changes_limits_max_lines_per_file
                    if changes_limits_max_lines_per_file is not None
                    else MAX_LINES_PER_FILE
                ),
            },
            "truncated_files": False,
            "files": [],
        }
    else:
        changes_payload = _serialize_changes(
            diff_content,
            sort_paths=sorted_paths,
            max_lines_per_file_limit=changes_limits_max_lines_per_file,
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
                "risk_score": risk_score,
            }
            for file_change, category, risk_score in sorted_entries
        ],
        "review_order": review_order,
        "files_by_category": files_by_category_mapping(sorted_entries),
        "focus_risk": [
            _serialize_focus_risk_hint(hint)
            for hint in sort_hints(list(result.hints))
        ],
        "changes": changes_payload,
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

    if fail_on_requested is not None:
        payload["fail_on"] = {
            "requested": list(fail_on_requested),
            "matched": list(fail_on_matched or []),
        }

    if result.llm_findings is not None:
        payload["llm_findings"] = result.llm_findings

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


def _serialize_changes(
    diff_content: DiffContent | None,
    *,
    sort_paths: list[str] | None = None,
    max_lines_per_file_limit: int | None = None,
) -> dict[str, object]:
    limits = {
        "max_files": MAX_CHANGE_FILES,
        "max_lines_per_file": (
            max_lines_per_file_limit
            if max_lines_per_file_limit is not None
            else MAX_LINES_PER_FILE
        ),
    }
    if diff_content is None:
        return {"limits": limits, "truncated_files": False, "files": []}

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

    files_payload: list[dict[str, object]] = []
    for path in path_order:
        file_diff = file_diffs_by_path[path]
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
