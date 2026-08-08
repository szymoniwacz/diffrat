"""Tests for the OpenAI-compatible LLM HTTP client."""

from __future__ import annotations

import io
import json
from typing import Any

import pytest

from diffrat.diff_parser import DiffContent, DiffHunk, FileDiffContent
from diffrat.llm_client import (
    LlmRunResult,
    format_diff_for_prompt,
    request_chat_completion,
    resolve_chat_completions_url,
    run_llm_analysis,
    validate_llm_endpoint_config,
)
from diffrat.llm_config import LlmConfig


def _success_response(content: str = "review notes") -> io.BytesIO:
    payload = {"choices": [{"message": {"content": content}}]}
    return io.BytesIO(json.dumps(payload).encode("utf-8"))


def test_resolve_chat_completions_url_openai_default() -> None:
    config = LlmConfig(enabled=True, provider="openai", api_key="sk-test")
    assert resolve_chat_completions_url(config) == "https://api.openai.com/v1/chat/completions"


def test_resolve_chat_completions_url_custom_base() -> None:
    config = LlmConfig(
        enabled=True,
        provider="ollama",
        api_key="local",
        base_url="http://localhost:11434/v1",
    )
    assert (
        resolve_chat_completions_url(config)
        == "http://localhost:11434/v1/chat/completions"
    )


def test_resolve_chat_completions_url_unknown_provider_without_base() -> None:
    config = LlmConfig(enabled=True, provider="unknown", api_key="sk-test")
    assert resolve_chat_completions_url(config) is None


def test_validate_llm_endpoint_config_ollama_without_base_url() -> None:
    config = LlmConfig(enabled=True, provider="ollama", api_key="local")
    message = validate_llm_endpoint_config(config)
    assert message is not None
    assert "DIFFRAT_LLM_BASE_URL" in message
    assert "11434" in message


def test_validate_llm_endpoint_config_rejects_chat_completions_suffix() -> None:
    config = LlmConfig(
        enabled=True,
        provider="ollama",
        api_key="local",
        base_url="http://localhost:11434/v1/chat/completions",
    )
    message = validate_llm_endpoint_config(config)
    assert message is not None
    assert "API root" in message


