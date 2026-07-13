from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from clipneuron.config import PipelineConfig
from clipneuron.crop_planner import SpeakerCropPlan
from clipneuron.render import (
    _build_crop_filter,
    _sanitize_caption_words,
    _write_ass,
    render_clips,
)
from clipneuron.segmenter import TranscriptWord


def test_build_crop_filter_landscape() -> None:
    crop = _build_crop_filter(1920, 1080)
    assert crop.startswith("crop=")
    assert ":" in crop


def test_build_crop_filter_portrait() -> None:
    crop = _build_crop_filter(1080, 1920)
    assert crop.startswith("crop=")


def test_write_ass_generates_entries(tmp_path: Path) -> None:
    ass_path = tmp_path / "clip.ass"
    words = [
        TranscriptWord(start=0.0, end=0.5, text="Hello"),
        TranscriptWord(start=0.6, end=1.0, text="viral"),
    ]
    _write_ass(ass_path, words, clip_start=0.0, clip_end=2.0, preset_name="creator")
    content = ass_path.read_text(encoding="utf-8")
    assert "[Script Info]" in content
    assert "Dialogue:" in content
    assert "viral" in content


def test_render_clips_builds_ffmpeg_command_and_plan_files(
    tmp_path: Path, monkeypatch
) -> None:
    input_path = tmp_path / "input.mp4"
    input_path.write_bytes(b"dummy")

    clips = [
        {
            "start": 1.0,
            "end": 4.5,
            "scores": {"overall": 90},
        }
    ]
    words = [
        TranscriptWord(start=1.0, end=1.5, text="Hello"),
        TranscriptWord(start=1.6, end=2.0, text="viral"),
    ]

    called = {}

    def fake_run(command, capture_output=False, text=False, check=False):
        called["command"] = command
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    def fake_crop_plan(_input, _start, _end, _config):
        return SpeakerCropPlan(
            source_width=1920,
            source_height=1080,
            crop_width=607,
            crop_height=1080,
            selected_speaker_id=1,
            tracked_faces=[{"face_id": 1, "samples": []}],
            crop_coordinates=[
                {"time": 0.0, "x": 656, "y": 0, "width": 607, "height": 1080}
            ],
            crop_filter="crop=607:1080:656:0",
        )

    monkeypatch.setattr(
        "clipneuron.render.get_video_dimensions", lambda _p: (1920, 1080)
    )
    monkeypatch.setattr("clipneuron.render.plan_speaker_crop", fake_crop_plan)
    monkeypatch.setattr("clipneuron.render.subprocess.run", fake_run)

    render_clips(input_path, tmp_path, clips, words, PipelineConfig(), top=1)

    cmd = called["command"]
    assert "ffmpeg" in cmd[0].lower()
    assert "-ss" in cmd
    assert "-to" in cmd
    assert "-vf" in cmd
    vf_index = cmd.index("-vf") + 1
    assert "ass='" in cmd[vf_index]

    assert (tmp_path / "caption_plan.json").exists()
    assert (tmp_path / "music_plan.json").exists()
    assert (tmp_path / "sfx_plan.json").exists()
    assert (tmp_path / "clip_01_crop.json").exists()
    caption_plan = json.loads(
        (tmp_path / "caption_plan.json").read_text(encoding="utf-8")
    )
    assert caption_plan["clips"][0]["preset"] == "creator"
    assert clips[0]["selected_speaker_id"] == 1
    assert clips[0]["crop_coordinates"][0]["x"] == 656


def test_sanitize_caption_words_drops_boilerplate_tokens() -> None:
    words = [
        TranscriptWord(start=0.0, end=0.5, text="Transcribed"),
        TranscriptWord(start=0.6, end=1.0, text="by"),
        TranscriptWord(start=1.1, end=1.5, text="ESO."),
        TranscriptWord(start=1.6, end=2.0, text="viral"),
    ]

    cleaned = _sanitize_caption_words(words)

    assert [word.text for word in cleaned] == ["by", "viral"]


def test_render_clips_invalid_duration(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "input.mp4"
    input_path.write_bytes(b"dummy")
    clips = [{"start": 5.0, "end": 2.0, "scores": {"overall": 10}}]
    monkeypatch.setattr(
        "clipneuron.render.get_video_dimensions", lambda _p: (1920, 1080)
    )
    with pytest.raises(ValueError):
        render_clips(input_path, tmp_path, clips, [], PipelineConfig(), top=1)


def test_render_clips_ffmpeg_failure(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "input.mp4"
    input_path.write_bytes(b"dummy")
    clips = [{"start": 1.0, "end": 3.0, "scores": {"overall": 10}}]
    words = [TranscriptWord(start=1.0, end=1.5, text="Hello")]

    def fake_run(command, capture_output=False, text=False, check=False):
        return SimpleNamespace(returncode=1, stdout="", stderr="ffmpeg error")

    def fake_crop_plan(_input, _start, _end, _config):
        return SpeakerCropPlan(
            source_width=1920,
            source_height=1080,
            crop_width=607,
            crop_height=1080,
            selected_speaker_id=1,
            tracked_faces=[{"face_id": 1, "samples": []}],
            crop_coordinates=[
                {"time": 0.0, "x": 656, "y": 0, "width": 607, "height": 1080}
            ],
            crop_filter="crop=607:1080:656:0",
        )

    monkeypatch.setattr(
        "clipneuron.render.get_video_dimensions", lambda _p: (1920, 1080)
    )
    monkeypatch.setattr("clipneuron.render.plan_speaker_crop", fake_crop_plan)
    monkeypatch.setattr("clipneuron.render.subprocess.run", fake_run)

    with pytest.raises(RuntimeError):
        render_clips(input_path, tmp_path, clips, words, PipelineConfig(), top=1)


def test_build_audio_filter_args_with_custom_ducking() -> None:
    from clipneuron.audio_director import AudioDirection
    from clipneuron.render import _build_audio_filter_args
    direction = AudioDirection(
        music={
            "asset": "dummy.mp3",
            "ducking": {
                "enabled": True,
                "music_target_db": -15.0,
                "ratio": 12.0,
                "threshold": 0.02,
            }
        },
        sound_effects=[],
        fade_in=0.5,
        fade_out=0.5
    )
    args = _build_audio_filter_args(direction, duration=10.0)
    assert len(args) > 0
    assert "dummy.mp3" in args
    filter_complex = args[args.index("-filter_complex") + 1]
    assert "volume=-15.00dB" in filter_complex
    assert "sidechaincompress=threshold=0.0200:ratio=12.00" in filter_complex
