"""Tests for diff content-derived Focus/Risk hints."""

from __future__ import annotations

import re
from pathlib import Path

from diffrat.analysis import analyze_diff
from diffrat.config import ContentRule, DiffratConfig, load_config
from diffrat.content_hints import LONG_ADDED_HUNK_THRESHOLD, content_focus_risk_hints
from diffrat.diff_parser import (
    DiffContent,
    DiffHunk,
    DiffSummary,
    FileChange,
    FileDiffContent,
)

_FILTER_GOOD = (
    'PROJECT_EXECUTOR_COMMENT_FILTER = "^/(execute-project|continue-project)$"'
)
_FILTER_TYPO = (
    'PROJECT_EXECUTOR_COMMENT_FILTER = "^/(execute-project|continue-projec)$"'
)

_DOGFOOD_CONFIG = load_config(Path(__file__).resolve().parents[1])


def _dogfood_regex_typo_config() -> DiffratConfig:
    rules = tuple(
        rule
        for rule in _DOGFOOD_CONFIG.content_rules
        if rule.code == "regex_typo"
    )
    return DiffratConfig(checks={}, content_rules=rules)


def _single_file_content(path: str, added_line: str) -> DiffContent:
    return DiffContent(
        files=(
            FileDiffContent(
                path=path,
                hunks=(
                    DiffHunk(
                        header="@@ -1 +1 @@",
                        lines=(f"+{added_line}",),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )


def _validator_typo_content() -> DiffContent:
    return DiffContent(
        files=(
            FileDiffContent(
                path="ci/validate-workflow-contracts.py",
                hunks=(
                    DiffHunk(
                        header="@@ -360,7 +360,7 @@",
                        lines=(f"-{_FILTER_GOOD}", f"+{_FILTER_TYPO}"),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )


def test_content_hints_regex_typo_for_continue_projec() -> None:
    hints = content_focus_risk_hints(
        _validator_typo_content(),
        config=_DOGFOOD_CONFIG,
    )

    assert len(hints) == 1
    assert hints[0].code == "regex_typo"
    assert "continue-project" in hints[0].message
    assert "continue-projec" in hints[0].message
    assert "ci/validate-workflow-contracts.py" in hints[0].message
    assert hints[0].path == "ci/validate-workflow-contracts.py"
    assert hints[0].line == 360


def test_content_hints_path_only_when_hunk_header_unparseable() -> None:
    content = DiffContent(
        files=(
            FileDiffContent(
                path="src/a.py",
                hunks=(
                    DiffHunk(
                        header="invalid header",
                        lines=("+print('debug')",),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    hints = content_focus_risk_hints(content)

    assert len(hints) == 1
    assert hints[0].code == "debug_leftover"
    assert hints[0].path == "src/a.py"
    assert hints[0].line is None


def test_content_hints_line_advances_across_context_lines() -> None:
    content = DiffContent(
        files=(
            FileDiffContent(
                path="src/a.py",
                hunks=(
                    DiffHunk(
                        header="@@ -1,3 +1,4 @@",
                        lines=(
                            " context",
                            "+print('debug')",
                        ),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    hints = content_focus_risk_hints(content)

    assert len(hints) == 1
    assert hints[0].path == "src/a.py"
    assert hints[0].line == 2


def test_content_hints_ignore_correct_constant() -> None:
    content = DiffContent(
        files=(
            FileDiffContent(
                path="ci/validate-workflow-contracts.py",
                hunks=(
                    DiffHunk(
                        header="@@ -1 +1 @@",
                        lines=(f"+{_FILTER_GOOD}",),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    assert content_focus_risk_hints(content, config=_DOGFOOD_CONFIG) == []
    content = _single_file_content("tests/test_foo.py", 'api_key = "sk-abcdefghijklmnopqrstuvwxyz"')

    assert content_focus_risk_hints(content) == []


def test_content_hints_skip_docs_paths() -> None:
    content = _single_file_content("docs/guide.md", "http://example.com")

    assert content_focus_risk_hints(content) == []


def test_content_hints_possible_secret_positive() -> None:
    content = _single_file_content(
        "src/diffrat/auth.py",
        'api_key = "sk-abcdefghijklmnopqrstuvwxyz"',
    )

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "possible_secret"
    assert "src/diffrat/auth.py" in hints[0].message


def test_content_hints_possible_secret_private_key() -> None:
    content = _single_file_content(
        "src/diffrat/crypto.py",
        "-----BEGIN PRIVATE KEY-----",
    )

    hints = content_focus_risk_hints(content)
    assert any(hint.code == "possible_secret" for hint in hints)


def test_content_hints_possible_secret_negative() -> None:
    content = _single_file_content("src/diffrat/auth.py", 'name = "short"')

    assert content_focus_risk_hints(content) == []


def test_content_hints_debug_leftover_positive() -> None:
    content = _single_file_content("src/diffrat/review.py", "print(result)")

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "debug_leftover"


def test_content_hints_debug_leftover_todo_remove_case_insensitive() -> None:
    content = _single_file_content("src/diffrat/review.py", "# todo: remove before merge")

    hints = content_focus_risk_hints(content)
    assert any(hint.code == "debug_leftover" for hint in hints)


def test_content_hints_debug_leftover_negative() -> None:
    content = _single_file_content("src/diffrat/review.py", "logger.info('done')")

    assert content_focus_risk_hints(content) == []


def test_content_hints_debug_leftover_ruby_binding_pry() -> None:
    content = _single_file_content("app/models/user.rb", "binding.pry")

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "debug_leftover"
    assert hints[0].path == "app/models/user.rb"
    assert hints[0].line == 1


def test_content_hints_debug_leftover_ruby_byebug() -> None:
    content = _single_file_content("lib/worker.rb", "byebug")

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "debug_leftover"
    assert hints[0].path == "lib/worker.rb"


def test_content_hints_debug_leftover_ruby_puts_call_like() -> None:
    content = _single_file_content("app/services/report.rb", 'puts("debug")')

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "debug_leftover"


def test_content_hints_debug_leftover_ruby_puts_not_substring() -> None:
    content = _single_file_content("app/services/report.rb", "outputs = compute()")

    assert content_focus_risk_hints(content) == []


def test_content_hints_dangerous_call_positive() -> None:
    content = _single_file_content("src/diffrat/shell.py", "subprocess.run(cmd, shell=True)")

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "dangerous_call"


def test_content_hints_dangerous_call_eval() -> None:
    content = _single_file_content("src/diffrat/shell.py", "result = eval(user_input)")

    hints = content_focus_risk_hints(content)
    assert any(hint.code == "dangerous_call" for hint in hints)


def test_content_hints_dangerous_call_negative() -> None:
    content = _single_file_content("src/diffrat/shell.py", "subprocess.run(cmd, check=True)")

    assert content_focus_risk_hints(content) == []


def test_content_hints_broad_exception_positive() -> None:
    content = _single_file_content("src/diffrat/review.py", "    except Exception:")

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "broad_exception"


def test_content_hints_broad_exception_bare_except() -> None:
    content = _single_file_content("src/diffrat/review.py", "    except:")

    hints = content_focus_risk_hints(content)
    assert any(hint.code == "broad_exception" for hint in hints)


def test_content_hints_broad_exception_negative_with_raise() -> None:
    content = _single_file_content(
        "src/diffrat/review.py",
        "    except Exception: raise",
    )

    assert content_focus_risk_hints(content) == []


def test_content_hints_hardcoded_url_positive() -> None:
    content = _single_file_content(
        "src/diffrat/client.py",
        'endpoint = "https://api.example.com/v1"',
    )

    hints = content_focus_risk_hints(content)
    assert any(hint.code == "hardcoded_url_or_ip" for hint in hints)


def test_content_hints_hardcoded_ip_positive() -> None:
    content = _single_file_content("src/diffrat/client.py", 'host = "192.168.1.100"')

    hints = content_focus_risk_hints(content)
    assert any(hint.code == "hardcoded_url_or_ip" for hint in hints)


def test_content_hints_hardcoded_url_negative() -> None:
    content = _single_file_content("src/diffrat/client.py", 'version = "1.0.0"')

    assert content_focus_risk_hints(content) == []


def test_content_hints_one_hint_per_code_per_line() -> None:
    content = _single_file_content(
        "src/diffrat/debug.py",
        "print(eval('x'))",
    )

    hints = content_focus_risk_hints(content)
    codes = [hint.code for hint in hints]
    assert codes.count("debug_leftover") == 1
    assert codes.count("dangerous_call") == 1


def test_content_hints_applies_to_ci_paths() -> None:
    content = _single_file_content("ci/deploy.sh", "curl http://internal.local")

    hints = content_focus_risk_hints(content)
    assert any(hint.code == "hardcoded_url_or_ip" for hint in hints)


def test_analyze_diff_merges_content_hints() -> None:
    summary = DiffSummary(
        files=(
            FileChange(
                path="ci/validate-workflow-contracts.py",
                additions=1,
                deletions=1,
                binary=False,
            ),
        )
    )

    result = analyze_diff(
        summary,
        diff_content=_validator_typo_content(),
        config=_DOGFOOD_CONFIG,
    )

    codes = [hint.code for hint in result.hints]
    assert "ci_workflow_paths" in codes
    assert "regex_typo" in codes


def test_content_hints_config_rule_hit() -> None:
    config = DiffratConfig(
        checks={},
        content_rules=(
            ContentRule(
                code="regex_typo",
                pattern=re.compile(r"foo(?!bar)"),
                expected="foobar",
                paths=("src/",),
            ),
        ),
    )
    content = _single_file_content("src/diffrat/review.py", "value = foo")

    hints = content_focus_risk_hints(content, config=config)

    assert len(hints) == 1
    assert hints[0].code == "regex_typo"
    assert "foobar" in hints[0].message


def test_content_hints_config_rule_miss_when_expected_present() -> None:
    config = DiffratConfig(
        checks={},
        content_rules=(
            ContentRule(
                code="regex_typo",
                pattern=re.compile(r"foo(?!bar)"),
                expected="foobar",
                paths=(),
            ),
        ),
    )
    content = _single_file_content("src/diffrat/review.py", "value = foobar")

    assert content_focus_risk_hints(content, config=config) == []


def test_content_hints_config_rule_path_scoping() -> None:
    config = DiffratConfig(
        checks={},
        content_rules=(
            ContentRule(
                code="regex_typo",
                pattern=re.compile(r"foo(?!bar)"),
                expected="foobar",
                paths=("ci/",),
            ),
        ),
    )
    content = _single_file_content("src/diffrat/review.py", "value = foo")

    assert content_focus_risk_hints(content, config=config) == []


def test_content_hints_without_config_skips_dogfood_rules() -> None:
    assert content_focus_risk_hints(_validator_typo_content()) == []


def test_content_hints_dogfood_rules_match_repo_pyproject() -> None:
    config = _dogfood_regex_typo_config()

    assert len(config.content_rules) == 2
    hints = content_focus_risk_hints(_validator_typo_content(), config=_DOGFOOD_CONFIG)
    assert any(hint.code == "regex_typo" for hint in hints)


def test_content_hints_long_added_hunk() -> None:
    lines = tuple(f"+added line {index}" for index in range(LONG_ADDED_HUNK_THRESHOLD))
    content = DiffContent(
        files=(
            FileDiffContent(
                path="src/diffrat/review.py",
                hunks=(
                    DiffHunk(
                        header="@@ -1 +1,40 @@",
                        lines=lines,
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "long_added_hunk"
    assert hints[0].path == "src/diffrat/review.py"
    assert hints[0].line == 1


def test_content_hints_no_long_added_hunk_below_threshold() -> None:
    lines = tuple(f"+line {index}" for index in range(LONG_ADDED_HUNK_THRESHOLD - 1))
    content = DiffContent(
        files=(
            FileDiffContent(
                path="src/diffrat/review.py",
                hunks=(
                    DiffHunk(
                        header="@@ -1 +1,39 @@",
                        lines=lines,
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    assert content_focus_risk_hints(content) == []


def test_content_hints_cli_flag_without_help() -> None:
    content = DiffContent(
        files=(
            FileDiffContent(
                path="src/diffrat/__main__.py",
                hunks=(
                    DiffHunk(
                        header="@@ -10 +10,2 @@",
                        lines=(
                            '+    review_parser.add_argument("--verbose", action="store_true")',
                        ),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "cli_flag_without_help"
    assert hints[0].path == "src/diffrat/__main__.py"
    assert hints[0].line == 10


def test_content_hints_cli_flag_with_help_not_flagged() -> None:
    content = DiffContent(
        files=(
            FileDiffContent(
                path="src/diffrat/__main__.py",
                hunks=(
                    DiffHunk(
                        header="@@ -10 +10,2 @@",
                        lines=(
                            '+    review_parser.add_argument("--verbose", help="Verbose output")',
                        ),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    assert content_focus_risk_hints(content) == []


def test_content_hints_cli_flag_multiline_without_help() -> None:
    content = DiffContent(
        files=(
            FileDiffContent(
                path="src/diffrat/__main__.py",
                hunks=(
                    DiffHunk(
                        header="@@ -10 +10,3 @@",
                        lines=(
                            '+    review_parser.add_argument(',
                            '+        "--verbose",',
                            '+        action="store_true",',
                            '+    )',
                        ),
                    ),
                ),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    hints = content_focus_risk_hints(content)
    assert len(hints) == 1
    assert hints[0].code == "cli_flag_without_help"
