"""Tests for deterministic analysis helpers."""

from __future__ import annotations

from numbat.analysis import (
    LARGE_DIFF_FILE_THRESHOLD,
    LARGE_DIFF_LINE_THRESHOLD,
    analyze_diff,
    categorize_path,
)
from numbat.diff_parser import DiffSummary, FileChange


def test_categorize_path_assigns_expected_buckets() -> None:
    assert categorize_path("src/numbat/review.py") == "source"
    assert categorize_path("tests/test_review.py") == "tests"
    assert categorize_path("test_helpers.py") == "tests"
    assert categorize_path("pyproject.toml") == "config"
    assert categorize_path("requirements.txt") == "config"
    assert categorize_path(".env.local") == "config"
    assert categorize_path("README.md") == "docs"
    assert categorize_path("docs/guide.md") == "docs"
    assert categorize_path("assets/logo.png") == "other"


def test_analyze_diff_emits_focus_risk_hints() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_cli.py", additions=10, deletions=2, binary=False),
            FileChange(path="pyproject.toml", additions=3, deletions=1, binary=False),
            FileChange(path="src/numbat/auth.py", additions=5, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert result.categories == ("tests", "config", "source")
    codes = [hint.code for hint in result.hints]
    assert codes == [
        "tests_touched",
        "config_or_deps",
        "security_sensitive_paths",
    ]
    assert "src/numbat/auth.py" in result.hints[2].message


def test_analyze_diff_large_diff_hint_by_line_count() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="src/big.py",
                additions=LARGE_DIFF_LINE_THRESHOLD,
                deletions=0,
                binary=False,
            ),
        )
    )

    result = analyze_diff(summary)

    assert any(hint.code == "large_diff" for hint in result.hints)


def test_analyze_diff_large_diff_hint_by_file_count() -> None:
    files = tuple(
        FileChange(path=f"src/f{index}.py", additions=1, deletions=0, binary=False)
        for index in range(LARGE_DIFF_FILE_THRESHOLD)
    )

    result = analyze_diff(DiffSummary(files=files))

    assert any(hint.code == "large_diff" for hint in result.hints)


def test_analyze_diff_ci_workflow_paths_hint() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=2,
                deletions=1,
                binary=False,
            ),
            FileChange(
                path=".github/workflows/validate-workflow-contracts.yml",
                additions=1,
                deletions=0,
                binary=False,
            ),
        )
    )

    result = analyze_diff(summary)

    ci_hints = [hint for hint in result.hints if hint.code == "ci_workflow_paths"]
    assert len(ci_hints) == 1
    assert "ci/validate-workflow-contracts.py" in ci_hints[0].message
    assert (
        "python ci/validate-workflow-contracts.py --mode project"
        in ci_hints[0].message
    )


def test_analyze_diff_no_ci_workflow_hint_for_source_only() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/review.py", additions=5, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "ci_workflow_paths" for hint in result.hints)
