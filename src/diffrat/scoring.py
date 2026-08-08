"""Hint severity registry and per-file risk scoring for review output."""

from __future__ import annotations

from typing import Literal

from diffrat.diff_parser import FileChange

HintSeverity = Literal["info", "warn", "risk"]

# Public severity label (JSON/API contract); not a credential.
SEVERITY_RISK: HintSeverity = "risk"  # nosec B105

# Per-file risk_score weights (Project Execution #32). Non-negative integer scale;
# files sort by descending score, ties by path name.
RISK_WEIGHT_LINE_SHARE_MAX = 50
RISK_WEIGHT_SECURITY_SENSITIVE = 40
RISK_WEIGHT_SOURCE_WITHOUT_TESTS = 25
RISK_WEIGHT_CI_CATEGORY = 20
RISK_WEIGHT_CONFIG_CATEGORY = 10
RISK_WEIGHT_BINARY = 5

# Default severities for built-in hint codes (Project Execution #32).
HINT_SEVERITY_REGISTRY: dict[str, HintSeverity] = {
    # risk
    "security_sensitive_paths": SEVERITY_RISK,
    "ci_workflow_paths": SEVERITY_RISK,
    "possible_secret": SEVERITY_RISK,
    "dangerous_call": SEVERITY_RISK,
    # warn
    "large_diff": "warn",
    "large_single_file": "warn",
    "deletions_heavy": "warn",
    "config_or_deps": "warn",
    "regex_typo": "warn",
    "suspicious_constant_change": "warn",
    "tests_touched": "warn",
    "rename_or_move": "warn",
    "source_without_tests": "warn",
    "tests_only": "warn",
    "ci_without_tests": "warn",
    "workflow_without_ci_validator": "warn",
    "generated_file_touched": "warn",
    "many_commits": "warn",
    "wip_commits": "warn",
    "mixed_concerns": "warn",
    "missing_test_file": "warn",
    "lockfile_without_manifest": "warn",
    "manifest_without_lockfile": "warn",
    "debug_leftover": "warn",
    "broad_exception": "warn",
    "hardcoded_url_or_ip": "warn",
    "long_added_hunk": "warn",
    "source_heavy_without_tests": "warn",
    "cli_flag_without_help": "warn",
    # info
    "docs_touched": "info",
}


def severity_for_code(code: str) -> HintSeverity:
    """Return the default severity for a hint code; unknown codes default to info."""
    return HINT_SEVERITY_REGISTRY.get(code, "info")


def risk_score_for_file(
    file_change: FileChange,
    category: str,
    *,
    total_non_binary_lines: int,
    has_tests_in_diff: bool,
    security_sensitive: bool,
) -> int:
    """Compute a deterministic non-negative risk score for one changed file."""
    if file_change.binary:
        return RISK_WEIGHT_BINARY

    score = 0
    file_lines = file_change.additions + file_change.deletions
    if total_non_binary_lines > 0 and file_lines > 0:
        score += (file_lines * RISK_WEIGHT_LINE_SHARE_MAX) // total_non_binary_lines

    if security_sensitive:
        score += RISK_WEIGHT_SECURITY_SENSITIVE

    if category == "source" and not has_tests_in_diff:
        score += RISK_WEIGHT_SOURCE_WITHOUT_TESTS

    if category == "ci":
        score += RISK_WEIGHT_CI_CATEGORY
    elif category == "config":
        score += RISK_WEIGHT_CONFIG_CATEGORY

    return score


def sort_file_entries(
    files: tuple[FileChange, ...],
    categories: tuple[str, ...],
    risk_scores: tuple[int, ...],
) -> list[tuple[FileChange, str, int]]:
    """Sort files by descending risk_score, then path name."""
    entries = list(zip(files, categories, risk_scores, strict=True))
    return sorted(entries, key=lambda entry: (-entry[2], entry[0].path))


# Fixed category subsection order for text and JSON reports (project #40).
CATEGORY_DISPLAY_ORDER: tuple[str, ...] = (
    "source",
    "tests",
    "ci",
    "config",
    "docs",
    "other",
)

REVIEW_ORDER_CAP = 5


def group_entries_by_category(
    sorted_entries: list[tuple[FileChange, str, int]],
) -> list[tuple[str, list[tuple[FileChange, str, int]]]]:
    """Group file entries by category in display order; omit empty categories."""
    by_category: dict[str, list[tuple[FileChange, str, int]]] = {}
    for entry in sorted_entries:
        by_category.setdefault(entry[1], []).append(entry)

    grouped: list[tuple[str, list[tuple[FileChange, str, int]]]] = []
    for category in CATEGORY_DISPLAY_ORDER:
        if category not in by_category:
            continue
        entries = sorted(by_category[category], key=lambda entry: (-entry[2], entry[0].path))
        grouped.append((category, entries))
    return grouped


def review_order_entries(
    sorted_entries: list[tuple[FileChange, str, int]],
    *,
    cap: int = REVIEW_ORDER_CAP,
) -> list[tuple[FileChange, str, int]]:
    """Return up to cap highest-priority file entries (already globally sorted)."""
    return sorted_entries[:cap]


def files_by_category_mapping(
    sorted_entries: list[tuple[FileChange, str, int]],
) -> dict[str, list[str]]:
    """Build category-to-paths mapping in display order with within-category sort."""
    return {
        category: [file_change.path for file_change, _category, _score in entries]
        for category, entries in group_entries_by_category(sorted_entries)
    }
