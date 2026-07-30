"""Local check execution for review --check."""

from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath

from numbat.analysis import (
    is_ci_workflow_validator_path,
    is_dependency_manifest_path,
    is_lockfile_path,
    is_pyproject_path,
    is_python_source_or_test_path,
)
from numbat.config import NumbatConfig
from numbat.diff_parser import DiffSummary

# v1: only ci_validator may be overridden via [tool.numbat.checks].

_CI_VALIDATOR_COMMAND = (
    "python ci/validate-workflow-contracts.py --mode project"
)
_PYTEST_COMMAND = "pytest"
_MYPY_COMMAND = "mypy"
_RUFF_COMMAND = "ruff check ."
_BANDIT_COMMAND = "bandit"
_PIP_AUDIT_COMMAND = "pip-audit"


@dataclass(frozen=True)
class CheckSpec:
    """One local check to run for the current diff."""

    code: str
    argv: tuple[str, ...]
    display_command: str
    skip_reason: str | None = None


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one local check."""

    code: str
    command: str
    passed: bool
    output: str
    skipped: bool = False


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


def bandit_targets_for_paths(paths: list[str]) -> list[str]:
    """Map changed source paths to bandit targets under src/numbat/."""
    return mypy_targets_for_paths(paths)


def is_pip_audit_dependency_path(path: str) -> bool:
    """Return True when a changed path should trigger pip-audit."""
    return (
        is_pyproject_path(path)
        or is_lockfile_path(path)
        or is_dependency_manifest_path(path)
    )


def mypy_targets_for_paths(paths: list[str]) -> list[str]:
    """Map changed source paths to mypy target modules under src/numbat/."""
    targets: list[str] = []
    seen: set[str] = set()

    for path in paths:
        posix = PurePosixPath(path.replace("\\", "/"))
        parts = posix.parts
        if (
            len(parts) >= 2
            and parts[0] == "src"
            and parts[1] == "numbat"
            and posix.suffix == ".py"
        ):
            target = "/".join(parts)
            if target not in seen:
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


def parse_check_argv(display_command: str) -> tuple[str, ...]:
    """Parse a shell-style display command into argv without invoking a shell."""
    tokens = shlex.split(display_command)
    if not tokens:
        return ()
    if tokens[0] in {"python", "python3"}:
        tokens[0] = sys.executable
    return tuple(tokens)


def _ci_validator_spec(config: NumbatConfig | None) -> CheckSpec:
    display_command = _CI_VALIDATOR_COMMAND
    argv: tuple[str, ...] = (
        sys.executable,
        "ci/validate-workflow-contracts.py",
        "--mode",
        "project",
    )
    if config is not None and "ci_validator" in config.checks:
        display_command = config.checks["ci_validator"]
        argv = parse_check_argv(display_command)
    return CheckSpec(
        code="ci_validator",
        argv=argv,
        display_command=display_command,
    )


def plan_checks(
    summary: DiffSummary,
    *,
    config: NumbatConfig | None = None,
) -> list[CheckSpec]:
    """Select applicable checks from changed paths."""
    paths = [file_change.path for file_change in summary.files]
    specs: list[CheckSpec] = []
    seen: set[str] = set()

    if any(is_ci_workflow_validator_path(path) for path in paths):
        if "ci_validator" not in seen:
            seen.add("ci_validator")
            specs.append(_ci_validator_spec(config))

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

    mypy_targets = mypy_targets_for_paths(paths)
    if mypy_targets:
        if "mypy" not in seen:
            seen.add("mypy")
            display_command = f"{_MYPY_COMMAND} {' '.join(mypy_targets)}"
            specs.append(
                CheckSpec(
                    code="mypy",
                    argv=(sys.executable, "-m", "mypy", *mypy_targets),
                    display_command=display_command,
                )
            )

    if any(is_pyproject_path(path) for path in paths):
        if "ruff" not in seen:
            seen.add("ruff")
            specs.append(
                CheckSpec(
                    code="ruff",
                    argv=(sys.executable, "-m", "ruff", "check", "."),
                    display_command=_RUFF_COMMAND,
                )
            )

    bandit_targets = bandit_targets_for_paths(paths)
    if bandit_targets:
        if "bandit" not in seen:
            seen.add("bandit")
            display_command = _bandit_display_command(bandit_targets)
            bandit_executable = shutil.which("bandit")
            if bandit_executable is None:
                specs.append(
                    CheckSpec(
                        code="bandit",
                        argv=(),
                        display_command=display_command,
                        skip_reason="bandit not found on PATH",
                    )
                )
            else:
                specs.append(
                    CheckSpec(
                        code="bandit",
                        argv=_bandit_argv(bandit_executable, bandit_targets),
                        display_command=display_command,
                    )
                )

    if any(is_pip_audit_dependency_path(path) for path in paths):
        if "pip-audit" not in seen:
            seen.add("pip-audit")
            pip_audit_executable = shutil.which("pip-audit")
            if pip_audit_executable is None:
                specs.append(
                    CheckSpec(
                        code="pip-audit",
                        argv=(),
                        display_command=_PIP_AUDIT_COMMAND,
                        skip_reason="pip-audit not found on PATH",
                    )
                )
            else:
                specs.append(
                    CheckSpec(
                        code="pip-audit",
                        argv=(pip_audit_executable,),
                        display_command=_PIP_AUDIT_COMMAND,
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
        if spec.skip_reason is not None:
            results.append(
                CheckResult(
                    code=spec.code,
                    command=spec.display_command,
                    passed=True,
                    output=spec.skip_reason,
                    skipped=True,
                )
            )
            continue
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


def _bandit_display_command(targets: list[str]) -> str:
    flags = " ".join(f"-r {target}" for target in targets)
    return f"{_BANDIT_COMMAND} {flags}"


def _bandit_argv(executable: str, targets: list[str]) -> tuple[str, ...]:
    argv: list[str] = [executable]
    for target in targets:
        argv.extend(["-r", target])
    return tuple(argv)
