"""Tests for report renderer."""

from __future__ import annotations

from diffrat.diff_parser import DiffSummary, FileChange
from diffrat.git_adapter import GitCommitInfo, GitContext
from diffrat.report import render_review_report


def test_render_review_report_includes_summary_and_files() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/a.py", additions=4, deletions=1, binary=False),
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
            FileChange(path="bin.dat", additions=0, deletions=0, binary=True),
        )
    )

    report = render_review_report(summary)

    assert "Review Report" in report
    assert "Files changed: 3" in report
    assert "Lines added: 6" in report
    assert "Lines deleted: 1" in report
    assert "Total lines changed: 7" in report
    assert "src/a.py  [source]  risk=" in report
    assert "tests/test_a.py  [tests]  risk=" in report
    assert "bin.dat  [other]  risk=5  (binary)" in report
    assert "Review order" in report
    assert "1." in report
    assert "Focus / Risk" in report
    assert "[tests_touched]" in report
    assert "[warn] [tests_touched]" in report
    assert "Changes" in report
    assert "Review quality" in report
    assert report.index("Review quality") < report.index("Files\n-----")


def test_render_review_report_review_quality_after_summary_lists_pillar_status() -> None:
    from diffrat.analysis import AnalysisResult, focus_risk_hint

    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=4, deletions=1, binary=False),)
    )
    analysis = AnalysisResult(
        categories=("source",),
        risk_scores=(10,),
        hints=(
            focus_risk_hint("large_diff", "Large diff", severity="warn"),
            focus_risk_hint("possible_secret", "Secret", severity="risk"),
        ),
        llm_findings=None,
        llm_error=None,
    )
    report = render_review_report(summary, analysis=analysis)

    summary_pos = report.index("Summary")
    review_quality_pos = report.index("Review quality")
    files_pos = report.index("Files\n-----")
    assert summary_pos < review_quality_pos < files_pos
    assert "- Understand in seconds: warn (large_diff)" in report
    assert "- Safe to change in six months: risk (possible_secret)" in report
    assert "- One thing well: ok" in report


def test_render_review_report_includes_changes_section() -> None:
    from diffrat.diff_parser import DiffContent, DiffHunk, FileDiffContent

    summary = DiffSummary(
        files=(FileChange(path="README.md", additions=1, deletions=0, binary=False),)
    )
    diff_content = DiffContent(
        files=(
            FileDiffContent(
                path="README.md",
                hunks=(DiffHunk(header="@@ -1 +1 @@", lines=("+extra line",)),),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )

    report = render_review_report(summary, diff_content=diff_content)

    assert "Changes" in report
    assert "README.md" in report
    assert "+extra line" in report
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
        )
    )

    report = render_review_report(summary)

    assert "tests/test_a.py  [tests]  risk=" in report
    assert "pyproject.toml  [config]  risk=" in report
    assert "[tests_touched]" in report
    assert "[warn] [tests_touched]" in report
    assert "[config_or_deps]" in report


def test_render_review_report_includes_git_context() -> None:
    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=1, deletions=0, binary=False),)
    )
    git_context = GitContext(
        branch="feature",
        base_ref="main",
        commit_count=2,
        commits=(
            GitCommitInfo(short_hash="abc1234", subject="second commit"),
            GitCommitInfo(short_hash="def5678", subject="first commit"),
        ),
    )

    report = render_review_report(summary, git_context=git_context)

    assert "Git context" in report
    assert "Branch: feature" in report
    assert "Base: main" in report
    assert "Commits since base: 2" in report
    assert "abc1234 second commit" in report


def test_render_review_report_includes_range_git_context() -> None:
    summary = DiffSummary(
        files=(FileChange(path="feature.txt", additions=2, deletions=0, binary=False),)
    )
    git_context = GitContext(
        commit_count=2,
        commits=(
            GitCommitInfo(short_hash="abc1234", subject="second commit"),
            GitCommitInfo(short_hash="def5678", subject="first commit"),
        ),
        range_spec="main..feature",
        from_ref="main",
        to_ref="feature",
    )

    report = render_review_report(summary, git_context=git_context)

    assert "Range: main..feature" in report
    assert "From: main" in report
    assert "To: feature" in report
    assert "Commits in range: 2" in report
    assert "abc1234 second commit" in report


