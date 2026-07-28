"""Tests for diff parser."""

from __future__ import annotations

from numbat.diff_parser import parse_numstat, parse_unified_diff

SAMPLE_PATCH = """diff --git a/README.md b/README.md
index 1234567..abcdef0 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 hello
+extra line
 still here
"""


def test_parse_unified_diff_extracts_hunks() -> None:
    content = parse_unified_diff(SAMPLE_PATCH)

    assert len(content.files) == 1
    assert content.truncated_files is False
    file_diff = content.files[0]
    assert file_diff.path == "README.md"
    assert file_diff.binary is False
    assert file_diff.truncated is False
    assert len(file_diff.hunks) == 1
    assert file_diff.hunks[0].header == "@@ -1,3 +1,4 @@"
    assert "+extra line" in file_diff.hunks[0].lines


def test_parse_unified_diff_truncates_files() -> None:
    blocks = []
    for index in range(3):
        blocks.append(
            f"diff --git a/file{index}.txt b/file{index}.txt\n"
            f"--- a/file{index}.txt\n+++ b/file{index}.txt\n"
            f"@@ -1 +1 @@\n+line\n"
        )
    patch = "\n".join(blocks)
    content = parse_unified_diff(patch, max_files=2)

    assert len(content.files) == 2
    assert content.truncated_files is True


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
