"""Deterministic Focus/Risk hints from diff hunk content."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from numbat.analysis import FocusRiskHint, categorize_path
from numbat.diff_parser import DiffContent, FileDiffContent

_VALIDATOR_PATH = "ci/validate-workflow-contracts.py"
_COMMENT_FILTER_CONSTANT = "PROJECT_EXECUTOR_COMMENT_FILTER"
_COMMENT_FILTER_EXPECTED = ("execute-project", "continue-project")

# Near-miss tokens: look like the real command but are truncated or mistyped.
_COMMAND_TYPO_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"continue-projec(?!t)"), "continue-project"),
    (re.compile(r"execute-projec(?!t)"), "execute-project"),
)

# High-entropy string literal detection (documented threshold).
_ENTROPY_MIN_LENGTH = 20
_ENTROPY_THRESHOLD_BITS = 3.5

_POSSIBLE_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY", re.IGNORECASE),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[a-zA-Z0-9]{20,}\b"),
    re.compile(
        r"""(?i)(?:api[_-]?key|secret|password|token|auth)\s*=\s*['"][^'"]{8,}['"]"""
    ),
)

_DEBUG_LEFTOVER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bprint\s*\("),
    re.compile(r"\bbreakpoint\s*\(\s*\)"),
    re.compile(r"\bdebugger\b", re.IGNORECASE),
    re.compile(r"\bconsole\.log\s*\("),
    re.compile(r"TODO:\s*remove", re.IGNORECASE),
)

_DANGEROUS_CALL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\beval\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"\bshell\s*=\s*True\b"),
    re.compile(r"\bos\.system\s*\("),
)

_BROAD_EXCEPTION_PATTERN = re.compile(r"\bexcept\s*(?::|Exception\s*:)\s*$")

_HARDCODED_URL_PATTERN = re.compile(r"https?://[^\s'\"]+", re.IGNORECASE)
_IPV4_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)

_STRING_LITERAL_PATTERN = re.compile(r"""['"]([^'"]+)['"]""")


@dataclass(frozen=True)
class _AddedLine:
    text: str
    path: str
    category: str


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
    category = categorize_path(file_diff.path)
    if category in {"tests", "docs"}:
        return []

    lines: list[_AddedLine] = []
    for hunk in file_diff.hunks:
        for line in hunk.lines:
            if line.startswith("+"):
                lines.append(
                    _AddedLine(text=line[1:], path=file_diff.path, category=category)
                )
    return lines


def _hints_for_added_line(added: _AddedLine) -> list[FocusRiskHint]:
    hints: list[FocusRiskHint] = []

    if _is_validator_path(added.path):
        hints.extend(_validator_hints_for_line(added))

    if added.category in {"source", "ci"}:
        hints.extend(_production_hints_for_line(added))

    return hints


def _validator_hints_for_line(added: _AddedLine) -> list[FocusRiskHint]:
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


def _production_hints_for_line(added: _AddedLine) -> list[FocusRiskHint]:
    hints: list[FocusRiskHint] = []
    preview = added.text.strip()

    if _matches_possible_secret(added.text):
        hints.append(
            FocusRiskHint(
                code="possible_secret",
                message=f"Possible secret in {added.path}: {preview}",
            )
        )

    if _matches_any_pattern(added.text, _DEBUG_LEFTOVER_PATTERNS):
        hints.append(
            FocusRiskHint(
                code="debug_leftover",
                message=f"Debug leftover in {added.path}: {preview}",
            )
        )

    if _matches_any_pattern(added.text, _DANGEROUS_CALL_PATTERNS):
        hints.append(
            FocusRiskHint(
                code="dangerous_call",
                message=f"Dangerous call in {added.path}: {preview}",
            )
        )

    if _matches_broad_exception(added.text):
        hints.append(
            FocusRiskHint(
                code="broad_exception",
                message=f"Broad exception handler in {added.path}: {preview}",
            )
        )

    if _matches_hardcoded_url_or_ip(added.text):
        hints.append(
            FocusRiskHint(
                code="hardcoded_url_or_ip",
                message=f"Hardcoded URL or IP in {added.path}: {preview}",
            )
        )

    return hints


def _is_validator_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized == _VALIDATOR_PATH or normalized.endswith(f"/{_VALIDATOR_PATH}")


def _find_project_command_typo(line: str) -> str | None:
    for pattern, expected in _COMMAND_TYPO_PATTERNS:
        if pattern.search(line) and expected not in line:
            return expected
    return None


def _matches_any_pattern(line: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    return any(pattern.search(line) for pattern in patterns)


def _matches_possible_secret(line: str) -> bool:
    if _matches_any_pattern(line, _POSSIBLE_SECRET_PATTERNS):
        return True
    return any(_is_high_entropy_literal(value) for value in _string_literals(line))


def _string_literals(line: str) -> list[str]:
    return [match.group(1) for match in _STRING_LITERAL_PATTERN.finditer(line)]


def _is_high_entropy_literal(value: str) -> bool:
    if len(value) < _ENTROPY_MIN_LENGTH:
        return False
    if "://" in value or "|" in value or value.startswith("^") or value.endswith("$"):
        return False
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        return False
    counts = Counter(value)
    length = len(value)
    entropy = -sum(
        (count / length) * math.log2(count / length) for count in counts.values()
    )
    return entropy >= _ENTROPY_THRESHOLD_BITS


def _matches_broad_exception(line: str) -> bool:
    stripped = line.strip()
    if "raise" in stripped:
        return False
    return _BROAD_EXCEPTION_PATTERN.search(stripped) is not None


def _matches_hardcoded_url_or_ip(line: str) -> bool:
    return (
        _HARDCODED_URL_PATTERN.search(line) is not None
        or _IPV4_PATTERN.search(line) is not None
    )
