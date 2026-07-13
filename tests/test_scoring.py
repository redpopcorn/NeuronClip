from __future__ import annotations

from clipneuron.config import ScoringWeights
from clipneuron.scoring import ClipScores, compute_overall, score_hook, score_retention
from clipneuron.segmenter import Sentence, TranscriptWord


def _make_sentence(text: str, start: float = 0.0, end: float = 10.0) -> Sentence:
    words = [TranscriptWord(start=start, end=end, text=text)]
    return Sentence(start=start, end=end, text=text, words=tuple(words))


def test_compute_overall_weights() -> None:
    scores = ClipScores(
        hook=80, retention=70, caption_quality=60, visual_engagement=50, shareability=40
    )
    weights = ScoringWeights(
        hook=0.5,
        retention=0.2,
        caption_quality=0.1,
        visual_engagement=0.1,
        shareability=0.1,
    )
    overall = compute_overall(scores, weights)
    assert overall == 0.5 * 80 + 0.2 * 70 + 0.1 * 60 + 0.1 * 50 + 0.1 * 40


def test_score_hook_detects_question() -> None:
    sentence = _make_sentence("Why does this work?")
    score = score_hook(sentence, hook_window_s=3.0)
    assert score >= 60


def test_score_retention_basic() -> None:
    sentence = _make_sentence("This is a test", 0.0, 4.0)
    energy_series = [0.1, 0.2, 0.15]
    energy_times = [0.0, 2.0, 4.0]
    score = score_retention(sentence, energy_series, energy_times)
    assert 0.0 <= score <= 100.0
