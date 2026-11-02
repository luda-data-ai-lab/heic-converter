"""iPhone-specific HEIC traits: 10-bit HDR, Display P3, multi-image containers, portrait EXIF."""

from __future__ import annotations

import struct
from pathlib import Path

import pillow_heif
from PIL import Image, ImageCms

from heic_converter.core import ConvertOptions, OutputFormat, convert
from tests.conftest import make_heic


def _p3_like_profile() -> bytes:
    # Pillow cannot build Display P3; any non-sRGB profile proves the bytes pass through.
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("LAB")).tobytes()


def test_10bit_hdr_heic_converts_to_8bit(tmp_path: Path) -> None:
    w, h = 64, 48
    data = b"".join(struct.pack("<HHH", (x * 1023 // w) << 6, (y * 1023 // h) << 6, 512 << 6)
                    for y in range(h) for x in range(w))
    src = tmp_path / "IMG_HDR.HEIC"
    pillow_heif.from_bytes(mode="RGB;16", size=(w, h), data=data).save(src, quality=90)
    assert pillow_heif.open_heif(src, convert_hdr_to_8bit=False).info["bit_depth"] == 10
    for fmt in (OutputFormat.JPG, OutputFormat.PNG):
        out = convert(src, tmp_path / f"out.{fmt.value}", ConvertOptions(format=fmt))
        with Image.open(out) as im:
            assert im.mode == "RGB" and im.size == (w, h)
            left, right = im.getpixel((1, 1)), im.getpixel((w - 2, 1))
            assert right[0] > left[0] + 150  # gradient survives the bit-depth reduction


def test_multi_image_container_uses_primary(tmp_path: Path) -> None:
    heif = pillow_heif.HeifFile()
    heif.add_from_pillow(Image.new("RGB", (32, 32), "red"))
    heif.add_from_pillow(Image.new("RGB", (80, 60), "blue"))
    heif[1].info["primary"] = True
    heif[0].info["primary"] = False
    src = tmp_path / "IMG_MULTI.HEIC"
    heif.save(src)
    out = convert(src, tmp_path / "out.png", ConvertOptions(format=OutputFormat.PNG))
    with Image.open(out) as im:
        assert im.size == (80, 60)
        r, g, b = im.getpixel((5, 5))
        assert b > 200 and r < 50


def test_wide_gamut_icc_passes_through_unchanged(tmp_path: Path) -> None:
    profile = _p3_like_profile()
    src = tmp_path / "IMG_P3.HEIC"
    Image.new("RGB", (40, 30), (10, 200, 90)).save(src, format="HEIF", icc_profile=profile)
    for fmt in (OutputFormat.JPG, OutputFormat.PNG):
        out = convert(src, tmp_path / f"out.{fmt.value}", ConvertOptions(format=fmt))
        with Image.open(out) as im:
            assert im.info.get("icc_profile") == profile


def test_portrait_photo_rotated_then_resized_on_long_edge(tmp_path: Path) -> None:
    # iPhone stores portrait shots as landscape pixels + Orientation=6.
    src = make_heic(tmp_path / "IMG_PORTRAIT.HEIC", size=(400, 300), orientation=6)
    with Image.open(convert(src, tmp_path / "out.jpg", ConvertOptions(max_size=200))) as im:
        assert im.size == (150, 200)
        assert im.getexif().get(0x0112) in (None, 1)
