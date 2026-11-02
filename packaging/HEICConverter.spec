# PyInstaller spec — build with: uv run --group build pyinstaller packaging/HEICConverter.spec
# (run `python packaging/version_info.py` first; scripts\build.ps1 does both)
from pathlib import Path

from PyInstaller.utils.hooks import collect_dynamic_libs

ROOT = Path(SPECPATH).parent
version_file = Path(SPECPATH) / "build" / "version_info.txt"

a = Analysis(
    [str(ROOT / "packaging" / "entry.py")],
    pathex=[str(ROOT / "src")],
    binaries=collect_dynamic_libs("pillow_heif"),
    hiddenimports=["pillow_heif"],
    excludes=["tkinter", "unittest", "pydoc", "pytest"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="HEICConverter",
    console=True,
    icon=str(ROOT / "assets" / "icon.ico"),
    version=str(version_file) if version_file.exists() else None,
    upx=False,
)
