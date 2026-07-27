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
    assert "Exit codes: 0 success, 1 git error, 2 empty diff." in captured.out
