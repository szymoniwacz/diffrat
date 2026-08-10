"""Tests for JSON report renderer."""

from __future__ import annotations

import json

from diffrat.diff_parser import DiffSummary, FileChange
from diffrat.git_adapter import GitCommitInfo, GitContext
from diffrat.json_renderer import JSON_SCHEMA_VERSION, render_review_json


def test_render_review_json_unstaged_mode() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/a.py", additions=4, deletions=1, binary=False),
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
        )
    )

    output = render_review_json(summary, mode="unstaged")
    payload = json.loads(output)

    assert payload["schema_version"] == JSON_SCHEMA_VERSION
    assert payload["mode"] == "unstaged"
    assert payload["summary"] == {
        "file_count": 2,
        "total_additions": 6,
        "total_deletions": 1,
    }
    files = payload["files"]
    assert len(files) == 2
    assert files[0]["path"] == "src/a.py"
    assert files[0]["category"] == "source"
    assert files[0]["risk_score"] >= files[1]["risk_score"]
    assert files[1]["path"] == "tests/test_a.py"
    assert "risk_score" in files[0]
    assert "risk_score" in files[1]
    assert any(hint["code"] == "tests_touched" for hint in payload["focus_risk"])
    assert "git_context" not in payload
    assert payload["changes"]["limits"] == {"max_files": 20, "max_lines_per_file": 100}
    assert payload["changes"]["truncated_files"] is False


def test_render_review_json_includes_changes() -> None:
    from diffrat.diff_parser import DiffContent, DiffHunk, FileDiffContent

    summary = DiffSummary(
        files=(FileChange(path="README.md", additions=1, deletions=0, binary=False),)
    )
    diff_content = DiffContent(
        files=(
            FileDiffContent(
                path="README.md",
                hunks=(DiffHunk(header="@@ -1 +1 @@", lines=("+extra line",)),),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    payload = json.loads(render_review_json(summary, mode="unstaged", diff_content=diff_content))

    assert payload["changes"]["files"][0]["path"] == "README.md"
    assert payload["changes"]["files"][0]["hunks"][0]["lines"] == ["+extra line"]


def test_render_review_json_brief_empties_changes_files() -> None:
    from diffrat.diff_parser import DiffContent, DiffHunk, FileDiffContent

    summary = DiffSummary(
        files=(FileChange(path="README.md", additions=1, deletions=0, binary=False),)
    )
    diff_content = DiffContent(
        files=(
            FileDiffContent(
                path="README.md",
                hunks=(DiffHunk(header="@@ -1 +1 @@", lines=("+extra line",)),),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    payload = json.loads(
        render_review_json(
            summary,
            mode="unstaged",
            diff_content=diff_content,
            brief=True,
        )
    )

    assert payload["summary"]["file_count"] == 1
    assert payload["review_order"] == ["README.md"]
    assert payload["focus_risk"]
    assert payload["changes"]["limits"] == {"max_files": 20, "max_lines_per_file": 100}
    assert payload["changes"]["truncated_files"] is False
    assert payload["changes"]["files"] == []


def test_render_review_json_includes_categories_and_focus_risk() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
            FileChange(path=".env", additions=1, deletions=0, binary=False),
        )
    )

    payload = json.loads(render_review_json(summary, mode="unstaged"))

    categories = {item["path"]: item["category"] for item in payload["files"]}
    assert categories["tests/test_a.py"] == "tests"
    assert categories[".env"] == "config"
    assert payload["files"][0]["path"] == ".env"
    codes = [item["code"] for item in payload["focus_risk"]]
    assert "tests_touched" in codes
    assert "config_or_deps" in codes
    assert "security_sensitive_paths" in codes
    assert all("severity" in item for item in payload["focus_risk"])
    assert payload["focus_risk"][0]["severity"] == "risk"
    assert "git_context" not in payload
    for item in payload["focus_risk"]:
        assert "path" not in item
        assert "line" not in item
    review_quality = payload["review_quality"]
    assert [p["id"] for p in review_quality["pillars"]] == [
        "understand",
        "focused",
        "maintainable",
    ]
    maintainable = next(p for p in review_quality["pillars"] if p["id"] == "maintainable")
    assert maintainable["status"] == "risk"
    assert "security_sensitive_paths" in maintainable["codes"]
    assert payload["schema_version"] == JSON_SCHEMA_VERSION


def test_render_review_json_review_quality_shape() -> None:
    from diffrat.analysis import AnalysisResult, focus_risk_hint

    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=4, deletions=1, binary=False),)
    )
    analysis = AnalysisResult(
        categories=("source",),
        risk_scores=(10,),
        hints=(
            focus_risk_hint("large_diff", "Large diff", severity="warn"),
            focus_risk_hint("docs_touched", "Docs", severity="info"),
        ),
        llm_findings=None,
        llm_error=None,
    )
    payload = json.loads(render_review_json(summary, mode="unstaged", analysis=analysis))
    pillars = payload["review_quality"]["pillars"]
    understand = next(p for p in pillars if p["id"] == "understand")
    assert understand == {
        "id": "understand",
        "label": "Understand in seconds",
        "status": "warn",
        "codes": ["large_diff"],
    }
    focused = next(p for p in pillars if p["id"] == "focused")
    assert focused["status"] == "ok"
    assert focused["codes"] == []


def test_render_review_json_focus_risk_includes_path_and_line_when_set() -> None:
    from diffrat.analysis import AnalysisResult, focus_risk_hint

    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=1, deletions=0, binary=False),)
    )
    analysis = AnalysisResult(
        categories=("source",),
        hints=(
            focus_risk_hint(
                "possible_secret",
                "Possible secret in src/a.py",
                path="src/a.py",
                line=10,
            ),
            focus_risk_hint("docs_touched", "Documentation changed"),
        ),
        risk_scores=(10,),
    )

    payload = json.loads(render_review_json(summary, mode="unstaged", analysis=analysis))

    secret_hint = next(item for item in payload["focus_risk"] if item["code"] == "possible_secret")
    assert secret_hint["path"] == "src/a.py"
    assert secret_hint["line"] == 10

    docs_hint = next(item for item in payload["focus_risk"] if item["code"] == "docs_touched")
    assert "path" not in docs_hint
    assert "line" not in docs_hint


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


