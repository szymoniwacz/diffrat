"""Numbat CLI entry point."""

from __future__ import annotations

import argparse
import sys

from numbat import __version__


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parsed = list(argv) if argv is not None else sys.argv[1:]
    if not parsed:
        parser.print_help()
        return 0
    parser.parse_args(parsed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
