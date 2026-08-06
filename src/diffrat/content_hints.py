"""Deterministic Focus/Risk hints from diff hunk content."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from fnmatch import fnmatch

from diffrat.analysis import FocusRiskHint, categorize_path, focus_risk_hint
from diffrat.config import ContentRule, DiffratConfig
from diffrat.diff_parser import DiffContent, FileDiffContent

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

_HUNK_HEADER_PATTERN = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


@dataclass(frozen=True)
class _AddedLine:
    text: str
    path: str
    category: str
    line: int | None


def content_focus_risk_hints(
    diff_content: DiffContent | None,
    *,
    config: DiffratConfig | None = None,
) -> list[FocusRiskHint]:
    """Return content-derived hints from unified-diff hunks."""
    if diff_content is None:
        return []

    hints: list[FocusRiskHint] = []
    for file_diff in diff_content.files:
        if file_diff.binary:
            continue
        for added in _iter_added_lines(file_diff):
            hints.extend(_hints_for_added_line(added, config=config))
    return hints


def _iter_added_lines(file_diff: FileDiffContent) -> list[_AddedLine]:
    category = categorize_path(file_diff.path)
    if category in {"tests", "docs"}:
        return []

    lines: list[_AddedLine] = []
    for hunk in file_diff.hunks:
        new_line = _new_file_start_line(hunk.header)
        for line in hunk.lines:
            if line.startswith("+"):
                lines.append(
                    _AddedLine(
                        text=line[1:],
                        path=file_diff.path,
                        category=category,
                        line=new_line,
                    )
                )
                if new_line is not None:
                    new_line += 1
            elif line.startswith(" "):
                if new_line is not None:
                    new_line += 1
    return lines


def _new_file_start_line(header: str) -> int | None:
    match = _HUNK_HEADER_PATTERN.search(header)
    if match is None:
        return None
    return int(match.group(1))


def _hints_for_added_line(
    added: _AddedLine,
    *,
    config: DiffratConfig | None,
) -> list[FocusRiskHint]:
    hints: list[FocusRiskHint] = []

    if config is not None:
        hints.extend(_config_rule_hints_for_line(added, config.content_rules))

    if added.category in {"source", "ci"}:
        hints.extend(_production_hints_for_line(added))

    return hints


def _config_rule_hints_for_line(
    added: _AddedLine,
    rules: tuple[ContentRule, ...],
) -> list[FocusRiskHint]:
    hints: list[FocusRiskHint] = []
    for rule in rules:
        if not _content_rule_applies_to_path(added.path, rule.paths):
            continue
        if rule.pattern.search(added.text) is None:
            continue
        if rule.expected in added.text:
            continue
        hints.append(
            focus_risk_hint(
                code=rule.code,
                message=(
                    f"Suspicious pattern in {added.path} "
                    f"(expected '{rule.expected}'): {added.text.strip()}"
                ),
                path=added.path,
                line=added.line,
            )
        )
    return hints


def _content_rule_applies_to_path(path: str, paths: tuple[str, ...]) -> bool:
    if not paths:
        return True
    normalized = path.replace("\\", "/")
    for entry in paths:
        if entry.endswith("/"):
            if normalized.startswith(entry) or normalized == entry.rstrip("/"):
                return True
            continue
        if fnmatch(normalized, entry):
            return True
        if normalized == entry or normalized.endswith(f"/{entry}"):
            return True
    return False


def _production_hints_for_line(added: _AddedLine) -> list[FocusRiskHint]:
    hints: list[FocusRiskHint] = []
    preview = added.text.strip()
    path = added.path
    line = added.line

    if _matches_possible_secret(added.text):
        hints.append(
            focus_risk_hint(
                code="possible_secret",
                message=f"Possible secret in {added.path}: {preview}",
                path=path,
                line=line,
            )
        )

    if _matches_any_pattern(added.text, _DEBUG_LEFTOVER_PATTERNS):
        hints.append(
            focus_risk_hint(
                code="debug_leftover",
                message=f"Debug leftover in {added.path}: {preview}",
                path=path,
                line=line,
            )
        )

    if _matches_any_pattern(added.text, _DANGEROUS_CALL_PATTERNS):
        hints.append(
            focus_risk_hint(
                code="dangerous_call",
                message=f"Dangerous call in {added.path}: {preview}",
                path=path,
                line=line,
            )
        )

    if _matches_broad_exception(added.text):
        hints.append(
            focus_risk_hint(
                code="broad_exception",
                message=f"Broad exception handler in {added.path}: {preview}",
                path=path,
                line=line,
            )
        )

    if _matches_hardcoded_url_or_ip(added.text):
        hints.append(
            focus_risk_hint(
                code="hardcoded_url_or_ip",
                message=f"Hardcoded URL or IP in {added.path}: {preview}",
                path=path,
                line=line,
            )
        )

    return hints


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