def test_render_review_json_includes_range_git_context() -> None:
    summary = DiffSummary(
        files=(FileChange(path="feature.txt", additions=2, deletions=0, binary=False),)
    )
    git_context = GitContext(
        commit_count=2,
        commits=(
            GitCommitInfo(short_hash="abc1234", subject="second commit"),
            GitCommitInfo(short_hash="def5678", subject="first commit"),
        ),
        range_spec="main..feature",
        from_ref="main",
        to_ref="feature",
    )

    output = render_review_json(summary, mode="range", git_context=git_context)
    payload = json.loads(output)

    assert payload["mode"] == "range"
    assert payload["git_context"] == {
        "range": "main..feature",
        "from_ref": "main",
        "to_ref": "feature",
        "commit_count": 2,
        "commits": [
            {"hash": "abc1234", "subject": "second commit"},
            {"hash": "def5678", "subject": "first commit"},
        ],
    }


def test_render_review_json_includes_review_order_and_files_by_category() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
            FileChange(path="src/a.py", additions=4, deletions=1, binary=False),
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
            FileChange(path="ci/run.py", additions=1, deletions=0, binary=False),
            FileChange(path="README.md", additions=1, deletions=0, binary=False),
            FileChange(path="bin.dat", additions=0, deletions=0, binary=True),
        )
    )

    payload = json.loads(render_review_json(summary, mode="unstaged"))

    assert len(payload["review_order"]) == 5
    assert payload["review_order"] == [entry["path"] for entry in payload["files"][:5]]
    assert list(payload["files_by_category"].keys()) == [
        "source",
        "tests",
        "ci",
        "config",
        "docs",
        "other",
    ]
    assert payload["files_by_category"]["source"] == ["src/a.py"]
    assert payload["files_by_category"]["tests"] == ["tests/test_a.py"]
    assert payload["files_by_category"]["ci"] == ["ci/run.py"]
    assert payload["files_by_category"]["other"] == ["bin.dat"]


def test_render_review_json_includes_llm_findings_when_present() -> None:
    from dataclasses import replace

    from diffrat.analysis import analyze_diff

    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=1, deletions=0, binary=False),)
    )
    analysis = replace(analyze_diff(summary), llm_findings="LLM narrative.")

    payload = json.loads(render_review_json(summary, mode="unstaged", analysis=analysis))

    assert payload["llm_findings"] == "LLM narrative."
    assert payload["llm_status"] == "ok"


def test_render_review_json_includes_llm_error_when_present() -> None:
    from dataclasses import replace

    from diffrat.analysis import analyze_diff

    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=1, deletions=0, binary=False),)
    )
    analysis = replace(
        analyze_diff(summary),
        llm_error="LLM authentication failed (HTTP 401)",
    )

    payload = json.loads(render_review_json(summary, mode="unstaged", analysis=analysis))

    assert payload["llm_status"] == "failed"
    assert payload["llm_error"] == "LLM authentication failed (HTTP 401)"
    assert "llm_findings" not in payload


def test_render_review_json_omits_llm_findings_when_absent() -> None:
    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=1, deletions=0, binary=False),)
    )

    payload = json.loads(render_review_json(summary, mode="unstaged"))

    assert "llm_findings" not in payload
    assert "llm_status" not in payload
    assert "llm_error" not in payload
