"""Deterministic analysis: file categories and focus/risk hints."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from numbat.diff_parser import DiffSummary, FileChange

FileCategory = str  # source | tests | config | docs | ci | other

LARGE_DIFF_LINE_THRESHOLD = 300
LARGE_DIFF_FILE_THRESHOLD = 20

_CONFIG_BASENAMES = frozenset(
    {
        "pyproject.toml",
        "setup.cfg",
        "setup.py",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "pipfile",
        "pipfile.lock",
        "poetry.lock",
        "cargo.toml",
        "cargo.lock",
        "go.mod",
        "go.sum",
        "gemfile",
        "gemfile.lock",
        "composer.json",
        "composer.lock",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "tox.ini",
        "makefile",
    }
)

_CONFIG_EXTENSIONS = frozenset({".toml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".lock"})

_DOC_BASENAMES = frozenset(
    {
        "readme",
        "readme.md",
        "readme.rst",
        "readme.txt",
        "license",
        "license.md",
        "licence",
        "licence.md",
        "changelog",
        "changelog.md",
        "changes",
        "changes.md",
        "contributing",
        "contributing.md",
        "authors",
        "authors.md",
    }
)

_DOC_EXTENSIONS = frozenset({".md", ".rst", ".adoc"})

_SOURCE_EXTENSIONS = frozenset(
    {
        ".py",
        ".pyi",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        ".go",
        ".rs",
        ".java",
        ".kt",
        ".rb",
        ".php",
        ".c",
        ".cc",
        ".cpp",
        ".cxx",
        ".h",
        ".hpp",
        ".cs",
        ".swift",
        ".scala",
        ".sh",
        ".bash",
        ".zsh",
    }
)

_CI_WORKFLOW_VALIDATOR_COMMAND = (
    "python ci/validate-workflow-contracts.py --mode project"
)

_SECURITY_NAME_TOKENS = frozenset(
    {
        "auth",
        "oauth",
        "secret",
        "secrets",
        "credential",
        "credentials",
        "password",
        "passwd",
        "token",
        "tokens",
        "crypto",
        "crypt",
        "security",
        "secure",
        "cert",
        "certs",
        "certificate",
        "certificates",
        "keystore",
        "privatekey",
        "apikey",
    }
)


@dataclass(frozen=True)
class FocusRiskHint:
    """One deterministic focus or risk signal for reviewers."""

    code: str
    message: str


@dataclass(frozen=True)
class AnalysisResult:
    """Analysis signals derived from a diff summary."""

    categories: tuple[FileCategory, ...]
    hints: tuple[FocusRiskHint, ...]


def categorize_path(path: str) -> FileCategory:
    """Assign a coarse category from a repository-relative path."""
    posix = PurePosixPath(path.replace("\\", "/"))
    name_lower = posix.name.lower()
    parts_lower = tuple(part.lower() for part in posix.parts)
    suffix = posix.suffix.lower()

    if _is_tests_path(name_lower, parts_lower):
        return "tests"
    if _is_config_path(name_lower, suffix, parts_lower):
        return "config"
    if _is_docs_path(name_lower, suffix, parts_lower):
        return "docs"
    if _is_ci_path(parts_lower):
        return "ci"
    if suffix in _SOURCE_EXTENSIONS or "src" in parts_lower:
        return "source"
    return "other"


def analyze_diff(summary: DiffSummary) -> AnalysisResult:
    """Compute per-file categories and focus/risk hints for a diff."""
    categories = tuple(categorize_path(file_change.path) for file_change in summary.files)
    return AnalysisResult(categories=categories, hints=tuple(_build_hints(summary, categories)))


def _build_hints(
    summary: DiffSummary,
    categories: tuple[FileCategory, ...],
) -> list[FocusRiskHint]:
    hints: list[FocusRiskHint] = []

    if (
        summary.total_lines_changed >= LARGE_DIFF_LINE_THRESHOLD
        or summary.file_count >= LARGE_DIFF_FILE_THRESHOLD
    ):
        hints.append(
            FocusRiskHint(
                code="large_diff",
                message=(
                    f"Large diff: {summary.file_count} files, "
                    f"{summary.total_lines_changed} lines changed"
                ),
            )
        )

    if any(category == "tests" for category in categories):
        hints.append(
            FocusRiskHint(
                code="tests_touched",
                message="Tests touched — confirm coverage matches behavior changes",
            )
        )

    if any(category == "config" for category in categories):
        hints.append(
            FocusRiskHint(
                code="config_or_deps",
                message="Config or dependency files changed — review install and runtime impact",
            )
        )

    if categories and all(category == "docs" for category in categories):
        hints.append(
            FocusRiskHint(
                code="docs_touched",
                message="Documentation changed — confirm product/code docs stay aligned",
            )
        )

    security_paths = [
        file_change.path
        for file_change in summary.files
        if _is_security_sensitive(file_change)
    ]
    if security_paths:
        preview = ", ".join(security_paths[:3])
        if len(security_paths) > 3:
            preview = f"{preview}, +{len(security_paths) - 3} more"
        hints.append(
            FocusRiskHint(
                code="security_sensitive_paths",
                message=f"Security-sensitive paths changed: {preview}",
            )
        )

    ci_workflow_paths = [
        file_change.path
        for file_change in summary.files
        if _is_ci_workflow_validator_path(file_change.path)
    ]
    if ci_workflow_paths:
        preview = ", ".join(ci_workflow_paths[:3])
        if len(ci_workflow_paths) > 3:
            preview = f"{preview}, +{len(ci_workflow_paths) - 3} more"
        hints.append(
            FocusRiskHint(
                code="ci_workflow_paths",
                message=(
                    f"CI/workflow paths changed ({preview}) — run: "
                    f"{_CI_WORKFLOW_VALIDATOR_COMMAND}"
                ),
            )
        )

    return hints


def _is_tests_path(name_lower: str, parts_lower: tuple[str, ...]) -> bool:
    if any(part in {"test", "tests", "spec", "specs", "__tests__"} for part in parts_lower):
        return True
    if name_lower.startswith("test_") or name_lower.endswith("_test.py"):
        return True
    if ".test." in name_lower or ".spec." in name_lower:
        return True
    return False


def _is_config_path(
    name_lower: str,
    suffix: str,
    parts_lower: tuple[str, ...],
) -> bool:
    if name_lower in _CONFIG_BASENAMES:
        return True
    if name_lower.startswith("dockerfile") or name_lower.startswith(".env"):
        return True
    if name_lower.startswith("requirements") and name_lower.endswith(".txt"):
        return True
    if "requirements" in parts_lower and suffix == ".txt":
        return True
    if name_lower.endswith(".config.js") or name_lower.endswith(".config.ts"):
        return True
    if suffix in _CONFIG_EXTENSIONS:
        return True
    if suffix == ".json" and ("config" in parts_lower or "configs" in parts_lower):
        return True
    return False


def _is_ci_path(parts_lower: tuple[str, ...]) -> bool:
    return bool(parts_lower and parts_lower[0] == "ci")


def _is_docs_path(
    name_lower: str,
    suffix: str,
    parts_lower: tuple[str, ...],
) -> bool:
    if any(part in {"docs", "doc", "documentation"} for part in parts_lower):
        return True
    if name_lower in _DOC_BASENAMES:
        return True
    if name_lower.startswith("readme") or name_lower.startswith("changelog"):
        return True
    if suffix in _DOC_EXTENSIONS:
        return True
    return False


def is_ci_workflow_validator_path(path: str) -> bool:
    """Return True when a changed path should trigger CI/workflow validator checks."""
    return _is_ci_workflow_validator_path(path)


def is_python_source_or_test_path(path: str) -> bool:
    """Return True when a changed path should trigger pytest checks."""
    posix = PurePosixPath(path.replace("\\", "/"))
    parts = posix.parts
    if len(parts) >= 2 and parts[0] == "src" and parts[1] == "numbat":
        return True
    return bool(parts and parts[0] == "tests")


def _is_ci_workflow_validator_path(path: str) -> bool:
    posix = PurePosixPath(path.replace("\\", "/"))
    parts_lower = tuple(part.lower() for part in posix.parts)
    name_lower = posix.name.lower()

    if parts_lower and parts_lower[0] == "ci":
        return True
    if (
        len(parts_lower) >= 2
        and parts_lower[0] == ".github"
        and parts_lower[1] == "workflows"
    ):
        return True
    if name_lower == "validate-workflow-contracts.py":
        return True
    return False


def _is_security_sensitive(file_change: FileChange) -> bool:
    posix = PurePosixPath(file_change.path.replace("\\", "/"))
    name_lower = posix.name.lower()
    stem_lower = posix.stem.lower()
    parts_lower = tuple(part.lower() for part in posix.parts)

    if name_lower.startswith(".env"):
        return True

    tokens: set[str] = set(parts_lower)
    for raw in (stem_lower, *parts_lower):
        normalized = raw.replace("_", "-").replace(".", "-")
        tokens.update(token for token in normalized.split("-") if token)
    return bool(tokens & _SECURITY_NAME_TOKENS)
