"""Pluggable analysis backend: heuristics always; LLM when configured."""

from __future__ import annotations

from dataclasses import replace

from diffrat.analysis import AnalysisResult, analyze_diff
from diffrat.config import DiffratConfig
from diffrat.diff_parser import DiffContent, DiffSummary
from diffrat.git_adapter import GitContext
from diffrat.llm_client import run_llm_analysis
from diffrat.llm_config import LlmConfig, load_llm_config


def run_analysis(
    summary: DiffSummary,
    *,
    diff_content: DiffContent | None = None,
    cwd: str | None = None,
    git_context: GitContext | None = None,
    config: DiffratConfig | None = None,
    llm_config: LlmConfig | None = None,
) -> AnalysisResult:
    """Run analysis through the configured backend.

    Deterministic heuristics always run. When LLM config is enabled and the
    request succeeds, optional LLM narrative is attached additively.
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
        llm_result = run_llm_analysis(resolved_llm, diff_content=diff_content)
        if llm_result.findings is not None:
            result = replace(result, llm_findings=llm_result.findings)
        elif llm_result.error is not None:
            result = replace(result, llm_error=llm_result.error)
    return result
