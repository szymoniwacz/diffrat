"""Diff parser: normalize git numstat output into a change model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileChange:
    """Per-file diff statistics."""

    path: str
    additions: int
    deletions: int
    binary: bool


@dataclass(frozen=True)
class DiffSummary:
    """Aggregated diff statistics."""

    files: tuple[FileChange, ...]

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_additions(self) -> int:
        return sum(file.additions for file in self.files)

    @property
    def total_deletions(self) -> int:
        return sum(file.deletions for file in self.files)

    @property
    def total_lines_changed(self) -> int:
        return self.total_additions + self.total_deletions


def parse_numstat(numstat: str) -> DiffSummary:
    """Parse ``git diff --numstat`` output into a diff summary."""
    files: list[FileChange] = []

    for line in numstat.splitlines():
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue

        additions_raw, deletions_raw, path = parts
        if additions_raw == "-" and deletions_raw == "-":
            files.append(FileChange(path=path, additions=0, deletions=0, binary=True))
            continue

        files.append(
            FileChange(
                path=path,
                additions=int(additions_raw),
                deletions=int(deletions_raw),
                binary=False,
            )
        )

    return DiffSummary(files=tuple(files))