def test_format_diff_for_prompt_includes_hunks() -> None:
    diff_content = DiffContent(
        files=(
            FileDiffContent(
                path="src/example.py",
                hunks=(
                    DiffHunk(
                        header="@@ -1,2 +1,3 @@",
                        lines=("+added", " context"),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    prompt = format_diff_for_prompt(diff_content)

    assert "--- src/example.py" in prompt
    assert "@@ -1,2 +1,3 @@" in prompt
    assert "+added" in prompt


def test_format_diff_for_prompt_empty() -> None:
    assert format_diff_for_prompt(None) == "(no diff content available)"


def test_request_chat_completion_sends_expected_request() -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: float = 0) -> io.BytesIO:
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        response = _success_response()
        response.status = 200  # type: ignore[attr-defined]
        return response

    config = LlmConfig(
        enabled=True,
        provider="openai",
        api_key="sk-secret",
    )

    result = request_chat_completion(
        config,
        user_message="diff text",
        urlopen=fake_urlopen,
    )

    assert result == LlmRunResult(findings="review notes")
    assert captured["url"] == "https://api.openai.com/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer sk-secret"
    assert captured["body"]["model"] == "gpt-4o-mini"
    assert captured["body"]["messages"][-1]["content"] == "diff text"


def test_request_chat_completion_uses_custom_base_url() -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: float = 0) -> io.BytesIO:
        captured["url"] = request.full_url
        response = _success_response()
        response.status = 200  # type: ignore[attr-defined]
        return response

    config = LlmConfig(
        enabled=True,
        provider="ollama",
        api_key="local-token",
        base_url="http://127.0.0.1:11434/v1",
    )

    request_chat_completion(config, user_message="diff", urlopen=fake_urlopen)

    assert captured["url"] == "http://127.0.0.1:11434/v1/chat/completions"


def test_request_chat_completion_http_error_warns(
    capsys: pytest.CaptureFixture[str],
) -> None:
    import urllib.error
    from email.message import Message

    def fake_urlopen(request: Any, timeout: float = 0) -> io.BytesIO:
        raise urllib.error.HTTPError(
            request.full_url,
            500,
            "server error",
            hdrs=Message(),
            fp=None,
        )

    config = LlmConfig(enabled=True, provider="openai", api_key="sk-test")
    result = request_chat_completion(config, user_message="diff", urlopen=fake_urlopen)

    assert result.findings is None
    assert result.error is not None
    assert "HTTP 500" in result.error
    captured = capsys.readouterr()
    assert "LLM request failed with HTTP 500" in captured.err


def test_request_chat_completion_http_401_mentions_api_key(
    capsys: pytest.CaptureFixture[str],
) -> None:
    import urllib.error
    from email.message import Message

    body = json.dumps(
        {"error": {"message": "Incorrect API key provided", "type": "invalid_request_error"}}
    ).encode("utf-8")

    def fake_urlopen(request: Any, timeout: float = 0) -> io.BytesIO:
        raise urllib.error.HTTPError(
            request.full_url,
            401,
            "unauthorized",
            hdrs=Message(),
            fp=io.BytesIO(body),
        )

    config = LlmConfig(enabled=True, provider="openai", api_key="sk-bad")
    result = request_chat_completion(config, user_message="diff", urlopen=fake_urlopen)

    assert result.error is not None
    assert "authentication failed (401)" in result.error
    assert "DIFFRAT_LLM_API_KEY" in result.error
    assert "Incorrect API key provided" in result.error
    captured = capsys.readouterr()
    assert "diffrat: warning:" in captured.err


def test_request_chat_completion_url_error_connection_refused(
    capsys: pytest.CaptureFixture[str],
) -> None:
    import urllib.error

    def fake_urlopen(request: Any, timeout: float = 0) -> io.BytesIO:
        raise urllib.error.URLError(ConnectionRefusedError(61, "Connection refused"))

    config = LlmConfig(
        enabled=True,
        provider="ollama",
        api_key="local",
        base_url="http://127.0.0.1:11434/v1",
    )
    result = request_chat_completion(config, user_message="diff", urlopen=fake_urlopen)

    assert result.error is not None
    assert "cannot reach LLM endpoint" in result.error
    assert "127.0.0.1:11434" in result.error
    captured = capsys.readouterr()
    assert "diffrat: warning:" in captured.err


def test_request_chat_completion_invalid_json_warns(
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_urlopen(request: Any, timeout: float = 0) -> io.BytesIO:
        response = io.BytesIO(b"not-json")
        response.status = 200  # type: ignore[attr-defined]
        return response

    config = LlmConfig(enabled=True, provider="openai", api_key="sk-test")
    result = request_chat_completion(config, user_message="diff", urlopen=fake_urlopen)

    assert result.error == "LLM response was not valid JSON"
    captured = capsys.readouterr()
    assert "LLM response was not valid JSON" in captured.err


def test_run_llm_analysis_ollama_without_base_url_preflight(
    capsys: pytest.CaptureFixture[str],
) -> None:
    config = LlmConfig(enabled=True, provider="ollama", api_key="local")

    result = run_llm_analysis(config)

    assert result.findings is None
    assert result.error is not None
    assert "DIFFRAT_LLM_BASE_URL" in result.error
    captured = capsys.readouterr()
    assert "diffrat: warning:" in captured.err


def test_run_llm_analysis_builds_prompt_from_diff_content() -> None:
    captured: dict[str, str] = {}

    def fake_urlopen(request: Any, timeout: float = 0) -> io.BytesIO:
        captured["prompt"] = json.loads(request.data.decode("utf-8"))["messages"][-1][
            "content"
        ]
        response = _success_response("ok")
        response.status = 200  # type: ignore[attr-defined]
        return response

    diff_content = DiffContent(
        files=(
            FileDiffContent(
                path="README.md",
                hunks=(DiffHunk(header="@@ -0,0 +1 @@", lines=("+hello",)),),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )
    config = LlmConfig(enabled=True, provider="openai", api_key="sk-test")

    result = run_llm_analysis(config, diff_content=diff_content, urlopen=fake_urlopen)

    assert result == LlmRunResult(findings="ok")
    assert "--- README.md" in captured["prompt"]
    assert "+hello" in captured["prompt"]
