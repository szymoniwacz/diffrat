"""LLM configuration from process environment (ADR-0001)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

_ENV_PROVIDER = "DIFFRAT_LLM_PROVIDER"
_ENV_API_KEY = "DIFFRAT_LLM_API_KEY"
_ENV_BASE_URL = "DIFFRAT_LLM_BASE_URL"


@dataclass(frozen=True)
class LlmConfig:
    """Parsed LLM opt-in configuration."""

    enabled: bool
    provider: str | None = None
    api_key: str | None = None
    base_url: str | None = None


def load_llm_config() -> LlmConfig:
    """Load LLM config from the process environment.

    LLM is enabled only when both provider and API key are non-empty.
    Partial configuration emits a stderr warning and stays disabled.
    """
    provider = _read_env(_ENV_PROVIDER)
    api_key = _read_env(_ENV_API_KEY)
    base_url = _read_env(_ENV_BASE_URL)

    if provider and api_key:
        return LlmConfig(
            enabled=True,
            provider=provider,
            api_key=api_key,
            base_url=base_url,
        )

    if provider or api_key or base_url:
        print(
            "diffrat: warning: incomplete LLM configuration — "
            f"set both {_ENV_PROVIDER} and {_ENV_API_KEY} to enable LLM analysis",
            file=sys.stderr,
        )

    return LlmConfig(enabled=False)


def _read_env(name: str) -> str | None:
    raw = os.environ.get(name)
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped if stripped else None
