from __future__ import annotations

import math
from dataclasses import dataclass

from .config import ScoringWeights
from .segmenter import HOOK_PHRASES, Sentence


@dataclass(frozen=True)
class ClipScores:
    hook: float
    retention: float
    caption_quality: float
    visual_engagement: float
    shareability: float


def compute_overall(scores: ClipScores, weights: ScoringWeights) -> float:
    total = (
        weights.hook * scores.hook
        + weights.retention * scores.retention
        + weights.caption_quality * scores.caption_quality
        + weights.visual_engagement * scores.visual_engagement
        + weights.shareability * scores.shareability
    )
    return max(0.0, min(100.0, total))


STRONG_WORDS = {
    "never",
    "always",
    "secret",
    "truth",
    "biggest",
    "mistake",
    "insane",
    "crazy",
    "wild",
    "shocking",
    "simple",
    "easy",
    "hard",
    "risk",
    "guarantee",
    "prove",
    "nobody",
}


def score_clip(
    sentence: Sentence,
    hook_window_s: float,
    energy_series: list[float],
    energy_times: list[float],
) -> ClipScores:
    hook_score = score_hook(sentence, hook_window_s)
    retention_score = score_retention(sentence, energy_series, energy_times)
    caption_score = score_caption_quality(sentence)
    visual_score = score_visual_engagement(energy_series, energy_times, sentence)
    shareability_score = score_shareability(sentence)
    return ClipScores(
        hook=hook_score,
        retention=retention_score,
        caption_quality=caption_score,
        visual_engagement=visual_score,
        shareability=shareability_score,
    )


def score_hook(sentence: Sentence, hook_window_s: float) -> float:
    hook_text = _slice_text_by_time(sentence, hook_window_s).lower()
    phrase_hits = sum(1 for phrase in HOOK_PHRASES if phrase in hook_text)
    strong_hits = sum(1 for word in STRONG_WORDS if word in hook_text.split())
    question_bonus = 1 if "?" in hook_text else 0
    score = min(100.0, 50 + phrase_hits * 15 + strong_hits * 5 + question_bonus * 10)
    return score


def score_retention(
    sentence: Sentence,
    energy_series: list[float],
    energy_times: list[float],
) -> float:
    duration = max(0.1, sentence.end - sentence.start)
    words_per_sec = len(sentence.words) / duration
    pacing_score = 100 - abs(words_per_sec - 2.8) * 20
    pacing_score = max(0.0, min(100.0, pacing_score))
    energy_score = _energy_variance_score(
        energy_series, energy_times, sentence.start, sentence.end
    )
    score = 0.6 * pacing_score + 0.4 * energy_score
    return max(0.0, min(100.0, score))


def score_caption_quality(sentence: Sentence) -> float:
    text = sentence.text
    if not text:
        return 0.0
    length = len(text.split())
    punctuation_bonus = 10 if any(p in text for p in (".", "?", "!")) else 0
    length_score = 60 if 20 <= length <= 120 else 40
    return min(100.0, length_score + punctuation_bonus + 20)


def score_visual_engagement(
    energy_series: list[float],
    energy_times: list[float],
    sentence: Sentence,
) -> float:
    energy_score = _energy_variance_score(
        energy_series, energy_times, sentence.start, sentence.end
    )
    return max(0.0, min(100.0, 50 + 0.5 * energy_score))


def score_shareability(sentence: Sentence) -> float:
    text = sentence.text.lower()
    quotable = sum(1 for word in STRONG_WORDS if word in text)
    question_bonus = 1 if "?" in text else 0
    score = min(100.0, 40 + quotable * 8 + question_bonus * 10)
    return score


def _slice_text_by_time(sentence: Sentence, window_s: float) -> str:
    if not sentence.words:
        return ""
    start = sentence.start
    end = start + window_s
    words = [w.text for w in sentence.words if w.start <= end]
    return " ".join(words)


def _energy_variance_score(
    energy_series: list[float],
    energy_times: list[float],
    start: float,
    end: float,
) -> float:
    values = [e for e, t in zip(energy_series, energy_times) if start <= t <= end]
    if len(values) < 2:
        return 50.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    scaled = min(100.0, math.sqrt(variance) * 3000)
    return max(0.0, scaled)
