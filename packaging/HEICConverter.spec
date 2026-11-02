# PyInstaller spec — builds two one-file exes sharing one analysis:
#   HEICConverter.exe      windowed GUI (double-click, or drop folders on the icon)
#   HEICConverter-cli.exe  console CLI for scripts (same options as `heic-convert`)
# Build with scripts\build.ps1 (runs packaging/version_info.py first).
from pathlib import Path

from PyInstaller.utils.hooks import collect_dynamic_libs

ROOT = Path(SPECPATH).parent
version_file = Path(SPECPATH) / "build" / "version_info.txt"
version = str(version_file) if version_file.exists() else None
icon = str(ROOT / "assets" / "icon.ico")

EXCLUDES = [
    "tkinter", "unittest", "pydoc", "pytest",
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtOpenGL",
    "PySide6.QtPdf", "PySide6.QtSvg", "PySide6.QtDBus", "PySide6.QtSql", "PySide6.QtTest",
    "PySide6.QtConcurrent", "PySide6.QtXml",
]

gui = Analysis(
    [str(ROOT / "packaging" / "entry_gui.py")],
    pathex=[str(ROOT / "src")],
    binaries=collect_dynamic_libs("pillow_heif"),
    datas=[
        (str(ROOT / "docs" / "manual.ko.md"), "docs"),
        (str(ROOT / "docs" / "manual.en.md"), "docs"),
        (icon, "assets"),
    ],
    hiddenimports=["pillow_heif"],
    excludes=EXCLUDES,
)
cli = Analysis(
    [str(ROOT / "packaging" / "entry_cli.py")],
    pathex=[str(ROOT / "src")],
    binaries=collect_dynamic_libs("pillow_heif"),
    hiddenimports=["pillow_heif"],
    excludes=EXCLUDES + ["PySide6", "shiboken6"],
)

for analysis, name, console in ((gui, "HEICConverter", False), (cli, "HEICConverter-cli", True)):
    pyz = PYZ(analysis.pure)
    EXE(
        pyz,
        analysis.scripts,
        analysis.binaries,
        analysis.datas,
        name=name,
        console=console,
        icon=icon,
        version=version,
        upx=False,
    )
