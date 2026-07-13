from __future__ import annotations

import pytest

from clipneuron.config import PipelineConfig
from clipneuron.segmenter import Sentence, TranscriptWord
from clipneuron.validation import (
    select_non_overlapping,
    validate_candidates,
    validate_config,
    validate_transcript,
)


def _make_sentence(start: float, end: float, text: str) -> Sentence:
    words = [TranscriptWord(start=start, end=end, text=text)]
    return Sentence(start=start, end=end, text=text, words=tuple(words))


def test_validate_transcript_empty() -> None:
    with pytest.raises(ValueError):
        validate_transcript([])


def test_validate_transcript_invalid_words() -> None:
    words = [
        TranscriptWord(start=1.0, end=0.5, text="bad"),
        TranscriptWord(start=-1.0, end=1.0, text="bad"),
        TranscriptWord(start=0.0, end=1.0, text=""),
    ]
    with pytest.raises(ValueError):
        validate_transcript(words)


def test_validate_candidates_min_max_duration() -> None:
    candidates = [
        _make_sentence(0.0, 5.0, "short"),
        _make_sentence(5.0, 15.0, "valid"),
        _make_sentence(15.0, 80.0, "long"),
    ]
    result = validate_candidates(
        candidates, min_s=10.0, max_s=60.0, media_duration=120.0
    )
    assert len(result.candidates) == 1
    assert result.candidates[0].text == "valid"


def test_validate_candidates_edges_at_limits() -> None:
    candidates = [
        _make_sentence(0.0, 10.0, "min"),
        _make_sentence(10.0, 70.0, "max"),
    ]
    result = validate_candidates(
        candidates, min_s=10.0, max_s=60.0, media_duration=120.0
    )
    assert len(result.candidates) == 2


def test_validate_candidates_invalid_timestamps() -> None:
    candidates = [
        _make_sentence(-1.0, 5.0, "neg"),
        _make_sentence(5.0, 4.0, "bad"),
        _make_sentence(0.0, 15.0, "ok"),
        _make_sentence(0.0, 200.0, "too long"),
    ]
    result = validate_candidates(
        candidates, min_s=5.0, max_s=60.0, media_duration=120.0
    )
    assert len(result.candidates) == 1
    assert result.candidates[0].text == "ok"


def test_validate_config_crop_controls() -> None:
    with pytest.raises(ValueError):
        validate_config(PipelineConfig(smoothing_factor=1.5))
    with pytest.raises(ValueError):
        validate_config(PipelineConfig(face_detection_interval=0))
    with pytest.raises(ValueError):
        validate_config(PipelineConfig(max_crop_velocity=0))


def test_select_non_overlapping() -> None:
    clips = [
        {"start": 0.0, "end": 10.0},
        {"start": 5.0, "end": 12.0},
        {"start": 12.0, "end": 20.0},
    ]
    selected = select_non_overlapping(clips)
    assert selected == [clips[0], clips[2]]
