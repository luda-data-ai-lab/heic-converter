"""Main window (SPEC 3.4)."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QAction, QActionGroup, QDesktopServices, QIcon, QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from heic_converter import __version__, shell
from heic_converter.batch import BatchResult, ConflictPolicy, FileResult, Status, scan, write_report
from heic_converter.core import ConvertOptions, MetadataMode, OutputFormat
from heic_converter.gui.manual import LicenseDialog, ManualDialog
from heic_converter.gui.settings import Settings
from heic_converter.gui.worker import BatchWorker
from heic_converter.i18n import LANGUAGES, Translator

MAX_SIZES = (0, 4096, 3072, 2048, 1600, 1280, 1024)
LANGUAGE_NAMES = {"ko": "한국어", "en": "English"}
STATUS_COLORS = {Status.FAILED: Qt.GlobalColor.red, Status.CANCELLED: Qt.GlobalColor.darkGray}


def _asset(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
    return base / "assets" / name


class DropList(QListWidget):
    """Input list that accepts dropped folders/files and shows a hint while empty."""

    def __init__(self, on_drop, parent: QWidget | None = None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self._on_drop = on_drop
        self.hint = ""
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setMinimumHeight(90)
        self.setMaximumHeight(150)

    def dragEnterEvent(self, event) -> None:  # noqa: ANN001, N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    dragMoveEvent = dragEnterEvent  # noqa: N815

    def dropEvent(self, event) -> None:  # noqa: ANN001, N802
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        if paths:
            self._on_drop(paths)
            event.acceptProposedAction()

    def paintEvent(self, event) -> None:  # noqa: ANN001, N802
        super().paintEvent(event)
        if self.count() == 0 and self.hint:
            painter = QPainter(self.viewport())
            painter.setPen(Qt.GlobalColor.gray)
            painter.drawText(self.viewport().rect(), Qt.AlignmentFlag.AlignCenter, self.hint)


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings | None = None, lang: str | None = None) -> None:
        super().__init__()
        self.settings = settings or Settings.load()
        self.t = Translator(lang or self.settings.language or None)
        self.worker: BatchWorker | None = None
        self.result: BatchResult | None = None
        self._started = 0.0
        self._heic_count = 0
        self._build()
        self._apply_settings()
        self.retranslate()
        self.resize(880, 760)
        icon = _asset("icon.ico")
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))

    # ---------- layout ----------
    def _build(self) -> None:
        central = QWidget(self)
        root = QVBoxLayout(central)

        row = QHBoxLayout()
        self.btn_add_folder = QPushButton(clicked=self._pick_folder)
        self.btn_add_files = QPushButton(clicked=self._pick_files)
        self.btn_remove = QPushButton(clicked=self._remove_selected)
        self.btn_clear = QPushButton(clicked=self._clear_inputs)
        self.chk_recursive = QCheckBox(toggled=lambda _: self._recount())
        for w in (self.btn_add_folder, self.btn_add_files, self.btn_remove, self.btn_clear):
            row.addWidget(w)
        row.addStretch(1)
        row.addWidget(self.chk_recursive)
        root.addLayout(row)

        self.inputs = DropList(self.add_paths)
        root.addWidget(self.inputs)
        self.lbl_count = QLabel()
        root.addWidget(self.lbl_count)

        self.grp_options = QGroupBox()
        form = QFormLayout(self.grp_options)
        fmt_row = QHBoxLayout()
        self.rb_jpg, self.rb_png = QRadioButton("JPG"), QRadioButton("PNG")
        self.fmt_group = QButtonGroup(self)
        for rb in (self.rb_jpg, self.rb_png):
            self.fmt_group.addButton(rb)
            fmt_row.addWidget(rb)
        fmt_row.addStretch(1)
        self.rb_jpg.toggled.connect(self._sync_enabled)
        self.spin_quality = QSpinBox(minimum=1, maximum=100)
        self.cmb_max = QComboBox()
        self.cmb_metadata = QComboBox()
        self.cmb_conflict = QComboBox()
        out_row = QHBoxLayout()
        self.rb_beside, self.rb_folder = QRadioButton(), QRadioButton()
        self.out_group = QButtonGroup(self)
        self.out_group.addButton(self.rb_beside)
        self.out_group.addButton(self.rb_folder)
        self.rb_folder.toggled.connect(self._sync_enabled)
        self.edit_out = QLineEdit()
        self.btn_browse = QPushButton(clicked=self._pick_out_dir)
        for w in (self.rb_beside, self.rb_folder, self.edit_out, self.btn_browse):
            out_row.addWidget(w)
        self.lbl_format, self.lbl_quality, self.lbl_max = QLabel(), QLabel(), QLabel()
        self.lbl_metadata, self.lbl_conflict, self.lbl_output = QLabel(), QLabel(), QLabel()
        form.addRow(self.lbl_format, fmt_row)
        form.addRow(self.lbl_quality, self.spin_quality)
        form.addRow(self.lbl_max, self.cmb_max)
        form.addRow(self.lbl_metadata, self.cmb_metadata)
        form.addRow(self.lbl_conflict, self.cmb_conflict)
        form.addRow(self.lbl_output, out_row)
        root.addWidget(self.grp_options)

        run_row = QHBoxLayout()
        run_row.addStretch(1)
        self.btn_start = QPushButton(clicked=self.start)
        self.btn_start.setDefault(True)
        self.btn_start.setMinimumWidth(140)
        self.btn_cancel = QPushButton(clicked=self.cancel)
        self.btn_cancel.setEnabled(False)
        run_row.addWidget(self.btn_start)
        run_row.addWidget(self.btn_cancel)
        root.addLayout(run_row)

        self.progress = QProgressBar()
        self.progress.setFormat("%v / %m")
        self.lbl_status = QLabel()
        root.addWidget(self.progress)
        root.addWidget(self.lbl_status)

        self.table = QTableWidget(0, 4)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(self.table, 1)

        res_row = QHBoxLayout()
        self.lbl_summary = QLabel()
        self.btn_csv = QPushButton(clicked=self._save_csv)
        self.btn_open = QPushButton(clicked=self._open_output)
        self.btn_csv.setEnabled(False)
        self.btn_open.setEnabled(False)
        res_row.addWidget(self.lbl_summary, 1)
        res_row.addWidget(self.btn_csv)
        res_row.addWidget(self.btn_open)
        root.addLayout(res_row)

        self.lbl_footer = QLabel()
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_footer.setStyleSheet("color: gray; font-size: 11px;")
        root.addWidget(self.lbl_footer)
        self.setCentralWidget(central)

        bar = self.menuBar()
        self.menu_file = bar.addMenu("")
        self.act_quit = QAction(self, triggered=self.close)
        self.act_shell = QAction(self, checkable=True)
        self.act_shell.setEnabled(shell.supported())
        self.act_shell.setChecked(shell.is_registered())
        self.act_shell.toggled.connect(self._toggle_shell)
        self.menu_file.addAction(self.act_shell)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.act_quit)
        self.menu_lang = bar.addMenu("")
        self.lang_group = QActionGroup(self)
        self.lang_actions: dict[str, QAction] = {}
        for code in LANGUAGES:
            act = QAction(LANGUAGE_NAMES.get(code, code), self, checkable=True)
            act.triggered.connect(lambda _=False, c=code: self.set_language(c))
            self.lang_group.addAction(act)
            self.menu_lang.addAction(act)
            self.lang_actions[code] = act
        self.menu_help = bar.addMenu("")
        self.act_manual = QAction(self, triggered=self.show_manual)
        self.act_about = QAction(self, triggered=self._about)
        self.act_license = QAction(self, triggered=self.show_license)
        self.menu_help.addAction(self.act_manual)
        self.menu_help.addAction(self.act_license)
        self.menu_help.addAction(self.act_about)

    def _fill_combo(self, combo: QComboBox, items: list[tuple[str, object]]) -> None:
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for label, data in items:
            combo.addItem(label, data)
        idx = combo.findData(current)
        combo.setCurrentIndex(max(idx, 0))
        combo.blockSignals(False)

    def retranslate(self) -> None:
        t = self.t
        self.setWindowTitle(t("app_title"))
        self.menu_file.setTitle(t("menu_file"))
        self.act_quit.setText(t("menu_quit"))
        self.act_shell.setText(t("menu_shell"))
        self.menu_lang.setTitle(t("menu_language"))
        self.menu_help.setTitle(t("menu_help"))
        self.act_manual.setText(t("menu_manual"))
        self.act_about.setText(t("menu_about"))
        self.act_license.setText(t("menu_license"))
        self.lang_actions[t.lang].setChecked(True)
        self.btn_add_folder.setText(t("add_folder"))
        self.btn_add_files.setText(t("add_files"))
        self.btn_remove.setText(t("remove_selected"))
        self.btn_clear.setText(t("clear_list"))
        self.chk_recursive.setText(t("recursive"))
        self.inputs.hint = t("drop_hint")
        self.inputs.viewport().update()
        self.grp_options.setTitle(t("group_options"))
        self.lbl_format.setText(t("format"))
        self.lbl_quality.setText(t("quality"))
        self.lbl_max.setText(t("max_size"))
        self.lbl_metadata.setText(t("metadata"))
        self.lbl_conflict.setText(t("conflict"))
        self.lbl_output.setText(t("output"))
        self._fill_combo(self.cmb_max, [
            (t("max_size_original") if n == 0 else f"{n} px", n) for n in MAX_SIZES])
        self._fill_combo(self.cmb_metadata, [(t(f"metadata_{m.value}"), m.value)
                                             for m in MetadataMode])
        self._fill_combo(self.cmb_conflict, [(t(f"conflict_{c.value}"), c.value)
                                             for c in ConflictPolicy])
        self.rb_beside.setText(t("output_beside"))
        self.rb_folder.setText(t("output_folder"))
        self.btn_browse.setText(t("browse"))
        self.btn_start.setText(t("start"))
        self.btn_cancel.setText(t("cancel"))
        self.btn_csv.setText(t("save_csv"))
        self.btn_open.setText(t("open_output"))
        self.table.setHorizontalHeaderLabels(
            [t("col_status"), t("col_source"), t("col_output"), t("col_message")])
        self.lbl_footer.setText(t("footer"))
        if not self.worker:
            self.lbl_status.setText(t("ready"))
        self._update_count_label()
        if self.result:
            self._show_summary(self.result)

    def set_language(self, lang: str) -> None:
        self.t = Translator(lang)
        self.settings.language = lang
        self.retranslate()

    # ---------- settings ----------
    def _apply_settings(self) -> None:
        s = self.settings
        (self.rb_png if s.format == "png" else self.rb_jpg).setChecked(True)
        self.spin_quality.setValue(s.quality if 1 <= s.quality <= 100 else 92)
        self.chk_recursive.setChecked(s.recursive)
        (self.rb_folder if s.output_mode == "folder" else self.rb_beside).setChecked(True)
        self.edit_out.setText(s.output_dir)
        self.retranslate()
        for combo, value in ((self.cmb_max, s.max_size), (self.cmb_metadata, s.metadata),
                             (self.cmb_conflict, s.conflict)):
            combo.setCurrentIndex(max(combo.findData(value), 0))
        self._sync_enabled()

    def _collect_settings(self) -> Settings:
        s = self.settings
        s.format = "png" if self.rb_png.isChecked() else "jpg"
        s.quality = self.spin_quality.value()
        s.max_size = int(self.cmb_max.currentData() or 0)
        s.metadata = self.cmb_metadata.currentData()
        s.conflict = self.cmb_conflict.currentData()
        s.recursive = self.chk_recursive.isChecked()
        s.output_mode = "folder" if self.rb_folder.isChecked() else "beside"
        s.output_dir = self.edit_out.text().strip()
        s.language = self.t.lang
        return s

    def _sync_enabled(self) -> None:
        self.spin_quality.setEnabled(self.rb_jpg.isChecked())
        folder = self.rb_folder.isChecked()
        self.edit_out.setEnabled(folder)
        self.btn_browse.setEnabled(folder)

    # ---------- inputs ----------
    def input_paths(self) -> list[str]:
        return [self.inputs.item(i).text() for i in range(self.inputs.count())]

    def add_paths(self, paths: list[str]) -> None:
        existing = set(self.input_paths())
        for p in paths:
            p = str(Path(p))
            if p not in existing and Path(p).exists():
                self.inputs.addItem(p)
                existing.add(p)
        if paths:
            self.settings.last_dir = str(Path(paths[0]).parent)
        self._recount()

    def _recount(self) -> None:
        paths = self.input_paths()
        self._heic_count = len(scan(paths, self.chk_recursive.isChecked()).sources) if paths else 0
        self._update_count_label()

    def _update_count_label(self) -> None:
        self.lbl_count.setText(self.t("inputs_count", count=self.inputs.count(),
                                      heic=self._heic_count))

    def _pick_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, self.t("add_folder"),
                                                  self.settings.last_dir)
        if folder:
            self.add_paths([folder])

    def _pick_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, self.t("add_files"), self.settings.last_dir,
                                                self.t("heic_filter"))
        self.add_paths(files)

    def _pick_out_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, self.t("output_folder"),
                                                  self.edit_out.text() or self.settings.last_dir)
        if folder:
            self.edit_out.setText(folder)

    def _remove_selected(self) -> None:
        for item in self.inputs.selectedItems():
            self.inputs.takeItem(self.inputs.row(item))
        self._recount()

    def _clear_inputs(self) -> None:
        self.inputs.clear()
        self._recount()

    # ---------- run ----------
    def build_options(self) -> ConvertOptions:
        s = self._collect_settings()
        return ConvertOptions(
            format=OutputFormat(s.format),
            quality=s.quality,
            max_size=s.max_size or None,
            metadata=MetadataMode(s.metadata),
        )

    def out_dir(self) -> Path | None:
        return Path(self.edit_out.text().strip()) if self.rb_folder.isChecked() else None

    def start(self) -> bool:
        if self.worker:
            return False
        paths = self.input_paths()
        if not paths:
            QMessageBox.information(self, self.t("app_title"), self.t("need_inputs"))
            return False
        if self.rb_folder.isChecked() and not self.edit_out.text().strip():
            QMessageBox.information(self, self.t("app_title"), self.t("need_out_dir"))
            return False
        options = self.build_options()
        self.settings.save()
        self.result = None
        self.table.setRowCount(0)
        self.progress.setRange(0, 0)
        self.lbl_summary.clear()
        self._set_running(True)
        self._started = time.perf_counter()
        self.worker = BatchWorker(
            paths, options, recursive=self.chk_recursive.isChecked(), out_dir=self.out_dir(),
            conflict=ConflictPolicy(self.settings.conflict),
        )
        self.worker.scanned.connect(self._on_scanned)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()
        return True

    def cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.btn_cancel.setEnabled(False)

    def _set_running(self, running: bool) -> None:
        for w in (self.btn_start, self.grp_options, self.btn_add_folder, self.btn_add_files,
                  self.btn_remove, self.btn_clear, self.chk_recursive, self.inputs):
            w.setEnabled(not running)
        self.btn_cancel.setEnabled(running)
        self.btn_csv.setEnabled(not running and self.result is not None)
        self.btn_open.setEnabled(not running and self.result is not None)

    def _on_scanned(self, heic: int, ignored: int) -> None:
        self.progress.setRange(0, max(heic, 1))
        self.progress.setValue(0)
        self.lbl_status.setText(self.t("found", count=heic, ignored=ignored))

    def _on_progress(self, done: int, total: int, item: FileResult) -> None:
        self.progress.setRange(0, max(total, 1))
        self.progress.setValue(done)
        elapsed = time.perf_counter() - self._started
        remaining = int(elapsed / done * (total - done)) if done else 0
        self.lbl_status.setText(self.t("eta", done=done, total=total,
                                       eta=f"{remaining // 60}:{remaining % 60:02d}"))
        self._append_row(item)

    def _append_row(self, item: FileResult) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        cells = [self.t(f"status_{item.status.value}"), str(item.src), str(item.dst or ""),
                 item.message]
        for col, text in enumerate(cells):
            cell = QTableWidgetItem(text)
            color = STATUS_COLORS.get(item.status)
            if color is not None:
                cell.setForeground(color)
            self.table.setItem(row, col, cell)

    def _on_finished(self, result: BatchResult) -> None:
        if self.worker:
            self.worker.thread.wait()
        self.worker = None
        self.result = result
        self.progress.setRange(0, max(len(result.files), 1))
        self.progress.setValue(len(result.files))
        self._set_running(False)
        self._show_summary(result)
        if result.cancelled:
            self.lbl_status.setText(self.t("cancelled", count=result.count(Status.CANCELLED)))
        else:
            self.lbl_status.setText(self.t("summary", ok=result.count(Status.OK),
                                           skipped=result.count(Status.SKIPPED),
                                           failed=result.count(Status.FAILED),
                                           seconds=time.perf_counter() - self._started))

    def _show_summary(self, result: BatchResult) -> None:
        self.lbl_summary.setText(self.t("result_summary", ok=result.count(Status.OK),
                                        skipped=result.count(Status.SKIPPED),
                                        failed=result.count(Status.FAILED)))

    def _save_csv(self) -> None:
        if not self.result:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, self.t("save_csv"), str(Path(self.settings.last_dir) / "heic-report.csv"),
            self.t("csv_filter"))
        if path:
            write_report(self.result, path)

    def output_folder(self) -> Path | None:
        if self.out_dir():
            return self.out_dir()
        if self.result:
            for item in self.result.files:
                if item.dst:
                    return item.dst.parent
        return None

    def _open_output(self) -> None:
        folder = self.output_folder()
        if folder and folder.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    # ---------- help ----------
    def show_manual(self) -> ManualDialog:
        dialog = ManualDialog(self.t.lang, self.t("menu_manual"), self)
        dialog.show()
        return dialog

    def show_license(self) -> LicenseDialog:
        dialog = LicenseDialog(self.t("menu_license"), self)
        dialog.show()
        return dialog

    def _toggle_shell(self, on: bool) -> None:
        try:
            if on:
                shell.register(sys.executable, self.t("shell_verb"))
            else:
                shell.unregister()
        except OSError as exc:
            QMessageBox.warning(self, self.t("app_title"), str(exc))
            return
        QMessageBox.information(self, self.t("app_title"),
                                self.t("shell_added" if on else "shell_removed"))

    def _about(self) -> None:
        QMessageBox.about(self, self.t("menu_about"), self.t("about_text", version=__version__))

    def closeEvent(self, event) -> None:  # noqa: ANN001, N802
        if self.worker:
            self.worker.cancel()
            self.worker.thread.wait(10_000)
        self._collect_settings().save()
        super().closeEvent(event)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="HEICConverter")
    parser.add_argument("inputs", nargs="*")
    parser.add_argument("--lang", default=None)
    parser.add_argument("--register-shell", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--unregister-shell", action="store_true", help=argparse.SUPPRESS)
    args, qt_args = parser.parse_known_args(argv if argv is not None else sys.argv[1:])
    if args.register_shell or args.unregister_shell:
        # Called by the installer/uninstaller; no window.
        if args.unregister_shell:
            shell.unregister()
        else:
            shell.register(sys.executable, Translator(args.lang)("shell_verb"))
        return 0
    app = QApplication.instance() or QApplication([sys.argv[0], *qt_args])
    app.setApplicationName("HEIC Converter")
    window = MainWindow(lang=args.lang)
    window.show()
    if args.inputs:
        # Folders/files dropped onto the exe icon: convert right away with saved options.
        window.add_paths(args.inputs)
        window.start()
    if os.environ.get("HEICCONV_SMOKE"):
        _smoke_exit(app, window)
    return app.exec()


def _smoke_exit(app: QApplication, window: MainWindow) -> None:
    """CI check for the frozen exe: exit 0 once the window is up and any run finished cleanly."""
    def check() -> None:
        if window.worker:
            QTimer.singleShot(200, check)
            return
        ok = not window.windowIcon().isNull()
        if window.result is not None:
            result = window.result
            ok = ok and result.count(Status.FAILED) == 0 and result.count(Status.OK) > 0
        app.exit(0 if ok else 3)

    QTimer.singleShot(500, check)


if __name__ == "__main__":
    sys.exit(main())
