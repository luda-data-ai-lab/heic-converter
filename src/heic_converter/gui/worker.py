"""Run a batch on a background QThread and report progress via signals."""

from __future__ import annotations

import threading
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from heic_converter.batch import BatchResult, ConflictPolicy, FileResult, plan_jobs, run_batch, scan
from heic_converter.core import ConvertOptions


class BatchWorker(QObject):
    scanned = Signal(int, int)
    """(heic files, ignored files)"""
    progress = Signal(int, int, object)
    """(done, total, FileResult)"""
    finished = Signal(object)
    """BatchResult"""

    def __init__(
        self,
        inputs: list[str],
        options: ConvertOptions,
        *,
        recursive: bool,
        out_dir: Path | None,
        conflict: ConflictPolicy,
    ) -> None:
        super().__init__()
        self.inputs, self.options = inputs, options
        self.recursive, self.out_dir, self.conflict = recursive, out_dir, conflict
        self.cancel_event = threading.Event()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)

    def start(self) -> None:
        self.thread.start()

    def cancel(self) -> None:
        self.cancel_event.set()

    def run(self) -> None:
        found = scan(self.inputs, recursive=self.recursive)
        self.scanned.emit(len(found.sources), found.ignored)
        jobs = plan_jobs(found.sources, self.options.format, self.out_dir, self.conflict)

        def on_progress(done: int, total: int, item: FileResult) -> None:
            self.progress.emit(done, total, item)

        result: BatchResult = run_batch(
            jobs, self.options, on_progress=on_progress, cancel=self.cancel_event
        )
        self.finished.emit(result)
        self.thread.quit()
