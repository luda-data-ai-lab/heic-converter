from __future__ import annotations

import sys

import pytest

from heic_converter import shell


def test_entries_cover_folders_background_and_heif(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HEICCONV_REG_ROOT", raising=False)
    items = shell.entries(r"C:\Apps\HEICConverter.exe", "Convert")
    keys = [key for key, _, _ in items]
    assert r"Software\Classes\Directory\shell\HEICConverter" in keys
    assert r"Software\Classes\SystemFileAssociations\.heic\shell\HEICConverter" in keys
    commands = dict((key, command) for key, _, command in items)
    assert commands[r"Software\Classes\Directory\shell\HEICConverter"] == \
        r'"C:\Apps\HEICConverter.exe" "%1"'
    assert commands[r"Software\Classes\Directory\Background\shell\HEICConverter"] == \
        r'"C:\Apps\HEICConverter.exe" "%V"'
    assert all(values["MultiSelectModel"] == "Single" for _, values, _ in items)


def test_not_supported_from_source() -> None:
    assert not shell.supported()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows registry")
def test_register_and_unregister_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    import winreg

    monkeypatch.setenv("HEICCONV_REG_ROOT", r"Software\HEICConverterTest\Classes")
    shell.unregister()
    assert not shell.is_registered()
    shell.register(r"C:\Apps\HEICConverter.exe", "JPG/PNG로 변환")
    try:
        assert shell.is_registered()
        key = shell.entries("", "")[0][0]
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as handle:
            assert winreg.QueryValueEx(handle, "MUIVerb")[0] == "JPG/PNG로 변환"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key + r"\command") as handle:
            assert winreg.QueryValueEx(handle, "")[0] == r'"C:\Apps\HEICConverter.exe" "%1"'
    finally:
        shell.unregister()
    assert not shell.is_registered()
