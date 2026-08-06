"""Repository configuration discovery and parsing for Diffrat.

Discovery order (from the git repository root, or ``cwd`` when not in a git repo):

1. ``pyproject.toml`` → ``[tool.diffrat]`` (base)
2. ``.diffrat.toml`` at the repo root overrides duplicate keys when both exist
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

_ARROW_SEPARATOR = re.compile(r"\s*→\s*")


@dataclass(frozen=True)
class ContentRule:
    """One declarative content hint rule from config."""

    code: str
    pattern: re.Pattern[str]
    expected: str
    paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiffratConfig:
    """Parsed per-repository Diffrat configuration."""

    checks: dict[str, str]
    content_rules: tuple[ContentRule, ...]


def load_config(cwd: Path | str) -> DiffratConfig:
    """Load Diffrat config for the repository containing ``cwd``."""
    root = _resolve_config_root(Path(cwd))
    merged = _merge_diffrat_sections(
        _read_diffrat_section(root / "pyproject.toml", nested=True),
        _read_diffrat_section(root / ".diffrat.toml", nested=False),
    )
    return _build_config(merged)


def _resolve_config_root(cwd: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return cwd.resolve()
    if result.returncode != 0:
        return cwd.resolve()
    toplevel = result.stdout.strip()
    if not toplevel:
        return cwd.resolve()
    return Path(toplevel)


def _read_diffrat_section(path: Path, *, nested: bool) -> dict[str, object]:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        print(f"diffrat config: warning: failed to parse {path}: {exc}", file=sys.stderr)
        return {}
    if nested:
        tool = data.get("tool")
        if not isinstance(tool, dict):
            return {}
        diffrat = tool.get("diffrat")
        if not isinstance(diffrat, dict):
            return {}
        return diffrat
    diffrat = data.get("diffrat")
    if not isinstance(diffrat, dict):
        return {}
    return diffrat


def _merge_diffrat_sections(
    base: dict[str, object],
    override: dict[str, object],
) -> dict[str, object]:
    merged = dict(base)
    for key, value in override.items():
        existing = merged.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            merged[key] = {**existing, **value}
        else:
            merged[key] = value
    return merged


def _build_config(section: dict[str, object]) -> DiffratConfig:
    checks = _parse_checks(section.get("checks"))
    content_rules = _parse_content_rules(section.get("content_rules"))
    return DiffratConfig(checks=checks, content_rules=content_rules)


def _parse_checks(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    checks: dict[str, str] = {}
    for code, command in raw.items():
        if not isinstance(code, str) or not isinstance(command, str):
            continue
        checks[code] = command
    return checks


def _parse_content_rules(raw: object) -> tuple[ContentRule, ...]:
    if not isinstance(raw, dict):
        return ()
    rules: list[ContentRule] = []
    for code, value in raw.items():
        if not isinstance(code, str):
            continue
        if isinstance(value, str):
            rule = _content_rule_from_shorthand(code, value)
            if rule is not None:
                rules.append(rule)
            continue
        if isinstance(value, dict):
            rule = _content_rule_from_mapping(code, value)
            if rule is not None:
                rules.append(rule)
            continue
        if isinstance(value, list):
            for entry in value:
                if not isinstance(entry, dict):
                    continue
                rule = _content_rule_from_mapping(code, entry)
                if rule is not None:
                    rules.append(rule)
    return tuple(rules)


def _content_rule_from_shorthand(code: str, value: str) -> ContentRule | None:
    parts = _ARROW_SEPARATOR.split(value, maxsplit=1)
    if len(parts) != 2:
        print(
            f"diffrat config: warning: content rule {code!r} "
            "shorthand must use 'pattern → expected'",
            file=sys.stderr,
        )
        return None
    pattern_text, expected = parts[0].strip(), parts[1].strip()
    return _compile_content_rule(code, pattern_text, expected, paths=())


def _content_rule_from_mapping(code: str, value: dict[str, object]) -> ContentRule | None:
    pattern = value.get("pattern")
    expected = value.get("expected")
    if not isinstance(pattern, str) or not isinstance(expected, str):
        print(
            f"diffrat config: warning: content rule {code!r} "
            "table must include pattern and expected",
            file=sys.stderr,
        )
        return None
    paths = _parse_paths(value.get("paths"))
    return _compile_content_rule(code, pattern, expected, paths=paths)


def _parse_paths(raw: object) -> tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        return ()
    paths: list[str] = []
    for entry in raw:
        if isinstance(entry, str):
            paths.append(entry)
    return tuple(paths)


def _compile_content_rule(
    code: str,
    pattern_text: str,
    expected: str,
    *,
    paths: tuple[str, ...],
) -> ContentRule | None:
    try:
        compiled = re.compile(pattern_text)
    except re.error as exc:
        print(
            f"diffrat config: warning: content rule {code!r} has invalid regex: {exc}",
            file=sys.stderr,
        )
        return None
    return ContentRule(code=code, pattern=compiled, expected=expected, paths=paths)
