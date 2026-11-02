"""Help → User manual: render the bundled docs/manual.<lang>.md offline."""

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
