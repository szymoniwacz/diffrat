"""JSON report renderer for machine-readable review output."""

from __future__ import annotations

import json

from numbat.diff_parser import DiffSummary
from numbat.git_adapter import GitContext

JSON_SCHEMA_VERSION = "1"


def render_review_json(
    summary: DiffSummary,
    *,
    mode: str,
    git_context: GitContext | None = None,
) -> str:
    """Render a review report as a JSON document for stdout."""
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
            }
            for file_change in summary.files
        ],
    }

    if git_context is not None:
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
