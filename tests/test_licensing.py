"""The shipped decoder must stay free of GPL code (x265) so the noncommercial license holds."""

from __future__ import annotations

from pathlib import Path

import pi_heif
from PIL import Image

import heic_converter.core.convert  # noqa: F401  (registers the app's HEIF opener)

ROOT = Path(__file__).resolve().parents[1]


def test_app_decodes_with_pi_heif() -> None:
    assert Image.OPEN["HEIF"][0].__module__.startswith("pi_heif")


def test_pi_heif_bundles_no_x265() -> None:
    site = Path(pi_heif.__file__).resolve().parents[1]
    libs = [p.name.lower() for d in site.glob("pi_heif*") for p in d.rglob("*")]
    assert libs and not any("x265" in name for name in libs)


def test_spec_never_bundles_pillow_heif() -> None:
    spec = (ROOT / "packaging" / "HEICConverter.spec").read_text(encoding="utf-8")
    assert 'collect_dynamic_libs("pillow_heif")' not in spec
    assert '"pillow_heif"' in spec  # listed in EXCLUDES
