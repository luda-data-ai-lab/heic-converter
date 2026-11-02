"""Map sources to output paths and resolve name conflicts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from heic_converter.batch.scan import Source
from heic_converter.core import OutputFormat


class ConflictPolicy(StrEnum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"


@dataclass(frozen=True)
class Job:
    src: Path
    dst: Path | None
    """None when the output already exists and the policy is SKIP."""


def plan_jobs(
    sources: list[Source],
    fmt: OutputFormat,
    out_dir: Path | None = None,
    conflict: ConflictPolicy = ConflictPolicy.RENAME,
) -> list[Job]:
    """``out_dir=None`` writes next to each source; otherwise mirrors each selected
    folder under ``out_dir/<folder name>/...``."""
    reserved: set[Path] = set()
    existing = _ExistingNames()
    jobs: list[Job] = []
    for source in sources:
        if out_dir is None:
            base = source.path.parent
        else:
            rel = source.path.parent.relative_to(source.root)
            base = out_dir / source.root.name / rel if source.root.name else out_dir / rel
        target = base / f"{source.path.stem}.{fmt.value}"
        if conflict is ConflictPolicy.RENAME:
            target = _free_name(target, reserved, existing)
        elif conflict is ConflictPolicy.SKIP and (
            existing.has(target) or _key(target) in reserved
        ):
            jobs.append(Job(source.path, None))
            continue
        reserved.add(_key(target))
        jobs.append(Job(source.path, target))
    return jobs


def _key(path: Path) -> Path:
    # Windows file names are case-insensitive: IMG.HEIC and IMG.heic collide.
    return Path(str(path).lower())


class _ExistingNames:
    """Case-insensitive view of files already on disk, cached per folder."""

    def __init__(self) -> None:
        self._dirs: dict[Path, set[str]] = {}

    def has(self, path: Path) -> bool:
        names = self._dirs.get(path.parent)
        if names is None:
            try:
                names = {p.name.lower() for p in path.parent.iterdir()}
            except OSError:
                names = set()
            self._dirs[path.parent] = names
        return path.name.lower() in names


def _free_name(target: Path, reserved: set[Path], existing: _ExistingNames) -> Path:
    candidate, n = target, 1
    while existing.has(candidate) or _key(candidate) in reserved:
        candidate = target.with_name(f"{target.stem}_{n}{target.suffix}")
        n += 1
    return candidate
