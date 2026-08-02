#!/usr/bin/env python3
"""Validate repository workflow contracts for template and project modes."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

BOOTSTRAP_MARKER = "REPLACE DURING BOOTSTRAP"

PASS_RESULTS = frozenset({"yes", "pass", "passed", "complete", "completed", "ready"})

VALID_DECISION_STATUSES = frozenset(
    {
        "decided",
        "default-accepted",
        "deferred",
        "not-applicable",
        "blocking-question",
    }
)

PRODUCT_MARKER_PATHS = (
    "README.md",
    ".ai/project/vision.md",
    ".ai/project/product-context.md",
    ".ai/project/scope.md",
    ".ai/project/roadmap.md",
)

TEMPLATE_README_SIGNATURES = (
    "AI Project Template",
    "Use this repository as a starting point",
    "documentation-first GitHub template",
)

TEMPLATE_AGENTS_SIGNATURES = (
    "It is not an application",
    "AI workflow template",
)

STACK_PLACEHOLDER_MARKERS = ("[profile]", "<profile>", "TODO", "TBD", "—")

STACK_PROFILE_PLACEHOLDER_PHRASES = (
    "replace with project-defined commands",
    "common commands (placeholders)",
)

PLACEHOLDER_COMMAND_LINE_RE = re.compile(r"<[^>]+>|\[profile\]|<profile>", re.IGNORECASE)

PLACEHOLDER_ONLY_COMMAND_LINES = frozenset({"todo", "tbd", "—", "-"})

REPLACE_PLACEHOLDER_RE = re.compile(r"^REPLACE(?:\.{3,}|\s*\.\.\.|(?:\s+WITH\b.*)?)?$", re.IGNORECASE)

COMMAND_EVIDENCE_PATH_RE = re.compile(r"(?:^|[\s,;]+)(README\.md|[\w./-]+\.md)")

LOADER_FENCE_LANGS = frozenset({"", "text", "txt", "plain"})


def normalize_loader_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def extract_loader_code_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    in_fence = False
    loader_fence = False
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_fence:
                if loader_fence:
                    blocks.append("\n".join(current))
                current = []
                in_fence = False
                loader_fence = False
            else:
                in_fence = True
                loader_fence = stripped[3:].strip().lower() in LOADER_FENCE_LANGS
            continue
        if in_fence and loader_fence:
            current.append(line)
    return blocks


SHELL_FENCE_LANGS = frozenset({"", "bash", "sh", "shell", "zsh"})


def extract_shell_code_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    in_fence = False
    shell_fence = False
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_fence:
                if shell_fence:
                    blocks.append("\n".join(current))
                current = []
                in_fence = False
                shell_fence = False
            else:
                in_fence = True
                shell_fence = stripped[3:].strip().lower() in SHELL_FENCE_LANGS
            continue
        if in_fence and shell_fence:
            current.append(line)
    return blocks


def is_replace_placeholder_command(stripped: str) -> bool:
    normalized = stripped.upper().rstrip()
    if normalized in {"REPLACE", "REPLACE..."}:
        return True
    return REPLACE_PLACEHOLDER_RE.fullmatch(normalized) is not None


def is_placeholder_only_command_line(stripped: str) -> bool:
    if PLACEHOLDER_COMMAND_LINE_RE.search(stripped):
        return True
    if is_replace_placeholder_command(stripped):
        return True
    normalized = stripped.lower().rstrip(".")
    return normalized in PLACEHOLDER_ONLY_COMMAND_LINES or stripped in PLACEHOLDER_ONLY_COMMAND_LINES


def line_has_concrete_command(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    return not is_placeholder_only_command_line(stripped)


def file_has_concrete_commands(text: str) -> bool:
    return any(
        line_has_concrete_command(line)
        for block in extract_shell_code_blocks(text)
        for line in block.splitlines()
    )


def stack_profile_has_placeholder_content(text: str) -> bool:
    lowered = text.lower()
    if any(phrase in lowered for phrase in STACK_PROFILE_PLACEHOLDER_PHRASES):
        return True
    for block in extract_shell_code_blocks(text):
        for line in block.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and PLACEHOLDER_COMMAND_LINE_RE.search(stripped):
                return True
    return False


def extract_command_evidence_paths(notes: str) -> list[str]:
    normalized = notes.replace("`", " ")
    paths: list[str] = []
    for match in COMMAND_EVIDENCE_PATH_RE.finditer(normalized):
        path = match.group(1).strip()
        if path not in paths:
            paths.append(path)
    return paths


def validate_command_evidence_path(root: Path, rel: str) -> tuple[bool, str]:
    rel = rel.strip()
    if not rel:
        return False, "command evidence path is empty"
    path_obj = Path(rel)
    if path_obj.is_absolute() or rel.startswith(("/", "\\")):
        return False, f"command evidence path must be relative: {rel}"
    if len(rel) > 1 and rel[1] == ":":
        return False, f"command evidence path must be relative: {rel}"
    root_resolved = root.resolve()
    candidate = (root_resolved / rel).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        return False, f"command evidence path must stay inside repository: {rel}"
    return True, ""


def parse_markdown_table(text: str, header_prefix: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip().startswith(header_prefix)), None)
    if start is None:
        return []

    rows: list[dict[str, str]] = []
    header = [cell.strip() for cell in lines[start].strip("|").split("|")]
    for line in lines[start + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def load_decision_areas(root: Path) -> list[str]:
    contract = root / ".ai/contracts/project-definition-contract.md"
    text = contract.read_text(encoding="utf-8")
    marker = "## Decision areas"
    start = text.find(marker)
    if start == -1:
        raise ValueError("decision areas section missing from project definition contract")

    section = text[start:]
    rows = parse_markdown_table(section, "| Area | What to establish |")
    areas = [row["Area"].strip() for row in rows if row.get("Area", "").strip()]
    if not areas:
        raise ValueError("no decision areas parsed from project definition contract")
    return areas


def load_readiness_checks(root: Path) -> list[str]:
    contract = root / ".ai/contracts/project-definition-contract.md"
    text = contract.read_text(encoding="utf-8")
    marker = "## Readiness check rows"
    start = text.find(marker)
    if start == -1:
        raise ValueError("readiness check rows section missing from project definition contract")

    section = text[start:]
    rows = parse_markdown_table(section, "| Check |")
    checks = [row["Check"].strip() for row in rows if row.get("Check", "").strip()]
    if not checks:
        raise ValueError("no readiness checks parsed from project definition contract")
    return checks


def is_pass_result(value: str) -> bool:
    return value.strip().lower() in PASS_RESULTS


def has_placeholder_stack_value(value: str) -> bool:
    stripped = value.strip()
    if not stripped or stripped in {"—", "-"}:
        return True
    lowered = stripped.lower()
    return any(marker.lower() in lowered for marker in STACK_PLACEHOLDER_MARKERS)


def status_metadata_valid(status: str, notes: str, location: str) -> tuple[bool, str]:
    notes = notes.strip()
    location = location.strip()
    if status == "decided":
        if notes and location:
            return True, ""
        return False, "decided status requires concrete value and link or location"
    if status == "default-accepted":
        if notes and location:
            return True, ""
        return False, "default-accepted status requires default and explicit human confirmation"
    if status == "deferred":
        if notes and location:
            return True, ""
        return False, "deferred status requires reason and return trigger or owner"
    if status == "not-applicable":
        if notes:
            return True, ""
        return False, "not-applicable status requires short justification"
    if status == "blocking-question":
        if notes:
            return True, ""
        return False, "blocking-question status requires an open question"
    return False, f"unknown status '{status}'"


WORKFLOW_STAGE_TERMS = (
    "ready for planning",
    "implementation-ready",
    "definition coverage",
    "project readiness",
)

CI_STABILIZATION_TERM = "ci stabilization"

FULL_WORKFLOW_LIFECYCLE_ORDER = (
    "create or update pr",
    "ci stabilization",
    "diff-risk assessment",
    "human review",
    "human merge",
)

EXECUTE_GOAL_LIFECYCLE_ORDER = (
    "create or update pr",
    "ci stabilization",
    "stop before merge",
)

LIFECYCLE_ORDER_CHECKS: dict[str, tuple[str, ...]] = {
    ".ai/docs/full-workflow.md": FULL_WORKFLOW_LIFECYCLE_ORDER,
    ".ai/skills/execute-goal.md": EXECUTE_GOAL_LIFECYCLE_ORDER,
}

LIFECYCLE_BLOCK_MARKERS: dict[str, str] = {
    ".ai/docs/full-workflow.md": "authorized goal",
    ".ai/skills/execute-goal.md": "resolve state",
}

WORKFLOW_STAGE_CHECKS: dict[str, tuple[str, ...]] = {
    ".ai/instructions/workflow.md": ("ready for planning", "implementation-ready"),
    ".ai/quality/definition-of-ready.md": ("ready for planning", "implementation-ready"),
    ".ai/docs/template-flow.md": WORKFLOW_STAGE_TERMS,
    ".ai/git/branch-and-pr-workflow.md": (CI_STABILIZATION_TERM, "applicable ci"),
    ".ai/quality/quality-gates.md": ("applicable ci",),
    ".ai/quality/definition-of-done.md": ("applicable ci",),
}

EXCLUDED_PATH_PREFIXES = (
    ".ai/roadmaps/",
    "ci/tests/fixtures/",
)

TECHNICAL_DIRECTORY_NAMES = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
    }
)

TECHNICAL_ROOT_DIRECTORIES = frozenset({".git"})

CI_VALIDATION_WORKFLOW = ".github/workflows/validate-workflow-contracts.yml"
CI_VALIDATE_TEMPLATE_COMMAND = "python ci/validate-workflow-contracts.py --mode template"
CI_VALIDATE_PROJECT_COMMAND = "python ci/validate-workflow-contracts.py --mode project"

GOAL_EXECUTOR_PROMPT = ".ai/automation/goal-executor.md"
GOAL_EXECUTOR_PRODUCTION_SETUP = ".ai/automation/goal-executor-production-setup.md"
GOAL_EXECUTOR_LIVE_LOADER_HEADING = "Live automation prompt"
GOAL_EXECUTOR_POST_MERGE_HEADING = "Post-merge loader migration"
GOAL_EXECUTOR_AUTOMATION_NAME = "Goal Executor"
GOAL_EXECUTOR_MODEL = "Composer 2.5"
GOAL_EXECUTOR_EXPECTED_LOADER = """You are running the Goal Executor automation.

