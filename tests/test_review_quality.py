"""Tests for review quality pillar mapping."""

from __future__ import annotations

from diffrat.analysis import focus_risk_hint
from diffrat.review_quality import (
    CODE_TO_PILLAR,
    REVIEW_QUALITY_PILLARS,
    assert_registry_pillar_coverage,
    pillar_for_code,
    pillar_label,
    rollup_pillars,
)
from diffrat.scoring import HINT_SEVERITY_REGISTRY


def test_review_quality_pillars_order_and_labels() -> None:
    assert [p.id for p in REVIEW_QUALITY_PILLARS] == [
        "understand",
        "focused",
        "maintainable",
    ]
    assert pillar_label("understand") == "Understand in seconds"
    assert pillar_label("focused") == "One thing well"
    assert pillar_label("maintainable") == "Safe to change in six months"


def test_code_to_pillar_covers_entire_hint_severity_registry() -> None:
    assert_registry_pillar_coverage()
    assert set(CODE_TO_PILLAR) == set(HINT_SEVERITY_REGISTRY)


def test_pillar_for_known_codes() -> None:
    assert pillar_for_code("large_diff") == "understand"
    assert pillar_for_code("mixed_concerns") == "focused"
    assert pillar_for_code("possible_secret") == "maintainable"
    assert pillar_for_code("docs_touched") == "understand"


def test_pillar_for_unknown_code_defaults_to_maintainable() -> None:
    assert pillar_for_code("future_hint_code") == "maintainable"
    assert "future_hint_code" not in HINT_SEVERITY_REGISTRY


def test_rollup_pillars_ok_when_no_warn_or_risk_hints() -> None:
    pillars = rollup_pillars(
        [
            focus_risk_hint("docs_touched", "Docs changed", severity="info"),
        ]
    )
    assert [p.status for p in pillars] == ["ok", "ok", "ok"]
    assert all(p.codes == () for p in pillars)


def test_rollup_pillars_warn_and_risk_by_pillar() -> None:
    pillars = rollup_pillars(
        [
            focus_risk_hint("large_diff", "Large diff", severity="warn"),
            focus_risk_hint("mixed_concerns", "Mixed", severity="warn"),
            focus_risk_hint("possible_secret", "Secret", severity="risk"),
        ]
    )
    by_id = {p.id: p for p in pillars}
    assert by_id["understand"].status == "warn"
    assert by_id["understand"].codes == ("large_diff",)
    assert by_id["focused"].status == "warn"
    assert by_id["focused"].codes == ("mixed_concerns",)
    assert by_id["maintainable"].status == "risk"
    assert by_id["maintainable"].codes == ("possible_secret",)


def test_rollup_pillars_risk_wins_over_warn_on_same_pillar() -> None:
    pillars = rollup_pillars(
        [
            focus_risk_hint("possible_secret", "Secret", severity="risk"),
            focus_risk_hint("tests_touched", "Tests", severity="warn"),
        ]
    )
    maintainable = next(p for p in pillars if p.id == "maintainable")
    assert maintainable.status == "risk"
    assert maintainable.codes == ("possible_secret", "tests_touched")
