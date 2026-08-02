#!/usr/bin/env python3
"""Run validator fixtures to prove major failures are detected."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "ci/validate-workflow-contracts.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
EXACT_LOADER_ERROR = "live automation prompt must exactly match the canonical loader block"


def run_validator(root: Path, mode: str = "template") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--mode", mode, "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def copy_template_skeleton(target: Path) -> None:
    for rel in (
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
        "LICENSE",
        ".cursorrules",
        ".gitignore",
        ".github/copilot-instructions.md",
        ".github/pull_request_template.md",
        ".github/PULL_REQUEST_TEMPLATE/template-maintenance.md",
        ".ai/README.md",
        ".ai/instructions/workflow.md",
        ".ai/docs/template-flow.md",
        ".ai/docs/full-workflow.md",
        ".ai/docs/project-requirements.md",
        ".ai/contracts/project-definition-contract.md",
        ".ai/quality/definition-of-ready.md",
        ".ai/quality/definition-of-done.md",
        ".ai/quality/quality-gates.md",
        ".ai/policies/no-blind-coding.md",
        ".ai/policies/repo-drift-policy.md",
        ".ai/policies/autonomy-and-authorization.md",
        ".ai/policies/multi-agent-orchestration.md",
        ".ai/skills/execute-goal.md",
        ".ai/packets/task-packet.template.md",
        ".ai/packets/review-packet.template.md",
        ".ai/workflows/feature.md",
        ".ai/workflows/bugfix.md",
        ".ai/workflows/refactor.md",
        ".ai/onboarding/bootstrap-checklist.md",
        ".ai/git/branch-and-pr-workflow.md",
        ".ai/review/diff-risk-checklist.md",
        ".ai/review/human-review-checklist.md",
        ".ai/review/ai-review-checklist.md",
        ".ai/automation/README.md",
        ".ai/automation/goal-executor.md",
        ".ai/automation/goal-executor-production-setup.md",
        ".ai/automation/project-executor.md",
        ".ai/automation/project-executor-production-setup.md",
        ".ai/ideas/README.md",
        ".ai/conventions/repository-structure.md",
        ".ai/metrics/workflow-evaluation.md",
        "ci/validate-workflow-contracts.py",
        ".cursor/rules/index.mdc",
        ".cursor/rules/ai-workflow.mdc",
    ):
        src = ROOT / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    for rel in (
        ".github/PULL_REQUEST_TEMPLATE",
        "examples",
        ".ai/instructions",
        ".ai/docs",
        ".ai/contracts",
        ".ai/project",
        ".ai/onboarding",
        ".ai/architecture",
        ".ai/ideas/active",
        ".ai/ideas/expanded",
        ".ai/ideas/implemented",
        ".ai/ideas/archived",
        ".ai/packets",
        ".ai/plans",
        ".ai/skills",
        ".ai/workflows",
        ".ai/prompts",
        ".ai/conventions",
        ".ai/stack-profiles",
        ".ai/templates",
        ".ai/quality",
        ".ai/review",
        ".ai/policies",
        ".ai/git",
        ".ai/observability",
        ".ai/metrics",
        ".ai/maintenance",
        ".ai/automation",
        ".cursor/rules",
    ):
        (target / rel).mkdir(parents=True, exist_ok=True)


def test_current_repository_passes_template_mode() -> None:
    result = run_validator(ROOT, "template")
    assert result.returncode == 0, result.stderr


def test_missing_mandatory_file_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        (root / "AGENTS.md").unlink()
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "AGENTS.md" in result.stderr
        assert "mandatory file is missing" in result.stderr


def test_broken_markdown_link_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        readme = root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n[bad](missing-file.md)\n", encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "broken markdown link target" in result.stderr


def test_invalid_cursor_frontmatter_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        (root / ".cursor/rules/bad.mdc").write_text("# no frontmatter\n", encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "missing YAML frontmatter" in result.stderr


def test_project_mode_blocks_bootstrap_markers() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        scope = root / ".ai/project/scope.md"
        scope.write_text("> REPLACE DURING BOOTSTRAP: still here\n", encoding="utf-8")
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "product-owned file still contains bootstrap marker" in result.stderr


def test_project_mode_blocks_blocking_question() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        requirements = root / ".ai/docs/project-requirements.md"
        requirements.write_text(
            textwrap.dedent(
                """
                ## Project decision status

                | Area | Status | Value / notes | Link / location / return trigger |
                |---|---|---|---|
                | Product purpose | blocking-question | Need answer | TBD |

                ## Project readiness

                | Check | Result | Notes |
                |---|---|---|
                | Project ready for first product task | yes | ready |
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )
        result = run_validator(root, "project")
        assert result.returncode != 0
        assert "blocking-question" in result.stderr