Before any repository mutation or remote write:
1. Resolve the repository default branch.
2. Read .ai/automation/goal-executor.md from that default branch.
3. If the default branch or canonical file cannot be resolved and read, fail closed: make no repository change and perform no remote write.
4. Follow the loaded file as the complete canonical Goal Executor instructions for this run."""
PROJECT_EXECUTOR_PROMPT = ".ai/automation/project-executor.md"
PROJECT_EXECUTOR_PRODUCTION_SETUP = ".ai/automation/project-executor-production-setup.md"
PROJECT_EXECUTOR_LIVE_LOADER_HEADING = "Live automation prompt"
PROJECT_EXECUTOR_AUTOMATION_NAME = "Project Executor"
PROJECT_EXECUTOR_COMMENT_FILTER = (
    "^/(execute-project( self-correcting-review( auto-merge)?)?|continue-project)$"
)
PROJECT_EXECUTOR_MATERIAL_DECISION_REQUIRED_PHRASES = (
    "Material decision questions on GitHub",
    "lettered options",
    "Other",
    "reply with",
    "reply with option letters",
    "/continue-project",
    "Trigger events",
    "Pull request merged",
    "Closes #",
    "project-executor:goal project=",
    "does not need",
    "Status comments before stop",
    "platform-injected",
    "Commits on `main`",
)
PROJECT_EXECUTOR_EXPECTED_LOADER = """You are running the Project Executor automation.

