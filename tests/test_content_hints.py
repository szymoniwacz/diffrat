"""Tests for diff content-derived Focus/Risk hints."""

from __future__ import annotations

from numbat.analysis import analyze_diff
from numbat.content_hints import content_focus_risk_hints
from numbat.diff_parser import (
    DiffContent,
    DiffHunk,
    DiffSummary,
    FileChange,
    FileDiffContent,
)

_FILTER_GOOD = (
    'PROJECT_EXECUTOR_COMMENT_FILTER = "^/(execute-project|continue-project)$"'
)
_FILTER_TYPO = (
    'PROJECT_EXECUTOR_COMMENT_FILTER = "^/(execute-project|continue-projec)$"'
)


def _validator_typo_content() -> DiffContent:
    return DiffContent(
        files=(
            FileDiffContent(
                path="ci/validate-workflow-contracts.py",
                hunks=(
                    DiffHunk(
                        header="@@ -360,7 +360,7 @@",
                        lines=(f"-{_FILTER_GOOD}", f"+{_FILTER_TYPO}"),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )


def test_content_hints_regex_typo_for_continue_projec() -> None:
    hints = content_focus_risk_hints(_validator_typo_content())

    assert len(hints) == 1
    assert hints[0].code == "regex_typo"
    assert "continue-project" in hints[0].message
    assert "continue-projec" in hints[0].message
    assert "ci/validate-workflow-contracts.py" in hints[0].message


def test_content_hints_ignore_correct_constant() -> None:
    content = DiffContent(
        files=(
            FileDiffContent(
                path="ci/validate-workflow-contracts.py",
                hunks=(
                    DiffHunk(
                        header="@@ -1 +1 @@",
                        lines=(f"+{_FILTER_GOOD}",),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    assert content_focus_risk_hints(content) == []


def test_content_hints_ignore_non_validator_paths() -> None:
    content = DiffContent(
        files=(
            FileDiffContent(
                path="src/numbat/review.py",
                hunks=(
                    DiffHunk(
                        header="@@ -1 +1 @@",
                        lines=('+token = "continue-projec"',),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    assert content_focus_risk_hints(content) == []


def test_analyze_diff_merges_content_hints() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=1,
                deletions=1,
                binary=False,
            ),
        )
    )

    result = analyze_diff(summary, diff_content=_validator_typo_content())

    codes = [hint.code for hint in result.hints]
    assert "ci_workflow_paths" in codes
    assert "regex_typo" in codes