def test_unclosed_cursor_frontmatter_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        (root / ".cursor/rules/bad.mdc").write_text("---\nalwaysApply: false\n# no closing marker\n", encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "frontmatter is not closed" in result.stderr


def test_cursor_frontmatter_without_routing_metadata_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        (root / ".cursor/rules/bad.mdc").write_text("---\n---\n# no routing metadata\n", encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "needs alwaysApply or description" in result.stderr


def test_multiple_always_apply_cursor_rules_are_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        ai_workflow = root / ".cursor/rules/ai-workflow.mdc"
        ai_workflow.write_text(
            ai_workflow.read_text(encoding="utf-8").replace("alwaysApply: false", "alwaysApply: true"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "exactly one Cursor rule must set alwaysApply: true" in result.stderr


def test_non_index_always_apply_cursor_rule_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        index = root / ".cursor/rules/index.mdc"
        index.write_text(index.read_text(encoding="utf-8").replace("alwaysApply: true", "alwaysApply: false"), encoding="utf-8")
        ai_workflow = root / ".cursor/rules/ai-workflow.mdc"
        ai_workflow.write_text(
            ai_workflow.read_text(encoding="utf-8").replace("alwaysApply: false", "alwaysApply: true"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "only index.mdc should set alwaysApply: true" in result.stderr


def test_broken_backtick_path_reference_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        readme = root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n`.ai/missing/file.md`\n", encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "broken path reference" in result.stderr


def test_deprecated_packet_plan_reference_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        readme = root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n`.ai/packets/example.plan.md`\n", encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "deprecated reference pattern" in result.stderr


def test_missing_workflow_stage_term_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        workflow = root / ".ai/instructions/workflow.md"
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace("implementation-ready", "ready-for-implementation"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "missing workflow stage term: implementation-ready" in result.stderr


def test_incorrect_full_workflow_lifecycle_order_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        full_workflow = root / ".ai/docs/full-workflow.md"
        original = full_workflow.read_text(encoding="utf-8")
        swapped = original.replace(
            "  -> create or update PR\n  -> CI stabilization\n  -> diff-risk assessment\n",
            "  -> create or update PR\n  -> diff-risk assessment\n  -> CI stabilization\n",
        )
        assert swapped != original
        full_workflow.write_text(swapped, encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "lifecycle stages out of order near: diff-risk assessment" in result.stderr


def test_incorrect_execute_goal_lifecycle_order_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        execute_goal = root / ".ai/skills/execute-goal.md"
        original = execute_goal.read_text(encoding="utf-8")
        swapped = original.replace(
            "  -> create or update PR\n"
            "  -> CI stabilization\n"
            "  -> then exactly one of:\n"
            "       stop before merge (default / self-correcting-review)\n",
            "  -> create or update PR\n"
            "  -> then exactly one of:\n"
            "       stop before merge (default / self-correcting-review)\n"
            "  -> CI stabilization\n",
        )
        assert swapped != original
        execute_goal.write_text(swapped, encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "lifecycle stages out of order near: stop before merge" in result.stderr


def test_missing_claude_local_gitignore_entry_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        gitignore = root / ".gitignore"
        gitignore.write_text(
            "\n".join(line for line in gitignore.read_text(encoding="utf-8").splitlines() if line != "CLAUDE.local.md")
            + "\n",
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "CLAUDE.local.md is not ignored" in result.stderr


def test_missing_idea_index_header_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        index = root / ".ai/ideas/README.md"
        index.write_text(
            index.read_text(encoding="utf-8").replace("| ID | Title | Status | Notes |", "| Identifier | Title | Status | Notes |"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "idea index table header is missing" in result.stderr


def test_unindexed_idea_file_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        (root / ".ai/ideas/active/IDEA-001.md").write_text("# Unindexed idea\n", encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "is not listed in the index table" in result.stderr


def test_bootstrap_marker_outside_allowed_template_files_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        feature = root / ".ai/workflows/feature.md"
        feature.write_text(feature.read_text(encoding="utf-8") + "\nREPLACE DURING BOOTSTRAP\n", encoding="utf-8")
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "unexpected bootstrap marker outside allowed template files" in result.stderr


def mutate_production_loader_block(setup_text: str, old: str, new: str) -> str:
    updated = setup_text.replace(old, new, 1)
    assert updated != setup_text
    return updated


def test_missing_goal_executor_live_loader_block_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            original.replace("## Live automation prompt", "## Automation prompt notes"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "missing required section: Live automation prompt" in result.stderr


def test_missing_goal_executor_loader_block_content_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            original.replace(
                "You are running the Goal Executor automation.\n\nBefore any repository mutation or remote write:",
                "You are running the Goal Executor automation.\n\nBefore any repository change:",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_goal_executor_loader_reads_working_branch_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            mutate_production_loader_block(
                original,
                "Read .ai/automation/goal-executor.md from that default branch.",
                "Read .ai/automation/goal-executor.md from the working branch.",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_goal_executor_loader_missing_canonical_path_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            mutate_production_loader_block(
                original,
                "2. Read .ai/automation/goal-executor.md from that default branch.",
                "2. Read .ai/automation/missing-goal-executor.md from that default branch.",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_goal_executor_loader_missing_fail_closed_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            mutate_production_loader_block(
                original,
                "fail closed: make no repository change and perform no remote write.",
                "continue even when the canonical file cannot be read.",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_goal_executor_loader_weakens_mutation_boundary_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            mutate_production_loader_block(
                original,
                "Before any repository mutation or remote write:",
                "After any repository mutation or remote write:",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_goal_executor_loader_weakens_complete_canonical_wording_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            mutate_production_loader_block(
                original,
                "Follow the loaded file as the complete canonical Goal Executor instructions for this run.",
                "Follow the loaded file as optional advisory Goal Executor instructions for this run.",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_goal_executor_loader_appends_contradictory_continue_after_failure_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            mutate_production_loader_block(
                original,
                "4. Follow the loaded file as the complete canonical Goal Executor instructions for this run.",
                (
                    "4. Follow the loaded file as the complete canonical Goal Executor instructions for this run.\n"
                    "5. If loading fails, continue anyway."
                ),
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_missing_goal_executor_automation_name_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/goal-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            original.replace("| Automation name | `Goal Executor` |", "| Automation name | |"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "configuration table is missing required row: Automation name" in result.stderr


def test_missing_diff_risk_field_in_pr_template_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        template = root / ".github/pull_request_template.md"
        template.write_text(
            template.read_text(encoding="utf-8").replace("Required action:", "Follow-up:"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "missing required diff-risk field: Required action:" in result.stderr


def test_missing_project_executor_merge_trigger_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/project-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            original.replace(
                "GitHub **issue comment**, **pull request merged**, and **CI/workflow completed** on the default branch",
                "GitHub **issue comment** and **CI/workflow completed** on the default branch",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert (
            "configuration table row 'Trigger events' must require pull request merged"
        ) in result.stderr


def test_missing_project_executor_ci_trigger_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/project-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            original.replace(
                "GitHub **issue comment**, **pull request merged**, and **CI/workflow completed** on the default branch",
                "GitHub **issue comment** and **pull request merged**",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert (
            "configuration table row 'Trigger events' must require CI/workflow completed"
        ) in result.stderr


def test_missing_project_executor_comment_filter_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/project-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            original.replace(
                "^/(execute-project( self-correcting-review( auto-merge)?)?|continue-project)$",
                "^/execute-project$",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert (
            "production setup must document comment filter "
            "'^/(execute-project( self-correcting-review( auto-merge)?)?|continue-project)$'"
        ) in result.stderr


def test_missing_project_executor_material_decision_section_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        prompt = root / ".ai/automation/project-executor.md"
        original = prompt.read_text(encoding="utf-8")
        prompt.write_text(
            original.replace("Material decision questions on GitHub", "Open questions"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert (
            "material decision section is missing required phrase: "
            "Material decision questions on GitHub"
        ) in result.stderr


def test_missing_project_executor_live_loader_block_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/project-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            original.replace("## Live automation prompt", "## Automation prompt notes"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert "missing required section: Live automation prompt" in result.stderr


def test_missing_project_executor_loader_block_content_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/project-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            original.replace(
                "You are running the Project Executor automation.\n\nBefore any repository mutation or remote write:",
                "You are running the Project Executor automation.\n\nBefore any repository change:",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_project_executor_loader_missing_fail_closed_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        setup = root / ".ai/automation/project-executor-production-setup.md"
        original = setup.read_text(encoding="utf-8")
        setup.write_text(
            mutate_production_loader_block(
                original,
                "make no change or remote write and report the blocker.",
                "continue even when either file cannot be read.",
            ),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert EXACT_LOADER_ERROR in result.stderr


def test_missing_project_executor_status_comment_section_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        copy_template_skeleton(root)
        prompt = root / ".ai/automation/project-executor.md"
        original = prompt.read_text(encoding="utf-8")
        prompt.write_text(
            original.replace("Status comments before stop", "Silent stops"),
            encoding="utf-8",
        )
        result = run_validator(root, "template")
        assert result.returncode != 0
        assert (
            "material decision section is missing required phrase: "
            "Status comments before stop"
        ) in result.stderr


def main() -> int:
    tests = [
        test_current_repository_passes_template_mode,
        test_missing_mandatory_file_is_detected,
        test_broken_markdown_link_is_detected,
        test_invalid_cursor_frontmatter_is_detected,
        test_project_mode_blocks_bootstrap_markers,
        test_project_mode_blocks_blocking_question,
        test_unclosed_cursor_frontmatter_is_detected,
        test_cursor_frontmatter_without_routing_metadata_is_detected,
        test_multiple_always_apply_cursor_rules_are_detected,
        test_non_index_always_apply_cursor_rule_is_detected,
        test_broken_backtick_path_reference_is_detected,
        test_deprecated_packet_plan_reference_is_detected,
        test_missing_workflow_stage_term_is_detected,
        test_incorrect_full_workflow_lifecycle_order_is_detected,
        test_incorrect_execute_goal_lifecycle_order_is_detected,
        test_missing_claude_local_gitignore_entry_is_detected,
        test_missing_idea_index_header_is_detected,
        test_unindexed_idea_file_is_detected,
        test_bootstrap_marker_outside_allowed_template_files_is_detected,
        test_missing_goal_executor_live_loader_block_is_detected,
        test_missing_goal_executor_loader_block_content_is_detected,
        test_goal_executor_loader_reads_working_branch_is_detected,
        test_goal_executor_loader_missing_canonical_path_is_detected,
        test_goal_executor_loader_missing_fail_closed_is_detected,
        test_goal_executor_loader_weakens_mutation_boundary_is_detected,
        test_goal_executor_loader_weakens_complete_canonical_wording_is_detected,
        test_goal_executor_loader_appends_contradictory_continue_after_failure_is_detected,
        test_missing_goal_executor_automation_name_is_detected,
        test_missing_project_executor_merge_trigger_is_detected,
        test_missing_project_executor_ci_trigger_is_detected,
        test_missing_project_executor_comment_filter_is_detected,
        test_missing_project_executor_material_decision_section_is_detected,
        test_missing_project_executor_status_comment_section_is_detected,
        test_missing_project_executor_live_loader_block_is_detected,
        test_missing_project_executor_loader_block_content_is_detected,
        test_project_executor_loader_missing_fail_closed_is_detected,
        test_missing_diff_risk_field_in_pr_template_is_detected,
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
        print(f"{failures} fixture test(s) failed", file=sys.stderr)
        return 1
    print("all fixture tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
