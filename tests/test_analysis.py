"""Tests for deterministic analysis helpers."""

from __future__ import annotations

from pathlib import Path

from numbat.analysis import (
    LARGE_DIFF_FILE_THRESHOLD,
    LARGE_DIFF_LINE_THRESHOLD,
    analyze_diff,
    categorize_path,
)
from numbat.diff_parser import DiffSummary, FileChange


def test_categorize_path_assigns_expected_buckets() -> None:
    assert categorize_path("src/numbat/review.py") == "source"
    assert categorize_path("tests/test_review.py") == "tests"
    assert categorize_path("test_helpers.py") == "tests"
    assert categorize_path("pyproject.toml") == "config"
    assert categorize_path("requirements.txt") == "config"
    assert categorize_path(".env.local") == "config"
    assert categorize_path("README.md") == "docs"
    assert categorize_path("docs/guide.md") == "docs"
    assert categorize_path("ci/validate-workflow-contracts.py") == "ci"
    assert categorize_path("assets/logo.png") == "other"


def test_analyze_diff_emits_focus_risk_hints() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_cli.py", additions=10, deletions=2, binary=False),
            FileChange(path="pyproject.toml", additions=3, deletions=1, binary=False),
            FileChange(path="src/numbat/auth.py", additions=5, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert result.categories == ("tests", "config", "source")
    codes = [hint.code for hint in result.hints]
    assert codes == [
        "tests_touched",
        "config_or_deps",
        "security_sensitive_paths",
    ]
    assert "src/numbat/auth.py" in result.hints[2].message


def test_analyze_diff_large_diff_hint_by_line_count() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="src/big.py",
                additions=LARGE_DIFF_LINE_THRESHOLD,
                deletions=0,
                binary=False,
            ),
        )
    )

    result = analyze_diff(summary)

    assert any(hint.code == "large_diff" for hint in result.hints)


def test_analyze_diff_large_diff_hint_by_file_count() -> None:
    files = tuple(
        FileChange(path=f"src/f{index}.py", additions=1, deletions=0, binary=False)
        for index in range(LARGE_DIFF_FILE_THRESHOLD)
    )

    result = analyze_diff(DiffSummary(files=files))

    assert any(hint.code == "large_diff" for hint in result.hints)


def test_analyze_diff_ci_workflow_paths_hint() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=2,
                deletions=1,
                binary=False,
            ),
            FileChange(
                path=".github/workflows/validate-workflow-contracts.yml",
                additions=1,
                deletions=0,
                binary=False,
            ),
        )
    )

    result = analyze_diff(summary)

    ci_hints = [hint for hint in result.hints if hint.code == "ci_workflow_paths"]
    assert len(ci_hints) == 1
    assert "ci/validate-workflow-contracts.py" in ci_hints[0].message
    assert (
        "python ci/validate-workflow-contracts.py --mode project"
        in ci_hints[0].message
    )


def test_analyze_diff_no_ci_workflow_hint_for_source_only() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/review.py", additions=5, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "ci_workflow_paths" for hint in result.hints)


def test_analyze_diff_rename_or_move_hint() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="old.py => new.py",
                additions=0,
                deletions=0,
                binary=False,
                change_type="R",
            ),
            FileChange(
                path="src/numbat/review.py",
                additions=2,
                deletions=0,
                binary=False,
                change_type="M",
            ),
        )
    )

    result = analyze_diff(summary)

    rename_hints = [hint for hint in result.hints if hint.code == "rename_or_move"]
    assert len(rename_hints) == 1
    assert "old.py => new.py" in rename_hints[0].message


def test_analyze_diff_no_rename_or_move_hint_for_modify_only() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/foo.py", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "rename_or_move" for hint in result.hints)


def test_analyze_diff_source_without_tests_hint() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/review.py", additions=5, deletions=0, binary=False),
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    hints = [hint for hint in result.hints if hint.code == "source_without_tests"]
    assert len(hints) == 1
    assert "src/numbat/review.py" in hints[0].message


def test_analyze_diff_no_source_without_tests_when_tests_in_diff() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/review.py", additions=5, deletions=0, binary=False),
            FileChange(path="tests/test_review.py", additions=3, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "source_without_tests" for hint in result.hints)


def test_analyze_diff_tests_only_hint() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_cli.py", additions=10, deletions=2, binary=False),
            FileChange(path="tests/test_review.py", additions=3, deletions=1, binary=False),
        )
    )

    result = analyze_diff(summary)

    hints = [hint for hint in result.hints if hint.code == "tests_only"]
    assert len(hints) == 1
    assert "tests/test_cli.py" in hints[0].message


def test_analyze_diff_no_tests_only_for_docs_only_diff() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="README.md", additions=3, deletions=1, binary=False),
            FileChange(path="docs/guide.md", additions=5, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "tests_only" for hint in result.hints)


def test_analyze_diff_no_tests_only_when_source_present() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/review.py", additions=2, deletions=0, binary=False),
            FileChange(path="tests/test_review.py", additions=3, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "tests_only" for hint in result.hints)


def test_analyze_diff_ci_without_tests_hint() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=2,
                deletions=1,
                binary=False,
            ),
        )
    )

    result = analyze_diff(summary)

    hints = [hint for hint in result.hints if hint.code == "ci_without_tests"]
    assert len(hints) == 1
    assert "ci/validate-workflow-contracts.py" in hints[0].message


