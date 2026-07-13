from __future__ import annotations

import logging
import os
import re
from dataclasses import asdict
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

from .config import PipelineConfig
from .errors import PipelineStageError
from .io_utils import (
    enhance_audio_for_transcription,
    extract_audio,
    get_media_duration,
    write_json,
)
from .optimizer import optimize_candidates
from .segmenter import TranscriptWord, generate_candidates, words_to_sentences
from .validation import (
    ensure_dependency,
    select_non_overlapping,
    validate_candidates,
    validate_config,
    validate_input_file,
    validate_transcript,
)

logger = logging.getLogger("clipneuron.pipeline")

TRANSCRIPT_BOILERPLATE_PHRASES = (
    "transcribed by",
    "thanks for watching",
    "learn more at",
    "subscribe for more",
    "visit our website",
)


def run_pipeline(
    input_path: Path, output_path: Path, config: PipelineConfig
) -> tuple[dict, list[TranscriptWord]]:
    ensure_dependency("ffmpeg")
    ensure_dependency("ffprobe")
    validate_config(config)
    validate_input_file(input_path)

    audio_path = output_path.with_suffix(".wav")
    extract_audio(input_path, audio_path, config.sample_rate)

    stage = "transcription"
    try:
        logger.info("Stage started: %s", stage)
        words = validate_transcript(transcribe_words(audio_path, config))
        write_json(
            output_path.with_name("transcript.json"), _build_transcript_payload(words)
        )
        logger.info("Stage completed: %s", stage)
    except Exception as exc:
        logger.exception("Stage failed: %s", stage)
        raise PipelineStageError(stage, exc) from exc
    sentences = words_to_sentences(words)
    if not sentences:
        raise ValueError("Transcript yielded no sentences for candidate generation.")
    stage = "candidate_generation"
    try:
        logger.info("Stage started: %s", stage)
        candidates = generate_candidates(
            sentences, config.min_clip_s, config.max_clip_s, config.target_candidates
        )
        logger.info("Stage completed: %s", stage)
    except Exception as exc:
        logger.exception("Stage failed: %s", stage)
        raise PipelineStageError(stage, exc) from exc

    media_duration = get_media_duration(input_path)
    if media_duration <= 0:
        raise ValueError("Media duration is zero or invalid.")
    validation = validate_candidates(
        candidates, config.min_clip_s, config.max_clip_s, media_duration
    )

    stage = "energy_analysis"
    try:
        logger.info("Stage started: %s", stage)
        energy_series, energy_times = compute_energy_series(audio_path, config)
        logger.info("Stage completed: %s", stage)
    except Exception as exc:
        logger.exception("Stage failed: %s", stage)
        raise PipelineStageError(stage, exc) from exc

    stage = "boundary_optimization"
    try:
        logger.info("Stage started: %s", stage)
        clip_payloads, optimization_metrics = optimize_candidates(
            validation.candidates,
            sentences,
            config,
            energy_series,
            energy_times,
            media_duration,
        )
        logger.info("Stage completed: %s", stage)
    except Exception as exc:
        logger.exception("Stage failed: %s", stage)
        raise PipelineStageError(stage, exc) from exc

    if optimization_metrics["improved_rate"] < config.improvement_target_rate:
        validation.warnings.append(
            "Optimization improvement rate below target. Consider adjusting recovery windows or hook thresholds."
        )
        if optimization_metrics.get("weak_hook_count", 0) > 0:
            validation.warnings.append(
                "Many candidates failed hook threshold; consider lowering min_hook_score or improving hook detection."
            )

    stage = "ranking"
    try:
        logger.info("Stage started: %s", stage)
        clip_payloads.sort(key=lambda item: item["scores"]["overall"], reverse=True)
        clip_payloads = select_non_overlapping(clip_payloads)
        logger.info("Stage completed: %s", stage)
    except Exception as exc:
        logger.exception("Stage failed: %s", stage)
        raise PipelineStageError(stage, exc) from exc

    if not clip_payloads:
        raise ValueError("No non-overlapping clips could be selected.")

    payload = {
        "input": str(input_path),
        "config": asdict(config),
        "warnings": validation.warnings,
        "optimization_metrics": optimization_metrics,
        "clips": clip_payloads,
    }
    write_json(output_path, payload)

    optimization_report_path = output_path.with_name("optimization_report.json")
    write_json(
        optimization_report_path,
        {
            "input": str(input_path),
            "optimization_metrics": optimization_metrics,
            "clip_count": len(clip_payloads),
        },
    )
    return payload, words


