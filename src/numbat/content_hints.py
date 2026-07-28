"""Deterministic Focus/Risk hints from diff hunk content."""

from __future__ import annotations

import re
from dataclasses import dataclass

from numbat.analysis import FocusRiskHint
from numbat.diff_parser import DiffContent, FileDiffContent

_VALIDATOR_PATH = "ci/validate-workflow-contracts.py"
_COMMENT_FILTER_CONSTANT = "PROJECT_EXECUTOR_COMMENT_FILTER"
_COMMENT_FILTER_EXPECTED = ("execute-project", "continue-project")

# Near-miss tokens: look like the real command but are truncated or mistyped.
_COMMAND_TYPO_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"continue-projec(?!t)"), "continue-project"),
    (re.compile(r"execute-projec(?!t)"), "execute-project"),
)


@dataclass(frozen=True)
class _AddedLine:
    text: str
    path: str


def content_focus_risk_hints(diff_content: DiffContent | None) -> list[FocusRiskHint]:
    """Return content-derived hints from unified-diff hunks."""
    if diff_content is None:
        return []

    hints: list[FocusRiskHint] = []
    for file_diff in diff_content.files:
        if file_diff.binary:
            continue
        for added in _iter_added_lines(file_diff):
            hints.extend(_hints_for_added_line(added))
    return hints


def _iter_added_lines(file_diff: FileDiffContent) -> list[_AddedLine]:
    if not _is_validator_path(file_diff.path):
        return []

    lines: list[_AddedLine] = []
    for hunk in file_diff.hunks:
        for line in hunk.lines:
            if line.startswith("+"):
                lines.append(_AddedLine(text=line[1:], path=file_diff.path))
    return lines


def _is_validator_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized == _VALIDATOR_PATH or normalized.endswith(f"/{_VALIDATOR_PATH}")


def _hints_for_added_line(added: _AddedLine) -> list[FocusRiskHint]:
    hints: list[FocusRiskHint] = []
    typo_expected = _find_project_command_typo(added.text)
    if typo_expected is not None:
        hints.append(
            FocusRiskHint(
                code="regex_typo",
                message=(
                    f"Suspicious typo in {added.path} "
                    f"(expected '{typo_expected}'): {added.text.strip()}"
                ),
            )
        )

    if _COMMENT_FILTER_CONSTANT in added.text and "=" in added.text:
        missing = [
            token
            for token in _COMMENT_FILTER_EXPECTED
            if token not in added.text
        ]
        if missing and typo_expected is None:
            preview = ", ".join(f"'{token}'" for token in missing)
            hints.append(
                FocusRiskHint(
                    code="suspicious_constant_change",
                    message=(
                        f"{_COMMENT_FILTER_CONSTANT} may be missing expected "
                        f"tokens ({preview}): {added.text.strip()}"
                    ),
                )
            )

    return hints


def _find_project_command_typo(line: str) -> str | None:
    for pattern, expected in _COMMAND_TYPO_PATTERNS:
        if pattern.search(line) and expected not in line:
            return expected
    return None
