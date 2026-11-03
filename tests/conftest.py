from __future__ import annotations

from pathlib import Path

import pillow_heif
import pytest
from PIL import Image, ImageCms


def write_heic(image: Image.Image, path: Path, **kwargs) -> Path:
    """Encode with pillow-heif directly so Pillow's HEIF opener stays the app's pi-heif."""
    pillow_heif.from_pillow(image).save(path, **kwargs)
    return path


def make_heic(
    path: Path,
    size: tuple[int, int] = (64, 32),
    *,
    mode: str = "RGB",
    orientation: int | None = None,
    gps: bool = False,
    icc: bool = False,
) -> Path:
    color = (200, 30, 30, 128) if mode == "RGBA" else (200, 30, 30)
    image = Image.new(mode, size, color)
    image.paste((30, 30, 200)[: len(mode)] if mode != "RGBA" else (30, 30, 200, 255),
                (0, 0, size[0] // 2, size[1] // 2))
    exif = Image.Exif()
    exif[0x010F] = "Apple"
    exif[0x0110] = "iPhone 15 Pro"
    if orientation is not None:
        exif[0x0112] = orientation
    if gps:
        exif.get_ifd(0x8825).update({1: "N", 2: (37.0, 33.0, 0.0), 3: "E", 4: (126.0, 58.0, 0.0)})
    kwargs: dict = {"exif": exif.tobytes()}
    if icc:
        kwargs["icc_profile"] = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    return write_heic(image, path, quality=90, **kwargs)


@pytest.fixture
def heic(tmp_path: Path) -> Path:
    return make_heic(tmp_path / "IMG_0001.HEIC", gps=True, icc=True)
