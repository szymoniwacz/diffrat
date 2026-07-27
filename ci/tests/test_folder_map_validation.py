#!/usr/bin/env python3
"""Focused tests for bidirectional folder map validation."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "ci/validate-workflow-contracts.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_workflow_contracts", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator_module = load_validator_module()
parse_folder_map_paths = validator_module.parse_folder_map_paths

from test_project_validator import bootstrap_valid_project  # noqa: E402
from test_validator import copy_template_skeleton, run_validator  # noqa: E402


def bootstrap_template(root: Path) -> None:
    copy_template_skeleton(root)
    shutil.copytree(ROOT / ".ai", root / ".ai", dirs_exist_ok=True)
    shutil.copytree(ROOT / "examples", root / "examples", dirs_exist_ok=True)
    shutil.copytree(ROOT / "ci", root / "ci", dirs_exist_ok=True)
    for rel in (
        ".github/workflows/validate-workflow-contracts.yml",
        ".github/PULL_REQUEST_TEMPLATE/template-maintenance.md",
        ".cursor/rules/index.mdc",
        ".cursor/rules/ai-workflow.mdc",
    ):
        src = ROOT / rel
        if src.is_file():
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    (root / "pyproject.toml").write_text('[project]\nname = "fixture"\n', encoding="utf-8")
    (root / "src").mkdir()
    (root / "tests").mkdir()


def test_valid_repository_passes_folder_map_validation() -> None:
    result = run_validator(ROOT, "template")
    assert result.returncode == 0, result.stderr


def test_mapped_directory_missing_from_repository() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_template(root)
        flow = root / ".ai/docs/template-flow.md"
        flow.write_text(
            flow.read_text(encoding="utf-8").replace(
                "| `.ai/plans/` | Implementation plans |",
                "| `.ai/removed-folder/` | stale folder map entry |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "folder map references missing path: .ai/removed-folder" in result.stderr


def test_undocumented_ai_directory_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_template(root)
        flow = root / ".ai/docs/template-flow.md"
        flow.write_text(
            flow.read_text(encoding="utf-8").replace("| `.ai/plans/` | Implementation plans |", ""),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "repository directory is not documented in folder map: .ai/plans" in result.stderr


def test_undocumented_root_directory_detected_in_template_mode() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_template(root)
        (root / "tools").mkdir()
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "repository directory is not documented in folder map: tools" in result.stderr


def test_arbitrary_product_directories_allowed_in_project_mode() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        for name in ("config", "db", "public", "custom-product-directory"):
            (root / name).mkdir()
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_purpose_column_backticks_are_ignored() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_template(root)
        flow = root / ".ai/docs/template-flow.md"
        flow.write_text(
            flow.read_text(encoding="utf-8").replace(
                "| `.ai/plans/` | Implementation plans |",
                "| `.ai/plans/` | References `.ai/phantom-path/` for context |",
            ),
            encoding="utf-8",
        )
        paths = parse_folder_map_paths(root)
        assert ".ai/phantom-path" not in paths
        assert ".ai/plans" in paths
        result = run_validator(root, "template")
        assert result.returncode == 0, result.stderr


def main() -> int:
    tests = [
        test_valid_repository_passes_folder_map_validation,
        test_mapped_directory_missing_from_repository,
        test_undocumented_ai_directory_detected,
        test_undocumented_root_directory_detected_in_template_mode,
        test_arbitrary_product_directories_allowed_in_project_mode,
        test_purpose_column_backticks_are_ignored,
    ]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {test.__name__}: {exc}", file=sys.stderr)
    if failures:
        print(f"{failures} folder map test(s) failed", file=sys.stderr)
        return 1
    print("all folder map tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
