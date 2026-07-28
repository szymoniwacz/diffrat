"""Diff parser: normalize git numstat output into a change model."""

from __future__ import annotations

from dataclasses import dataclass

# Bounds for Changes sections in text and JSON reports (documented in CLI --help).
MAX_CHANGE_FILES = 20
MAX_LINES_PER_FILE = 100


ChangeType = str  # M | A | D | R | C


@dataclass(frozen=True)
class FileChange:
    """Per-file diff statistics."""

    path: str
    additions: int
    deletions: int
    binary: bool
    change_type: ChangeType = "M"


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


@dataclass(frozen=True)
class DiffHunk:
    """One @@ hunk with display lines (context, additions, deletions)."""

    header: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class FileDiffContent:
    """Bounded unified-diff content for one file."""

    path: str
    hunks: tuple[DiffHunk, ...]
    binary: bool
    truncated: bool


@dataclass(frozen=True)
class DiffContent:
    """Bounded unified-diff content across files."""

    files: tuple[FileDiffContent, ...]
    truncated_files: bool


def parse_name_status(name_status: str) -> dict[str, ChangeType]:
    """Parse ``git diff --name-status`` into a path -> change-type map."""
    mapping: dict[str, ChangeType] = {}

    for line in name_status.splitlines():
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        status_token = parts[0]
        change_type = status_token[0] if status_token else "M"
        if change_type not in {"M", "A", "D", "R", "C"}:
            change_type = "M"

        if change_type in {"R", "C"} and len(parts) >= 3:
            old_path, new_path = parts[1], parts[2]
            mapping[old_path] = change_type
            mapping[new_path] = change_type
            mapping[f"{old_path} => {new_path}"] = change_type
            continue

        mapping[parts[1]] = change_type

    return mapping


def parse_numstat(
    numstat: str,
    *,
    name_status: str | None = None,
) -> DiffSummary:
    """Parse ``git diff --numstat`` output into a diff summary."""
    change_types = parse_name_status(name_status) if name_status else {}
    files: list[FileChange] = []

    for line in numstat.splitlines():
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue

        additions_raw, deletions_raw, path = parts
        change_type = change_types.get(path, "M")
        if additions_raw == "-" and deletions_raw == "-":
            files.append(
                FileChange(
                    path=path,
                    additions=0,
                    deletions=0,
                    binary=True,
                    change_type=change_type,
                )
            )
            continue

        files.append(
            FileChange(
                path=path,
                additions=int(additions_raw),
                deletions=int(deletions_raw),
                binary=False,
                change_type=change_type,
            )
        )

    return DiffSummary(files=tuple(files))


def parse_unified_diff(
    patch: str,
    *,
    max_files: int = MAX_CHANGE_FILES,
    max_lines_per_file: int = MAX_LINES_PER_FILE,
) -> DiffContent:
    """Parse a unified diff patch into bounded per-file hunk content."""
    if not patch.strip():
        return DiffContent(files=(), truncated_files=False)

    file_blocks = _split_patch_into_file_blocks(patch)
    truncated_files = len(file_blocks) > max_files
    selected_blocks = file_blocks[:max_files]

    files: list[FileDiffContent] = []
    for block in selected_blocks:
        files.append(_parse_file_block(block, max_lines_per_file=max_lines_per_file))

    return DiffContent(files=tuple(files), truncated_files=truncated_files)


def _split_patch_into_file_blocks(patch: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in patch.splitlines():
        if line.startswith("diff --git "):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)

    if current:
        blocks.append(current)

    return blocks


def _parse_file_block(block: list[str], *, max_lines_per_file: int) -> FileDiffContent:
    path = _extract_path_from_block(block)
    if _is_binary_block(block):
        return FileDiffContent(path=path, hunks=(), binary=True, truncated=False)

    hunks: list[DiffHunk] = []
    current_header: str | None = None
    current_lines: list[str] = []
    line_count = 0
    truncated = False

    for line in block:
        if line.startswith("@@"):
            if current_header is not None:
                hunks.append(DiffHunk(header=current_header, lines=tuple(current_lines)))
                current_lines = []
            current_header = line
            continue

        if current_header is None:
            continue

        if line_count >= max_lines_per_file:
            truncated = True
            break

        if line.startswith(("+", "-", " ", "\\")):
            current_lines.append(line)
            line_count += 1

    if current_header is not None and not truncated:
        hunks.append(DiffHunk(header=current_header, lines=tuple(current_lines)))
    elif current_header is not None and truncated and current_lines:
        hunks.append(DiffHunk(header=current_header, lines=tuple(current_lines)))

    return FileDiffContent(path=path, hunks=tuple(hunks), binary=False, truncated=truncated)


def _extract_path_from_block(block: list[str]) -> str:
    for line in block:
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path.startswith("b/"):
                return path[2:]
            return path
    for line in block:
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                b_path = parts[3]
                if b_path.startswith("b/"):
                    return b_path[2:]
                return b_path
    return "(unknown)"


def _is_binary_block(block: list[str]) -> bool:
    return any("Binary files" in line for line in block)
