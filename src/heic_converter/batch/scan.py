"""Find HEIC/HEIF files under the user's selected folders/files."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass, field
from pathlib import Path

from heic_converter.core import is_heif_path


@dataclass(frozen=True)
class Source:
    path: Path
    root: Path
    """Folder the user selected (or the file's own folder); used to mirror structure."""


@dataclass
class ScanResult:
    sources: list[Source] = field(default_factory=list)
    ignored: int = 0
    """Non-HEIF, hidden or empty files that were skipped (e.g. Live Photo .MOV, .AAE)."""


def _is_hidden(path: Path) -> bool:
    if path.name.startswith("."):
        return True
    attrs = getattr(os.stat(path, follow_symlinks=False), "st_file_attributes", 0)
    return bool(attrs & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM))


def _accept(path: Path) -> bool:
    try:
        return is_heif_path(path) and not _is_hidden(path) and path.stat().st_size > 0
    except OSError:
        return False


def scan(inputs: list[str | os.PathLike[str]], recursive: bool = True) -> ScanResult:
    result = ScanResult()
    seen: set[Path] = set()

    def add(path: Path, root: Path) -> None:
        key = path.resolve()
        if key in seen:
            return
        seen.add(key)
        if _accept(path):
            result.sources.append(Source(path, root))
        else:
            result.ignored += 1

    for raw in inputs:
        item = Path(raw)
        if item.is_file():
            add(item, item.parent)
        elif item.is_dir():
            walker = item.rglob("*") if recursive else item.glob("*")
            for path in sorted(walker):
                if path.is_file() and not any(
                    part.startswith(".") for part in path.relative_to(item).parts[:-1]
                ):
                    add(path, item)
    return result
