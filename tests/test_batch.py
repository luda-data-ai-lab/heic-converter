from __future__ import annotations

import threading
from pathlib import Path

from heic_converter.batch import ConflictPolicy, Status, plan_jobs, run_batch, scan, write_report
from heic_converter.core import ConvertOptions, OutputFormat
from tests.conftest import make_heic


def _tree(root: Path) -> Path:
    (root / "2024" / "여름").mkdir(parents=True)
    make_heic(root / "a.HEIC")
    make_heic(root / "2024" / "b.heic")
    make_heic(root / "2024" / "여름" / "c.heif")
    (root / "a.MOV").write_bytes(b"live photo")
    (root / "a.AAE").write_text("<plist/>")
    (root / "empty.heic").write_bytes(b"")
    (root / ".hidden").mkdir()
    make_heic(root / ".hidden" / "x.heic")
    return root


def test_scan_recursive_skips_non_heif_hidden_empty(tmp_path: Path) -> None:
    root = _tree(tmp_path / "photos")
    found = scan([root])
    assert sorted(s.path.name for s in found.sources) == ["a.HEIC", "b.heic", "c.heif"]
    assert found.ignored == 3
    assert all(s.root == root for s in found.sources)


def test_scan_non_recursive_and_dedup(tmp_path: Path) -> None:
    root = _tree(tmp_path / "photos")
    found = scan([root, root / "a.HEIC"], recursive=False)
    assert [s.path.name for s in found.sources] == ["a.HEIC"]


def test_plan_beside_source(tmp_path: Path) -> None:
    root = _tree(tmp_path / "photos")
    jobs = plan_jobs(scan([root]).sources, OutputFormat.JPG)
    assert {j.dst for j in jobs} == {
        root / "a.jpg", root / "2024" / "b.jpg", root / "2024" / "여름" / "c.jpg",
    }


def test_plan_mirrors_structure_into_out_dir(tmp_path: Path) -> None:
    root = _tree(tmp_path / "photos")
    out = tmp_path / "out"
    jobs = plan_jobs(scan([root]).sources, OutputFormat.PNG, out)
    assert out / "photos" / "2024" / "여름" / "c.png" in {j.dst for j in jobs}


def test_conflict_policies(tmp_path: Path) -> None:
    make_heic(tmp_path / "IMG.HEIC")
    make_heic(tmp_path / "img.heif")  # collides case-insensitively
    (tmp_path / "IMG.jpg").write_bytes(b"existing")
    sources = scan([tmp_path]).sources

    renamed = [j.dst.name for j in plan_jobs(sources, OutputFormat.JPG)]
    assert sorted(renamed) == ["IMG_1.jpg", "img_2.jpg"]

    skipped = plan_jobs(sources, OutputFormat.JPG, conflict=ConflictPolicy.SKIP)
    assert [j.dst for j in skipped] == [None, None]

    overwrite = plan_jobs(sources, OutputFormat.JPG, conflict=ConflictPolicy.OVERWRITE)
    assert all(j.dst is not None for j in overwrite)


def test_run_batch_reports_ok_skip_fail(tmp_path: Path) -> None:
    root = _tree(tmp_path / "photos")
    (root / "broken.heic").write_bytes(b"not really heic")
    make_heic(root / "dup.heic")
    (root / "dup.jpg").write_bytes(b"existing")
    jobs = plan_jobs(scan([root]).sources, OutputFormat.JPG, conflict=ConflictPolicy.SKIP)
    seen: list[int] = []
    result = run_batch(jobs, ConvertOptions(), workers=2,
                       on_progress=lambda done, total, item: seen.append(done))
    assert (result.count(Status.OK), result.count(Status.SKIPPED), result.count(Status.FAILED)) \
        == (3, 1, 1)
    assert seen == list(range(1, 6))
    assert (root / "2024" / "여름" / "c.jpg").exists()

    report = write_report(result, tmp_path / "report.csv")
    text = report.read_text(encoding="utf-8-sig")
    assert text.splitlines()[0] == "status,source,output,message,seconds"
    assert "broken.heic" in text and "failed" in text


def test_run_batch_cancel(tmp_path: Path) -> None:
    for i in range(20):
        make_heic(tmp_path / f"{i:02}.heic")
    jobs = plan_jobs(scan([tmp_path]).sources, OutputFormat.JPG)
    cancel = threading.Event()

    def stop_after_first(done: int, total: int, item) -> None:  # noqa: ANN001
        cancel.set()

    result = run_batch(jobs, ConvertOptions(), workers=1, on_progress=stop_after_first,
                       cancel=cancel)
    assert result.cancelled
    assert len(result.files) == 20
    assert result.count(Status.CANCELLED) >= 15
    assert not list(tmp_path.glob("*.tmp"))
