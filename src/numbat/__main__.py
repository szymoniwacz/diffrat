"""Numbat CLI entry point."""

from __future__ import annotations

import argparse
import sys

from numbat import __version__
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
            "Use --staged for staged changes (index vs HEAD)."
        ),
        epilog="Exit codes: 0 success, 1 git error, 2 empty diff.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    review_parser.add_argument(
        "--staged",
        action="store_true",
        help="Analyze staged changes (index vs HEAD) instead of unstaged changes",
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
        return run_review(staged=args.staged)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
