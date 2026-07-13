from __future__ import annotations

import logging

from .config import PipelineConfig
from .errors import PipelineStageError
from .hook_analyzer import analyze_hook
from .segmenter import Sentence

logger = logging.getLogger("clipneuron.optimizer")

FILLER_PHRASES = (
    "um",
    "uh",
    "you know",
    "like",
    "sort of",
    "kind of",
    "basically",
    "literally",
    "i mean",
)

HOOK_CUES = (
    "?",
    "the biggest mistake",
    "nobody talks about",
    "what happened next",
    "the truth is",
    "most people",
    "here's why",
)

PUNCHLINE_CUES = (
    "in summary",
    "the point is",
    "that's why",
    "bottom line",
    "so",
    "therefore",
    "the result",
    "what we learned",
)

STORY_CUES = (
    "when",
    "then",
    "once",
    "after",
    "before",
    "suddenly",
    "I",
    "we",
    "my",
    "our",
    "story",
)


def optimize_candidates(
    candidates: list[Sentence],
    sentences: list[Sentence],
    config: PipelineConfig,
    energy_series: list[float],
    energy_times: list[float],
    media_duration: float,
) -> tuple[list[dict], dict]:
    stage = "hook_detection"
    logger.info("Stage started: %s", stage)
    logger.info("Stage started: boundary_optimization")
    stage = "boundary_optimization"
    payloads: list[dict] = []
    improvements: list[float] = []
    improved_count = 0
    before_scores: list[float] = []
    after_scores: list[float] = []
    weak_hook_count = 0

    try:
        for candidate in candidates:
            original_scores = score_variant(
                candidate, config, energy_series, energy_times
            )
            before_scores.append(original_scores["overall"])
            if (
                original_scores["overall"] == 0.0
                and original_scores["hook"] < config.min_hook_score
            ):
                weak_hook_count += 1

            best = _pick_best_variant(
                candidate,
                sentences,
                config,
                energy_series,
                energy_times,
                media_duration,
            )

            improvement_pct = 0.0
            if original_scores["overall"] > 0:
                improvement_pct = (
                    (best["scores"]["overall"] - original_scores["overall"])
                    / original_scores["overall"]
                ) * 100
            elif best["scores"]["overall"] > 0:
                improvement_pct = 100.0

            keep_original = improvement_pct < config.improvement_threshold_pct
            chosen = candidate
            chosen_scores = original_scores
            if not keep_original:
                chosen = best["sentence"]
                chosen_scores = best["scores"]
                improved_count += 1

            after_scores.append(chosen_scores["overall"])
            improvements.append(improvement_pct)

            payloads.append(
                {
                    "start": chosen.start,
                    "end": chosen.end,
                    "text": chosen.text,
                    "scores": chosen_scores,
                    "original_start": candidate.start,
                    "original_end": candidate.end,
                    "optimized_start": best["sentence"].start,
                    "optimized_end": best["sentence"].end,
                    "original_score": original_scores["overall"],
                    "optimized_score": best["scores"]["overall"],
                    "improvement_percent": improvement_pct,
                }
            )

        metrics = _summarize_metrics(
            improvements,
            improved_count,
            len(payloads),
            before_scores,
            after_scores,
            weak_hook_count,
        )
        logger.info("Stage completed: hook_detection")
        logger.info("Stage completed: boundary_optimization")
        return payloads, metrics
    except Exception as exc:
        logger.exception("Stage failed: %s", stage)
        raise PipelineStageError(stage, exc) from exc


