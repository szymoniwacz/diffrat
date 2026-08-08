"""OpenAI-compatible LLM HTTP client for diff-scoped analysis (ADR-0001)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

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
    preflight_error = validate_llm_endpoint_config(config)
    if preflight_error is not None:
        _warn(preflight_error)
        return LlmRunResult(error=preflight_error)

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


def validate_llm_endpoint_config(config: LlmConfig) -> str | None:
    """Return an error message when the endpoint cannot be resolved."""
    if config.base_url:
        base = config.base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            return (
                "DIFFRAT_LLM_BASE_URL should be the API root (e.g. "
                "http://localhost:11434/v1), not the full /chat/completions path"
            )
        return None

    provider = (config.provider or "").lower()
    if provider in _PROVIDER_BASE_URLS:
        return None

    if provider == "ollama":
        return (
            "provider 'ollama' requires DIFFRAT_LLM_BASE_URL "
            "(e.g. http://localhost:11434/v1)"
        )

    return (
        f"unknown LLM provider {config.provider!r} — set DIFFRAT_LLM_BASE_URL "
        "for custom OpenAI-compatible endpoints"
    )


def resolve_chat_completions_url(config: LlmConfig) -> str | None:
    """Resolve the chat-completions endpoint from config."""
    if config.base_url:
        return f"{config.base_url.rstrip('/')}/chat/completions"

    provider = (config.provider or "").lower()
    base = _PROVIDER_BASE_URLS.get(provider)
    if base is None:
        return None
    return f"{base.rstrip('/')}/chat/completions"


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
    url = resolve_chat_completions_url(config)
    if url is None:
        message = (
            f"unknown LLM provider {config.provider!r} — set DIFFRAT_LLM_BASE_URL "
            "for custom endpoints"
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
        error_body = exc.read().decode("utf-8", errors="replace")
        message = format_http_error(exc.code, error_body)
        _warn(message)
        return LlmRunResult(error=message)
    except urllib.error.URLError as exc:
        message = format_url_error(exc, config)
        _warn(message)
        return LlmRunResult(error=message)
    except OSError as exc:
        message = f"LLM request failed: {exc}"
        _warn(message)
        return LlmRunResult(error=message)

    if status < 200 or status >= 300:
        message = format_http_error(status, raw.decode("utf-8", errors="replace"))
        _warn(message)
        return LlmRunResult(error=message)

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        message = "LLM response was not valid JSON"
        _warn(message)
        return LlmRunResult(error=message)

    content, parse_error = _extract_message_content(parsed)
    if parse_error is not None:
        _warn(parse_error)
        return LlmRunResult(error=parse_error)
    return LlmRunResult(findings=content)


def format_http_error(code: int, body: str) -> str:
    """Map an HTTP failure to an actionable message."""
    api_message = _parse_api_error_message(body)
    if code in (401, 403):
        hint = "check DIFFRAT_LLM_API_KEY"
        if api_message:
            return f"LLM authentication failed ({code}): {api_message} — {hint}"
        return f"LLM authentication failed ({code}) — {hint}"
    if code == 404:
        hint = (
            "check DIFFRAT_LLM_BASE_URL (should end with /v1, not /chat/completions)"
        )
        if api_message:
            return f"LLM endpoint not found ({code}): {api_message} — {hint}"
        return f"LLM endpoint not found ({code}) — {hint}"
    if api_message:
        return f"LLM request failed with HTTP {code}: {api_message}"
    return f"LLM request failed with HTTP {code}"


def format_url_error(exc: urllib.error.URLError, config: LlmConfig) -> str:
    """Map a transport failure to an actionable message."""
    reason = exc.reason
    reason_text = str(reason)
    if isinstance(reason, TimeoutError) or "timed out" in reason_text.lower():
        return f"LLM request timed out after {_REQUEST_TIMEOUT_SECONDS:g}s"
    host = _config_host(config)
    return f"cannot reach LLM endpoint at {host} — {reason_text}"


def _config_host(config: LlmConfig) -> str:
    if config.base_url:
        parsed = urlparse(config.base_url)
        if parsed.netloc:
            return parsed.netloc
        return config.base_url
    provider = (config.provider or "").lower()
    base = _PROVIDER_BASE_URLS.get(provider)
    if base is not None:
        return urlparse(base).netloc or base
    return config.provider or "unknown host"


def _parse_api_error_message(body: str) -> str | None:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    error = parsed.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    if isinstance(error, str) and error.strip():
        return error.strip()
    return None


def _extract_message_content(payload: dict[str, Any]) -> tuple[str | None, str | None]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None, "LLM response missing choices"

    first = choices[0]
    if not isinstance(first, dict):
        return None, "LLM response choices entry is invalid"

    message = first.get("message")
    if not isinstance(message, dict):
        return None, "LLM response missing message"

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        return None, "LLM response missing message content"

    return content, None


def _warn(message: str) -> None:
    print(f"diffrat: warning: {message}", file=sys.stderr)
