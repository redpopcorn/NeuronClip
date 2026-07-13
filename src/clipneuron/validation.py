from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from .config import PipelineConfig
from .segmenter import Sentence, TranscriptWord


@dataclass(frozen=True)
class ValidationResult:
    candidates: list[Sentence]
    warnings: list[str]


def ensure_dependency(name: str) -> None:
    override = None
    if name == "ffmpeg":
        override = os.environ.get("FFMPEG_PATH")
    if name == "ffprobe":
        override = os.environ.get("FFPROBE_PATH")
    if override:
        override_path = Path(override)
        if override_path.is_dir():
            candidate = override_path / f"{name}.exe"
            if candidate.exists():
                return
        elif override_path.exists():
            return
        raise RuntimeError(f"{name} override path is invalid: {override_path}")
    common = Path("C:/ffmpeg/bin") / f"{name}.exe"
    if common.exists():
        return
    if shutil.which(name) is None:
        raise RuntimeError(f"Required dependency '{name}' is not available in PATH.")


def validate_config(config: PipelineConfig) -> None:
    if config.min_clip_s <= 0 or config.max_clip_s <= 0:
        raise ValueError("Clip duration bounds must be positive.")
    if config.min_clip_s >= config.max_clip_s:
        raise ValueError("min_clip_s must be less than max_clip_s.")
    if config.target_candidates <= 0:
        raise ValueError("target_candidates must be positive.")
    if config.sample_rate <= 0:
        raise ValueError("sample_rate must be positive.")
    if config.crop_aspect_ratio <= 0:
        raise ValueError("crop_aspect_ratio must be positive.")
    if config.face_detection_interval <= 0:
        raise ValueError("face_detection_interval must be positive.")
    if config.smoothing_factor < 0 or config.smoothing_factor > 1:
        raise ValueError("smoothing_factor must be between 0 and 1.")
    if config.max_crop_velocity <= 0:
        raise ValueError("max_crop_velocity must be positive.")
    if config.minimum_face_size <= 0:
        raise ValueError("minimum_face_size must be positive.")
    if config.hook_window_s <= 0:
        raise ValueError("hook_window_s must be positive.")
    if config.max_sentence_shift < 0:
        raise ValueError("max_sentence_shift must be non-negative.")
    if config.hook_inspect_s <= 0 or config.ending_inspect_s <= 0:
        raise ValueError("inspection windows must be positive.")
    if config.hook_recovery_window_s < 0 or config.punchline_recovery_window_s < 0:
        raise ValueError("recovery windows must be non-negative.")
    if config.filler_ratio_threshold < 0 or config.filler_ratio_threshold > 1:
        raise ValueError("filler_ratio_threshold must be between 0 and 1.")
    if config.filler_penalty_weight < 0:
        raise ValueError("filler_penalty_weight must be non-negative.")
    if config.min_hook_score < 0 or config.min_hook_score > 100:
        raise ValueError("min_hook_score must be between 0 and 100.")
    if config.improvement_threshold_pct < 0:
        raise ValueError("improvement_threshold_pct must be non-negative.")
    if not (0 < config.improvement_target_rate <= 1):
        raise ValueError("improvement_target_rate must be in (0, 1].")
    if str(config.caption_preset).lower() not in {
        "classic",
        "creator",
        "mrbeast",
        "podcast",
        "minimal",
        "documentary",
        "gaming",
    }:
        raise ValueError(
            "caption_preset must be one of classic, creator, mrbeast, podcast, minimal, documentary, gaming."
        )


def validate_input_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"Input file is empty: {path}")


def validate_transcript(words: list[TranscriptWord]) -> list[TranscriptWord]:
    if not words:
        raise ValueError("Transcript is empty. No words were returned by ASR.")
    cleaned: list[TranscriptWord] = []
    for word in words:
        if word.start is None or word.end is None:
            continue
        if word.end <= word.start or word.start < 0:
            continue
        if not word.text:
            continue
        cleaned.append(word)
    if not cleaned:
        raise ValueError("Transcript has no valid word timestamps after validation.")
    return cleaned


def validate_candidates(
    candidates: list[Sentence],
    min_s: float,
    max_s: float,
    media_duration: float,
) -> ValidationResult:
    warnings: list[str] = []
    cleaned: list[Sentence] = []
    for candidate in candidates:
        if candidate.start < 0 or candidate.end < 0:
            warnings.append("Dropped candidate with negative timestamps.")
            continue
        if candidate.end <= candidate.start:
            warnings.append("Dropped candidate with non-positive duration.")
            continue
        if candidate.end > media_duration:
            warnings.append("Dropped candidate beyond media duration.")
            continue
        duration = candidate.end - candidate.start
        if duration < min_s or duration > max_s:
            warnings.append("Dropped candidate outside configured duration bounds.")
            continue
        cleaned.append(candidate)
    if not cleaned:
        raise ValueError("No valid clip candidates after validation.")
    return ValidationResult(candidates=cleaned, warnings=warnings)


def select_non_overlapping(candidates: list[dict]) -> list[dict]:
    selected: list[dict] = []
    for candidate in candidates:
        start = float(candidate["start"])
        end = float(candidate["end"])
        overlap = any(start < s["end"] and end > s["start"] for s in selected)
        if not overlap:
            selected.append(candidate)
    return selected
