"""OpenAI-compatible LLM HTTP client for diff-scoped analysis (ADR-0001)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from diffrat.diff_parser import DiffContent
from diffrat.llm_config import LlmConfig

_PROVIDER_BASE_URLS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
}

_DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "ollama": "llama3",
}

_REQUEST_TIMEOUT_SECONDS = 60.0

Urlopen = Callable[..., Any]


@dataclass(frozen=True)
class LlmRunResult:
    """Outcome of an optional LLM analysis request."""

    findings: str | None = None
    error: str | None = None


def run_llm_analysis(
    config: LlmConfig,
    *,
    diff_content: DiffContent | None = None,
    urlopen: Urlopen | None = None,
) -> LlmRunResult:
    """Request LLM analysis for a bounded diff."""
    prompt = format_diff_for_prompt(diff_content)
    return request_chat_completion(config, user_message=prompt, urlopen=urlopen)


def format_diff_for_prompt(diff_content: DiffContent | None) -> str:
    """Build a diff-scoped user message from parsed unified-diff content."""
    if diff_content is None or not diff_content.files:
        return "(no diff content available)"

    parts: list[str] = []
    for file_diff in diff_content.files:
        if file_diff.binary:
            parts.append(f"--- {file_diff.path} (binary)")
            continue
        parts.append(f"--- {file_diff.path}")
        for hunk in file_diff.hunks:
            parts.append(hunk.header)
            parts.extend(hunk.lines)
        if file_diff.truncated:
            parts.append("... (truncated)")
    if diff_content.truncated_files:
        parts.append("... (additional files truncated)")
    return "\n".join(parts)


def resolve_chat_completions_url(config: LlmConfig) -> str | None:
    """Resolve the chat-completions endpoint from config."""
    if config.base_url:
        base = config.base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            return None
        return f"{base}/chat/completions"

    provider = (config.provider or "").lower()
    provider_base = _PROVIDER_BASE_URLS.get(provider)
    if provider_base is None:
        return None
    return f"{provider_base.rstrip('/')}/chat/completions"


def resolve_model_name(config: LlmConfig) -> str:
    """Pick a default model for the configured provider."""
    provider = (config.provider or "").lower()
    return _DEFAULT_MODELS.get(provider, config.provider or "gpt-4o-mini")


def request_chat_completion(
    config: LlmConfig,
    *,
    user_message: str,
    urlopen: Urlopen | None = None,
) -> LlmRunResult:
    """POST an OpenAI-compatible chat completion request."""
    preflight_error = _preflight_error(config)
    if preflight_error is not None:
        _warn(preflight_error)
        return LlmRunResult(error=preflight_error)

    url = resolve_chat_completions_url(config)
    if url is None:
        if config.base_url and config.base_url.rstrip("/").endswith("/chat/completions"):
            message = (
                "DIFFRAT_LLM_BASE_URL must be the API root (e.g. "
                "http://localhost:11434/v1), not the full /chat/completions path"
            )
        else:
            provider = config.provider or "unknown"
            message = (
                f"unknown LLM provider {provider!r} — set DIFFRAT_LLM_BASE_URL "
                "for custom or local endpoints (e.g. http://localhost:11434/v1 "
                "for Ollama)"
            )
        _warn(message)
        return LlmRunResult(error=message)

    payload = {
        "model": resolve_model_name(config),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a code review assistant. Analyze the git diff and "
                    "highlight risks, bugs, and review focus areas."
                ),
            },
            {"role": "user", "content": user_message},
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    opener = urlopen if urlopen is not None else urllib.request.urlopen
    try:
        with opener(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", None) or response.getcode()
            raw = response.read()
    except urllib.error.HTTPError as exc:
        message = _http_error_message(exc)
        _warn(message)
        return LlmRunResult(error=message)
    except urllib.error.URLError as exc:
        message = _connection_error_message(url, exc.reason)
        _warn(message)
        return LlmRunResult(error=message)
    except OSError as exc:
        message = f"LLM request failed: {exc}"
        _warn(message)
        return LlmRunResult(error=message)

    if status < 200 or status >= 300:
        message = f"LLM request failed with HTTP {status}"
        _warn(message)
        return LlmRunResult(error=message)

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        message = "LLM response was not valid JSON"
        _warn(message)
        return LlmRunResult(error=message)

    content = _extract_message_content(parsed)
    if content is None:
        message = "LLM response missing message content"
        _warn(message)
        return LlmRunResult(error=message)

    return LlmRunResult(findings=content)


def _preflight_error(config: LlmConfig) -> str | None:
    if config.base_url and config.base_url.rstrip("/").endswith("/chat/completions"):
        return (
            "DIFFRAT_LLM_BASE_URL must be the API root (e.g. "
            "http://localhost:11434/v1), not the full /chat/completions path"
        )

    provider = (config.provider or "").lower()
    if provider in _PROVIDER_BASE_URLS or config.base_url:
        return None

    return (
        f"provider {provider!r} requires DIFFRAT_LLM_BASE_URL — set it to your "
        "OpenAI-compatible API root (e.g. http://localhost:11434/v1 for Ollama)"
    )


def _http_error_message(exc: urllib.error.HTTPError) -> str:
    body_text = _read_http_error_body(exc)
    api_message = _parse_openai_error_message(body_text)

    if exc.code in (401, 403):
        if api_message:
            return f"LLM authentication failed (HTTP {exc.code}): {api_message}"
        return f"LLM authentication failed (HTTP {exc.code}) — check DIFFRAT_LLM_API_KEY"

    if exc.code == 404:
        if api_message:
            return f"LLM endpoint not found (HTTP 404): {api_message}"
        return (
            "LLM endpoint not found (HTTP 404) — verify DIFFRAT_LLM_BASE_URL "
            "points to an OpenAI-compatible API root"
        )

    if api_message:
        return f"LLM request failed with HTTP {exc.code}: {api_message}"
    return f"LLM request failed with HTTP {exc.code}"


def _connection_error_message(url: str, reason: object) -> str:
    reason_text = str(reason)
    if "Connection refused" in reason_text or "Errno 111" in reason_text:
        return (
            f"LLM connection refused at {url} — is the server running and is "
            "DIFFRAT_LLM_BASE_URL correct?"
        )
    return f"LLM request failed: {reason_text}"


def _read_http_error_body(exc: urllib.error.HTTPError) -> str | None:
    try:
        raw = exc.read()
    except OSError:
        return None
    if not raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _parse_openai_error_message(body_text: str | None) -> str | None:
    if not body_text:
        return None
    try:
        payload = json.loads(body_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    error = payload.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    message = payload.get("message")
    if isinstance(message, str) and message.strip():
        return message.strip()
    return None


def _extract_message_content(payload: dict[str, Any]) -> str | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None

    first = choices[0]
    if not isinstance(first, dict):
        return None

    message = first.get("message")
    if not isinstance(message, dict):
        return None

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        return None

    return content


def _warn(message: str) -> None:
    print(f"diffrat: warning: {message}", file=sys.stderr)