def _pick_best_variant(
    candidate: Sentence,
    sentences: list[Sentence],
    config: PipelineConfig,
    energy_series: list[float],
    energy_times: list[float],
    media_duration: float,
) -> dict:
    best = {
        "sentence": candidate,
        "scores": score_variant(candidate, config, energy_series, energy_times),
    }

    start_idx = _find_sentence_index(sentences, candidate.start)
    end_idx = _find_sentence_index(sentences, candidate.end)
    if start_idx is None or end_idx is None:
        return best

    start_candidates = _collect_start_boundaries(
        sentences, start_idx, config.max_sentence_shift
    )
    end_candidates = _collect_end_boundaries(
        sentences, end_idx, config.max_sentence_shift
    )

    base_hook_score = analyze_hook(
        _slice_text(candidate, candidate.start, candidate.start + config.hook_inspect_s)
    ).score
    hook_start = _find_hook_start(
        sentences,
        candidate.start,
        config.hook_recovery_window_s,
        base_hook_score,
    )
    if hook_start is not None:
        start_candidates.add(hook_start)

    punchline_end = _find_punchline_end(
        sentences, candidate.end, config.punchline_recovery_window_s
    )
    if punchline_end is not None:
        end_candidates.add(punchline_end)

    for start in start_candidates:
        for end in end_candidates:
            if end <= start:
                continue
            if start < 0 or end > media_duration:
                continue
            duration = end - start
            if duration < config.min_clip_s or duration > config.max_clip_s:
                continue
            sentence = _build_sentence_from_boundaries(sentences, start, end)
            if sentence is None:
                continue
            scores = score_variant(sentence, config, energy_series, energy_times)
            if scores["overall"] > best["scores"]["overall"]:
                best = {"sentence": sentence, "scores": scores}

    return best


def score_variant(
    sentence: Sentence,
    config: PipelineConfig,
    energy_series: list[float],
    energy_times: list[float],
) -> dict:
    hook_text = _slice_text(
        sentence, sentence.start, sentence.start + config.hook_inspect_s
    )
    hook_components = analyze_hook(hook_text)
    hook_score = hook_components.score
    if hook_score < config.min_hook_score:
        return {
            "hook": hook_score,
            "retention": 0.0,
            "completion": 0.0,
            "story": 0.0,
            "educational": hook_components.educational,
            "overall": 0.0,
        }

    retention_score = _score_retention(sentence, energy_series, energy_times, config)
    completion_score = _score_completion(sentence, config)
    story_score = _score_story(sentence.text)
    educational_score = hook_components.educational

    overall = (
        0.35 * hook_score
        + 0.25 * retention_score
        + 0.20 * completion_score
        + 0.10 * story_score
        + 0.10 * educational_score
    )
    overall = max(0.0, min(100.0, overall))

    return {
        "hook": hook_score,
        "retention": retention_score,
        "completion": completion_score,
        "story": story_score,
        "educational": educational_score,
        "overall": overall,
    }


def _score_retention(
    sentence: Sentence,
    energy_series: list[float],
    energy_times: list[float],
    config: PipelineConfig,
) -> float:
    duration = max(0.1, sentence.end - sentence.start)
    words_per_sec = len(sentence.words) / duration
    pacing_score = 100 - abs(words_per_sec - 2.8) * 20
    pacing_score = max(0.0, min(100.0, pacing_score))
    energy_score = _energy_variance_score(
        energy_series, energy_times, sentence.start, sentence.end
    )
    filler_ratio = _filler_ratio(sentence.text)
    filler_penalty = 0.0
    if filler_ratio > config.filler_ratio_threshold:
        filler_penalty = (
            (filler_ratio - config.filler_ratio_threshold)
            * config.filler_penalty_weight
            * 100
        )
    score = 0.6 * pacing_score + 0.4 * energy_score - filler_penalty
    return max(0.0, min(100.0, score))


def _score_completion(sentence: Sentence, config: PipelineConfig) -> float:
    end_text = _slice_text(
        sentence,
        max(sentence.start, sentence.end - config.ending_inspect_s),
        sentence.end,
    ).lower()
    cues = (
        "in summary",
        "the point is",
        "that's why",
        "bottom line",
        "so",
        "therefore",
        "the result",
        "what we learned",
    )
    cue_hits = sum(1 for cue in cues if cue in end_text)
    punctuation_bonus = 10 if end_text.strip().endswith((".", "!")) else 0
    score = 50 + cue_hits * 12 + punctuation_bonus
    if end_text.strip().endswith((",", "and", "but")):
        score -= 15
    return max(0.0, min(100.0, score))


def _score_story(text: str) -> float:
    lower = text.lower()
    hits = sum(1 for cue in STORY_CUES if cue.lower() in lower)
    score = 40 + hits * 8
    return max(0.0, min(100.0, score))


def _slice_text(sentence: Sentence, start: float, end: float) -> str:
    words = [w.text for w in sentence.words if w.start < end and w.end > start]
    return " ".join(words).strip()