Before any repository mutation or remote write:
1. Resolve the repository default branch.
2. Read .ai/automation/project-executor.md from that default branch.
3. Read .ai/automation/goal-executor.md from that default branch.
4. If the default branch or either file cannot be read, make no change or remote write and report the blocker.
5. Follow project-executor.md for orchestration and goal-executor.md for the delegated goal.
6. If this run was triggered by a merged pull request, resolve the parent Project Execution issue via Closes #<goal> and the project-executor:goal marker before state resolution. If resolution fails, no-op.
7. If this run was triggered by CI or workflow completion on the default branch, resolve the single active authorized Project Execution issue (prefer the project linked from the latest merged delegated goal on that tip). If resolution fails or is ambiguous, no-op."""
EXACT_LOADER_MATCH_ERROR = (
    "live automation prompt must exactly match the canonical loader block"
)

DIFF_RISK_CHECKLIST = ".ai/review/diff-risk-checklist.md"
DIFF_RISK_PR_TEMPLATE = ".github/pull_request_template.md"
DIFF_RISK_MAINTENANCE_TEMPLATE = ".github/PULL_REQUEST_TEMPLATE/template-maintenance.md"
DIFF_RISK_OUTPUT_FIELDS = (
    "Diff-risk:",
    "Signals:",
    "Evidence:",
    "Reviewer focus:",
    "Required action:",
)
DIFF_RISK_OBSOLETE_TABLE_INSTRUCTION = "copy the completed **risk signals** table"

MANDATORY_FILES = (
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "LICENSE",
    ".cursorrules",
    ".gitignore",
    ".github/copilot-instructions.md",
    ".github/pull_request_template.md",
    ".ai/README.md",
    ".ai/instructions/workflow.md",
    ".ai/docs/template-flow.md",
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
    ".ai/ideas/README.md",
    ".ai/conventions/repository-structure.md",
    ".ai/metrics/workflow-evaluation.md",
    "ci/validate-workflow-contracts.py",
)

FOLDER_MAP_PATH_CELL_RE = re.compile(r"^`([^`]+)`")

REMOVED_REFERENCE_PATTERNS = (
    re.compile(r"\.ai/packets/[^\s`]+\.plan\.md"),
    re.compile(r"plan lives in `\.ai/packets/`", re.IGNORECASE),
    re.compile(r"plans? in `\.ai/packets/`", re.IGNORECASE),
)

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
BACKTICK_PATH_RE = re.compile(
    r"`((?:\.(?:ai|github|cursor|claude)|examples|AGENTS\.md|CLAUDE\.md|README\.md)[^`\n]*)`"
)

IDEA_INDEX_HEADER = "| ID | Title | Status | Notes |"

PLACEHOLDER_PATH_MARKERS = ("*", "<", ">", "[", "]", "NNNN", "YYYY-MM-DD", "task-", "plan-", "adr-", "short-slug")


def parse_folder_map_paths(root: Path) -> list[str]:
    template_flow = root / ".ai/docs/template-flow.md"
    if not template_flow.is_file():
        return []
    text = template_flow.read_text(encoding="utf-8")
    start = text.find("## Complete folder map")
    if start == -1:
        return []
    search_from = start + len("## Complete folder map")
    next_heading = re.search(r"^## ", text[search_from:], re.MULTILINE)
    end = search_from + next_heading.start() if next_heading else len(text)
    section = text[start:end]
    paths: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("|---"):
            continue
        if stripped.startswith("| Path |"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        match = FOLDER_MAP_PATH_CELL_RE.match(cells[0])
        if not match:
            continue
        path = match.group(1).strip().rstrip("/")
        if path and path != ".ai":
            paths.append(path)
    return paths


def path_covered_by_map(path: str, map_paths: set[str]) -> bool:
    normalized = path.rstrip("/")
    for mapped in map_paths:
        mapped_normalized = mapped.rstrip("/")
        if (
            normalized == mapped_normalized
            or normalized.startswith(f"{mapped_normalized}/")
            or mapped_normalized.startswith(f"{normalized}/")
        ):
            return True
    return False


def extract_fenced_block_containing(text: str, marker: str) -> str | None:
    marker_lower = marker.lower()
    pos = 0
    while True:
        start = text.find("```", pos)
        if start == -1:
            return None
        end = text.find("```", start + 3)
        if end == -1:
            return None
        block = text[start:end]
        if marker_lower in block.lower():
            return block
        pos = end + 3


def lifecycle_stages_in_order(block: str, stages: tuple[str, ...]) -> str | None:
    """Return the first missing or out-of-order stage, or None when valid."""
    text = block.lower()
    search_from = 0
    for stage in stages:
        idx = text.find(stage, search_from)
        if idx == -1:
            return stage
        search_from = idx + len(stage)
    return None


@dataclass
class ValidationError:
    file: str
    message: str
    line: int | None = None

    def format(self) -> str:
        if self.line is not None:
            return f"{self.file}:{self.line}: {self.message}"
        return f"{self.file}: {self.message}"


def extract_markdown_section(text: str, heading: str) -> str | None:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return None
    start = match.end()
    next_heading = re.search(r"^## ", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


class Validator:
    def __init__(self, root: Path, mode: str) -> None:
        self.root = root.resolve()
        self.mode = mode
        self.errors: list[ValidationError] = []

    def add_error(self, file: str, message: str, line: int | None = None) -> None:
        self.errors.append(ValidationError(file, message, line))

    def is_excluded_path(self, rel: str) -> bool:
        normalized = f"{rel.rstrip('/')}/"
        for prefix in EXCLUDED_PATH_PREFIXES:
            excluded = prefix if prefix.endswith("/") else f"{prefix.rstrip('/')}/"
            if normalized.startswith(excluded):
                return True
        return False

    def is_placeholder_path(self, raw: str) -> bool:
        lowered = raw.lower()
        return any(marker.lower() in lowered for marker in PLACEHOLDER_PATH_MARKERS)

    def run(self) -> int:
        self.check_mandatory_files()
        self.check_folder_map()
        self.check_cursor_frontmatter()
        self.check_gitignore()
        self.check_markdown_links_and_paths()
        self.check_removed_references()
        self.check_workflow_stage_terms()
        self.check_lifecycle_order()
        self.check_goal_executor_loader_contract()
        self.check_project_executor_loader_contract()
        self.check_project_executor_material_decision_contract()
        self.check_diff_risk_output_contract()
        self.check_idea_index()
        self.check_bootstrap_markers()
        if self.mode == "project":
            self.check_project_mode()
        return 1 if self.errors else 0

    def check_mandatory_files(self) -> None:
        for rel in MANDATORY_FILES:
            path = self.root / rel
            if not path.is_file():
                self.add_error(rel, "mandatory file is missing")

    def should_skip_directory_scan(self, rel: str) -> bool:
        if self.is_excluded_path(rel):
            return True
        name = Path(rel).name
        if name in TECHNICAL_DIRECTORY_NAMES:
            return True
        if rel.rstrip("/") in TECHNICAL_ROOT_DIRECTORIES:
            return True
        return False

    def collect_relevant_repo_directories(self, mapped_paths: set[str]) -> list[str]:
        found: list[str] = []
        seen: set[str] = set()

        def add(rel: str) -> None:
            rel = rel.rstrip("/")
            if not rel or rel in seen or self.should_skip_directory_scan(rel):
                return
            seen.add(rel)
            found.append(rel)

        ai_contract = any(path == ".ai" or path.startswith(".ai/") for path in mapped_paths)
        ai_dir = self.root / ".ai"
        if ai_contract and ai_dir.is_dir():
            for child in sorted(ai_dir.iterdir()):
                if child.is_dir():
                    add(child.relative_to(self.root).as_posix())

        if self.mode == "template":
            for child in sorted(self.root.iterdir()):
                if child.is_dir():
                    add(child.relative_to(self.root).as_posix())

        return found

    def check_folder_map(self) -> None:
        map_paths = parse_folder_map_paths(self.root)
        if not map_paths:
            self.add_error(
                ".ai/docs/template-flow.md",
                "could not parse canonical folder map table under ## Complete folder map",
            )
            return

        normalized_map = {path.rstrip("/") for path in map_paths}

        for rel in sorted(normalized_map):
            if not (self.root / rel).exists():
                self.add_error(
                    ".ai/docs/template-flow.md",
                    f"folder map references missing path: {rel}",
                )

        for rel in self.collect_relevant_repo_directories(normalized_map):
            if not path_covered_by_map(rel, normalized_map):
                self.add_error(
                    ".ai/docs/template-flow.md",
                    f"repository directory is not documented in folder map: {rel}",
                )

    def check_cursor_frontmatter(self) -> None:
        rules_dir = self.root / ".cursor/rules"
        if not rules_dir.is_dir():
            self.add_error(".cursor/rules", "Cursor rules directory is missing")
            return

        always_apply_files: list[str] = []
        for path in sorted(rules_dir.glob("*.mdc")):
            rel = path.relative_to(self.root).as_posix()
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                self.add_error(rel, "Cursor rule is missing YAML frontmatter")
                continue

            end = text.find("---", 3)
            if end == -1:
                self.add_error(rel, "Cursor rule frontmatter is not closed")
                continue

            frontmatter = text[3:end]
            has_always_apply = re.search(r"^alwaysApply:\s*(true|false)\s*$", frontmatter, re.M)
            has_description = re.search(r"^description:\s*.+\s*$", frontmatter, re.M)
            if not has_always_apply and not has_description:
                self.add_error(rel, "Cursor rule frontmatter needs alwaysApply or description")

            if has_always_apply and has_always_apply.group(1) == "true":
                always_apply_files.append(rel)

        if len(always_apply_files) != 1:
            self.add_error(
                ".cursor/rules",
                "exactly one Cursor rule must set alwaysApply: true "
                f"(found {len(always_apply_files)})",
            )
        elif always_apply_files[0] != ".cursor/rules/index.mdc":
            self.add_error(
                ".cursor/rules/index.mdc",
                "only index.mdc should set alwaysApply: true",
            )

    def check_gitignore(self) -> None:
        gitignore = self.root / ".gitignore"
        if not gitignore.is_file():
            return
        content = gitignore.read_text(encoding="utf-8")
        if "CLAUDE.local.md" not in content.splitlines():
            self.add_error(".gitignore", "CLAUDE.local.md is not ignored")

    def iter_markdown_files(self) -> list[Path]:
        files: list[Path] = []
        for pattern in ("**/*.md", "**/*.mdc"):
            for path in self.root.glob(pattern):
                rel = path.relative_to(self.root).as_posix()
                if self.is_excluded_path(rel):
                    continue
                if "/.git/" in f"/{rel}/":
                    continue
                files.append(path)
        return sorted(files)

    def resolve_local_target(self, source: Path, target: str) -> Path | None:
        target = target.strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            return None
        if target.startswith("#"):
            return None

        target = target.split("#", 1)[0].strip()
        if not target:
            return None

        if target.startswith("/"):
            candidate = self.root / target.lstrip("/")
        else:
            candidate = (source.parent / target).resolve()
        return candidate

    def check_markdown_links_and_paths(self) -> None:
        for path in self.iter_markdown_files():
            rel = path.relative_to(self.root).as_posix()
            text = path.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                for match in MARKDOWN_LINK_RE.finditer(line):
                    target = match.group(1)
                    resolved = self.resolve_local_target(path, target)
                    if resolved is None:
                        continue
                    if not resolved.exists():
                        self.add_error(rel, f"broken markdown link target: {target}", line_no)

                for match in BACKTICK_PATH_RE.finditer(line):
                    raw = match.group(1).strip()
                    if self.is_placeholder_path(raw):
                        continue
                    if raw.endswith("/"):
                        parent_rel = "/".join(raw.rstrip("/").split("/")[:-1])
                        if parent_rel and (self.root / parent_rel).is_dir():
                            continue
                    candidate = self.root / raw.rstrip("/")
                    if candidate.exists():
                        continue
                    if raw.endswith(".md") or raw.endswith(".mdc") or "/" in raw:
                        self.add_error(rel, f"broken path reference: {raw}", line_no)

    def check_removed_references(self) -> None:
        for path in self.iter_markdown_files():
            rel = path.relative_to(self.root).as_posix()
            text = path.read_text(encoding="utf-8")
            for pattern in REMOVED_REFERENCE_PATTERNS:
                if pattern.search(text):
                    self.add_error(rel, f"deprecated reference pattern: {pattern.pattern}")

    def check_workflow_stage_terms(self) -> None:
        for rel, terms in WORKFLOW_STAGE_CHECKS.items():
            path = self.root / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8").lower()
            for term in terms:
                if term not in text:
                    self.add_error(rel, f"missing workflow stage term: {term}")

    def check_lifecycle_order(self) -> None:
        for rel, stages in LIFECYCLE_ORDER_CHECKS.items():
            path = self.root / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            marker = LIFECYCLE_BLOCK_MARKERS[rel]
            block = extract_fenced_block_containing(text, marker)
            if block is None:
                self.add_error(rel, f"lifecycle order block missing marker: {marker}")
                continue
            bad_stage = lifecycle_stages_in_order(block, stages)
            if bad_stage is not None:
                self.add_error(rel, f"lifecycle stages out of order near: {bad_stage}")

    def check_goal_executor_loader_contract(self) -> None:
        prompt_path = self.root / GOAL_EXECUTOR_PROMPT
        if not prompt_path.is_file():
            self.add_error(GOAL_EXECUTOR_PROMPT, "Goal Executor prompt is missing")
            return

        prompt_text = prompt_path.read_text(encoding="utf-8")
        if "GOAL_EXECUTOR_RUNTIME_VERSION" in prompt_text:
            self.add_error(
                GOAL_EXECUTOR_PROMPT,
                "runtime version marker must not remain in canonical Goal Executor prompt",
            )
        if re.search(r"paste this file into cursor automation", prompt_text, re.I):
            self.add_error(
                GOAL_EXECUTOR_PROMPT,
                "canonical Goal Executor prompt must not require pasting into Cursor",
            )

        setup_path = self.root / GOAL_EXECUTOR_PRODUCTION_SETUP
        if not setup_path.is_file():
            self.add_error(
                GOAL_EXECUTOR_PRODUCTION_SETUP,
                "Goal Executor production setup guide is missing",
            )
            return

        setup_text = setup_path.read_text(encoding="utf-8")
        loader_section = extract_markdown_section(setup_text, GOAL_EXECUTOR_LIVE_LOADER_HEADING)
        if loader_section is None:
            self.add_error(
                GOAL_EXECUTOR_PRODUCTION_SETUP,
                f"missing required section: {GOAL_EXECUTOR_LIVE_LOADER_HEADING}",
            )
            return

        loader_blocks = extract_loader_code_blocks(loader_section)
        if len(loader_blocks) != 1:
            self.add_error(
                GOAL_EXECUTOR_PRODUCTION_SETUP,
                "production setup must contain exactly one live automation prompt block",
            )
            return

        normalized_loader = normalize_loader_text(loader_blocks[0])
        normalized_expected = normalize_loader_text(GOAL_EXECUTOR_EXPECTED_LOADER)
        if normalized_loader != normalized_expected:
            self.add_error(GOAL_EXECUTOR_PRODUCTION_SETUP, EXACT_LOADER_MATCH_ERROR)

        if extract_markdown_section(setup_text, GOAL_EXECUTOR_POST_MERGE_HEADING) is None:
            self.add_error(
                GOAL_EXECUTOR_PRODUCTION_SETUP,
                f"missing required section: {GOAL_EXECUTOR_POST_MERGE_HEADING}",
            )
        else:
            migration_text = extract_markdown_section(
                setup_text, GOAL_EXECUTOR_POST_MERGE_HEADING
            )
            assert migration_text is not None
            migration_lower = migration_text.lower()
            for step in (
                "disable automation",
                "human merges this change",
                "replace the old full live prompt with the loader block",
                "verify the saved prompt exactly",
                "enable for one controlled test",
                "verify the run loaded the canonical file from the default branch",
            ):
                if step not in migration_lower:
                    self.add_error(
                        GOAL_EXECUTOR_PRODUCTION_SETUP,
                        f"post-merge loader migration is missing step: {step}",
                    )

        config_rows = parse_markdown_table(setup_text, "| Parameter | Required value |")
        config_map = {
            row.get("Parameter", "").strip(): row.get("Required value", "").strip()
            for row in config_rows
            if row.get("Parameter", "").strip()
        }
        for label, expected in (
            ("Automation name", GOAL_EXECUTOR_AUTOMATION_NAME),
            ("Model", GOAL_EXECUTOR_MODEL),
        ):
            actual = config_map.get(label, "")
            if not actual:
                self.add_error(
                    GOAL_EXECUTOR_PRODUCTION_SETUP,
                    f"configuration table is missing required row: {label}",
                )
            elif expected not in actual:
                self.add_error(
                    GOAL_EXECUTOR_PRODUCTION_SETUP,
                    f"configuration table row '{label}' must include required value '{expected}'",
                )

        if "runtime version" in setup_text.lower():
            self.add_error(
                GOAL_EXECUTOR_PRODUCTION_SETUP,
                "production setup must not retain runtime version synchronization",
            )

    def check_project_executor_loader_contract(self) -> None:
        setup_path = self.root / PROJECT_EXECUTOR_PRODUCTION_SETUP
        if not setup_path.is_file():
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                "Project Executor production setup guide is missing",
            )
            return

        setup_text = setup_path.read_text(encoding="utf-8")
        loader_section = extract_markdown_section(
            setup_text, PROJECT_EXECUTOR_LIVE_LOADER_HEADING
        )
        if loader_section is None:
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                f"missing required section: {PROJECT_EXECUTOR_LIVE_LOADER_HEADING}",
            )
            return

        loader_blocks = extract_loader_code_blocks(loader_section)
        if len(loader_blocks) != 1:
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                "production setup must contain exactly one live automation prompt block",
            )
            return

        normalized_loader = normalize_loader_text(loader_blocks[0])
        normalized_expected = normalize_loader_text(PROJECT_EXECUTOR_EXPECTED_LOADER)
        if normalized_loader != normalized_expected:
            self.add_error(PROJECT_EXECUTOR_PRODUCTION_SETUP, EXACT_LOADER_MATCH_ERROR)

        config_rows = parse_markdown_table(setup_text, "| Parameter | Required value |")
        config_map = {
            row.get("Parameter", "").strip(): row.get("Required value", "").strip()
            for row in config_rows
            if row.get("Parameter", "").strip()
        }
        automation_name = config_map.get("Automation name", "")
        if not automation_name:
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                "configuration table is missing required row: Automation name",
            )
        elif PROJECT_EXECUTOR_AUTOMATION_NAME not in automation_name:
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                f"configuration table row 'Automation name' must include required value '{PROJECT_EXECUTOR_AUTOMATION_NAME}'",
            )

        trigger_events = config_map.get("Trigger events", "")
        if not trigger_events:
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                "configuration table is missing required row: Trigger events",
            )
        else:
            trigger_lower = trigger_events.lower()
            if "issue comment" not in trigger_lower:
                self.add_error(
                    PROJECT_EXECUTOR_PRODUCTION_SETUP,
                    "configuration table row 'Trigger events' must require GitHub issue comment",
                )
            if "pull request merged" not in trigger_lower:
                self.add_error(
                    PROJECT_EXECUTOR_PRODUCTION_SETUP,
                    "configuration table row 'Trigger events' must require pull request merged",
                )
            if (
                "ci/workflow completed" not in trigger_lower
                and "workflow completed" not in trigger_lower
            ):
                self.add_error(
                    PROJECT_EXECUTOR_PRODUCTION_SETUP,
                    "configuration table row 'Trigger events' must require CI/workflow completed",
                )

        comment_filter = config_map.get("Comment filter regex", "")
        if not comment_filter:
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                "configuration table is missing required row: Comment filter regex",
            )
        elif PROJECT_EXECUTOR_COMMENT_FILTER not in setup_text:
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                f"production setup must document comment filter '{PROJECT_EXECUTOR_COMMENT_FILTER}'",
            )

        if re.search(r"\bschedule\b", setup_text, re.I):
            self.add_error(
                PROJECT_EXECUTOR_PRODUCTION_SETUP,
                "production setup must not use a schedule trigger",
            )

    def check_project_executor_material_decision_contract(self) -> None:
        prompt_path = self.root / PROJECT_EXECUTOR_PROMPT
        if not prompt_path.is_file():
            self.add_error(
                PROJECT_EXECUTOR_PROMPT,
                "Project Executor prompt is missing",
            )
            return

        prompt_text = prompt_path.read_text(encoding="utf-8")
        for phrase in PROJECT_EXECUTOR_MATERIAL_DECISION_REQUIRED_PHRASES:
            if phrase not in prompt_text:
                self.add_error(
                    PROJECT_EXECUTOR_PROMPT,
                    f"material decision section is missing required phrase: {phrase}",
                )

    def check_diff_risk_output_contract(self) -> None:
        checklist_path = self.root / DIFF_RISK_CHECKLIST
        if not checklist_path.is_file():
            self.add_error(DIFF_RISK_CHECKLIST, "diff-risk checklist is missing")
            return

        checklist_text = checklist_path.read_text(encoding="utf-8").lower()
        for field in DIFF_RISK_OUTPUT_FIELDS:
            if field.lower() not in checklist_text:
                self.add_error(
                    DIFF_RISK_CHECKLIST,
                    f"diff-risk checklist is missing required output field: {field}",
                )
        if DIFF_RISK_OBSOLETE_TABLE_INSTRUCTION in checklist_text:
            self.add_error(
                DIFF_RISK_CHECKLIST,
                "diff-risk checklist must not require copying the completed eleven-row table",
            )

        for rel in (DIFF_RISK_PR_TEMPLATE, DIFF_RISK_MAINTENANCE_TEMPLATE):
            path = self.root / rel
            if not path.is_file():
                self.add_error(rel, "pull request template is missing")
                continue
            text = path.read_text(encoding="utf-8").lower()
            for field in DIFF_RISK_OUTPUT_FIELDS:
                if field.lower() not in text:
                    self.add_error(
                        rel,
                        f"pull request template is missing required diff-risk field: {field}",
                    )
            if DIFF_RISK_OBSOLETE_TABLE_INSTRUCTION in text:
                self.add_error(
                    rel,
                    "pull request template must not require copying the completed eleven-row table",
                )

    def check_idea_index(self) -> None:
        index_path = self.root / ".ai/ideas/README.md"
        if not index_path.is_file():
            return
        text = index_path.read_text(encoding="utf-8")
        if IDEA_INDEX_HEADER not in text:
            self.add_error(".ai/ideas/README.md", "idea index table header is missing")

        indexed_ids = set(re.findall(r"^\|\s*([A-Za-z0-9-]+)\s*\|", text, re.M))
        indexed_ids.discard("ID")

        for subdir in ("active", "expanded", "implemented", "archived"):
            folder = self.root / ".ai/ideas" / subdir
            if not folder.is_dir():
                continue
            for idea_file in sorted(folder.glob("*.md")):
                if idea_file.name == "README.md":
                    continue
                idea_id = idea_file.stem
                if idea_id.startswith("_"):
                    continue
                if self.mode == "template" and idea_id in {"example", "sample"}:
                    continue
                if idea_id not in indexed_ids:
                    self.add_error(
                        ".ai/ideas/README.md",
                        f"idea file {idea_file.relative_to(self.root).as_posix()} "
                        "is not listed in the index table",
                    )

    def check_bootstrap_markers(self) -> None:
        marker_files: list[tuple[str, int]] = []
        for path in self.iter_markdown_files():
            rel = path.relative_to(self.root).as_posix()
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if BOOTSTRAP_MARKER in line:
                    marker_files.append((rel, line_no))

        if self.mode == "template":
            allowed = {
                ".ai/project/vision.md",
                ".ai/project/product-context.md",
                ".ai/project/scope.md",
                ".ai/project/roadmap.md",
                "README.md",
                ".ai/onboarding/bootstrap-checklist.md",
                ".ai/onboarding/template-customization-guide.md",
                ".ai/contracts/project-definition-contract.md",
            }
            for rel, line_no in marker_files:
                if self.is_excluded_path(rel):
                    continue
                if rel not in allowed:
                    self.add_error(
                        rel,
                        f"unexpected bootstrap marker outside allowed template files ({BOOTSTRAP_MARKER})",
                        line_no,
                    )
            return

        for rel in PRODUCT_MARKER_PATHS:
            path = self.root / rel
            if not path.is_file():
                continue
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if BOOTSTRAP_MARKER in line:
                    self.add_error(
                        rel,
                        f"product-owned file still contains bootstrap marker ({BOOTSTRAP_MARKER})",
                        line_no,
                    )

    def parse_markdown_table(self, text: str, header_prefix: str) -> list[dict[str, str]]:
        return parse_markdown_table(text, header_prefix)

    def check_project_identity(self) -> None:
        readme = self.root / "README.md"
        if readme.is_file():
            text = readme.read_text(encoding="utf-8")
            for signature in TEMPLATE_README_SIGNATURES:
                if signature in text:
                    self.add_error(
                        "README.md",
                        f"root README still contains template identity marker: {signature}",
                    )

        agents = self.root / "AGENTS.md"
        if agents.is_file():
            text = agents.read_text(encoding="utf-8")
            for signature in TEMPLATE_AGENTS_SIGNATURES:
                if signature in text:
                    self.add_error(
                        "AGENTS.md",
                        f"AGENTS.md still contains template-only identity marker: {signature}",
                    )

    def check_ci_validation_mode(self) -> None:
        workflow = self.root / CI_VALIDATION_WORKFLOW
        if not workflow.is_file():
            self.add_error(
                CI_VALIDATION_WORKFLOW,
                "CI workflow for contract validation is missing",
            )
            return

        text = workflow.read_text(encoding="utf-8")
        if CI_VALIDATE_TEMPLATE_COMMAND in text:
            self.add_error(
                CI_VALIDATION_WORKFLOW,
                "CI workflow still runs validate-workflow-contracts.py with --mode template; "
                "switch to --mode project after bootstrap",
            )
            return
        if CI_VALIDATE_PROJECT_COMMAND not in text:
            self.add_error(
                CI_VALIDATION_WORKFLOW,
                "CI workflow must run validate-workflow-contracts.py with --mode project after bootstrap",
            )

    def check_project_mode(self) -> None:
        self.check_ci_validation_mode()

        requirements_path = self.root / ".ai/docs/project-requirements.md"
        if not requirements_path.is_file():
            self.add_error(".ai/docs/project-requirements.md", "project requirements file is missing")
            return

        try:
            canonical_areas = load_decision_areas(self.root)
            canonical_checks = load_readiness_checks(self.root)
        except ValueError as exc:
            self.add_error(".ai/contracts/project-definition-contract.md", str(exc))
            return

        text = requirements_path.read_text(encoding="utf-8")
        decision_rows = self.parse_markdown_table(text, "| Area | Status |")
        if not decision_rows:
            self.add_error(
                ".ai/docs/project-requirements.md",
                "project decision status table is missing or empty",
            )
        else:
            seen: dict[str, int] = {}
            present_areas: set[str] = set()
            for row in decision_rows:
                area = row.get("Area", "").strip()
                status = row.get("Status", "").strip().strip("`")
                notes = row.get("Value / notes", "").strip()
                location = row.get("Link / location / return trigger", "").strip()
                if not area:
                    continue
                present_areas.add(area)
                seen[area] = seen.get(area, 0) + 1
                if seen[area] > 1:
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"decision area '{area}' appears more than once",
                    )
                    continue
                if area not in canonical_areas:
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"unknown decision area '{area}'",
                    )
                    continue
                if not status:
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"decision area '{area}' has an empty status",
                    )
                    continue
                if status not in VALID_DECISION_STATUSES:
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"decision area '{area}' has invalid status '{status}'",
                    )
                    continue
                if status == "blocking-question":
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"decision area '{area}' is still blocking-question",
                    )
                ok, reason = status_metadata_valid(status, notes, location)
                if not ok:
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"decision area '{area}': {reason}",
                    )

            for area in canonical_areas:
                if area not in present_areas:
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"missing decision area '{area}'",
                    )

        stack_rows = self.parse_markdown_table(text, "| Active profile |")
        if not stack_rows:
            self.add_error(
                ".ai/docs/project-requirements.md",
                "active stack profile table is missing or empty",
            )
        else:
            valid_stack = False
            for row in stack_rows:
                profile = row.get("Active profile", "").strip()
                notes = row.get("Notes", "").strip()
                if not profile or profile in {"—", "-"}:
                    continue
                if profile.lower() == "not-applicable":
                    if notes:
                        valid_stack = True
                    else:
                        self.add_error(
                            ".ai/docs/project-requirements.md",
                            "stack marked not-applicable must include a reason in Notes",
                        )
                    continue
                if has_placeholder_stack_value(profile):
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"stack profile placeholder is not allowed: {profile}",
                    )
                    continue
                profile_path = self.root / profile
                if not profile_path.is_file():
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"active stack profile path does not exist: {profile}",
                    )
                else:
                    profile_text = profile_path.read_text(encoding="utf-8")
                    if stack_profile_has_placeholder_content(profile_text):
                        self.add_error(
                            ".ai/docs/project-requirements.md",
                            "active stack profile still contains placeholder commands or "
                            f"replace instructions: {profile}",
                        )
                    else:
                        valid_stack = True
            if not valid_stack:
                self.add_error(
                    ".ai/docs/project-requirements.md",
                    "active stack profile must be a real profile path or explicit not-applicable with reason",
                )

        readiness_rows = self.parse_markdown_table(text, "| Check | Result |")
        if not readiness_rows:
            self.add_error(
                ".ai/docs/project-requirements.md",
                "project readiness table is missing or empty",
            )
        else:
            readiness_map = {row.get("Check", "").strip(): row for row in readiness_rows}
            for check in canonical_checks:
                row = readiness_map.get(check)
                if row is None:
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"missing project readiness row: {check}",
                    )
                    continue
                result = row.get("Result", "").strip()
                notes = row.get("Notes", "").strip()
                if not is_pass_result(result):
                    self.add_error(
                        ".ai/docs/project-requirements.md",
                        f"project readiness row not passing: {check}",
                    )
                if check == "Real project commands recorded":
                    if not notes or is_pass_result(notes) or len(notes) < 8:
                        self.add_error(
                            ".ai/docs/project-requirements.md",
                            "real project commands require evidence location in Notes, not a bare pass result",
                        )
                        continue
                    evidence_paths = extract_command_evidence_paths(notes)
                    if not evidence_paths:
                        self.add_error(
                            ".ai/docs/project-requirements.md",
                            "real project commands require a repository file path in Notes",
                        )
                        continue
                    valid_evidence = False
                    for rel in evidence_paths:
                        ok, reason = validate_command_evidence_path(self.root, rel)
                        if not ok:
                            self.add_error(
                                ".ai/docs/project-requirements.md",
                                reason,
                            )
                            continue
                        evidence_path = (self.root.resolve() / rel).resolve()
                        if not evidence_path.is_file():
                            self.add_error(
                                ".ai/docs/project-requirements.md",
                                f"command evidence file does not exist: {rel}",
                            )
                            continue
                        if not file_has_concrete_commands(
                            evidence_path.read_text(encoding="utf-8")
                        ):
                            self.add_error(
                                ".ai/docs/project-requirements.md",
                                f"command evidence file lacks concrete project commands: {rel}",
                            )
                            continue
                        valid_evidence = True
                    if not valid_evidence:
                        self.add_error(
                            ".ai/docs/project-requirements.md",
                            "real project commands require at least one evidence file with concrete commands",
                        )

        self.check_project_identity()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("template", "project"),
        default="template",
        help="validation mode (default: template)",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="repository root to validate (default: current directory)",
    )
    args = parser.parse_args()

    validator = Validator(Path(args.root), args.mode)
    exit_code = validator.run()

    if validator.errors:
        for error in validator.errors:
            print(error.format(), file=sys.stderr)
        print(f"validation failed with {len(validator.errors)} error(s)", file=sys.stderr)
    else:
        print(f"validation passed ({args.mode} mode)")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
