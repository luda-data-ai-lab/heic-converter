"""Explorer right-click menu ("Convert to JPG/PNG") under HKCU — no admin rights needed."""

from __future__ import annotations

import os
import sys

KEY_NAME = "HEICConverter"
# (Classes subkey, argument placeholder). Background = right-click inside an open folder.
TARGETS: tuple[tuple[str, str], ...] = (
    (r"Directory\shell", "%1"),
    (r"Directory\Background\shell", "%V"),
    (r"SystemFileAssociations\.heic\shell", "%1"),
    (r"SystemFileAssociations\.heif\shell", "%1"),
    (r"SystemFileAssociations\.hif\shell", "%1"),
)


def classes_root() -> str:
    return os.environ.get("HEICCONV_REG_ROOT", r"Software\Classes")


def supported() -> bool:
    """Only a frozen Windows exe has a stable path to register."""
    return sys.platform == "win32" and getattr(sys, "frozen", False)


def entries(exe: str, label: str) -> list[tuple[str, dict[str, str], str]]:
    """(key path, values, command) for every menu entry."""
    root = classes_root()
    values = {"MUIVerb": label, "Icon": f'"{exe}",0', "MultiSelectModel": "Single"}
    return [(rf"{root}\{target}\{KEY_NAME}", values, f'"{exe}" "{arg}"') for target, arg in TARGETS]


def register(exe: str, label: str) -> None:
    import winreg

    for key, values, command in entries(exe, label):
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key) as handle:
            for name, value in values.items():
                winreg.SetValueEx(handle, name, 0, winreg.REG_SZ, value)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{key}\command") as handle:
            winreg.SetValueEx(handle, "", 0, winreg.REG_SZ, command)


def unregister() -> None:
    import winreg

    for key, _, _ in entries("", ""):
        for sub in (rf"{key}\command", key):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
            except FileNotFoundError:
                pass


def is_registered() -> bool:
    if sys.platform != "win32":
        return False
    import winreg

    try:
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, entries("", "")[0][0]).Close()
    except OSError:
        return False
    return True
