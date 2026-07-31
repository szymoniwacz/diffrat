"""Numbat CLI entry point."""

from __future__ import annotations

import argparse
import sys

from numbat import __version__
from numbat.diff_parser import HUNKS_FOR_MAX_LINES_PER_FILE, MAX_CHANGE_FILES, MAX_LINES_PER_FILE
from numbat.review import run_review


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="numbat",
        description="Local CLI for diff and PR review assistance.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser(
        "review",
        help="Analyze a local git diff and print a review report",
        description=(
            "Read a local git diff and print a human-readable review report to stdout.\n"
            "By default analyzes unstaged changes (working tree vs index).\n"
            "Use --staged for staged changes (index vs HEAD).\n"
            "Use --base to compare the current branch to a base ref (default: main).\n"
            "Use --range to compare two git refs (e.g. main..feature)."
        ),
        epilog=(
            "Exit codes: 0 success, 1 git/usage error, 2 empty diff, "
            "3 check failure, 4 --fail-on match.\n"
            f"Changes sections show up to {MAX_CHANGE_FILES} files and "
            f"{MAX_LINES_PER_FILE} diff lines per file."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    review_parser.add_argument(
        "--staged",
        action="store_true",
        help="Analyze staged changes (index vs HEAD) instead of unstaged changes",
    )
    review_parser.add_argument(
        "--base",
        nargs="?",
        const="main",
        default=None,
        metavar="REF",
        help=(
            "Compare HEAD to merge-base with REF (default: main when flag is given "
            "without a value). Mutually exclusive with --staged."
        ),
    )
    review_parser.add_argument(
        "--range",
        metavar="REV",
        dest="range_spec",
        help=(
            "Compare two git refs using two-dot range semantics (e.g. main..feature). "
            "Mutually exclusive with --staged and --base."
        ),
    )
    review_parser.add_argument(
        "--json",
        action="store_true",
        help=(
            "Write a structured JSON document to stdout instead of the human-readable "
            "report (schema_version field documents the output format)"
        ),
    )
    review_parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Run applicable local validators/tests for touched paths and include "
            "results in the report (exit code 3 when a check fails)"
        ),
    )
    review_parser.add_argument(
        "--fail-on",
        metavar="CODES",
        dest="fail_on",
        help=(
            "Comma-separated hint codes (no spaces); exit code 4 when any "
            "requested code appears in Focus/Risk hints"
        ),
    )
    review_parser.add_argument(
        "--hunks-for",
        metavar="PATH",
        dest="hunks_for",
        help=(
            "Show Changes hunks for a single repository-relative path only "
            f"(up to {HUNKS_FOR_MAX_LINES_PER_FILE} diff lines for that file; "
            "exit 1 if the path is not in the diff)"
        ),
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parsed = list(argv) if argv is not None else sys.argv[1:]
    if not parsed:
        parser.print_help()
        return 0

    args = parser.parse_args(parsed)
    if args.command == "review":
        return run_review(
            staged=args.staged,
            base=args.base,
            range_spec=args.range_spec,
            json_output=args.json,
            run_checks_flag=args.check,
            fail_on=args.fail_on,
            hunks_for=args.hunks_for,
        )

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
