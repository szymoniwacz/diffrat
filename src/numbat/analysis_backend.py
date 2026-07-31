"""Pluggable analysis backend: heuristics always; LLM when configured."""

from __future__ import annotations

from numbat.analysis import AnalysisResult, analyze_diff
from numbat.config import NumbatConfig
from numbat.diff_parser import DiffContent, DiffSummary
from numbat.git_adapter import GitContext
from numbat.llm_client import run_llm_analysis
from numbat.llm_config import LlmConfig, load_llm_config


def run_analysis(
    summary: DiffSummary,
    *,
    diff_content: DiffContent | None = None,
    cwd: str | None = None,
    git_context: GitContext | None = None,
    config: NumbatConfig | None = None,
    llm_config: LlmConfig | None = None,
) -> AnalysisResult:
    """Run analysis through the configured backend.

    Deterministic heuristics always run. When LLM config is enabled, the LLM path
    is selected but does not add findings until a later implementation slice.
    """
    resolved_llm = llm_config if llm_config is not None else load_llm_config()
    result = analyze_diff(
        summary,
        diff_content=diff_content,
        cwd=cwd,
        git_context=git_context,
        config=config,
    )
    if resolved_llm.enabled:
        run_llm_analysis(resolved_llm, diff_content=diff_content)
    return result

