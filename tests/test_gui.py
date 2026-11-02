from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from heic_converter.batch import Status  # noqa: E402
from heic_converter.gui.app import MainWindow  # noqa: E402
from heic_converter.gui.settings import Settings  # noqa: E402
from tests.conftest import make_heic  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "settings.json"
    monkeypatch.setenv("HEICCONV_SETTINGS", str(path))
    return path


@pytest.fixture
def window(qtbot) -> MainWindow:  # noqa: ANN001
    w = MainWindow(Settings(), lang="ko")
    qtbot.addWidget(w)
    return w


def _photos(root: Path) -> Path:
    (root / "sub").mkdir(parents=True)
    make_heic(root / "a.heic")
    make_heic(root / "sub" / "b.HEIC")
    (root / "c.MOV").write_bytes(b"x")
    return root


def test_defaults_match_spec(window: MainWindow) -> None:
    opts = window.build_options()
    assert (opts.format.value, opts.quality, opts.max_size, opts.metadata.value) == \
        ("jpg", 92, None, "strip_gps")
    assert window.rb_beside.isChecked() and window.chk_recursive.isChecked()
    assert window.cmb_conflict.currentData() == "rename"


def test_add_paths_counts_heic(window: MainWindow, tmp_path: Path) -> None:
    root = _photos(tmp_path / "p")
    window.add_paths([str(root), str(root)])
    assert window.inputs.count() == 1
    assert "HEIC 2개" in window.lbl_count.text()
    window.chk_recursive.setChecked(False)
    assert "HEIC 1개" in window.lbl_count.text()


def test_convert_to_folder_png(window: MainWindow, qtbot, tmp_path: Path) -> None:  # noqa: ANN001
    root = _photos(tmp_path / "p")
    out = tmp_path / "out"
    window.add_paths([str(root)])
    window.rb_png.setChecked(True)
    window.rb_folder.setChecked(True)
    window.edit_out.setText(str(out))
    assert window.start()
    with qtbot.waitSignal(window.worker.finished, timeout=20_000):
        pass
    qtbot.waitUntil(lambda: window.worker is None)
    assert (out / "p" / "a.png").exists() and (out / "p" / "sub" / "b.png").exists()
    assert window.table.rowCount() == 2
    assert window.result.count(Status.OK) == 2
    assert "성공 2" in window.lbl_summary.text()
    assert window.btn_csv.isEnabled() and window.btn_start.isEnabled()
    assert window.output_folder() == out


def test_start_without_inputs_is_refused(window: MainWindow, monkeypatch) -> None:  # noqa: ANN001
    shown = []
    monkeypatch.setattr("heic_converter.gui.app.QMessageBox.information",
                        lambda *a: shown.append(a[2]))
    assert window.start() is False
    assert shown == ["변환할 폴더나 파일을 먼저 추가하세요."]


def test_language_switch_retranslates(window: MainWindow) -> None:
    assert window.btn_start.text() == "변환 시작"
    window.set_language("en")
    assert window.btn_start.text() == "Convert"
    assert window.cmb_metadata.currentText() == "Strip GPS only"
    assert window.menu_help.title() == "Help"


def test_settings_persist_on_close(qtbot, _isolated_settings: Path) -> None:  # noqa: ANN001
    w = MainWindow(Settings(), lang="en")
    qtbot.addWidget(w)
    w.rb_png.setChecked(True)
    w.cmb_metadata.setCurrentIndex(w.cmb_metadata.findData("keep"))
    w.close()
    data = json.loads(_isolated_settings.read_text(encoding="utf-8"))
    assert data["format"] == "png" and data["metadata"] == "keep" and data["language"] == "en"
    again = MainWindow(Settings.load(), lang=None)
    qtbot.addWidget(again)
    assert again.rb_png.isChecked() and again.t.lang == "en"


def test_settings_load_ignores_bad_values(tmp_path: Path) -> None:
    path = tmp_path / "s.json"
    path.write_text('{"quality": "high", "format": "png", "unknown": 1}', encoding="utf-8")
    s = Settings.load(path)
    assert s.quality == 92 and s.format == "png"
    path.write_text("not json", encoding="utf-8")
    assert Settings.load(path) == Settings()


def test_manual_dialog_renders(window: MainWindow) -> None:
    dialog = window.show_manual()
    assert "HEIC Converter" in dialog.browser.toPlainText()
    dialog.close()
