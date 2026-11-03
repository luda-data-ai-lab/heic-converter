"""Help → User manual / License: render the bundled docs and license files offline."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QDialog, QTextBrowser, QVBoxLayout, QWidget


def manual_path(lang: str) -> Path | None:
    roots = []
    if hasattr(sys, "_MEIPASS"):
        roots.append(Path(sys._MEIPASS) / "docs")
    roots.append(Path(__file__).resolve().parents[3] / "docs")
    for root in roots:
        candidate = root / f"manual.{lang}.md"
        if candidate.exists():
            return candidate
    return None


LICENSE_FILES = ("LICENSE", "THIRD-PARTY-NOTICES.txt")


def license_text() -> str:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
    parts = [(root / name).read_text(encoding="utf-8") for name in LICENSE_FILES
             if (root / name).exists()]
    return ("\n\n" + "=" * 72 + "\n\n").join(parts) or "license not found"


class LicenseDialog(QDialog):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(760, 640)
        self.browser = QTextBrowser(self)
        self.browser.setPlainText(license_text())
        layout = QVBoxLayout(self)
        layout.addWidget(self.browser)


class ManualDialog(QDialog):
    def __init__(self, lang: str, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(820, 720)
        self.browser = QTextBrowser(self)
        self.browser.setOpenExternalLinks(True)
        path = manual_path(lang) or manual_path("en")
        if path:
            self.browser.setSource(QUrl.fromLocalFile(str(path)))
        else:
            self.browser.setPlainText("manual not found")
        layout = QVBoxLayout(self)
        layout.addWidget(self.browser)