def transcribe_words(audio_path: Path, config: PipelineConfig) -> list[TranscriptWord]:
    audio_duration = float(sf.info(str(audio_path)).duration or 0.0)
    attempts: list[tuple[float, list[TranscriptWord], dict]] = []

    primary_words = _run_transcription_attempts(audio_path, config.model_size, config)
    primary_score, primary_audit = _score_transcript_quality(
        primary_words, audio_duration
    )
    primary_score, primary_audit = _apply_candidate_viability(
        primary_score, primary_audit, primary_words, config
    )
    attempts.append((primary_score, primary_words, primary_audit))

    best_score, best_words, best_audit = max(attempts, key=lambda item: item[0])

    if best_audit["likely_low_quality"]:
        enhanced_path = audio_path.with_name(f"{audio_path.stem}_enhanced.wav")
        try:
            enhance_audio_for_transcription(
                audio_path, enhanced_path, config.sample_rate
            )
            enhanced_words = _run_transcription_attempts(
                enhanced_path, config.model_size, config
            )
            enhanced_score, enhanced_audit = _score_transcript_quality(
                enhanced_words, audio_duration
            )
            enhanced_score, enhanced_audit = _apply_candidate_viability(
                enhanced_score, enhanced_audit, enhanced_words, config
            )
            attempts.append((enhanced_score, enhanced_words, enhanced_audit))
        except Exception:
            logger.exception("Enhanced audio transcription retry failed")
        finally:
            enhanced_path.unlink(missing_ok=True)

    best_score, best_words, best_audit = max(attempts, key=lambda item: item[0])

    fallback_model_size = getattr(config, "fallback_model_size", None)
    if (
        best_audit["likely_low_quality"]
        and fallback_model_size
        and fallback_model_size != config.model_size
    ):
        logger.info(
            "Low-quality transcript detected; retrying with %s model",
            fallback_model_size,
        )
        stronger_words = _run_transcription_attempts(
            audio_path, str(fallback_model_size), config
        )
        stronger_score, stronger_audit = _score_transcript_quality(
            stronger_words, audio_duration
        )
        stronger_score, stronger_audit = _apply_candidate_viability(
            stronger_score, stronger_audit, stronger_words, config
        )
        attempts.append((stronger_score, stronger_words, stronger_audit))

    best_score, best_words, best_audit = max(attempts, key=lambda item: item[0])
    logger.info(
        "Selected transcript quality score=%.2f words=%s flags=%s",
        best_score,
        len(best_words),
        best_audit.get("flags", []),
    )
    return best_words


def _run_transcription_attempts(
    audio_path: Path, model_size: str, config: PipelineConfig
) -> list[TranscriptWord]:
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=4)
    attempt_specs: list[dict[str, str | bool | None]] = [
        {"language": config.language, "vad_filter": True},
        {"language": config.language, "vad_filter": False},
    ]
    if config.language is None:
        attempt_specs.extend(
            [
                {"language": "hi", "vad_filter": False},
                {"language": "en", "vad_filter": False},
            ]
        )

    best_words: list[TranscriptWord] = []
    best_score = float("-inf")
    seen_attempts: set[tuple[str | None, bool]] = set()
    audio_duration = float(sf.info(str(audio_path)).duration or 0.0)
    for spec in attempt_specs:
        language = spec["language"]
        vad_filter = bool(spec["vad_filter"])
        attempt_key = (language if isinstance(language, str) else None, vad_filter)
        if attempt_key in seen_attempts:
            continue
        seen_attempts.add(attempt_key)
        logger.info(
            "Transcription attempt: model=%s language=%s vad_filter=%s",
            model_size,
            language or "auto",
            vad_filter,
        )
        prompt = "This audio may contain Hindi, Hinglish, and English mixed together. Transcribe naturally and preserve mixed-language words."
        if config.task == "translate":
            prompt = "Translate the audio spoken in Hindi, Urdu, or Hinglish into English text."

        segments, _ = model.transcribe(
            str(audio_path),
            language=language if isinstance(language, str) else None,
            task=config.task,
            word_timestamps=True,
            vad_filter=vad_filter,
            beam_size=5,
            best_of=5,
            condition_on_previous_text=False,
            initial_prompt=prompt,
        )
        words = _collect_transcript_words(segments)
        score, audit = _score_transcript_quality(words, audio_duration)
        score, audit = _apply_candidate_viability(score, audit, words, config)
        if score > best_score:
            best_score = score
            best_words = words
    return best_words


def _collect_transcript_words(segments) -> list[TranscriptWord]:
    words: list[TranscriptWord] = []
    for segment in segments:
        for word in segment.words or []:
            token = word.word.strip()
            if not token:
                continue
            start = float(word.start)
            end = float(word.end)
            if start < 0 or end <= start:
                continue
            words.append(
                TranscriptWord(
                    start=start,
                    end=end,
                    text=token,
                )
            )
    return words


