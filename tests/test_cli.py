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
