from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import PipelineConfig
from .phrase_chunker import CaptionChunk
from .segmenter import TranscriptWord
from .typography_engine import TypographyPlan

MUSIC_CATEGORIES = {
    "upbeat": {"win", "growth", "viral", "amazing", "excited", "success"},
    "tension": {"mistake", "wrong", "secret", "shocking", "fear", "problem"},
    "podcast": {"podcast", "conversation", "interview", "founder", "story"},
    "inspirational": {"lesson", "journey", "build", "dream", "future", "believe"},
    "gaming": {"game", "level", "boss", "win", "clutch"},
    "chill": set(),
}

SFX_CUES = {
    "whoosh": {"fast", "quick", "suddenly", "instantly", "rush"},
    "pop": {"new", "launch", "reveal", "show", "open"},
    "ding": {"tip", "hack", "win", "correct", "right"},
    "impact": {"shocking", "crazy", "massive", "huge", "important"},
    "boom": {"boom", "exploded", "viral", "biggest", "money"},
}


@dataclass(frozen=True)
class AudioDirection:
    music: dict
    sound_effects: list[dict]
    fade_in: float
    fade_out: float


def build_audio_direction(
    clip_index: int,
    words: list[TranscriptWord],
    chunks: list[CaptionChunk],
    typography: list[TypographyPlan],
    assets_root: Path,
    config: PipelineConfig | None = None,
) -> AudioDirection:
    category = "chill"
    if config is not None and config.music_category:
        category = config.music_category
    else:
        text = " ".join(word.text for word in words).lower()
        best_hits = -1
        for name, cues in MUSIC_CATEGORIES.items():
            hits = sum(1 for cue in cues if cue in text)
            if hits > best_hits:
                best_hits = hits
                category = name

    music_enabled = config.music_enabled if config is not None else True
    music_asset = assets_root / "music" / f"{category}.mp3" if music_enabled else None
    
    music_volume_db = config.music_volume_db if config is not None else -22.0
    ducking_ratio = config.ducking_ratio if config is not None else 8.0
    ducking_threshold = config.ducking_threshold if config is not None else 0.03

    sfx_events = _build_sound_effects(words, chunks, typography)
    return AudioDirection(
        music={
            "clip_index": clip_index,
            "category": category,
            "asset": str(music_asset) if (music_asset and music_asset.exists()) else None,
            "ducking": {
                "enabled": music_enabled,
                "speech_target_db": -4,
                "music_target_db": music_volume_db,
                "ratio": ducking_ratio,
                "threshold": ducking_threshold,
            },
        },
        sound_effects=sfx_events,
        fade_in=0.35,
        fade_out=0.45,
    )


def _build_sound_effects(
    words: list[TranscriptWord],
    chunks: list[CaptionChunk],
    typography: list[TypographyPlan],
) -> list[dict]:
    events: list[dict] = []
    for word in words:
        normalized = "".join(ch for ch in word.text.lower() if ch.isalnum())
        if not normalized:
            continue
        for effect, cues in SFX_CUES.items():
            if normalized in cues:
                events.append(
                    {"type": effect, "time": round(word.start, 2), "trigger": word.text}
                )
                break
    for chunk, plan in zip(chunks, typography, strict=False):
        for highlighted in plan.highlighted_words:
            if highlighted.kind in {"money", "number"}:
                events.append(
                    {
                        "type": "pop",
                        "time": round(chunk.start, 2),
                        "trigger": highlighted.word,
                    }
                )
    return events
