from __future__ import annotations

from pathlib import Path

from clipneuron.config import PipelineConfig
from clipneuron.pipeline import _score_transcript_quality, run_pipeline
from clipneuron.segmenter import TranscriptWord


def _make_words() -> list[TranscriptWord]:
    words = []
    text = [
        "Most",
        "people",
        "get",
        "this",
        "wrong.",
        "Here",
        "is",
        "why",
        "it",
        "matters.",
        "The",
        "result",
        "was",
        "shocking.",
    ]
    t = 0.0
    for token in text:
        words.append(TranscriptWord(start=t, end=t + 1.5, text=token))
        t += 1.6
    return words


def test_score_transcript_quality_flags_boilerplate_low_coverage() -> None:
    words = [
        TranscriptWord(start=28.58, end=29.98, text="Transcribed"),
        TranscriptWord(start=29.98, end=29.98, text="by"),
        TranscriptWord(start=29.98, end=29.98, text="ESO."),
        TranscriptWord(start=32.70, end=34.10, text="Transcribed"),
    ]

    score, audit = _score_transcript_quality(words, audio_duration=34.13)

    assert audit["likely_low_quality"] is True
    assert "boilerplate_phrase_detected" in audit["flags"]
    assert "low_speech_coverage" in audit["flags"]
    assert score < 20


def test_optimization_report_generation(monkeypatch, tmp_path: Path) -> None:
    input_path = tmp_path / "input.mp4"
    input_path.write_bytes(b"dummy")
    output_path = tmp_path / "clips.json"

    def fake_extract_audio(_input: Path, _output: Path, _sr: int) -> None:
        return None

    def fake_transcribe_words(_audio: Path, _config: PipelineConfig):
        return _make_words()

    def fake_get_media_duration(_input: Path) -> float:
        return 120.0

    def fake_compute_energy_series(_audio: Path, _config: PipelineConfig):
        return [0.2, 0.3, 0.25], [0.0, 5.0, 10.0]

    def fake_optimize_candidates(*_args, **_kwargs):
        return (
            [
                {"start": 5.0, "end": 15.0, "scores": {"overall": 50}},
                {"start": 0.0, "end": 10.0, "scores": {"overall": 80}},
            ],
            {"improved_rate": 1.0, "weak_hook_count": 0},
        )

    monkeypatch.setattr("clipneuron.pipeline.ensure_dependency", lambda _name: None)
    monkeypatch.setattr("clipneuron.pipeline.extract_audio", fake_extract_audio)
    monkeypatch.setattr("clipneuron.pipeline.transcribe_words", fake_transcribe_words)
    monkeypatch.setattr(
        "clipneuron.pipeline.get_media_duration", fake_get_media_duration
    )
    monkeypatch.setattr(
        "clipneuron.pipeline.compute_energy_series", fake_compute_energy_series
    )
    monkeypatch.setattr(
        "clipneuron.pipeline.optimize_candidates", fake_optimize_candidates
    )

    config = PipelineConfig(min_clip_s=3.0, max_clip_s=30.0, target_candidates=5)
    payload, _ = run_pipeline(input_path, output_path, config)

    report_path = output_path.with_name("optimization_report.json")
    assert report_path.exists()
    assert report_path.read_text(encoding="utf-8")
    assert payload["clips"][0]["scores"]["overall"] == 80
