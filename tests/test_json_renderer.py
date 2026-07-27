"""Tests for JSON report renderer."""

from __future__ import annotations

import json

from numbat.diff_parser import DiffSummary, FileChange
from numbat.git_adapter import GitCommitInfo, GitContext
from numbat.json_renderer import JSON_SCHEMA_VERSION, render_review_json


def test_render_review_json_unstaged_mode() -> None:
    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=4, deletions=1, binary=False),)
    )

    output = render_review_json(summary, mode="unstaged")
    payload = json.loads(output)

    assert payload["schema_version"] == JSON_SCHEMA_VERSION
    assert payload["mode"] == "unstaged"
    assert payload["summary"] == {
        "file_count": 1,
        "total_additions": 4,
        "total_deletions": 1,
    }
    assert payload["files"] == [{"path": "src/a.py", "additions": 4, "deletions": 1}]
    assert "git_context" not in payload


def test_render_review_json_includes_git_context() -> None:
    summary = DiffSummary(
        files=(FileChange(path="feature.txt", additions=2, deletions=0, binary=False),)
    )
    git_context = GitContext(
        branch="feature",
        base_ref="main",
        commit_count=2,
        commits=(
            GitCommitInfo(short_hash="abc1234", subject="second commit"),
            GitCommitInfo(short_hash="def5678", subject="first commit"),
        ),
    )

    output = render_review_json(summary, mode="branch", git_context=git_context)
    payload = json.loads(output)

    assert payload["mode"] == "branch"
    assert payload["git_context"] == {
        "branch": "feature",
        "base": "main",
        "commit_count": 2,
        "commits": [
            {"hash": "abc1234", "subject": "second commit"},
            {"hash": "def5678", "subject": "first commit"},
        ],
    }
