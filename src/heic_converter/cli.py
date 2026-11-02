"""Command line / drag-and-drop entry point (``heic-convert`` / HEICConverter.exe)."""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from pathlib import Path

from heic_converter import __version__
from heic_converter.batch import ConflictPolicy, Status, plan_jobs, run_batch, scan, write_report
from heic_converter.batch.runner import default_workers
from heic_converter.core import ConvertOptions, MetadataMode, OutputFormat
from heic_converter.i18n import LANGUAGES, Translator


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="HEICConverter",
        description="Batch-convert iPhone HEIC/HEIF photos to JPG/PNG.",
    )
    p.add_argument("inputs", nargs="*", help="folders and/or .heic files")
    p.add_argument("-f", "--format", choices=[f.value for f in OutputFormat], default="jpg")
    p.add_argument("-q", "--quality", type=int, default=92, help="JPG quality 1-100 (92)")
    p.add_argument("--max-size", type=int, default=None, help="shrink long edge to N px")
    p.add_argument("--metadata", choices=[m.value for m in MetadataMode],
                   default=MetadataMode.STRIP_GPS.value)
    p.add_argument("-o", "--out", type=Path, default=None,
                   help="output folder (default: next to each source)")
    p.add_argument("--conflict", choices=[c.value for c in ConflictPolicy],
                   default=ConflictPolicy.RENAME.value)
    p.add_argument("--no-recursive", action="store_true", help="do not scan subfolders")
    p.add_argument("-j", "--workers", type=int, default=default_workers())
    p.add_argument("--report", type=Path, default=None, help="write a CSV report here")
    p.add_argument("--lang", choices=LANGUAGES, default=None)
    p.add_argument("--pause", dest="pause", action="store_true", default=None,
                   help="wait for Enter before exiting (default when run from the .exe)")
    p.add_argument("--no-pause", dest="pause", action="store_false")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def _setup_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def main(argv: list[str] | None = None) -> int:
    _setup_console()
    args = build_parser().parse_args(argv)
    t = Translator(args.lang)
    pause = args.pause if args.pause is not None else bool(getattr(sys, "frozen", False))
    try:
        return _run(args, t)
    except KeyboardInterrupt:
        return 130
    finally:
        if pause and sys.stdin and sys.stdin.isatty():
            try:
                input(t("press_enter"))
            except (EOFError, KeyboardInterrupt):
                pass


def _run(args: argparse.Namespace, t: Translator) -> int:
    if not args.inputs:
        print(f"HEIC Converter {__version__}")
        print(t("usage_hint"))
        build_parser().print_usage()
        return 2

    options = ConvertOptions(
        format=OutputFormat(args.format),
        quality=args.quality,
        max_size=args.max_size,
        metadata=MetadataMode(args.metadata),
    )
    print(t("scanning"))
    found = scan(args.inputs, recursive=not args.no_recursive)
    print(t("found", count=len(found.sources), ignored=found.ignored))
    if not found.sources:
        print(t("nothing"))
        return 1

    jobs = plan_jobs(found.sources, options.format, args.out, ConflictPolicy(args.conflict))
    workers = max(1, args.workers)
    print(t("converting", fmt=options.format.value.upper(), workers=workers))

    cancel = threading.Event()
    started = time.perf_counter()

    def progress(done: int, total: int, item) -> None:  # noqa: ANN001
        line = t("progress", done=done, total=total, status=t(f"status_{item.status.value}"),
                 name=item.src.name)
        if item.message:
            line += f" — {item.message}"
        print(line, flush=True)

    try:
        result = run_batch(jobs, options, workers=workers, on_progress=progress, cancel=cancel)
    except KeyboardInterrupt:
        cancel.set()
        raise

    print(t("summary", ok=result.count(Status.OK), skipped=result.count(Status.SKIPPED),
            failed=result.count(Status.FAILED), seconds=time.perf_counter() - started))
    if result.cancelled:
        print(t("cancelled", count=result.count(Status.CANCELLED)))
    if args.report:
        print(t("report", path=os.fspath(write_report(result, args.report))))
    return 0 if result.count(Status.FAILED) == 0 and not result.cancelled else 1


if __name__ == "__main__":
    sys.exit(main())