def _filler_ratio(text: str) -> float:
    lower = text.lower()
    total_words = max(1, len(lower.split()))
    filler_hits = 0
    for phrase in FILLER_PHRASES:
        filler_hits += lower.count(phrase)
    return filler_hits / total_words


def _find_sentence_index(sentences: list[Sentence], timestamp: float) -> int | None:
    for idx, sentence in enumerate(sentences):
        if sentence.start <= timestamp <= sentence.end:
            return idx
    if timestamp < sentences[0].start:
        return 0
    if timestamp > sentences[-1].end:
        return len(sentences) - 1
    return None


def _collect_start_boundaries(
    sentences: list[Sentence], start_idx: int, max_shift: int
) -> set[float]:
    boundaries: set[float] = set()
    for shift in range(0, max_shift + 1):
        idx = start_idx - shift
        if idx >= 0:
            boundaries.add(sentences[idx].start)
    return boundaries


def _collect_end_boundaries(
    sentences: list[Sentence], end_idx: int, max_shift: int
) -> set[float]:
    boundaries: set[float] = set()
    for shift in range(0, max_shift + 1):
        idx = end_idx + shift
        if idx < len(sentences):
            boundaries.add(sentences[idx].end)
    return boundaries


def _find_hook_start(
    sentences: list[Sentence],
    start_time: float,
    window_s: float,
    base_hook_score: float,
) -> float | None:
    if window_s <= 0:
        return None
    window_start = max(0.0, start_time - window_s)
    best_score = base_hook_score
    best_start: float | None = None
    for sentence in sentences:
        if sentence.end < window_start or sentence.start >= start_time:
            continue
        text = sentence.text.lower()
        if not any(cue in text for cue in HOOK_CUES):
            continue
        hook_score = analyze_hook(sentence.text).score
        if hook_score > best_score:
            best_score = hook_score
            best_start = sentence.start
    return best_start


def _find_punchline_end(
    sentences: list[Sentence], end_time: float, window_s: float
) -> float | None:
    if window_s <= 0:
        return None
    window_end = end_time + window_s
    best_end: float | None = None
    for sentence in sentences:
        if sentence.start <= end_time or sentence.end > window_end:
            continue
        text = sentence.text.lower()
        if any(cue in text for cue in PUNCHLINE_CUES):
            best_end = sentence.end
            break
    return best_end


def _build_sentence_from_boundaries(
    sentences: list[Sentence], start: float, end: float
) -> Sentence | None:
    start_idx = None
    end_idx = None
    for idx, sentence in enumerate(sentences):
        if sentence.start == start:
            start_idx = idx
        if sentence.end == end:
            end_idx = idx
    if start_idx is None or end_idx is None or end_idx < start_idx:
        return None
    slice_sentences = sentences[start_idx : end_idx + 1]
    words = [word for sentence in slice_sentences for word in sentence.words]
    text = " ".join(sentence.text for sentence in slice_sentences).strip()
    if not text:
        return None
    return Sentence(start=start, end=end, text=text, words=tuple(words))


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
    scaled = min(100.0, (variance**0.5) * 3000)
    return max(0.0, scaled)


def _summarize_metrics(
    improvements: list[float],
    improved_count: int,
    total: int,
    before_scores: list[float],
    after_scores: list[float],
    weak_hook_count: int,
) -> dict:
    if not improvements:
        return {
            "average_before": 0.0,
            "average_after": 0.0,
            "average_improvement_pct": 0.0,
            "best_improvement_pct": 0.0,
            "worst_improvement_pct": 0.0,
            "improved_count": 0,
            "improved_rate": 0.0,
            "weak_hook_count": 0,
        }
    avg_improvement = sum(improvements) / len(improvements)
    return {
        "average_before": sum(before_scores) / len(before_scores)
        if before_scores
        else 0.0,
        "average_after": sum(after_scores) / len(after_scores) if after_scores else 0.0,
        "average_improvement_pct": avg_improvement,
        "best_improvement_pct": max(improvements),
        "worst_improvement_pct": min(improvements),
        "improved_count": improved_count,
        "improved_rate": improved_count / total if total else 0.0,
        "weak_hook_count": weak_hook_count,
    }