def test_render_review_report_groups_files_by_category() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
            FileChange(path="src/a.py", additions=4, deletions=1, binary=False),
            FileChange(path="pyproject.toml", additions=1, deletions=0, binary=False),
            FileChange(path="ci/run.py", additions=1, deletions=0, binary=False),
            FileChange(path="README.md", additions=1, deletions=0, binary=False),
            FileChange(path="bin.dat", additions=0, deletions=0, binary=True),
        )
    )

    report = render_review_report(summary)
    files_section = report.split("Review order", maxsplit=1)[0]
    files_section = files_section.split("Files\n-----", maxsplit=1)[1]

    assert files_section.index("source") < files_section.index("tests")
    assert files_section.index("tests") < files_section.index("ci")
    assert files_section.index("ci") < files_section.index("config")
    assert files_section.index("config") < files_section.index("docs")
    assert files_section.index("docs") < files_section.index("other")
    assert "  src/a.py  [source]  risk=" in report
    assert "  tests/test_a.py  [tests]  risk=" in report
    assert "  ci/run.py  [ci]  risk=" in report
    assert "  pyproject.toml  [config]  risk=" in report
    assert "  README.md  [docs]  risk=" in report
    assert "  bin.dat  [other]  risk=5  (binary)" in report


def test_render_review_report_review_order_before_changes_and_caps_at_five() -> None:
    files = tuple(
        FileChange(path=f"src/file_{index}.py", additions=index + 1, deletions=0, binary=False)
        for index in range(6)
    )
    summary = DiffSummary(files=files)

    report = render_review_report(summary)

    review_section = report.split("Review order", maxsplit=1)[1].split("Changes", maxsplit=1)[0]
    ranked_lines = [
        line for line in review_section.splitlines() if line.strip().startswith(tuple("12345."))
    ]
    assert len(ranked_lines) == 5
    assert "6." not in review_section
    assert report.index("Review order") < report.index("Changes")


def test_render_review_report_review_order_lists_all_when_five_or_fewer_files() -> None:
    summary = DiffSummary(
        files=(
            FileChange(path="src/a.py", additions=4, deletions=1, binary=False),
            FileChange(path="tests/test_a.py", additions=2, deletions=0, binary=False),
        )
    )

    report = render_review_report(summary)
    review_section = report.split("Review order", maxsplit=1)[1].split("Changes", maxsplit=1)[0]

    assert "1. src/a.py  [source]  (+4 -1 lines)" in review_section
    assert "2. tests/test_a.py  [tests]  (+2 -0 lines)" in review_section


def test_render_review_report_includes_llm_analysis_when_present() -> None:
    from dataclasses import replace

    from diffrat.analysis import analyze_diff

    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=1, deletions=0, binary=False),)
    )
    analysis = replace(
        analyze_diff(summary),
        llm_findings="Review auth changes carefully.\nCheck token expiry.",
    )

    report = render_review_report(summary, analysis=analysis)

    assert "LLM analysis" in report
    assert "Review auth changes carefully." in report
    assert "Check token expiry." in report
    llm_section = report.split("LLM analysis", maxsplit=1)[1]
    assert "Local checks" not in llm_section


def test_render_review_report_omits_llm_analysis_when_absent() -> None:
    summary = DiffSummary(
        files=(FileChange(path="src/a.py", additions=1, deletions=0, binary=False),)
    )

    report = render_review_report(summary)

    assert "LLM analysis" not in report


def test_render_review_report_brief_omits_changes_section() -> None:
    from diffrat.diff_parser import DiffContent, DiffHunk, FileDiffContent

    summary = DiffSummary(
        files=(FileChange(path="README.md", additions=1, deletions=0, binary=False),)
    )
    diff_content = DiffContent(
        files=(
            FileDiffContent(
                path="README.md",
                hunks=(DiffHunk(header="@@ -1 +1 @@", lines=("+extra line",)),),
                binary=False,
                truncated=False,
            ),
        ),
        truncated_files=False,
    )
    git_context = GitContext(
        branch="feature",
        base_ref="main",
        commit_count=1,
        commits=(GitCommitInfo(short_hash="abc1234", subject="add brief"),),
    )

    report = render_review_report(
        summary,
        git_context=git_context,
        diff_content=diff_content,
        brief=True,
    )

    assert "Git context" in report
    assert "Summary" in report
    assert "Files" in report
    assert "Review order" in report
    assert "Focus / Risk" in report
    assert "Changes" not in report
    assert "+extra line" not in report
    assert report.index("Review order") < report.index("Focus / Risk")
