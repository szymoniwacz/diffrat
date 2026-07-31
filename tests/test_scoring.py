"""Tests for hint severity registry, risk scoring, and sorting."""

from __future__ import annotations

from numbat.analysis import focus_risk_hint, sort_hints
from numbat.diff_parser import FileChange
from numbat.scoring import (
    HINT_SEVERITY_REGISTRY,
    RISK_WEIGHT_BINARY,
    RISK_WEIGHT_CI_CATEGORY,
    RISK_WEIGHT_CONFIG_CATEGORY,
    RISK_WEIGHT_SECURITY_SENSITIVE,
    RISK_WEIGHT_SOURCE_WITHOUT_TESTS,
    risk_score_for_file,
    severity_for_code,
    sort_file_entries,
)


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
    assert hint.path is None
    assert hint.line is None


def test_focus_risk_hint_accepts_path_and_line() -> None:
    hint = focus_risk_hint(
        "possible_secret",
        "test message",
        path="src/a.py",
        line=42,
    )
    assert hint.path == "src/a.py"
    assert hint.line == 42


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


def test_risk_score_binary_fixed_weight() -> None:
    file_change = FileChange(path="bin.dat", additions=0, deletions=0, binary=True)
    score = risk_score_for_file(
        file_change,
        "other",
        total_non_binary_lines=10,
        has_tests_in_diff=False,
        security_sensitive=False,
    )
    assert score == RISK_WEIGHT_BINARY


def test_risk_score_line_share() -> None:
    file_change = FileChange(path="src/a.py", additions=8, deletions=2, binary=False)
    score = risk_score_for_file(
        file_change,
        "source",
        total_non_binary_lines=10,
        has_tests_in_diff=True,
        security_sensitive=False,
    )
  # 10 lines = 100% share -> 50 points, source with tests -> no extra
    assert score == 50


def test_risk_score_security_sensitive_and_source_without_tests() -> None:
    file_change = FileChange(path=".env", additions=1, deletions=0, binary=False)
    score = risk_score_for_file(
        file_change,
        "config",
        total_non_binary_lines=1,
        has_tests_in_diff=False,
        security_sensitive=True,
    )
    # line share 50 + security 40 + config 10 = 100 (source_without_tests not config)
    assert score == 50 + RISK_WEIGHT_SECURITY_SENSITIVE + RISK_WEIGHT_CONFIG_CATEGORY


def test_risk_score_source_without_tests() -> None:
    file_change = FileChange(path="src/a.py", additions=1, deletions=0, binary=False)
    score = risk_score_for_file(
        file_change,
        "source",
        total_non_binary_lines=1,
        has_tests_in_diff=False,
        security_sensitive=False,
    )
    assert score == 50 + RISK_WEIGHT_SOURCE_WITHOUT_TESTS


def test_risk_score_ci_category() -> None:
    file_change = FileChange(path="ci/foo.py", additions=1, deletions=0, binary=False)
    score = risk_score_for_file(
        file_change,
        "ci",
        total_non_binary_lines=1,
        has_tests_in_diff=False,
        security_sensitive=False,
    )
    assert score == 50 + RISK_WEIGHT_CI_CATEGORY


def test_sort_file_entries_by_risk_then_path() -> None:
    files = (
        FileChange(path="b.py", additions=1, deletions=0, binary=False),
        FileChange(path="a.py", additions=10, deletions=0, binary=False),
        FileChange(path="c.py", additions=0, deletions=0, binary=True),
    )
    categories = ("source", "source", "other")
    risk_scores = (10, 50, RISK_WEIGHT_BINARY)
    sorted_entries = sort_file_entries(files, categories, risk_scores)
    assert [e[0].path for e in sorted_entries] == ["a.py", "b.py", "c.py"]
