"""Tests for diff parser."""

from __future__ import annotations

from numbat.diff_parser import parse_numstat


def test_parse_numstat_text_files() -> None:
    numstat = "10\t5\tsrc/foo.py\n3\t0\tREADME.md\n"
    summary = parse_numstat(numstat)

    assert summary.file_count == 2
    assert summary.total_additions == 13
    assert summary.total_deletions == 5
    assert summary.total_lines_changed == 18

    first, second = summary.files
    assert first.path == "src/foo.py"
    assert first.additions == 10
    assert first.deletions == 5
    assert first.binary is False

    assert second.path == "README.md"
    assert second.additions == 3
    assert second.deletions == 0


def test_parse_numstat_binary_file() -> None:
    numstat = "-\t-\tassets/logo.png\n"
    summary = parse_numstat(numstat)

    assert summary.file_count == 1
    assert summary.total_additions == 0
    assert summary.total_deletions == 0

    file_change = summary.files[0]
    assert file_change.path == "assets/logo.png"
    assert file_change.binary is True


def test_parse_numstat_empty() -> None:
    summary = parse_numstat("")
    assert summary.file_count == 0
    assert summary.total_lines_changed == 0
