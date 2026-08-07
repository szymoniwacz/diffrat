"""Tests for review command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from diffrat.json_renderer import JSON_SCHEMA_VERSION
from diffrat.review import (
    EXIT_CHECK_FAILED,
    EXIT_EMPTY_DIFF,
    EXIT_ERROR,
    EXIT_FAIL_ON_MATCH,
    EXIT_SUCCESS,
    matched_fail_on_codes,
    parse_fail_on_codes,
    run_review,
)


def test_run_review_unstaged(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, cwd=str(git_repo_with_changes))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Review Report" in captured.out
    assert "README.md" in captured.out
    assert "Changes" in captured.out
    assert "+extra line" in captured.out
    assert captured.err == ""


def test_run_review_staged(
    git_repo_with_staged_change: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, cwd=str(git_repo_with_staged_change))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "staged.txt  [other]  risk=" in captured.out
    assert "Focus / Risk" in captured.out


def test_run_review_empty_diff(git_repo_clean: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_review(staged=False, cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no unstaged changes to review" in captured.err


def test_run_review_not_a_repo(
    outside_git_directory: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, cwd=str(outside_git_directory))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert captured.out == ""
    assert "not a git repository" in captured.err


def test_run_review_base_main(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="main", cwd=str(git_repo_with_feature_branch))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Git context" in captured.out
    assert "Branch: feature" in captured.out
    assert "Base: main" in captured.out
    assert "Commits since base: 2" in captured.out
    assert "add feature file" in captured.out
    assert "feature.txt" in captured.out
    assert captured.err == ""


def test_run_review_base_invalid_ref(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="not-a-real-ref", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert captured.out == ""
    assert "Needed a single revision" in captured.err


def test_run_review_base_empty_diff(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no changes on branch since main" in captured.err


def test_run_review_staged_and_base_conflict(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, base="main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "cannot use --staged with --base" in captured.err


def test_run_review_range_main_feature(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(range_spec="main..feature", cwd=str(git_repo_with_feature_branch))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Range: main..feature" in captured.out
    assert "From: main" in captured.out
    assert "To: feature" in captured.out
    assert "Commits in range: 2" in captured.out
    assert "feature.txt" in captured.out
    assert captured.err == ""


def test_run_review_range_invalid_spec(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(range_spec="not-a-range", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "expected REV format A..B" in captured.err


def test_run_review_range_invalid_ref(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(range_spec="main..not-a-real-ref", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "Needed a single revision" in captured.err


def test_run_review_range_empty_diff(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(range_spec="main..main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no changes in range main..main" in captured.err


def test_run_review_staged_and_range_conflict(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, range_spec="main..main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "cannot use --staged with --range" in captured.err


def test_run_review_base_and_range_conflict(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="main", range_spec="main..main", cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert "cannot use --base with --range" in captured.err


def test_run_review_json_range(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        range_spec="main..feature",
        json_output=True,
        cwd=str(git_repo_with_feature_branch),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["mode"] == "range"
    assert payload["git_context"]["range"] == "main..feature"
    assert payload["git_context"]["from_ref"] == "main"
    assert payload["git_context"]["to_ref"] == "feature"
    assert payload["git_context"]["commit_count"] == 2
    assert payload["git_context"]["commits"][0]["subject"] == "extend feature file"


def test_run_review_json_unstaged(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, json_output=True, cwd=str(git_repo_with_changes))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert captured.err == ""

    payload = json.loads(captured.out)
    assert payload["schema_version"] == JSON_SCHEMA_VERSION
    assert payload["mode"] == "unstaged"
    assert payload["summary"]["file_count"] == 1
    assert payload["files"][0]["path"] == "README.md"
    assert payload["files"][0]["category"] == "docs"
    assert "focus_risk" in payload
    assert "git_context" not in payload


def test_run_review_json_staged(
    git_repo_with_staged_change: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=True, json_output=True, cwd=str(git_repo_with_staged_change))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["mode"] == "staged"
    assert payload["files"] == [
        {
            "path": "staged.txt",
            "additions": 1,
            "deletions": 0,
            "category": "other",
            "risk_score": 50,
        }
    ]
    assert payload["focus_risk"] == []


def test_run_review_json_base(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(base="main", json_output=True, cwd=str(git_repo_with_feature_branch))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["mode"] == "branch"
    assert payload["git_context"]["branch"] == "feature"
    assert payload["git_context"]["base"] == "main"
    assert payload["git_context"]["commit_count"] == 2
    assert payload["git_context"]["commits"][0]["subject"] == "extend feature file"
    assert any(file_entry["path"] == "feature.txt" for file_entry in payload["files"])


def test_run_review_json_empty_diff_no_stdout(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, json_output=True, cwd=str(git_repo_clean))

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""
    assert "no unstaged changes to review" in captured.err


def test_run_review_check_no_applicable_checks(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        run_checks_flag=True,
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Local checks" in captured.out
    assert "(none applicable)" in captured.out
    assert captured.err == ""


def test_run_review_check_reports_failure(
    git_repo_with_staged_change: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from diffrat.checks import CheckResult, CheckSpec

    monkeypatch.setattr(
        "diffrat.review.plan_checks",
        lambda summary, *, config=None: [
            CheckSpec(
                code="ci_validator",
                argv=("python",),
                display_command=(
                    "python ci/validate-workflow-contracts.py --mode project"
                ),
            )
        ],
    )
    monkeypatch.setattr(
        "diffrat.review.run_checks",
        lambda specs, *, cwd=None: [
            CheckResult(
                code="ci_validator",
                command="python ci/validate-workflow-contracts.py --mode project",
                passed=False,
                output="validator failed",
            )
        ],
    )

    exit_code = run_review(staged=True, run_checks_flag=True, cwd=str(git_repo_with_staged_change))

    captured = capsys.readouterr()
    assert exit_code == EXIT_CHECK_FAILED
    assert "[ci_validator] failed" in captured.out
    assert "validator failed" in captured.out
    assert "check failed: ci_validator" in captured.err


def test_run_review_check_json_includes_checks(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from diffrat.checks import CheckResult

    monkeypatch.setattr(
        "diffrat.review.run_checks",
        lambda specs, *, cwd=None: [
            CheckResult(code="pytest", command="pytest", passed=True, output="")
        ],
    )

    exit_code = run_review(
        staged=False,
        json_output=True,
        run_checks_flag=True,
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["checks"] == [
        {
            "code": "pytest",
            "command": "pytest",
            "passed": True,
            "output": "",
        }
    ]


def test_parse_fail_on_codes_splits_comma_separated() -> None:
    codes, error = parse_fail_on_codes("regex_typo,possible_secret")
    assert error is None
    assert codes == ["regex_typo", "possible_secret"]


def test_parse_fail_on_codes_rejects_empty_token() -> None:
    codes, error = parse_fail_on_codes("regex_typo,")
    assert codes is None
    assert error is not None


def test_parse_fail_on_codes_rejects_whitespace_token() -> None:
    codes, error = parse_fail_on_codes("regex typo")
    assert codes is None
    assert error is not None


def test_matched_fail_on_codes_preserves_request_order() -> None:
    matched = matched_fail_on_codes(
        ["possible_secret", "regex_typo", "docs_touched"],
        {"docs_touched", "regex_typo"},
    )
    assert matched == ["regex_typo", "docs_touched"]


def test_run_review_fail_on_match_exits_four(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        fail_on="docs_touched",
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_FAIL_ON_MATCH
    assert "Review Report" in captured.out
    assert captured.err == ""


def test_run_review_fail_on_no_match_exits_zero(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        fail_on="possible_secret",
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert captured.err == ""


def test_run_review_fail_on_invalid_token(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        fail_on="bad token",
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert captured.out == ""
    assert "invalid --fail-on token" in captured.err


def test_run_review_fail_on_empty_diff_before_evaluation(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        fail_on="docs_touched",
        cwd=str(git_repo_clean),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_EMPTY_DIFF
    assert captured.out == ""


def test_run_review_fail_on_json_includes_fail_on_metadata(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        json_output=True,
        fail_on="docs_touched,possible_secret",
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_FAIL_ON_MATCH

    payload = json.loads(captured.out)
    assert payload["fail_on"] == {
        "requested": ["docs_touched", "possible_secret"],
        "matched": ["docs_touched"],
    }


def test_run_review_fail_on_check_failure_precedence(
    git_repo_with_staged_change: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from diffrat.checks import CheckResult, CheckSpec

    monkeypatch.setattr(
        "diffrat.review.plan_checks",
        lambda summary, *, config=None: [
            CheckSpec(
                code="ci_validator",
                argv=("python",),
                display_command=(
                    "python ci/validate-workflow-contracts.py --mode project"
                ),
            )
        ],
    )
    monkeypatch.setattr(
        "diffrat.review.run_checks",
        lambda specs, *, cwd=None: [
            CheckResult(
                code="ci_validator",
                command="python ci/validate-workflow-contracts.py --mode project",
                passed=False,
                output="validator failed",
            )
        ],
    )

    exit_code = run_review(
        staged=True,
        run_checks_flag=True,
        fail_on="large_diff",
        cwd=str(git_repo_with_staged_change),
    )

    assert exit_code == EXIT_CHECK_FAILED


def test_run_review_hunks_for_shows_single_file_changes(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        hunks_for="README.md",
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "README.md" in captured.out
    assert "extra line" in captured.out
    assert captured.out.index("Review order") < captured.out.index("Changes")
    assert captured.out.index("Changes") < captured.out.index("Focus / Risk")


def test_run_review_hunks_for_unknown_path_exits_one(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        hunks_for="missing.py",
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert captured.err.strip() == "path not in diff: missing.py"


def test_run_review_hunks_for_json_single_file_changes(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        json_output=True,
        hunks_for="README.md",
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS

    payload = json.loads(captured.out)
    assert payload["summary"]["file_count"] == 1
    assert payload["review_order"] == ["README.md"]
    assert len(payload["changes"]["files"]) == 1
    assert payload["changes"]["files"][0]["path"] == "README.md"
    assert payload["changes"]["limits"]["max_lines_per_file"] == 500


def test_run_review_default_unchanged_without_hunks_for(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, cwd=str(git_repo_with_changes))
    default_output = capsys.readouterr().out

    assert exit_code == EXIT_SUCCESS
    assert "Review order" in default_output
    assert "Changes" in default_output
    assert "+extra line" in default_output


def test_run_review_brief_omits_changes_keeps_triage_sections(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, brief=True, cwd=str(git_repo_with_changes))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Summary" in captured.out
    assert "Files" in captured.out
    assert "Review order" in captured.out
    assert "Focus / Risk" in captured.out
    assert "Changes" not in captured.out
    assert "+extra line" not in captured.out


def test_run_review_brief_json_empties_changes_files(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        brief=True,
        json_output=True,
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    payload = json.loads(captured.out)
    assert payload["schema_version"] == JSON_SCHEMA_VERSION
    assert payload["summary"]["file_count"] == 1
    assert payload["review_order"]
    assert payload["focus_risk"]
    assert payload["changes"]["files"] == []
    assert payload["changes"]["limits"]["max_files"] == 20


def test_run_review_brief_with_base(
    git_repo_with_feature_branch: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        base="main",
        brief=True,
        cwd=str(git_repo_with_feature_branch),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Git context" in captured.out
    assert "Review order" in captured.out
    assert "Focus / Risk" in captured.out
    assert "Changes" not in captured.out


def test_run_review_brief_with_hunks_for_errors(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(
        staged=False,
        brief=True,
        hunks_for="README.md",
        cwd=str(git_repo_with_changes),
    )

    captured = capsys.readouterr()
    assert exit_code == EXIT_ERROR
    assert captured.out == ""
    assert "cannot use --brief with --hunks-for" in captured.err


def test_run_review_default_still_includes_changes_without_brief(
    git_repo_with_changes: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run_review(staged=False, brief=False, cwd=str(git_repo_with_changes))

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert "Changes" in captured.out
    assert "+extra line" in captured.out
