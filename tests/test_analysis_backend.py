"""Tests for the pluggable analysis backend."""

from __future__ import annotations

import pytest

from numbat.analysis import analyze_diff
from numbat.analysis_backend import run_analysis
from numbat.diff_parser import DiffSummary, FileChange
from numbat.llm_config import LlmConfig


def test_run_analysis_matches_analyze_diff_when_llm_disabled() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_cli.py", additions=10, deletions=2, binary=False),
            FileChange(path="pyproject.toml", additions=3, deletions=1, binary=False),
            FileChange(path="src/numbat/auth.py", additions=5, deletions=0, binary=False),
        )
    )

    expected = analyze_diff(summary)
    actual = run_analysis(summary, llm_config=LlmConfig(enabled=False))

    assert actual == expected


def test_run_analysis_matches_analyze_diff_when_llm_enabled() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_cli.py", additions=10, deletions=2, binary=False),
            FileChange(path="pyproject.toml", additions=3, deletions=1, binary=False),
        )
    )
    llm_config = LlmConfig(
        enabled=True,
        provider="openai",
        api_key="sk-test",
        base_url="http://localhost:11434/v1",
    )

    expected = analyze_diff(summary)
    actual = run_analysis(summary, llm_config=llm_config)

    assert actual == expected


def test_run_analysis_loads_llm_config_from_env_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NUMBAT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("NUMBAT_LLM_API_KEY", raising=False)
    monkeypatch.delenv("NUMBAT_LLM_BASE_URL", raising=False)

    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/review.py", additions=1, deletions=0, binary=False),
        )
    )

    expected = analyze_diff(summary)
    actual = run_analysis(summary)

    assert actual == expected
