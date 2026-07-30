"""Hint severity registry for Focus/Risk output."""

from __future__ import annotations

from typing import Literal

HintSeverity = Literal["info", "warn", "risk"]

# Default severities for built-in hint codes (Project Execution #32).
HINT_SEVERITY_REGISTRY: dict[str, HintSeverity] = {
    # risk
    "security_sensitive_paths": "risk",
    "ci_workflow_paths": "risk",
    "possible_secret": "risk",
    "dangerous_call": "risk",
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
    # info
    "docs_touched": "info",
}


def severity_for_code(code: str) -> HintSeverity:
    """Return the default severity for a hint code; unknown codes default to info."""
    return HINT_SEVERITY_REGISTRY.get(code, "info")
