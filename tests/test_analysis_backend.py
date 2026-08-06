"""Tests for the pluggable analysis backend."""

from __future__ import annotations

from dataclasses import replace

import pytest

from diffrat.analysis import analyze_diff
from diffrat.analysis_backend import run_analysis
from diffrat.diff_parser import DiffContent, DiffHunk, DiffSummary, FileChange, FileDiffContent
from diffrat.llm_config import LlmConfig


def test_run_analysis_matches_analyze_diff_when_llm_disabled() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_cli.py", additions=10, deletions=2, binary=False),
            FileChange(path="pyproject.toml", additions=3, deletions=1, binary=False),
            FileChange(path="src/diffrat/auth.py", additions=5, deletions=0, binary=False),
        )
    )

    expected = analyze_diff(summary)
    actual = run_analysis(summary, llm_config=LlmConfig(enabled=False))

    assert actual == expected


def test_run_analysis_matches_analyze_diff_when_llm_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "diffrat.analysis_backend.run_llm_analysis",
        lambda config, *, diff_content=None: None,
    )

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


def test_run_analysis_invokes_llm_client_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[LlmConfig, DiffContent | None]] = []

    def fake_run_llm(
        config: LlmConfig,
        *,
        diff_content: DiffContent | None = None,
    ) -> str | None:
        calls.append((config, diff_content))
        return "llm-output"

    monkeypatch.setattr("diffrat.analysis_backend.run_llm_analysis", fake_run_llm)

    diff_content = DiffContent(
        files=(
            FileDiffContent(
                path="src/diffrat/review.py",
                hunks=(DiffHunk(header="@@ -1 +1 @@", lines=("+x",)),),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )
    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )
    llm_config = LlmConfig(enabled=True, provider="openai", api_key="sk-test")

    result = run_analysis(summary, diff_content=diff_content, llm_config=llm_config)

    assert analyze_diff(summary) == replace(result, llm_findings=None)
    assert result.llm_findings == "llm-output"
    assert len(calls) == 1
    assert calls[0][0] == llm_config
    assert calls[0][1] == diff_content


def test_run_analysis_loads_llm_config_from_env_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DIFFRAT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("DIFFRAT_LLM_API_KEY", raising=False)
    monkeypatch.delenv("DIFFRAT_LLM_BASE_URL", raising=False)

    summary = DiffSummary(
        files=(
            FileChange(path="src/diffrat/review.py", additions=1, deletions=0, binary=False),
        )
    )

    expected = analyze_diff(summary)
    actual = run_analysis(summary)

    assert actual == expected
