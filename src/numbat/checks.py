"""Local check execution for review --check."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath

from numbat.analysis import is_ci_workflow_validator_path, is_python_source_or_test_path
from numbat.diff_parser import DiffSummary

_CI_VALIDATOR_COMMAND = (
    "python ci/validate-workflow-contracts.py --mode project"
)
_PYTEST_COMMAND = "pytest"


@dataclass(frozen=True)
class CheckSpec:
    """One local check to run for the current diff."""

    code: str
    argv: tuple[str, ...]
    display_command: str


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one local check."""

    code: str
    command: str
    passed: bool
    output: str


def pytest_targets_for_paths(paths: list[str]) -> list[str]:
    """Map changed source/test paths to pytest target paths."""
    targets: list[str] = []
    seen: set[str] = set()

    for path in paths:
        if not is_python_source_or_test_path(path):
            continue
        target = _map_path_to_pytest_target(path)
        if target is not None and target not in seen:
            seen.add(target)
            targets.append(target)

    return sorted(targets)


def _map_path_to_pytest_target(path: str) -> str | None:
    posix = PurePosixPath(path.replace("\\", "/"))
    parts = posix.parts

    if len(parts) >= 2 and parts[0] == "src" and parts[1] == "numbat":
        if posix.suffix == ".py":
            return f"tests/test_{posix.stem}.py"
        return "tests"

    if parts and parts[0] == "tests":
        if posix.name.startswith("test_") and posix.suffix == ".py":
            return "/".join(parts)
        return "tests"

    return None


def plan_checks(summary: DiffSummary) -> list[CheckSpec]:
    """Select applicable checks from changed paths."""
    paths = [file_change.path for file_change in summary.files]
    specs: list[CheckSpec] = []
    seen: set[str] = set()

    if any(is_ci_workflow_validator_path(path) for path in paths):
        if "ci_validator" not in seen:
            seen.add("ci_validator")
            specs.append(
                CheckSpec(
                    code="ci_validator",
                    argv=(
                        sys.executable,
                        "ci/validate-workflow-contracts.py",
                        "--mode",
                        "project",
                    ),
                    display_command=_CI_VALIDATOR_COMMAND,
                )
            )

    pytest_targets = pytest_targets_for_paths(paths)
    if pytest_targets:
        if "pytest" not in seen:
            seen.add("pytest")
            display_command = f"{_PYTEST_COMMAND} {' '.join(pytest_targets)}"
            specs.append(
                CheckSpec(
                    code="pytest",
                    argv=(sys.executable, "-m", "pytest", *pytest_targets),
                    display_command=display_command,
                )
            )

    return specs


def run_checks(
    specs: list[CheckSpec],
    *,
    cwd: str | None = None,
) -> list[CheckResult]:
    """Run planned checks and return structured results."""
    results: list[CheckResult] = []
    for spec in specs:
        completed = subprocess.run(
            list(spec.argv),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        output = _format_subprocess_output(completed.stdout, completed.stderr)
        results.append(
            CheckResult(
                code=spec.code,
                command=spec.display_command,
                passed=completed.returncode == 0,
                output=output,
            )
        )
    return results


def _format_subprocess_output(stdout: str, stderr: str) -> str:
    parts = [part.strip() for part in (stdout, stderr) if part.strip()]
    return "\n".join(parts)
