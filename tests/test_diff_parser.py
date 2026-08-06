"""Tests for diff parser."""

from __future__ import annotations

from diffrat.diff_parser import parse_name_status, parse_numstat, parse_unified_diff

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


def test_parse_unified_diff_only_paths_filters_to_matching_file() -> None:
    blocks = [
        "diff --git a/a.txt b/a.txt\n--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n+a\n",
        "diff --git a/b.txt b/b.txt\n--- a/b.txt\n+++ b/b.txt\n@@ -1 +1 @@\n+b\n",
    ]
    patch = "\n".join(blocks)
    content = parse_unified_diff(patch, only_paths=frozenset({"b.txt"}))

    assert len(content.files) == 1
    assert content.files[0].path == "b.txt"
    assert content.truncated_files is False
    assert "+b" in content.files[0].hunks[0].lines


def test_parse_unified_diff_elevated_per_path_line_limit() -> None:
    from diffrat.diff_parser import HUNKS_FOR_MAX_LINES_PER_FILE

    lines = "\n".join(f"+line {index}" for index in range(HUNKS_FOR_MAX_LINES_PER_FILE + 1))
    patch = (
        "diff --git a/large.txt b/large.txt\n"
        "--- a/large.txt\n+++ b/large.txt\n"
        "@@ -1 +1,501 @@\n"
        f"{lines}\n"
    )
    content = parse_unified_diff(
        patch,
        only_paths=frozenset({"large.txt"}),
        max_lines_per_file_by_path={"large.txt": HUNKS_FOR_MAX_LINES_PER_FILE},
    )

    assert len(content.files) == 1
    assert content.files[0].truncated is True


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


def test_parse_name_status_modify_add_delete() -> None:
    name_status = "M\tsrc/foo.py\nA\tnew.py\nD\tremoved.py\n"
    mapping = parse_name_status(name_status)

    assert mapping == {
        "src/foo.py": "M",
        "new.py": "A",
        "removed.py": "D",
    }


def test_parse_name_status_rename_and_copy() -> None:
    name_status = "R100\told.py\tnew.py\nC90\tcopy_src.py\tcopy_dst.py\n"
    mapping = parse_name_status(name_status)

    assert mapping["old.py"] == "R"
    assert mapping["new.py"] == "R"
    assert mapping["old.py => new.py"] == "R"
    assert mapping["copy_src.py"] == "C"
    assert mapping["copy_dst.py"] == "C"
    assert mapping["copy_src.py => copy_dst.py"] == "C"


def test_parse_numstat_merges_name_status() -> None:
    numstat = "10\t5\told.py => new.py\n3\t0\tREADME.md\n"
    name_status = "R100\told.py\tnew.py\nM\tREADME.md\n"
    summary = parse_numstat(numstat, name_status=name_status)

    assert summary.files[0].path == "old.py => new.py"
    assert summary.files[0].change_type == "R"
    assert summary.files[1].path == "README.md"
    assert summary.files[1].change_type == "M"


def test_parse_numstat_defaults_change_type_to_modify() -> None:
    numstat = "1\t0\tsrc/foo.py\n"
    summary = parse_numstat(numstat)

    assert summary.files[0].change_type == "M"