def test_analyze_diff_no_ci_without_tests_when_tests_in_diff() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=2,
                deletions=1,
                binary=False,
            ),
            FileChange(path="tests/test_ci.py", additions=5, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "ci_without_tests" for hint in result.hints)


def test_analyze_diff_workflow_without_ci_validator_hint() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path=".github/workflows/validate-workflow-contracts.yml",
                additions=1,
                deletions=0,
                binary=False,
            ),
        )
    )

    result = analyze_diff(summary)

    hints = [
        hint for hint in result.hints if hint.code == "workflow_without_ci_validator"
    ]
    assert len(hints) == 1
    assert ".github/workflows/validate-workflow-contracts.yml" in hints[0].message


def test_analyze_diff_no_workflow_without_ci_validator_when_ci_changed() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path=".github/workflows/validate-workflow-contracts.yml",
                additions=1,
                deletions=0,
                binary=False,
            ),
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=2,
                deletions=1,
                binary=False,
            ),
        )
    )

    result = analyze_diff(summary)

    assert not any(
        hint.code == "workflow_without_ci_validator" for hint in result.hints
    )
    assert any(hint.code == "ci_workflow_paths" for hint in result.hints)


def test_analyze_diff_docs_touched_hint_for_docs_only() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="README.md", additions=3, deletions=1, binary=False),
            FileChange(path="docs/guide.md", additions=10, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    docs_hints = [hint for hint in result.hints if hint.code == "docs_touched"]
    assert len(docs_hints) == 1
    assert docs_hints[0].message == (
        "Documentation changed — confirm product/code docs stay aligned"
    )


def test_analyze_diff_no_docs_touched_when_mixed_with_source() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="docs/guide.md", additions=5, deletions=0, binary=False),
            FileChange(path="src/numbat/review.py", additions=2, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "docs_touched" for hint in result.hints)


def test_analyze_diff_missing_test_file_hint_when_test_absent(tmp_path: Path) -> None:
    (tmp_path / "src" / "numbat").mkdir(parents=True)
    (tmp_path / "src" / "numbat" / "foo.py").write_text("x = 1\n")

    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/foo.py", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary, cwd=str(tmp_path))

    assert any(hint.code == "missing_test_file" for hint in result.hints)
    hint = next(hint for hint in result.hints if hint.code == "missing_test_file")
    assert "tests/test_foo.py" in hint.message


def test_analyze_diff_no_missing_test_file_when_test_exists(tmp_path: Path) -> None:
    (tmp_path / "src" / "numbat").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "numbat" / "foo.py").write_text("x = 1\n")
    (tmp_path / "tests" / "test_foo.py").write_text("def test_foo() -> None: pass\n")

    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/foo.py", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary, cwd=str(tmp_path))

    assert not any(hint.code == "missing_test_file" for hint in result.hints)


def test_analyze_diff_no_missing_test_file_without_cwd() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/numbat/foo.py", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "missing_test_file" for hint in result.hints)


def test_analyze_diff_no_missing_test_file_for_test_only_change(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("def test_foo() -> None: pass\n")

    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_foo.py", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary, cwd=str(tmp_path))

    assert not any(hint.code == "missing_test_file" for hint in result.hints)


def test_analyze_diff_lockfile_without_manifest_hint() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="poetry.lock", additions=10, deletions=5, binary=False),
        )
    )

    result = analyze_diff(summary)

    hints = [hint for hint in result.hints if hint.code == "lockfile_without_manifest"]
    assert len(hints) == 1
    assert "poetry.lock" in hints[0].message


def test_analyze_diff_no_lockfile_without_manifest_when_manifest_changed() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="poetry.lock", additions=10, deletions=5, binary=False),
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "lockfile_without_manifest" for hint in result.hints)


def test_analyze_diff_manifest_without_lockfile_when_lockfile_on_disk(
    tmp_path: Path,
) -> None:
    (tmp_path / "poetry.lock").write_text("lock\n")

    summary = DiffSummary(
        files=(
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary, cwd=str(tmp_path))

    hints = [hint for hint in result.hints if hint.code == "manifest_without_lockfile"]
    assert len(hints) == 1
    assert "pyproject.toml" in hints[0].message
    assert "poetry.lock" in hints[0].message


def test_analyze_diff_no_manifest_without_lockfile_when_no_lockfile_on_disk(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n")

    summary = DiffSummary(
        files=(
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary, cwd=str(tmp_path))

    assert not any(hint.code == "manifest_without_lockfile" for hint in result.hints)


def test_analyze_diff_no_manifest_without_lockfile_when_lockfile_changed(
    tmp_path: Path,
) -> None:
    (tmp_path / "poetry.lock").write_text("lock\n")

    summary = DiffSummary(
        files=(
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
            FileChange(path="poetry.lock", additions=2, deletions=1, binary=False),
        )
    )

    result = analyze_diff(summary, cwd=str(tmp_path))

    assert not any(hint.code == "manifest_without_lockfile" for hint in result.hints)
    assert not any(hint.code == "lockfile_without_manifest" for hint in result.hints)


def test_analyze_diff_no_manifest_without_lockfile_without_cwd() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    result = analyze_diff(summary)

    assert not any(hint.code == "manifest_without_lockfile" for hint in result.hints)
