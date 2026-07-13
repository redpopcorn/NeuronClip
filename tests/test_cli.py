from __future__ import annotations

import sys
from pathlib import Path

import pytest

from clipneuron import cli
from clipneuron.segmenter import TranscriptWord


def test_cli_parse_args_render(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--input",
            "input.mp4",
            "--output",
            "out.json",
            "--render",
            "--top",
            "3",
            "--clips-dir",
            "out",
        ],
    )
    args = cli.parse_args()
    assert args.render is True
    assert args.top == 3
    assert args.clips_dir == "out"


def test_cli_error_handling(monkeypatch, capsys) -> None:
    def fake_run_pipeline(_input: Path, _output: Path, _config):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(sys, "argv", ["prog", "--input", "a", "--output", "b"])

    with pytest.raises(SystemExit) as excinfo:
        cli.main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_cli_renders_when_flag_set(monkeypatch, tmp_path: Path) -> None:
    payload = {"clips": [{"start": 0.0, "end": 5.0, "scores": {"overall": 10}}]}
    words = [TranscriptWord(start=0.0, end=1.0, text="Hi")]

    def fake_run_pipeline(_input: Path, _output: Path, _config):
        return payload, words

    called = {"rendered": False}

    def fake_render(_input, _outdir, _clips, _words, _config, top):
        called["rendered"] = True

    monkeypatch.setattr(cli, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(cli, "render_clips", fake_render)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--input",
            str(tmp_path / "in.mp4"),
            "--output",
            str(tmp_path / "out.json"),
            "--render",
        ],
    )

    cli.main()
    assert called["rendered"] is True
