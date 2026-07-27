#!/usr/bin/env python3
"""Project-mode validator fixture tests."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "ci/validate-workflow-contracts.py"


def _load_validator_helpers():
    spec = importlib.util.spec_from_file_location("validate_workflow_contracts", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.load_decision_areas, module.load_readiness_checks


load_decision_areas, load_readiness_checks = _load_validator_helpers()

from test_validator import copy_template_skeleton, run_validator  # noqa: E402

NUMBAT_STACK_PROFILE = """# Numbat CLI Stack Profile

## Common commands

```bash
pip install -e ".[dev]"
pytest
ruff check .
python -m numbat --help
```
"""

NUMBAT_README = """# Numbat

Local CLI for reviewing repository diffs.

## Setup

```bash
pip install -e ".[dev]"
pytest
```
"""


def build_valid_requirements(root: Path) -> None:
    areas = load_decision_areas(root)
    checks = load_readiness_checks(root)
    lines = [
        "## Project decision status",
        "",
        "| Area | Status | Value / notes | Link / location / return trigger |",
        "|---|---|---|---|",
    ]
    for area in areas:
        slug = area.lower().replace(" ", "-")
        lines.append(
            f"| {area} | decided | {area} value | .ai/project/decisions.md#{slug} |"
        )
    lines.extend(
        [
            "",
            "## Active stack profile",
            "",
            "| Active profile | Applies to | Notes |",
            "|---|---|---|",
            "| .ai/stack-profiles/numbat-cli.md | CLI | Primary stack |",
            "",
            "## Project readiness",
            "",
            "| Check | Result | Notes |",
            "|---|---|---|",
        ]
    )
    for check in checks:
        notes = "recorded during bootstrap"
        if check == "Real project commands recorded":
            notes = "README.md and .ai/stack-profiles/numbat-cli.md"
        lines.append(f"| {check} | yes | {notes} |")
    (root / ".ai/docs/project-requirements.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def bootstrap_valid_project(root: Path) -> None:
    copy_template_skeleton(root)
    shutil.copytree(ROOT / ".ai", root / ".ai", dirs_exist_ok=True)
    shutil.copytree(ROOT / "examples", root / "examples", dirs_exist_ok=True)
    for rel in (
        "ci/validate-workflow-contracts.py",
        ".github/PULL_REQUEST_TEMPLATE/template-maintenance.md",
    ):
        src = ROOT / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    workflow_src = ROOT / ".github/workflows/validate-workflow-contracts.yml"
    workflow_dst = root / ".github/workflows/validate-workflow-contracts.yml"
    workflow_dst.parent.mkdir(parents=True, exist_ok=True)
    workflow_dst.write_text(
        workflow_src.read_text(encoding="utf-8").replace(
            "python ci/validate-workflow-contracts.py --mode template",
            "python ci/validate-workflow-contracts.py --mode project",
        ),
        encoding="utf-8",
    )

    build_valid_requirements(root)
    stack_profile = root / ".ai/stack-profiles/numbat-cli.md"
    stack_profile.parent.mkdir(parents=True, exist_ok=True)
    stack_profile.write_text(NUMBAT_STACK_PROFILE, encoding="utf-8")
    (root / "README.md").write_text(NUMBAT_README, encoding="utf-8")
    (root / "AGENTS.md").write_text(
        "# Agent Instructions\n\nThis repository contains the Numbat CLI product.\n",
        encoding="utf-8",
    )
    (root / ".ai/project/vision.md").write_text(
        "Numbat helps developers review repository diffs locally.\n",
        encoding="utf-8",
    )
    (root / ".ai/project/product-context.md").write_text("Numbat reviews diffs locally.\n", encoding="utf-8")
    (root / ".ai/project/scope.md").write_text("CLI diff review in scope.\n", encoding="utf-8")
    (root / ".ai/project/roadmap.md").write_text("Phase 1: CLI MVP.\n", encoding="utf-8")
    (root / "pyproject.toml").write_text('[project]\nname = "numbat"\n', encoding="utf-8")
    (root / "src" / "numbat").mkdir(parents=True)
    (root / "src" / "numbat" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tests").mkdir(parents=True)
    (root / "tests" / "test_placeholder.py").write_text("def test_ok() -> None:\n    assert True\n", encoding="utf-8")


def test_valid_bootstrapped_project_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_instructional_marker_allowed_in_project_mode() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        checklist = root / ".ai/onboarding/bootstrap-checklist.md"
        checklist.write_text(
            checklist.read_text(encoding="utf-8")
            + "\nInstructional reference: REPLACE DURING BOOTSTRAP\n",
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_product_marker_rejected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / ".ai/project/scope.md").write_text("> REPLACE DURING BOOTSTRAP: still here\n", encoding="utf-8")
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "bootstrap marker" in result.stderr


def test_unchanged_template_vision_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        vision = root / ".ai/project/vision.md"
        vision.write_text("> REPLACE DURING BOOTSTRAP: still here\n", encoding="utf-8")
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert ".ai/project/vision.md" in result.stderr
        assert "bootstrap marker" in result.stderr


def test_missing_decision_area_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        lines = [line for line in req.read_text(encoding="utf-8").splitlines() if not line.startswith("| Users |")]
        req.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "missing decision area 'Users'" in result.stderr


def test_duplicate_decision_area_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        text = req.read_text(encoding="utf-8")
        duplicate = "| Users | decided | duplicate | .ai/project/decisions.md#users-dup |"
        text = text.replace(
            "| Users | decided | Users value | .ai/project/decisions.md#users |",
            "| Users | decided | Users value | .ai/project/decisions.md#users |\n" + duplicate,
        )
        req.write_text(text, encoding="utf-8")
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "appears more than once" in result.stderr


def test_decided_metadata_missing_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "| Product purpose | decided | Product purpose value |",
                "| Product purpose | decided |  | ",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "decided status requires" in result.stderr


def test_placeholder_stack_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                ".ai/stack-profiles/numbat-cli.md",
                ".ai/stack-profiles/[profile].md",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "placeholder" in result.stderr.lower()


def test_missing_stack_file_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                ".ai/stack-profiles/numbat-cli.md",
                ".ai/stack-profiles/missing-profile.md",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "does not exist" in result.stderr


def test_incomplete_readiness_row_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "| Bootstrap markers removed | yes |",
                "| Bootstrap markers removed | no |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "readiness row not passing" in result.stderr


def test_missing_readiness_row_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        lines = [
            line
            for line in req.read_text(encoding="utf-8").splitlines()
            if not line.startswith("| License and ownership decided |")
        ]
        req.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "missing project readiness row: License and ownership decided" in result.stderr


def test_default_accepted_metadata_missing_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "| Accessibility and localization | decided | Accessibility and localization value | .ai/project/decisions.md#accessibility-and-localization |",
                "| Accessibility and localization | default-accepted |  |  |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "default-accepted status requires" in result.stderr


def test_deferred_metadata_missing_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "| Compliance, backup, and recovery | decided | Compliance, backup, and recovery value | .ai/project/decisions.md#compliance,-backup,-and-recovery |",
                "| Compliance, backup, and recovery | deferred |  |  |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "deferred status requires" in result.stderr


def test_not_applicable_metadata_missing_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "| Supported platforms and compatibility | decided | Supported platforms and compatibility value | .ai/project/decisions.md#supported-platforms-and-compatibility |",
                "| Supported platforms and compatibility | not-applicable |  | .ai/project/decisions.md#supported-platforms |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "not-applicable status requires" in result.stderr


def test_placeholder_commands_in_stack_profile_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        shutil.copy(ROOT / ".ai/stack-profiles/python-cli.md", root / ".ai/stack-profiles/python-cli.md")
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                ".ai/stack-profiles/numbat-cli.md",
                ".ai/stack-profiles/python-cli.md",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "placeholder commands" in result.stderr.lower()


def test_missing_command_evidence_path_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/missing-commands.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "command evidence file does not exist" in result.stderr


def test_evidence_file_without_concrete_commands_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / ".ai/docs/commands.md").write_text(
            "# Commands\n\nReplace with project-defined commands.\n",
            encoding="utf-8",
        )
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | .ai/docs/commands.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "lacks concrete project commands" in result.stderr


def test_stack_profile_without_commands_with_readme_evidence_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / ".ai/stack-profiles/numbat-cli.md").write_text(
            "# Numbat CLI Stack Profile\n\nCommands are recorded in README.md.\n",
            encoding="utf-8",
        )
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | README.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_bin_rails_and_rubocop_commands_pass() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / "README.md").write_text(
            "# Numbat\n\n```bash\nbin/rails test\nbin/rubocop\nrspec\nrubocop\n```\n",
            encoding="utf-8",
        )
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | README.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_angle_bracket_placeholder_command_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / ".ai/docs/commands.md").write_text(
            "# Commands\n\n```bash\npython -m <package-name> --help\n```\n",
            encoding="utf-8",
        )
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | .ai/docs/commands.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "lacks concrete project commands" in result.stderr


def test_backtick_wrapped_evidence_paths_pass() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | `README.md` and `.ai/stack-profiles/numbat-cli.md` |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_absolute_command_evidence_path_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | /README.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "must be relative" in result.stderr


def test_command_evidence_path_escapes_repo_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | ../README.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "must stay inside repository" in result.stderr


def test_replace_command_is_concrete() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / ".ai/docs/commands.md").write_text(
            "# Commands\n\n```bash\nreplace old new file.txt\n```\n",
            encoding="utf-8",
        )
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | .ai/docs/commands.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_resolved_dotdot_evidence_path_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | .ai/../README.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_command_block_with_only_todo_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / ".ai/docs/commands.md").write_text(
            "# Commands\n\n```bash\nTODO\n```\n",
            encoding="utf-8",
        )
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | .ai/docs/commands.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "lacks concrete project commands" in result.stderr


def test_command_block_with_only_tbd_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / ".ai/docs/commands.md").write_text(
            "# Commands\n\n```bash\nTBD\n```\n",
            encoding="utf-8",
        )
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | .ai/docs/commands.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "lacks concrete project commands" in result.stderr


def test_example_stack_profile_path_allowed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        example_profile = root / ".ai/stack-profiles/ruby-example.md"
        example_profile.write_text(
            "# Ruby example profile\n\n```bash\nbundle exec rspec\nrubocop\n```\n",
            encoding="utf-8",
        )
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8")
            .replace(
                ".ai/stack-profiles/numbat-cli.md",
                ".ai/stack-profiles/ruby-example.md",
            )
            .replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/ruby-example.md |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode == 0, result.stderr


def test_template_readme_identity_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / "README.md").write_text(
            "# AI Project Template\n\nUse this repository as a starting point.\n",
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "template identity" in result.stderr


def test_template_agents_identity_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        (root / "AGENTS.md").write_text(
            "This is a documentation-first AI workflow template. It is not an application.\n",
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "template-only identity" in result.stderr


def test_commands_without_evidence_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "Real project commands recorded | yes | README.md and .ai/stack-profiles/numbat-cli.md |",
                "Real project commands recorded | yes | yes |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "evidence location" in result.stderr


def test_unknown_decision_area_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "| Product purpose | decided | Product purpose value | .ai/project/decisions.md#product-purpose |",
                "| Product purpose | decided | Product purpose value | .ai/project/decisions.md#product-purpose |\n"
                "| Imaginary area | decided | value | .ai/project/decisions.md#imaginary |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "unknown decision area" in result.stderr


def test_invalid_decision_status_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "| Product purpose | decided | Product purpose value |",
                "| Product purpose | in-progress | Product purpose value |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "invalid status" in result.stderr


def test_not_applicable_stack_without_reason_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bootstrap_valid_project(root)
        req = root / ".ai/docs/project-requirements.md"
        req.write_text(
            req.read_text(encoding="utf-8").replace(
                "| .ai/stack-profiles/numbat-cli.md | CLI | Primary stack |",
                "| not-applicable | None | |",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "stack marked not-applicable must include a reason in Notes" in result.stderr


def main() -> int:
    tests = [
        test_valid_bootstrapped_project_passes,
        test_instructional_marker_allowed_in_project_mode,
        test_product_marker_rejected,
        test_unchanged_template_vision_fails,
        test_missing_decision_area_fails,
        test_duplicate_decision_area_fails,
        test_decided_metadata_missing_fails,
        test_placeholder_stack_fails,
        test_missing_stack_file_fails,
        test_incomplete_readiness_row_fails,
        test_missing_readiness_row_fails,
        test_default_accepted_metadata_missing_fails,
        test_deferred_metadata_missing_fails,
        test_not_applicable_metadata_missing_fails,
        test_placeholder_commands_in_stack_profile_fails,
        test_missing_command_evidence_path_fails,
        test_evidence_file_without_concrete_commands_fails,
        test_stack_profile_without_commands_with_readme_evidence_passes,
        test_bin_rails_and_rubocop_commands_pass,
        test_angle_bracket_placeholder_command_fails,
        test_backtick_wrapped_evidence_paths_pass,
        test_absolute_command_evidence_path_fails,
        test_command_evidence_path_escapes_repo_fails,
        test_replace_command_is_concrete,
        test_resolved_dotdot_evidence_path_passes,
        test_command_block_with_only_todo_fails,
        test_command_block_with_only_tbd_fails,
        test_example_stack_profile_path_allowed,
        test_template_readme_identity_fails,
        test_template_agents_identity_fails,
        test_commands_without_evidence_fails,
        test_unknown_decision_area_fails,
        test_invalid_decision_status_fails,
        test_not_applicable_stack_without_reason_fails,
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
        print(f"{failures} project fixture test(s) failed", file=sys.stderr)
        return 1
    print("all project fixture tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
