"""Run conversion jobs in parallel with progress and cancellation."""

from __future__ import annotations

import csv
import os
import threading
import time
from collections.abc import Callable
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from heic_converter.batch.plan import Job
from heic_converter.core import ConvertError, ConvertOptions, convert


class Status(StrEnum):
    OK = "ok"
    SKIPPED = "skipped"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class FileResult:
    src: Path
    dst: Path | None
    status: Status
    message: str = ""
    seconds: float = 0.0


@dataclass
class BatchResult:
    files: list[FileResult] = field(default_factory=list)
    cancelled: bool = False

    def count(self, status: Status) -> int:
        return sum(1 for f in self.files if f.status is status)


ProgressCallback = Callable[[int, int, FileResult], None]


def default_workers() -> int:
    return max(1, min(8, (os.cpu_count() or 2) - 1))


def run_batch(
    jobs: list[Job],
    options: ConvertOptions,
    *,
    workers: int | None = None,
    on_progress: ProgressCallback | None = None,
    cancel: threading.Event | None = None,
) -> BatchResult:
    """Threads, not processes: libheif and Pillow release the GIL, and threads keep
    the frozen .exe simple (no multiprocessing bootstrap) and cancellation immediate."""
    cancel = cancel or threading.Event()
    result = BatchResult()
    total, done = len(jobs), 0

    def record(item: FileResult) -> None:
        nonlocal done
        done += 1
        result.files.append(item)
        if on_progress:
            on_progress(done, total, item)

    def work(job: Job) -> FileResult:
        assert job.dst is not None
        if cancel.is_set():
            return FileResult(job.src, job.dst, Status.CANCELLED)
        start = time.perf_counter()
        try:
            convert(job.src, job.dst, options)
        except ConvertError as exc:
            return FileResult(job.src, job.dst, Status.FAILED, str(exc))
        return FileResult(job.src, job.dst, Status.OK, seconds=time.perf_counter() - start)

    pending_jobs = []
    for job in jobs:
        if job.dst is None:
            record(FileResult(job.src, None, Status.SKIPPED, "output exists"))
        else:
            pending_jobs.append(job)

    with ThreadPoolExecutor(max_workers=workers or default_workers()) as pool:
        queue = iter(pending_jobs)
        running: set[Future[FileResult]] = set()
        limit = (workers or default_workers()) * 2
        for job in queue:
            running.add(pool.submit(work, job))
            if len(running) >= limit:
                break
        while running:
            finished, running = wait(running, return_when=FIRST_COMPLETED)
            for fut in finished:
                record(fut.result())
            if cancel.is_set():
                continue
            for job in queue:
                running.add(pool.submit(work, job))
                if len(running) >= limit:
                    break
        if cancel.is_set():
            for job in queue:
                record(FileResult(job.src, job.dst, Status.CANCELLED))

    result.cancelled = cancel.is_set()
    return result


def write_report(result: BatchResult, path: str | os.PathLike[str]) -> Path:
    out = Path(path)
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow(["status", "source", "output", "message", "seconds"])
        for item in result.files:
            writer.writerow([
                item.status.value, str(item.src), str(item.dst or ""), item.message,
                f"{item.seconds:.3f}",
            ])
    return out
