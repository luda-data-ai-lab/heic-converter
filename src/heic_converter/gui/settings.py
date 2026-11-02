"""Persist GUI choices to %APPDATA%\\HEICConverter\\settings.json."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, fields
from pathlib import Path


def settings_path() -> Path:
    override = os.environ.get("HEICCONV_SETTINGS")
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "HEICConverter" / "settings.json"


@dataclass
class Settings:
    format: str = "jpg"
    quality: int = 92
    max_size: int = 0
    metadata: str = "strip_gps"
    conflict: str = "rename"
    recursive: bool = True
    output_mode: str = "beside"
    output_dir: str = ""
    language: str = ""
    last_dir: str = ""

    @classmethod
    def load(cls, path: Path | None = None) -> Settings:
        path = path or settings_path()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls()
        known = {f.name: f.type for f in fields(cls)}
        defaults = cls()
        kwargs = {}
        for key, value in data.items() if isinstance(data, dict) else ():
            if key in known and isinstance(value, type(getattr(defaults, key))):
                kwargs[key] = value
        return cls(**kwargs)

    def save(self, path: Path | None = None) -> None:
        path = path or settings_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), "utf-8")
            os.replace(tmp, path)
        except OSError:
            pass
