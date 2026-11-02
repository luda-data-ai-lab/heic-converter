from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from PIL import Image

from heic_converter.core import (
    ConvertError,
    ConvertOptions,
    MetadataMode,
    OutputFormat,
    convert,
    is_heif_path,
)
from tests.conftest import make_heic

PNG_OPTS = ConvertOptions(format=OutputFormat.PNG)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("fmt,pil_format", [(OutputFormat.JPG, "JPEG"), (OutputFormat.PNG, "PNG")])
def test_converts_to_format(heic: Path, tmp_path: Path, fmt: OutputFormat, pil_format: str) -> None:
    out = convert(heic, tmp_path / f"out.{fmt}", ConvertOptions(format=fmt))
    with Image.open(out) as im:
        assert im.format == pil_format
        assert im.size == (64, 32)


def test_source_is_never_modified(heic: Path, tmp_path: Path) -> None:
    before, mtime = _sha(heic), heic.stat().st_mtime_ns
    convert(heic, tmp_path / "out.jpg")
    assert _sha(heic) == before
    assert heic.stat().st_mtime_ns == mtime


def test_same_path_rejected(heic: Path) -> None:
    with pytest.raises(ConvertError):
        convert(heic, heic)


def test_default_strips_gps_keeps_camera(heic: Path, tmp_path: Path) -> None:
    out = convert(heic, tmp_path / "out.jpg")
    with Image.open(out) as im:
        exif = im.getexif()
        assert exif.get(0x010F) == "Apple"
        assert 0x8825 not in exif


def test_keep_metadata_keeps_gps(heic: Path, tmp_path: Path) -> None:
    out = convert(heic, tmp_path / "out.jpg", ConvertOptions(metadata=MetadataMode.KEEP))
    with Image.open(out) as im:
        assert im.getexif().get_ifd(0x8825).get(1) == "N"


def test_strip_all_removes_exif(heic: Path, tmp_path: Path) -> None:
    out = convert(heic, tmp_path / "out.jpg", ConvertOptions(metadata=MetadataMode.STRIP_ALL))
    with Image.open(out) as im:
        assert len(im.getexif()) == 0


def test_orientation_applied_and_reset(tmp_path: Path) -> None:
    src = make_heic(tmp_path / "rot.heic", size=(60, 20), orientation=6)
    out = convert(src, tmp_path / "rot.jpg")
    with Image.open(out) as im:
        assert im.size == (20, 60)
        assert im.getexif().get(0x0112) in (None, 1)


def test_icc_profile_kept_and_optional(heic: Path, tmp_path: Path) -> None:
    with Image.open(convert(heic, tmp_path / "a.png", PNG_OPTS)) as im:
        assert im.info.get("icc_profile")
    with Image.open(convert(heic, tmp_path / "b.jpg", ConvertOptions(keep_icc=False))) as im:
        assert not im.info.get("icc_profile")


def test_max_size_downscales_without_enlarging(heic: Path, tmp_path: Path) -> None:
    with Image.open(convert(heic, tmp_path / "s.jpg", ConvertOptions(max_size=32))) as im:
        assert im.size == (32, 16)
    with Image.open(convert(heic, tmp_path / "l.jpg", ConvertOptions(max_size=4000))) as im:
        assert im.size == (64, 32)


def test_alpha_composited_on_white_for_jpg_kept_for_png(tmp_path: Path) -> None:
    src = make_heic(tmp_path / "alpha.heic", mode="RGBA")
    with Image.open(convert(src, tmp_path / "a.jpg")) as im:
        assert im.mode == "RGB"
        r, g, b = im.getpixel((60, 30))
        assert r > 200 and g > 100 and b > 100
    with Image.open(convert(src, tmp_path / "a.png", PNG_OPTS)) as im:
        assert im.mode == "RGBA"


def test_mtime_preserved(heic: Path, tmp_path: Path) -> None:
    os.utime(heic, (1_600_000_000, 1_600_000_000))
    out = convert(heic, tmp_path / "out.jpg")
    assert int(out.stat().st_mtime) == 1_600_000_000


def test_quality_affects_size(heic: Path, tmp_path: Path) -> None:
    big = make_heic(tmp_path / "big.heic", size=(400, 300))
    low = convert(big, tmp_path / "low.jpg", ConvertOptions(quality=10))
    high = convert(big, tmp_path / "high.jpg", ConvertOptions(quality=100))
    assert low.stat().st_size < high.stat().st_size


def test_invalid_input_raises_and_leaves_no_temp(tmp_path: Path) -> None:
    bad = tmp_path / "bad.heic"
    bad.write_bytes(b"not an image")
    with pytest.raises(ConvertError):
        convert(bad, tmp_path / "out" / "bad.jpg")
    assert not list(tmp_path.rglob("*.tmp"))
    assert not (tmp_path / "out" / "bad.jpg").exists()


def test_unicode_and_space_paths(tmp_path: Path) -> None:
    folder = tmp_path / "아이폰 사진"
    folder.mkdir()
    src = make_heic(folder / "가족 여행.heic")
    out = convert(src, folder / "변환" / "가족 여행.jpg")
    assert out.exists()


@pytest.mark.parametrize("name,expected", [
    ("a.HEIC", True), ("b.heif", True), ("c.hif", True), ("d.jpg", False), ("e.MOV", False),
])
def test_is_heif_path(name: str, expected: bool) -> None:
    assert is_heif_path(name) is expected


@pytest.mark.parametrize("kwargs", [{"quality": 0}, {"quality": 101}, {"max_size": 0}])
def test_invalid_options(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        ConvertOptions(**kwargs)
