"""Tests for LLM environment configuration."""

from __future__ import annotations

import pytest

from diffrat.llm_config import load_llm_config


@pytest.fixture(autouse=True)
def _clear_llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DIFFRAT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("DIFFRAT_LLM_API_KEY", raising=False)
    monkeypatch.delenv("DIFFRAT_LLM_BASE_URL", raising=False)


def test_load_llm_config_disabled_by_default() -> None:
    config = load_llm_config()
    assert config.enabled is False
    assert config.provider is None
    assert config.api_key is None
    assert config.base_url is None


def test_load_llm_config_enabled_when_provider_and_key_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DIFFRAT_LLM_PROVIDER", "openai")
    monkeypatch.setenv("DIFFRAT_LLM_API_KEY", "sk-test")

    config = load_llm_config()

    assert config.enabled is True
    assert config.provider == "openai"
    assert config.api_key == "sk-test"
    assert config.base_url is None


def test_load_llm_config_optional_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DIFFRAT_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("DIFFRAT_LLM_API_KEY", "local-token")
    monkeypatch.setenv("DIFFRAT_LLM_BASE_URL", "http://localhost:11434/v1")

    config = load_llm_config()

    assert config.enabled is True
    assert config.base_url == "http://localhost:11434/v1"


def test_load_llm_config_partial_provider_without_key_warns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DIFFRAT_LLM_PROVIDER", "openai")

    config = load_llm_config()

    assert config.enabled is False


def test_load_llm_config_partial_key_without_provider_warns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DIFFRAT_LLM_API_KEY", "sk-test")

    config = load_llm_config()

    assert config.enabled is False


def test_load_llm_config_partial_base_url_only_warns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DIFFRAT_LLM_BASE_URL", "http://localhost:11434/v1")

    config = load_llm_config()

    assert config.enabled is False


def test_load_llm_config_ignores_whitespace_only_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DIFFRAT_LLM_PROVIDER", "  ")
    monkeypatch.setenv("DIFFRAT_LLM_API_KEY", "sk-test")

    config = load_llm_config()

    assert config.enabled is False