def _score_transcript_quality(
    words: list[TranscriptWord], audio_duration: float | None = None
) -> tuple[float, dict]:
    tokens = [word.text.strip() for word in words if word.text and word.text.strip()]
    lowered = [_normalize_token(token) for token in tokens]
    lowered = [token for token in lowered if token]
    unique_ratio = (len(set(lowered)) / len(lowered)) if lowered else 0.0
    repeated_words = sorted({token for token in lowered if lowered.count(token) > 1})
    hinglish_signal_count = sum(
        1
        for token in lowered
        if token in {"hai", "nahi", "kya", "kyun", "kaise", "haan", "acha"}
    )
    website_token_count = sum(
        1
        for token in lowered
        if token in {"www", "http", "https", "com", "org", "net"}
        or token.startswith("www")
        or token.endswith(("com", "org", "net"))
    )
    joined = " ".join(lowered)
    boilerplate_hits = sum(
        1 for phrase in TRANSCRIPT_BOILERPLATE_PHRASES if phrase in joined
    )
    valid_words = [
        word
        for word in words
        if word.end is not None and word.start is not None and word.end > word.start
    ]
    spoken_duration = sum(max(0.0, word.end - word.start) for word in valid_words)
    coverage_ratio = (spoken_duration / audio_duration) if audio_duration else 0.0

    flags: list[str] = []
    if len(tokens) < 5:
        flags.append("very_short_transcript")
    if unique_ratio < 0.45:
        flags.append("low_unique_ratio")
    if repeated_words:
        flags.append("repeated_words_detected")
    if website_token_count >= 2:
        flags.append("website_text_detected")
    if boilerplate_hits > 0:
        flags.append("boilerplate_phrase_detected")
    if audio_duration and coverage_ratio < 0.12:
        flags.append("low_speech_coverage")

    score = (
        len(valid_words) * 4.0
        + unique_ratio * 20.0
        + min(coverage_ratio, 1.0) * 30.0
        + min(float(hinglish_signal_count), 4.0) * 2.0
        - len(repeated_words) * 3.0
        - website_token_count * 6.0
        - boilerplate_hits * 15.0
    )
    return score, {
        "unique_ratio": unique_ratio,
        "hinglish_signal_count": hinglish_signal_count,
        "repeated_words": repeated_words,
        "flags": flags,
        "likely_low_quality": bool(flags),
    }


def _apply_candidate_viability(
    score: float, audit: dict, words: list[TranscriptWord], config: PipelineConfig
) -> tuple[float, dict]:
    sentences = words_to_sentences(words)
    has_viable_candidates = bool(
        generate_candidates(
            sentences,
            config.min_clip_s,
            config.max_clip_s,
            config.target_candidates,
        )
    )
    updated_audit = {
        **audit,
        "has_viable_candidates": has_viable_candidates,
        "flags": list(audit.get("flags", [])),
    }
    if has_viable_candidates:
        return score + 40.0, updated_audit
    updated_audit["flags"].append("no_viable_clip_candidates")
    updated_audit["likely_low_quality"] = True
    return score - 40.0, updated_audit


def _normalize_token(token: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", token.lower())


def _build_transcript_payload(words: list[TranscriptWord]) -> dict:
    quality_score, audit = _score_transcript_quality(words)
    return {
        "word_count": len(words),
        "unique_ratio": audit["unique_ratio"],
        "hinglish_signal_count": audit["hinglish_signal_count"],
        "quality": {
            "score": quality_score,
            "likely_low_quality": audit["likely_low_quality"],
            "flags": audit["flags"],
            "repeated_words": audit["repeated_words"],
            "has_viable_candidates": audit.get("has_viable_candidates", False),
        },
        "words": [
            {"start": word.start, "end": word.end, "text": word.text} for word in words
        ],
    }


def compute_energy_series(
    audio_path: Path, config: PipelineConfig
) -> tuple[list[float], list[float]]:
    audio, sr = sf.read(str(audio_path))
    if audio.size == 0:
        raise ValueError("Extracted audio is empty.")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != config.sample_rate:
        raise ValueError("Audio sample rate mismatch. Expected 16k after ffmpeg.")
    window = int(config.energy_window_s * sr)
    if window <= 0:
        window = 1
    energies = []
    times = []
    for i in range(0, len(audio), window):
        frame = audio[i : i + window]
        if frame.size == 0:
            continue
        rms = float(np.sqrt(np.mean(frame**2)))
        energies.append(rms)
        times.append(i / sr)
    return energies, times
