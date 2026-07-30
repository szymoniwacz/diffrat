"""Tests for repository config loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from numbat.config import ContentRule, NumbatConfig, load_config


def _write_pyproject(repo: Path, body: str) -> None:
    (repo / "pyproject.toml").write_text(body, encoding="utf-8")


def _write_numbat_toml(repo: Path, body: str) -> None:
    (repo / ".numbat.toml").write_text(body, encoding="utf-8")


def test_load_config_empty_when_no_config(git_repo_clean: Path) -> None:
    config = load_config(git_repo_clean)

    assert config == NumbatConfig(checks={}, content_rules={})


def test_load_config_parses_pyproject_checks_and_shorthand_rules(git_repo_clean: Path) -> None:
    _write_pyproject(
        git_repo_clean,
        """\
[tool.numbat.checks]
ci_validator = "python ci/validate.py --mode project"

[tool.numbat.content_rules]
regex_typo = "continue-projec(?!t) → continue-project"
""",
    )

    config = load_config(git_repo_clean)

    assert config.checks == {"ci_validator": "python ci/validate.py --mode project"}
    assert "regex_typo" in config.content_rules
    rule = config.content_rules["regex_typo"]
    assert isinstance(rule, ContentRule)
    assert rule.expected == "continue-project"
    assert rule.pattern.search("continue-projec")


def test_load_config_parses_table_form_content_rule(git_repo_clean: Path) -> None:
    _write_pyproject(
        git_repo_clean,
        """\
[tool.numbat.content_rules.scoped_rule]
paths = ["ci/", "scripts/"]
pattern = "execute-projec(?!t)"
expected = "execute-project"
""",
    )

    config = load_config(git_repo_clean)
    rule = config.content_rules["scoped_rule"]

    assert rule.paths == ("ci/", "scripts/")
    assert rule.expected == "execute-project"
    assert rule.pattern.search("execute-projec")


def test_load_config_parses_array_table_content_rule(git_repo_clean: Path) -> None:
    _write_pyproject(
        git_repo_clean,
        """\
[[tool.numbat.content_rules.array_rule]]
paths = ["docs/"]
pattern = "foo"
expected = "bar"
""",
    )

    config = load_config(git_repo_clean)
    rule = config.content_rules["array_rule"]

    assert rule.paths == ("docs/",)
    assert rule.expected == "bar"


def test_load_config_numbat_toml_overrides_pyproject(git_repo_clean: Path) -> None:
    _write_pyproject(
        git_repo_clean,
        """\
[tool.numbat.checks]
ci_validator = "python old.py"
pytest = "pytest old"

[tool.numbat.content_rules]
shared = "old → new"
""",
    )
    _write_numbat_toml(
        git_repo_clean,
        """\
[numbat.checks]
ci_validator = "python new.py"

[numbat.content_rules]
shared = "pat → exp"
only_numbat = "x → y"
""",
    )

    config = load_config(git_repo_clean)

    assert config.checks == {
        "ci_validator": "python new.py",
        "pytest": "pytest old",
    }
    assert set(config.content_rules) == {"shared", "only_numbat"}
    assert config.content_rules["shared"].expected == "exp"
    assert config.content_rules["only_numbat"].expected == "y"


def test_load_config_skips_invalid_regex_with_warning(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write_pyproject(
        git_repo_clean,
        """\
[tool.numbat.content_rules]
bad = "[unclosed → replacement"
good = "foo → bar"
""",
    )

    config = load_config(git_repo_clean)
    captured = capsys.readouterr()

    assert "bad" not in config.content_rules
    assert "good" in config.content_rules
    assert "invalid regex" in captured.err


def test_load_config_skips_invalid_shorthand(
    git_repo_clean: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write_pyproject(
        git_repo_clean,
        """\
[tool.numbat.content_rules]
broken = "missing arrow separator"
""",
    )

    config = load_config(git_repo_clean)
    captured = capsys.readouterr()

    assert config.content_rules == {}
    assert "shorthand must use" in captured.err


def test_load_config_uses_cwd_when_not_in_git_repo(outside_git_directory: Path) -> None:
    _write_pyproject(
        outside_git_directory,
        """\
[tool.numbat.checks]
ci_validator = "python local.py"
""",
    )

    config = load_config(outside_git_directory)

    assert config.checks == {"ci_validator": "python local.py"}


def test_load_config_uses_git_toplevel_not_subdirectory(git_repo_clean: Path) -> None:
    _write_pyproject(
        git_repo_clean,
        """\
[tool.numbat.checks]
ci_validator = "python root.py"
""",
    )
    subdir = git_repo_clean / "pkg"
    subdir.mkdir()

    config = load_config(subdir)

    assert config.checks == {"ci_validator": "python root.py"}


def test_load_config_ignores_non_string_check_values(git_repo_clean: Path) -> None:
    _write_pyproject(
        git_repo_clean,
        """\
[tool.numbat.checks]
valid = "pytest"
invalid = 42
""",
    )

    config = load_config(git_repo_clean)

    assert config.checks == {"valid": "pytest"}
