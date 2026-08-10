"""Review quality pillars: map Focus/Risk hint codes to three review questions."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from diffrat.analysis import FocusRiskHint
from diffrat.scoring import HINT_SEVERITY_REGISTRY

PillarId = Literal["understand", "focused", "maintainable"]
PillarStatus = Literal["ok", "warn", "risk"]

_DEFAULT_PILLAR: PillarId = "maintainable"


@dataclass(frozen=True, slots=True)
class ReviewQualityPillar:
    """One review-quality pillar surfaced in text and JSON reports."""

    id: PillarId
    label: str


@dataclass(frozen=True, slots=True)
class ReviewQualityPillarResult:
    """Rollup status for one pillar after mapping Focus/Risk hints."""

    id: PillarId
    label: str
    status: PillarStatus
    codes: tuple[str, ...]


REVIEW_QUALITY_PILLARS: tuple[ReviewQualityPillar, ...] = (
    ReviewQualityPillar(
        id="understand",
        label="Understand in seconds",
    ),
    ReviewQualityPillar(
        id="focused",
        label="One thing well",
    ),
    ReviewQualityPillar(
        id="maintainable",
        label="Safe to change in six months",
    ),
)

# Built-in Focus/Risk codes → pillar. Keys must cover HINT_SEVERITY_REGISTRY.
CODE_TO_PILLAR: dict[str, PillarId] = {
    # understand — clarity, size, navigation
    "large_diff": "understand",
    "large_single_file": "understand",
    "deletions_heavy": "understand",
    "rename_or_move": "understand",
    "generated_file_touched": "understand",
    "regex_typo": "understand",
    "docs_touched": "understand",
    "long_added_hunk": "understand",
    "cli_flag_without_help": "understand",
    # focused — scope and change hygiene
    "tests_only": "focused",
    "many_commits": "focused",
    "wip_commits": "focused",
    "mixed_concerns": "focused",
    # maintainable — safety, tests, dependencies, fragile patterns
    "security_sensitive_paths": "maintainable",
    "ci_workflow_paths": "maintainable",
    "possible_secret": "maintainable",
    "dangerous_call": "maintainable",
    "config_or_deps": "maintainable",
    "suspicious_constant_change": "maintainable",
    "tests_touched": "maintainable",
    "source_without_tests": "maintainable",
    "source_heavy_without_tests": "maintainable",
    "ci_without_tests": "maintainable",
    "missing_test_file": "maintainable",
    "lockfile_without_manifest": "maintainable",
    "manifest_without_lockfile": "maintainable",
    "debug_leftover": "maintainable",
    "broad_exception": "maintainable",
    "hardcoded_url_or_ip": "maintainable",
}


def pillar_for_code(code: str) -> PillarId:
    """Return the review-quality pillar for a Focus/Risk hint code."""
    return CODE_TO_PILLAR.get(code, _DEFAULT_PILLAR)


def pillar_label(pillar_id: PillarId) -> str:
    """Return the human label for a pillar id."""
    for pillar in REVIEW_QUALITY_PILLARS:
        if pillar.id == pillar_id:
            return pillar.label
    raise KeyError(pillar_id)


def assert_registry_pillar_coverage() -> None:
    """Raise when a built-in registry code lacks an explicit pillar mapping."""
    missing = sorted(set(HINT_SEVERITY_REGISTRY) - set(CODE_TO_PILLAR))
    if missing:
        raise ValueError(
            "HINT_SEVERITY_REGISTRY codes missing from CODE_TO_PILLAR: " + ", ".join(missing)
        )


def rollup_pillars(hints: Iterable[FocusRiskHint]) -> tuple[ReviewQualityPillarResult, ...]:
    """Roll Focus/Risk hints into per-pillar ok/warn/risk status and matched codes."""
    codes_by_pillar: dict[PillarId, set[str]] = {
        pillar.id: set() for pillar in REVIEW_QUALITY_PILLARS
    }
    status_by_pillar: dict[PillarId, PillarStatus] = {
        pillar.id: "ok" for pillar in REVIEW_QUALITY_PILLARS
    }

    for hint in hints:
        if hint.severity == "info":
            continue
        pillar_id = pillar_for_code(hint.code)
        codes_by_pillar[pillar_id].add(hint.code)
        if hint.severity == "risk":
            status_by_pillar[pillar_id] = "risk"
        elif hint.severity == "warn" and status_by_pillar[pillar_id] != "risk":
            status_by_pillar[pillar_id] = "warn"

    return tuple(
        ReviewQualityPillarResult(
            id=pillar.id,
            label=pillar.label,
            status=status_by_pillar[pillar.id],
            codes=tuple(sorted(codes_by_pillar[pillar.id])),
        )
        for pillar in REVIEW_QUALITY_PILLARS
    )
