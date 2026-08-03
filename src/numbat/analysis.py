"""Deterministic analysis: file categories and focus/risk hints."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from numbat.config import NumbatConfig
from numbat.diff_parser import DiffContent, DiffSummary, FileChange
from numbat.git_adapter import GitContext
from numbat.scoring import HintSeverity, risk_score_for_file, severity_for_code

_SEVERITY_ORDER: dict[HintSeverity, int] = {"risk": 0, "warn": 1, "info": 2}

FileCategory = str  # source | tests | config | docs | ci | other

LARGE_DIFF_LINE_THRESHOLD = 300
LARGE_DIFF_FILE_THRESHOLD = 20

# Per-file concentration (complements aggregate large_diff threshold).
LARGE_SINGLE_FILE_PERCENT_THRESHOLD = 60
LARGE_SINGLE_FILE_MIN_FILE_LINES = 30
LARGE_SINGLE_FILE_MIN_TOTAL_LINES = 20

DELETIONS_HEAVY_MIN_DELETIONS = 20

MANY_COMMITS_THRESHOLD = 10
MIXED_CONCERNS_MIN_SEGMENTS = 3
MIXED_CONCERNS_MIN_SOURCE_CI_SEGMENTS = 2

_GENERATED_LOCKFILE_BASENAMES = frozenset(
    {
        "package-lock.json",
        "yarn.lock",
        "poetry.lock",
    }
)

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
_PYPROJECT_DEV_INSTALL_COMMAND = 'pip install -e ".[dev]"'
_RUFF_CHECK_COMMAND = "ruff check ."

_LOCKFILE_BASENAMES = frozenset(
    {
        "poetry.lock",
        "uv.lock",
        "pipfile.lock",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "go.sum",
        "cargo.lock",
        "gemfile.lock",
        "composer.lock",
    }
)

_MANIFEST_BASENAMES = frozenset(
    {
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "pipfile",
        "go.mod",
        "cargo.toml",
        "gemfile",
        "composer.json",
    }
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
    severity: HintSeverity
    path: str | None = None
    line: int | None = None


def focus_risk_hint(
    code: str,
    message: str,
    *,
    severity: HintSeverity | None = None,
    path: str | None = None,
    line: int | None = None,
) -> FocusRiskHint:
    """Create a hint with severity resolved from the registry when omitted."""
    return FocusRiskHint(
        code=code,
        message=message,
        severity=severity if severity is not None else severity_for_code(code),
        path=path,
        line=line,
    )


def sort_hints(hints: list[FocusRiskHint]) -> list[FocusRiskHint]:
    """Sort hints by severity (risk → warn → info), then by code."""
    return sorted(hints, key=lambda hint: (_SEVERITY_ORDER[hint.severity], hint.code))


@dataclass(frozen=True)
class AnalysisResult:
    """Analysis signals derived from a diff summary."""

    categories: tuple[FileCategory, ...]
    hints: tuple[FocusRiskHint, ...]
    risk_scores: tuple[int, ...]
    llm_findings: str | None = None


def categorize_path(path: str) -> FileCategory:
    """Assign a coarse category from a repository-relative path."""
    posix = PurePosixPath(path.replace("\\", "/"))
    name_lower = posix.name.lower()
    parts_lower = tuple(part.lower() for part in posix.parts)
    suffix = posix.suffix.lower()

    if _is_tests_path(name_lower, parts_lower):
        return "tests"
    if _is_ci_path(parts_lower):
        return "ci"
    if _is_config_path(name_lower, suffix, parts_lower):
        return "config"
    if _is_docs_path(name_lower, suffix, parts_lower):
        return "docs"
    if suffix in _SOURCE_EXTENSIONS or "src" in parts_lower:
        return "source"
    return "other"


def analyze_diff(
    summary: DiffSummary,
    *,
    diff_content: DiffContent | None = None,
    cwd: str | None = None,
    git_context: GitContext | None = None,
    config: NumbatConfig | None = None,
) -> AnalysisResult:
    """Compute per-file categories and focus/risk hints for a diff."""
    categories = tuple(categorize_path(file_change.path) for file_change in summary.files)
    hints = _build_hints(summary, categories, cwd=cwd)
    hints.extend(_git_context_hints(summary, categories, git_context=git_context))
    if diff_content is not None:
        from numbat.content_hints import content_focus_risk_hints

        hints.extend(content_focus_risk_hints(diff_content, config=config))

    non_binary_total_lines = sum(
        file_change.additions + file_change.deletions
        for file_change in summary.files
        if not file_change.binary
    )
    has_tests_in_diff = any(category == "tests" for category in categories)
    risk_scores = tuple(
        risk_score_for_file(
            file_change,
            category,
            total_non_binary_lines=non_binary_total_lines,
            has_tests_in_diff=has_tests_in_diff,
            security_sensitive=_is_security_sensitive(file_change),
        )
        for file_change, category in zip(summary.files, categories, strict=True)
    )
    return AnalysisResult(
        categories=categories,
        hints=tuple(hints),
        risk_scores=risk_scores,
    )


def _build_hints(
    summary: DiffSummary,
    categories: tuple[FileCategory, ...],
    *,
    cwd: str | None = None,
) -> list[FocusRiskHint]:
    hints: list[FocusRiskHint] = []

    if (
        summary.total_lines_changed >= LARGE_DIFF_LINE_THRESHOLD
        or summary.file_count >= LARGE_DIFF_FILE_THRESHOLD
    ):
        hints.append(
            focus_risk_hint(
                code="large_diff",
                message=(
                    f"Large diff: {summary.file_count} files, "
                    f"{summary.total_lines_changed} lines changed"
                ),
            )
        )

    # Per-file concentration: distinct from aggregate large_diff (300 lines / 20 files).
    if summary.total_lines_changed >= LARGE_SINGLE_FILE_MIN_TOTAL_LINES:
        dominant_file: FileChange | None = None
        dominant_lines = 0
        for file_change in summary.files:
            if file_change.binary:
                continue
            file_lines = file_change.additions + file_change.deletions
            if file_lines > dominant_lines:
                dominant_file = file_change
                dominant_lines = file_lines
        if (
            dominant_file is not None
            and dominant_lines >= LARGE_SINGLE_FILE_MIN_FILE_LINES
            and dominant_lines * 100
            >= LARGE_SINGLE_FILE_PERCENT_THRESHOLD * summary.total_lines_changed
        ):
            percent = dominant_lines * 100 // summary.total_lines_changed
            hints.append(
                focus_risk_hint(
                    code="large_single_file",
                    message=(
                        f"Single file dominates diff: {dominant_file.path} "
                        f"({dominant_lines} lines, {percent}% of total)"
                    ),
                    path=dominant_file.path,
                )
            )

    if (
        summary.total_deletions >= DELETIONS_HEAVY_MIN_DELETIONS
        and summary.total_deletions >= summary.total_additions
    ):
        hints.append(
            focus_risk_hint(
                code="deletions_heavy",
                message=(
                    f"Deletion-heavy diff: {summary.total_deletions} deletions vs "
                    f"{summary.total_additions} additions"
                ),
            )
        )

    if any(category == "tests" for category in categories):
        hints.append(
            focus_risk_hint(
                code="tests_touched",
                message="Tests touched — confirm coverage matches behavior changes",
            )
        )

    if any(category == "config" for category in categories):
        if any(is_pyproject_path(file_change.path) for file_change in summary.files):
            hints.append(
                focus_risk_hint(
                    code="config_or_deps",
                    message=(
                        "pyproject.toml changed — run: "
                        f"{_PYPROJECT_DEV_INSTALL_COMMAND} ; {_RUFF_CHECK_COMMAND}"
                    ),
                )
            )
        else:
            hints.append(
                focus_risk_hint(
                    code="config_or_deps",
                    message=(
                        "Config or dependency files changed — "
                        "review install and runtime impact"
                    ),
                )
            )

    if categories and all(category == "docs" for category in categories):
        hints.append(
            focus_risk_hint(
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
            focus_risk_hint(
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
            focus_risk_hint(
                code="ci_workflow_paths",
                message=(
                    f"CI/workflow paths changed ({preview}) — run: "
                    f"{_CI_WORKFLOW_VALIDATOR_COMMAND}"
                ),
            )
        )

    rename_paths = [
        file_change.path
        for file_change in summary.files
        if file_change.change_type in {"R", "C"}
    ]
    if rename_paths:
        preview = ", ".join(rename_paths[:3])
        if len(rename_paths) > 3:
            preview = f"{preview}, +{len(rename_paths) - 3} more"
        hints.append(
            focus_risk_hint(
                code="rename_or_move",
                message=f"Rename or copy detected: {preview}",
            )
        )

    # Structural hints from category composition (complement tests_touched / ci_workflow_paths).
    has_tests_in_diff = any(category == "tests" for category in categories)
    source_paths = [
        file_change.path
        for file_change, category in zip(summary.files, categories, strict=True)
        if category == "source"
    ]
    if source_paths and not has_tests_in_diff:
        preview = ", ".join(source_paths[:3])
        if len(source_paths) > 3:
            preview = f"{preview}, +{len(source_paths) - 3} more"
        hints.append(
            focus_risk_hint(
                code="source_without_tests",
                message=(
                    f"Source changed without tests in diff ({preview}) — "
                    "confirm test coverage"
                ),
            )
        )

    non_binary_files = [
        file_change for file_change in summary.files if not file_change.binary
    ]
    if non_binary_files and all(
        categorize_path(file_change.path) == "tests" for file_change in non_binary_files
    ):
        test_paths = [file_change.path for file_change in non_binary_files]
        preview = ", ".join(test_paths[:3])
        if len(test_paths) > 3:
            preview = f"{preview}, +{len(test_paths) - 3} more"
        hints.append(
            focus_risk_hint(
                code="tests_only",
                message=f"Tests-only diff ({preview}) — verify behavior change is covered",
            )
        )

    ci_paths = [
        file_change.path
        for file_change, category in zip(summary.files, categories, strict=True)
        if category == "ci"
    ]
    if ci_paths and not has_tests_in_diff:
        preview = ", ".join(ci_paths[:3])
        if len(ci_paths) > 3:
            preview = f"{preview}, +{len(ci_paths) - 3} more"
        hints.append(
            focus_risk_hint(
                code="ci_without_tests",
                message=(
                    f"CI files changed without tests in diff ({preview}) — "
                    "confirm CI changes are validated"
                ),
            )
        )

    workflow_paths = [
        file_change.path
        for file_change in summary.files
        if _is_github_workflow_path(file_change.path)
    ]
    if workflow_paths and not any(
        _is_ci_directory_path(file_change.path)
        or file_change.path.endswith("validate-workflow-contracts.py")
        for file_change in summary.files
    ):
        preview = ", ".join(workflow_paths[:3])
        if len(workflow_paths) > 3:
            preview = f"{preview}, +{len(workflow_paths) - 3} more"
        hints.append(
            focus_risk_hint(
                code="workflow_without_ci_validator",
                message=(
                    f"Workflow changed without CI validator paths ({preview}) — "
                    "confirm workflow contracts are validated"
                ),
            )
        )

    generated_paths = _generated_file_paths_without_source(summary)
    if generated_paths:
        preview = ", ".join(generated_paths[:3])
        if len(generated_paths) > 3:
            preview = f"{preview}, +{len(generated_paths) - 3} more"
        hints.append(
            focus_risk_hint(
                code="generated_file_touched",
                message=(
                    f"Generated artifact changed without source in diff ({preview}) — "
                    "verify regeneration is intentional"
                ),
            )
        )

    hints.extend(_missing_test_file_hints(summary, cwd=cwd))
    hints.extend(_lockfile_consistency_hints(summary, cwd=cwd))

    return hints


def _git_context_hints(
    summary: DiffSummary,
    categories: tuple[FileCategory, ...],
    *,
    git_context: GitContext | None,
) -> list[FocusRiskHint]:
    """Emit git-derived focus/risk hints from commit and path context."""
    hints: list[FocusRiskHint] = []

    if git_context is not None:
        if git_context.commit_count > MANY_COMMITS_THRESHOLD:
            hints.append(
                focus_risk_hint(
                    code="many_commits",
                    message=(
                        f"Many commits in reviewed range: {git_context.commit_count} "
                        f"(threshold > {MANY_COMMITS_THRESHOLD}) — consider smaller "
                        "slices or squash before review"
                    ),
                )
            )

        wip_subjects = [
            commit.subject
            for commit in git_context.commits
            if _is_wip_commit_subject(commit.subject)
        ]
        if wip_subjects:
            preview = ", ".join(wip_subjects[:3])
            if len(wip_subjects) > 3:
                preview = f"{preview}, +{len(wip_subjects) - 3} more"
            hints.append(
                focus_risk_hint(
                    code="wip_commits",
                    message=(
                        f"WIP/fixup/squash commit subjects detected: {preview} — "
                        "clean up before merge"
                    ),
                )
            )

    mixed_concerns = _mixed_concerns_hint(summary, categories)
    if mixed_concerns is not None:
        hints.append(mixed_concerns)

    return hints


def _is_wip_commit_subject(subject: str) -> bool:
    """Return True when a commit subject matches WIP/fixup/squash patterns."""
    lower = subject.strip().lower()
    if lower.startswith("wip"):
        return True
    return lower.startswith(("fixup!", "squash!", "sq!", "fixup:", "squash:"))


def _mixed_concerns_hint(
    summary: DiffSummary,
    categories: tuple[FileCategory, ...],
) -> FocusRiskHint | None:
    """Return a hint when unrelated top-level areas change together."""
    segment_categories: dict[str, set[FileCategory]] = {}
    for file_change, category in zip(summary.files, categories, strict=True):
        if category == "docs":
            continue
        posix = PurePosixPath(file_change.path.replace("\\", "/"))
        if not posix.parts:
            continue
        segment = posix.parts[0]
        segment_categories.setdefault(segment, set()).add(category)

    if len(segment_categories) < MIXED_CONCERNS_MIN_SEGMENTS:
        return None

    source_ci_segments = sorted(
        segment
        for segment, cats in segment_categories.items()
        if "source" in cats or "ci" in cats
    )
    if len(source_ci_segments) < MIXED_CONCERNS_MIN_SOURCE_CI_SEGMENTS:
        return None

    all_segments = sorted(segment_categories)
    preview = ", ".join(all_segments[:5])
    if len(all_segments) > 5:
        preview = f"{preview}, +{len(all_segments) - 5} more"
    return focus_risk_hint(
        code="mixed_concerns",
        message=(
            f"Changes span multiple top-level areas ({preview}) — "
            "confirm unrelated work is not bundled"
        ),
    )


def _is_generated_artifact_path(path: str) -> bool:
    """Return True when a path matches a known generated-artifact pattern."""
    posix = PurePosixPath(path.replace("\\", "/"))
    name_lower = posix.name.lower()
    if name_lower.endswith("_pb2.py"):
        return True
    if name_lower in _GENERATED_LOCKFILE_BASENAMES:
        return True
    return name_lower.endswith(".min.js")


def _generated_artifact_source_counterpart(path: str) -> str | None:
    """Return the expected source path for a generated artifact, if known."""
    posix = PurePosixPath(path.replace("\\", "/"))
    name_lower = posix.name.lower()
    if name_lower.endswith("_pb2.py"):
        stem = posix.stem[: -len("_pb2")]
        return str(posix.with_name(f"{stem}.proto"))
    if name_lower == "package-lock.json":
        return str(posix.with_name("package.json"))
    if name_lower == "yarn.lock":
        return str(posix.with_name("package.json"))
    if name_lower == "poetry.lock":
        return str(posix.with_name("pyproject.toml"))
    if name_lower.endswith(".min.js"):
        base_name = posix.name[: -len(".min.js")] + ".js"
        return str(posix.with_name(base_name))
    return None


def _generated_file_paths_without_source(summary: DiffSummary) -> list[str]:
    """List generated-artifact paths changed without their source counterpart."""
    changed_paths = {file_change.path for file_change in summary.files}
    unmatched: list[str] = []
    for file_change in summary.files:
        if not _is_generated_artifact_path(file_change.path):
            continue
        counterpart = _generated_artifact_source_counterpart(file_change.path)
        if counterpart is None or counterpart not in changed_paths:
            unmatched.append(file_change.path)
    return unmatched


def _missing_test_file_hints(
    summary: DiffSummary,
    *,
    cwd: str | None,
) -> list[FocusRiskHint]:
    """Emit hints when a changed src/numbat module lacks a mapped test file."""
    if cwd is None:
        return []

    root = Path(cwd)
    hints: list[FocusRiskHint] = []

    for file_change in summary.files:
        posix = PurePosixPath(file_change.path.replace("\\", "/"))
        parts = posix.parts
        if (
            len(parts) >= 2
            and parts[0] == "src"
            and parts[1] == "numbat"
            and posix.suffix == ".py"
        ):
            test_rel = f"tests/test_{posix.stem}.py"
            if not (root / test_rel).exists():
                hints.append(
                    focus_risk_hint(
                        code="missing_test_file",
                        message=(
                            f"Changed {file_change.path} has no {test_rel} on disk"
                        ),
                        path=file_change.path,
                    )
                )

    return hints


def _lockfile_consistency_hints(
    summary: DiffSummary,
    *,
    cwd: str | None,
) -> list[FocusRiskHint]:
    """Emit hints when lockfile and manifest changes are inconsistent."""
    changed_lockfiles = [
        file_change.path
        for file_change in summary.files
        if is_lockfile_path(file_change.path)
    ]
    changed_manifests = [
        file_change.path
        for file_change in summary.files
        if is_dependency_manifest_path(file_change.path)
    ]

    hints: list[FocusRiskHint] = []

    if changed_lockfiles and not changed_manifests:
        preview = ", ".join(changed_lockfiles[:3])
        if len(changed_lockfiles) > 3:
            preview = f"{preview}, +{len(changed_lockfiles) - 3} more"
        hints.append(
            focus_risk_hint(
                code="lockfile_without_manifest",
                message=(
                    f"Lockfile changed without manifest ({preview}) — "
                    "verify dependency manifest is updated"
                ),
            )
        )

    if changed_manifests and not changed_lockfiles and cwd is not None:
        root = Path(cwd)
        lockfiles_on_disk = [
            name for name in sorted(_LOCKFILE_BASENAMES) if (root / name).exists()
        ]
        if lockfiles_on_disk:
            preview = ", ".join(changed_manifests[:3])
            if len(changed_manifests) > 3:
                preview = f"{preview}, +{len(changed_manifests) - 3} more"
            lockfile_preview = ", ".join(lockfiles_on_disk[:3])
            if len(lockfiles_on_disk) > 3:
                lockfile_preview = (
                    f"{lockfile_preview}, +{len(lockfiles_on_disk) - 3} more"
                )
            hints.append(
                focus_risk_hint(
                    code="manifest_without_lockfile",
                    message=(
                        f"Manifest changed without lockfile ({preview}) — "
                        f"lockfile on disk: {lockfile_preview}"
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
    if parts_lower and parts_lower[0] == "ci":
        return True
    return (
        len(parts_lower) >= 2
        and parts_lower[0] == ".github"
        and parts_lower[1] == "workflows"
    )


def _is_ci_directory_path(path: str) -> bool:
    posix = PurePosixPath(path.replace("\\", "/"))
    parts_lower = tuple(part.lower() for part in posix.parts)
    return bool(parts_lower and parts_lower[0] == "ci")


def _is_github_workflow_path(path: str) -> bool:
    posix = PurePosixPath(path.replace("\\", "/"))
    parts_lower = tuple(part.lower() for part in posix.parts)
    return (
        len(parts_lower) >= 2
        and parts_lower[0] == ".github"
        and parts_lower[1] == "workflows"
    )


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


def is_pyproject_path(path: str) -> bool:
    """Return True when a changed path is pyproject.toml."""
    posix = PurePosixPath(path.replace("\\", "/"))
    return posix.name.lower() == "pyproject.toml"


def is_lockfile_path(path: str) -> bool:
    """Return True when a changed path is a recognized dependency lockfile."""
    posix = PurePosixPath(path.replace("\\", "/"))
    return posix.name.lower() in _LOCKFILE_BASENAMES


def is_dependency_manifest_path(path: str) -> bool:
    """Return True when a changed path is a recognized dependency manifest."""
    posix = PurePosixPath(path.replace("\\", "/"))
    name_lower = posix.name.lower()
    if name_lower in _MANIFEST_BASENAMES:
        return True
    return name_lower.startswith("requirements") and name_lower.endswith(".txt")


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
