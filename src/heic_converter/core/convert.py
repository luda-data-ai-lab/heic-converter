"""Single-file HEIC/HEIF → JPG/PNG conversion."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import pillow_heif
from PIL import Image, ImageOps, UnidentifiedImageError

pillow_heif.register_heif_opener()

HEIF_EXTENSIONS = frozenset({".heic", ".heif", ".hif"})

_EXIF_ORIENTATION = 0x0112
_EXIF_GPS_IFD = 0x8825


class OutputFormat(StrEnum):
    JPG = "jpg"
    PNG = "png"


class MetadataMode(StrEnum):
    KEEP = "keep"
    STRIP_GPS = "strip_gps"
    STRIP_ALL = "strip_all"


@dataclass(frozen=True)
class ConvertOptions:
    format: OutputFormat = OutputFormat.JPG
    quality: int = 92
    max_size: int | None = None
    metadata: MetadataMode = MetadataMode.STRIP_GPS
    keep_icc: bool = True
    progressive: bool = False
    png_optimize: bool = False
    keep_mtime: bool = True

    def __post_init__(self) -> None:
        if not 1 <= self.quality <= 100:
            raise ValueError("quality must be between 1 and 100")
        if self.max_size is not None and self.max_size < 1:
            raise ValueError("max_size must be positive")


class ConvertError(Exception):
    """Raised when a source file cannot be decoded or the output cannot be written."""


def is_heif_path(path: str | os.PathLike[str]) -> bool:
    return Path(path).suffix.lower() in HEIF_EXTENSIONS


def convert(
    src: str | os.PathLike[str],
    dst: str | os.PathLike[str],
    options: ConvertOptions | None = None,
) -> Path:
    """Convert ``src`` to ``dst`` (overwriting it). The source file is never modified."""
    opts = options or ConvertOptions()
    src_path, dst_path = Path(src), Path(dst)
    if src_path.resolve() == dst_path.resolve():
        raise ConvertError("destination must differ from source")

    try:
        with Image.open(src_path) as opened:
            image, exif, icc = _prepare(opened, opts)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ConvertError(f"cannot read image: {exc}") from exc

    save_kwargs = _save_kwargs(opts, exif, icc)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".heicconv-", suffix=".tmp", dir=dst_path.parent)
    os.close(fd)
    try:
        image.save(tmp_name, format="JPEG" if opts.format is OutputFormat.JPG else "PNG",
                   **save_kwargs)
        os.replace(tmp_name, dst_path)
    except OSError as exc:
        raise ConvertError(f"cannot write output: {exc}") from exc
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

    if opts.keep_mtime:
        st = src_path.stat()
        os.utime(dst_path, ns=(st.st_atime_ns, st.st_mtime_ns))
    return dst_path


def _prepare(
    opened: Image.Image, opts: ConvertOptions
) -> tuple[Image.Image, Image.Exif | None, bytes | None]:
    icc = opened.info.get("icc_profile") if opts.keep_icc else None
    image = ImageOps.exif_transpose(opened) or opened
    image.load()

    exif: Image.Exif | None = None
    if opts.metadata is not MetadataMode.STRIP_ALL:
        exif = opened.getexif()
        exif[_EXIF_ORIENTATION] = 1
        if opts.metadata is MetadataMode.STRIP_GPS:
            exif.pop(_EXIF_GPS_IFD, None)

    image = _normalize_mode(image, opts.format)
    if opts.max_size and max(image.size) > opts.max_size:
        image.thumbnail((opts.max_size, opts.max_size), Image.Resampling.LANCZOS)
    return image, exif, icc


def _normalize_mode(image: Image.Image, fmt: OutputFormat) -> Image.Image:
    has_alpha = image.mode in ("RGBA", "LA", "PA") or (
        image.mode == "P" and "transparency" in image.info
    )
    if fmt is OutputFormat.JPG:
        if has_alpha:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.getchannel("A"))
            return background
        return image if image.mode in ("RGB", "L") else image.convert("RGB")
    if image.mode in ("RGB", "RGBA", "L", "LA"):
        return image
    return image.convert("RGBA" if has_alpha else "RGB")


def _save_kwargs(opts: ConvertOptions, exif: Image.Exif | None, icc: bytes | None) -> dict:
    kwargs: dict = {}
    if exif is not None and len(exif):
        kwargs["exif"] = exif.tobytes()
    if icc:
        kwargs["icc_profile"] = icc
    if opts.format is OutputFormat.JPG:
        kwargs.update(
            quality=opts.quality,
            subsampling=0 if opts.quality >= 95 else 2,
            progressive=opts.progressive,
            optimize=True,
        )
    else:
        kwargs.update(optimize=opts.png_optimize, compress_level=9 if opts.png_optimize else 6)
    return kwargs
