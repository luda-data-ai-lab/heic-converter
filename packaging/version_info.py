"""Write the Windows VERSIONINFO resource for PyInstaller from heic_converter.__version__."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from heic_converter import __version__  # noqa: E402

parts = [int(p) for p in __version__.split(".")] + [0] * 4
nums = tuple(parts[:4])
text = f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={nums}, prodvers={nums}),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'LUDA Research Group'),
      StringStruct('FileDescription', 'HEIC Converter'),
      StringStruct('FileVersion', '{__version__}'),
      StringStruct('InternalName', 'HEICConverter'),
      StringStruct('LegalCopyright', 'MIT License, LUDA Research Group'),
      StringStruct('OriginalFilename', 'HEICConverter.exe'),
      StringStruct('ProductName', 'HEIC Converter'),
      StringStruct('ProductVersion', '{__version__}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
out = Path(__file__).resolve().parent / "build" / "version_info.txt"
out.parent.mkdir(exist_ok=True)
out.write_text(text, encoding="utf-8")
print(out)
