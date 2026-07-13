from __future__ import annotations

from dataclasses import dataclass

from .crop_planner import SpeakerCropPlan
from .phrase_chunker import CaptionChunk
from .style_presets import StylePreset


@dataclass(frozen=True)
class CaptionPlacement:
    chunk_index: int
    anchor: str
    x: int
    y: int
    font_size: int
    safe_margin_y: int


def plan_caption_layout(
    chunks: list[CaptionChunk],
    preset: StylePreset,
    crop_plan: SpeakerCropPlan,
    output_width: int = 1080,
    output_height: int = 1920,
) -> list[CaptionPlacement]:
    placements: list[CaptionPlacement] = []
    for chunk in chunks:
        speaker_y_ratio = _speaker_vertical_ratio(crop_plan, chunk)
        anchor = "bottom"
        safe_margin_y = preset.margin_v
        y = output_height - safe_margin_y
        if speaker_y_ratio >= 0.54:
            anchor = "top"
            safe_margin_y = max(110, preset.margin_v - 10)
            y = safe_margin_y + 60
        font_size = _dynamic_font_size(chunk, preset)
        placements.append(
            CaptionPlacement(
                chunk_index=chunk.chunk_index,
                anchor=anchor,
                x=output_width // 2,
                y=y,
                font_size=font_size,
                safe_margin_y=safe_margin_y,
            )
        )
    return placements


def _speaker_vertical_ratio(crop_plan: SpeakerCropPlan, chunk: CaptionChunk) -> float:
    if crop_plan.selected_speaker_id is None:
        return 0.5
    midpoint = (chunk.start + chunk.end) / 2
    for track in crop_plan.tracked_faces:
        if track.get("face_id") != crop_plan.selected_speaker_id:
            continue
        samples = track.get("samples", [])
        if not samples:
            return 0.5
        closest = min(samples, key=lambda sample: abs(sample["time"] - midpoint))
        bbox = closest["bbox"]
        return (bbox["y"] + bbox["height"] / 2) / max(crop_plan.source_height, 1)
    return 0.5


def _dynamic_font_size(chunk: CaptionChunk, preset: StylePreset) -> int:
    longest_line = max((len(line) for line in chunk.lines), default=0)
    adjustment = max(0, longest_line - 18) * 1.5
    size = int(round(preset.base_font_size - adjustment))
    return max(preset.min_font_size, min(preset.max_font_size, size))
