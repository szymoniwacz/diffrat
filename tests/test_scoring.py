"""Tests for hint severity registry and sorting."""

from __future__ import annotations

from numbat.analysis import focus_risk_hint, sort_hints
from numbat.scoring import HINT_SEVERITY_REGISTRY, severity_for_code


def test_severity_for_known_codes() -> None:
    assert severity_for_code("security_sensitive_paths") == "risk"
    assert severity_for_code("possible_secret") == "risk"
    assert severity_for_code("tests_touched") == "warn"
    assert severity_for_code("regex_typo") == "warn"
    assert severity_for_code("docs_touched") == "info"


def test_severity_for_unknown_code_defaults_to_info() -> None:
    assert severity_for_code("future_hint_code") == "info"


def test_registry_covers_all_documented_builtin_codes() -> None:
    assert "security_sensitive_paths" in HINT_SEVERITY_REGISTRY
    assert "docs_touched" in HINT_SEVERITY_REGISTRY
    assert len(HINT_SEVERITY_REGISTRY) >= 25


def test_focus_risk_hint_resolves_severity_from_registry() -> None:
    hint = focus_risk_hint("possible_secret", "test message")
    assert hint.severity == "risk"
    assert hint.code == "possible_secret"


def test_focus_risk_hint_unknown_code_defaults_to_info() -> None:
    hint = focus_risk_hint("unknown_future_code", "test")
    assert hint.severity == "info"


def test_sort_hints_by_severity_then_code() -> None:
    hints = [
        focus_risk_hint("docs_touched", "docs"),
        focus_risk_hint("possible_secret", "secret"),
        focus_risk_hint("tests_touched", "tests"),
        focus_risk_hint("security_sensitive_paths", "sec"),
    ]
    sorted_hints = sort_hints(hints)
    assert [h.code for h in sorted_hints] == [
        "possible_secret",
        "security_sensitive_paths",
        "tests_touched",
        "docs_touched",
    ]
    assert [h.severity for h in sorted_hints] == ["risk", "risk", "warn", "info"]
