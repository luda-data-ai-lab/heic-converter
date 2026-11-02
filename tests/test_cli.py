from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from heic_converter.cli import main
from tests.conftest import make_heic


def test_cli_converts_folder_png_out_dir(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    src = tmp_path / "in"
    src.mkdir()
    make_heic(src / "a.heic")
    make_heic(src / "b.HEIC")
    out = tmp_path / "out"
    code = main([str(src), "-f", "png", "-o", str(out), "--report", str(tmp_path / "r.csv"),
                 "--lang", "en", "--no-pause"])
    assert code == 0
    assert sorted(p.name for p in (out / "in").iterdir()) == ["a.png", "b.png"]
    with Image.open(out / "in" / "a.png") as im:
        assert im.format == "PNG"
    stdout = capsys.readouterr().out
    assert "Done: 2 converted" in stdout
    assert (tmp_path / "r.csv").exists()


def test_cli_korean_and_failure_exit(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    (tmp_path / "bad.heic").write_bytes(b"x")
    code = main([str(tmp_path), "--lang", "ko", "--no-pause"])
    assert code == 1
    assert "실패 1" in capsys.readouterr().out


def test_cli_no_inputs_shows_hint(capsys: pytest.CaptureFixture) -> None:
    assert main(["--lang", "ko", "--no-pause"]) == 2
    assert "끌어다 놓으세요" in capsys.readouterr().out


def test_cli_nothing_to_convert(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"x")
    assert main([str(tmp_path), "--no-pause"]) == 1
