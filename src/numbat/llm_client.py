"""OpenAI-compatible LLM HTTP client for diff-scoped analysis (ADR-0001)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from numbat.diff_parser import DiffContent
from numbat.llm_config import LlmConfig

_PROVIDER_BASE_URLS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
}

_DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "ollama": "llama3",
}

_REQUEST_TIMEOUT_SECONDS = 60.0

Urlopen = Callable[..., Any]


def run_llm_analysis(
    config: LlmConfig,
    *,
    diff_content: DiffContent | None = None,
    urlopen: Urlopen | None = None,
) -> str | None:
    """Request LLM analysis for a bounded diff. Returns content or None on failure."""
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
) -> str | None:
    """POST an OpenAI-compatible chat completion request."""
    url = resolve_chat_completions_url(config)
    if url is None:
        _warn(
            f"unknown LLM provider {config.provider!r} — set NUMBAT_LLM_BASE_URL "
            "for custom endpoints"
        )
        return None

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
        _warn(f"LLM request failed with HTTP {exc.code}")
        return None
    except urllib.error.URLError as exc:
        _warn(f"LLM request failed: {exc.reason}")
        return None
    except OSError as exc:
        _warn(f"LLM request failed: {exc}")
        return None

    if status < 200 or status >= 300:
        _warn(f"LLM request failed with HTTP {status}")
        return None

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        _warn("LLM response was not valid JSON")
        return None

    return _extract_message_content(parsed)


def _extract_message_content(payload: dict[str, Any]) -> str | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        _warn("LLM response missing choices")
        return None

    first = choices[0]
    if not isinstance(first, dict):
        _warn("LLM response choices entry is invalid")
        return None

    message = first.get("message")
    if not isinstance(message, dict):
        _warn("LLM response missing message")
        return None

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        _warn("LLM response missing message content")
        return None

    return content


def _warn(message: str) -> None:
    print(f"numbat: warning: {message}", file=sys.stderr)
