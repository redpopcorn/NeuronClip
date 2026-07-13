from __future__ import annotations

from clipneuron.config import PipelineConfig
from clipneuron.optimizer import (
    _collect_end_boundaries,
    _collect_start_boundaries,
    _find_hook_start,
    _find_punchline_end,
    _find_sentence_index,
    _pick_best_variant,
    score_variant,
)
from clipneuron.segmenter import Sentence, TranscriptWord


def _make_sentence(start: float, end: float, text: str) -> Sentence:
    words = []
    tokens = text.split()
    duration = max(0.1, end - start)
    step = duration / max(1, len(tokens))
    for i, token in enumerate(tokens):
        w_start = start + i * step
        w_end = min(end, w_start + step * 0.9)
        words.append(TranscriptWord(start=w_start, end=w_end, text=token))
    return Sentence(start=start, end=end, text=text, words=tuple(words))


def test_sentence_boundary_detection() -> None:
    sentences = [
        _make_sentence(0.0, 5.0, "Hello there."),
        _make_sentence(5.0, 10.0, "This is sentence two."),
        _make_sentence(10.0, 15.0, "Final sentence here."),
    ]
    assert _find_sentence_index(sentences, 6.2) == 1
    assert _find_sentence_index(sentences, -1.0) == 0
    assert _find_sentence_index(sentences, 20.0) == 2

    start_bounds = _collect_start_boundaries(sentences, 1, 2)
    assert start_bounds == {0.0, 5.0}

    end_bounds = _collect_end_boundaries(sentences, 1, 2)
    assert end_bounds == {10.0, 15.0}


def test_hook_detection_prefers_stronger_hook() -> None:
    sentences = [
        _make_sentence(0.0, 5.0, "Most people get this wrong."),
        _make_sentence(5.0, 10.0, "This is the setup."),
        _make_sentence(10.0, 15.0, "Main idea starts now."),
    ]
    hook_start = _find_hook_start(sentences, 12.0, 15.0, base_hook_score=30.0)
    assert hook_start == 0.0


def test_punchline_detection_finds_next_sentence() -> None:
    sentences = [
        _make_sentence(0.0, 5.0, "We did the work."),
        _make_sentence(5.0, 10.0, "The result was shocking."),
        _make_sentence(10.0, 15.0, "Bottom line: it worked."),
    ]
    punchline_end = _find_punchline_end(sentences, 5.0, 15.0)
    assert punchline_end == 15.0


def test_variant_generation_respects_sentence_boundaries() -> None:
    sentences = [
        _make_sentence(0.0, 6.0, "Most people get this wrong."),
        _make_sentence(6.0, 12.0, "Here is why it matters."),
        _make_sentence(12.0, 20.0, "The result was shocking."),
    ]
    candidate = sentences[1]
    config = PipelineConfig(min_clip_s=6.0, max_clip_s=20.0, max_sentence_shift=2)
    energy_series = [0.1, 0.2, 0.3, 0.4]
    energy_times = [0.0, 5.0, 10.0, 15.0]
    best = _pick_best_variant(
        candidate,
        sentences,
        config,
        energy_series,
        energy_times,
        media_duration=30.0,
    )
    assert best["sentence"].start in {0.0, 6.0}
    assert best["sentence"].end in {12.0, 20.0}


def test_scoring_penalizes_filler() -> None:
    clean = _make_sentence(0.0, 10.0, "This is a clear point about strategy.")
    filler = _make_sentence(
        0.0, 10.0, "Um you know like basically this is like a point."
    )
    config = PipelineConfig(min_clip_s=5.0, max_clip_s=20.0)
    energy_series = [0.2, 0.2, 0.2]
    energy_times = [0.0, 5.0, 10.0]

    clean_scores = score_variant(clean, config, energy_series, energy_times)
    filler_scores = score_variant(filler, config, energy_series, energy_times)
    assert filler_scores["retention"] <= clean_scores["retention"]


def test_low_hook_score_zeroes_overall() -> None:
    sentence = _make_sentence(0.0, 10.0, "This is a neutral sentence.")
    config = PipelineConfig(min_clip_s=5.0, max_clip_s=20.0, min_hook_score=80.0)
    energy_series = [0.2, 0.2, 0.2]
    energy_times = [0.0, 5.0, 10.0]

    scores = score_variant(sentence, config, energy_series, energy_times)
    assert scores["overall"] == 0.0


def test_single_sentence_variant_generation() -> None:
    sentence = _make_sentence(0.0, 12.0, "Most people get this wrong.")
    config = PipelineConfig(min_clip_s=5.0, max_clip_s=20.0, max_sentence_shift=2)
    energy_series = [0.1, 0.2]
    energy_times = [0.0, 6.0]

    best = _pick_best_variant(
        sentence,
        [sentence],
        config,
        energy_series,
        energy_times,
        media_duration=30.0,
    )
    assert best["sentence"].start == 0.0
    assert best["sentence"].end == 12.0


def test_variant_scoring_formula() -> None:
    sentence = _make_sentence(0.0, 10.0, "Most people get this wrong, and here is why.")
    config = PipelineConfig(min_clip_s=5.0, max_clip_s=20.0, min_hook_score=10.0)
    energy_series = [0.2, 0.2]
    energy_times = [0.0, 5.0]
    scores = score_variant(sentence, config, energy_series, energy_times)
    assert 0.0 <= scores["overall"] <= 100.0
    assert scores["hook"] >= 0.0


def test_variant_at_video_edges() -> None:
    sentences = [
        _make_sentence(0.0, 6.0, "Most people get this wrong."),
        _make_sentence(6.0, 12.0, "Here is why it matters."),
    ]
    config = PipelineConfig(min_clip_s=6.0, max_clip_s=12.0, max_sentence_shift=2)
    energy_series = [0.1, 0.2, 0.3]
    energy_times = [0.0, 4.0, 8.0]

    best_start = _pick_best_variant(
        sentences[0],
        sentences,
        config,
        energy_series,
        energy_times,
        media_duration=12.0,
    )
    assert best_start["sentence"].start == 0.0

    best_end = _pick_best_variant(
        sentences[1],
        sentences,
        config,
        energy_series,
        energy_times,
        media_duration=12.0,
    )
    assert best_end["sentence"].end == 12.0
