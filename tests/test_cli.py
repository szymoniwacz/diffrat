"""CLI smoke tests."""

from __future__ import annotations

import pytest

from numbat.__main__ import build_parser, main


def test_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_version_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_parser_program_name() -> None:
    parser = build_parser()
    assert parser.prog == "numbat"


def test_review_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["review", "--help"])
    assert exc.value.code == 0


def test_review_help_documents_empty_diff_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["review", "--help"])
    assert exc.value.code == 0

    captured = capsys.readouterr()
    assert (
        "Exit codes: 0 success, 1 git/usage error, 2 empty diff, "
        "3 check failure, 4 --fail-on match."
    ) in captured.out
    assert "--base" in captured.out
    assert "--range" in captured.out
    assert "--json" in captured.out
    assert "--check" in captured.out
    assert "--fail-on" in captured.out
    assert "--hunks-for" in captured.out
    assert "schema_version" in captured.out
    assert "20 files" in captured.out
    assert "100 diff lines" in captured.out
