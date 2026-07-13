from __future__ import annotations

import logging
import os
import re
import subprocess
from dataclasses import asdict
from pathlib import Path

from .animation_engine import write_ass_subtitles
from .audio_director import AudioDirection, build_audio_direction
from .caption_layout import CaptionPlacement, plan_caption_layout
from .config import PipelineConfig
from .crop_planner import SpeakerCropPlan, build_static_crop_filter, plan_speaker_crop
from .io_utils import ensure_parent, get_video_dimensions, write_json
from .phrase_chunker import CaptionChunk, chunk_transcript
from .segmenter import TranscriptWord
from .style_presets import StylePreset, resolve_style_preset
from .transcript_repair import RepairedTranscript, repair_transcript
from .typography_engine import TypographyPlan, build_typography_plan

logger = logging.getLogger("clipneuron.render")

CAPTION_BLOCKLIST = {
    "transcribed",
    "subtitle",
    "subtitles",
    "caption",
    "captions",
    "eso",
    "www",
    "http",
    "https",
    "com",
    "org",
    "net",
}


class PlannedClipRender(dict):
    """Small typed dict-like container for planned clip rendering context."""


def render_clips(
    input_path: Path,
    output_dir: Path,
    clips: list[dict],
    words: list[TranscriptWord],
    config: PipelineConfig | None,
    top: int | None = None,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = config or PipelineConfig()
    preset = resolve_style_preset(getattr(cfg, "caption_preset", "creator"))
    assets_root = Path(__file__).resolve().parents[2] / "assets"
    targets = clips[:top] if top else clips

    planned_clips = [
        _plan_clip_render(
            input_path=input_path,
            output_dir=output_dir,
            clip=clip,
            words=words,
            config=cfg,
            preset=preset,
            clip_index=index,
            assets_root=assets_root,
        )
        for index, clip in enumerate(targets, start=1)
    ]

    plans_dir = output_dir.parent if output_dir.name == "clips" else output_dir
    render_plan_payload = {
        "clips": [planned["render_plan"] for planned in planned_clips]
    }
    write_json(plans_dir / "render_plan.json", render_plan_payload)
    write_json(
        plans_dir / "caption_plan.json",
        {"clips": [planned["caption_plan"] for planned in planned_clips]},
    )
    write_json(
        plans_dir / "subtitle_plan.json",
        {"clips": [planned["subtitle_plan"] for planned in planned_clips]},
    )
    write_json(
        plans_dir / "music_plan.json",
        {"clips": [planned["music_plan"] for planned in planned_clips]},
    )
    write_json(
        plans_dir / "sfx_plan.json",
        {"clips": [planned["sfx_plan"] for planned in planned_clips]},
    )

    rendered_paths: list[Path] = []
    for planned in planned_clips:
        rendered_paths.append(_render_planned_clip(input_path, planned))

    render_plan_path = plans_dir / "render_plan.json"
    for planned in planned_clips:
        clip = planned["clip"]
        clip["render_plan_path"] = str(render_plan_path)
    return rendered_paths


def _plan_clip_render(
    input_path: Path,
    output_dir: Path,
    clip: dict,
    words: list[TranscriptWord],
    config: PipelineConfig,
    preset: StylePreset,
    clip_index: int,
    assets_root: Path,
) -> PlannedClipRender:
    start = float(clip["start"])
    end = float(clip["end"])
    if end <= start:
        raise ValueError("Clip has non-positive duration; cannot render.")

    score = clip.get("scores", {}).get("overall", 0)
    output_path = output_dir / f"clip_{clip_index:02d}_{int(score)}.mp4"
    ass_path = output_dir / f"clip_{clip_index:02d}.ass"
    crop_path = output_dir / f"clip_{clip_index:02d}_crop.json"

    clip_words = [word for word in words if word.start < end and word.end > start]
    repaired = repair_transcript(_sanitize_caption_words(clip_words))
    chunks = chunk_transcript(repaired.words, start, end)

    try:
        crop_plan = plan_speaker_crop(input_path, start, end, config)
    except Exception:
        logger.exception("Speaker crop planning failed for clip %s", clip_index)
        width, height = get_video_dimensions(input_path)
        crop_filter = build_static_crop_filter(width, height, config.crop_aspect_ratio)
        crop_plan = SpeakerCropPlan(
            source_width=width,
            source_height=height,
            crop_width=int(round(height * config.crop_aspect_ratio))
            if width / max(height, 1) > config.crop_aspect_ratio
            else width,
            crop_height=height
            if width / max(height, 1) > config.crop_aspect_ratio
            else int(round(width / config.crop_aspect_ratio)),
            selected_speaker_id=None,
            tracked_faces=[],
            crop_coordinates=[
                {"time": 0.0, "x": 0, "y": 0, "width": width, "height": height}
            ],
            crop_filter=crop_filter,
        )

    placements = plan_caption_layout(chunks, preset, crop_plan)
    typography = build_typography_plan(chunks)
    audio_direction = build_audio_direction(
        clip_index=clip_index,
        words=clip_words,
        chunks=chunks,
        typography=typography,
        assets_root=assets_root,
        config=config,
    )
    zoom_events = _build_zoom_events(chunks, typography, preset)
    animation_timing = _build_animation_timing(chunks, preset, start)

    write_json(
        crop_path,
        {
            "clip_index": clip_index,
            "clip_start": start,
            "clip_end": end,
            "selected_speaker_id": crop_plan.selected_speaker_id,
            "tracked_faces": crop_plan.tracked_faces,
            "crop_coordinates": crop_plan.crop_coordinates,
            "crop_filter": crop_plan.crop_filter,
        },
    )

    clip["tracked_faces"] = crop_plan.tracked_faces
    clip["selected_speaker_id"] = crop_plan.selected_speaker_id
    clip["crop_path"] = str(crop_path)
    clip["crop_coordinates"] = crop_plan.crop_coordinates

    suppression_reason = None
    if clip_words and not chunks:
        suppression_reason = "caption_suppressed_after_transcript_repair"

    render_plan = {
        "clip_index": clip_index,
        "preset": preset.name,
        "start": start,
        "end": end,
        "caption_chunks": [_serialize_chunk(chunk) for chunk in chunks],
        "highlighted_words": _serialize_highlighted_words(chunks, typography),
        "caption_positions": [_serialize_placement(item) for item in placements],
        "camera_moves": crop_plan.crop_coordinates,
        "zoom_events": zoom_events,
        "music": {
            **audio_direction.music,
            "fade_in": audio_direction.fade_in,
            "fade_out": audio_direction.fade_out,
        },
        "sound_effects": audio_direction.sound_effects,
        "animation_timing": animation_timing,
        "transcript_repair": {
            "removed_fillers": repaired.report.removed_fillers,
            "merged_words": repaired.report.merged_words,
            "punctuation_restorations": repaired.report.punctuation_restorations,
        },
        "tracked_faces": crop_plan.tracked_faces,
        "selected_speaker_id": crop_plan.selected_speaker_id,
        "crop_path": str(crop_path),
        "crop_coordinates": crop_plan.crop_coordinates,
    }
    if suppression_reason:
        render_plan["suppression_reason"] = suppression_reason

    caption_plan = {
        "clip_index": clip_index,
        "preset": preset.name,
        "start": start,
        "end": end,
        "segments": [_serialize_chunk(chunk) for chunk in chunks],
        "highlighted_words": render_plan["highlighted_words"],
        "caption_positions": render_plan["caption_positions"],
    }
    if suppression_reason:
        caption_plan["suppression_reason"] = suppression_reason

    subtitle_plan = {
        "clip_index": clip_index,
        "preset": preset.name,
        "start": start,
        "end": end,
        "segments": [_serialize_chunk(chunk) for chunk in chunks],
        "animation_timing": animation_timing,
    }
    if suppression_reason:
        subtitle_plan["suppression_reason"] = suppression_reason

    return PlannedClipRender(
        clip=clip,
        output_path=output_path,
        ass_path=ass_path,
        clip_start=start,
        clip_end=end,
        crop_plan=crop_plan,
        chunks=chunks,
        placements=placements,
        typography=typography,
        preset=preset,
        audio_direction=audio_direction,
        render_plan=render_plan,
        caption_plan=caption_plan,
        subtitle_plan=subtitle_plan,
        music_plan={
            **audio_direction.music,
            "fade_in": audio_direction.fade_in,
            "fade_out": audio_direction.fade_out,
        },
        sfx_plan={
            "clip_index": clip_index,
            "start": start,
            "end": end,
            "events": audio_direction.sound_effects,
        },
        config=config,
    )


def _render_planned_clip(input_path: Path, planned: PlannedClipRender) -> Path:
    chunks: list[CaptionChunk] = planned["chunks"]
    if chunks:
        write_ass_subtitles(
            ass_path=planned["ass_path"],
            chunks=chunks,
            placements=planned["placements"],
            typography=planned["typography"],
            preset=planned["preset"],
            clip_start=planned["clip_start"],
        )

    config = planned.get("config")
    crop_enabled = config.crop_enabled if config is not None else True
    if crop_enabled:
        filter_chain = f"{planned['crop_plan'].crop_filter},scale=1080:1920"
    else:
        filter_chain = "scale=w='min(iw,1920)':h=-2"

    if planned["ass_path"].exists():
        filter_chain = (
            f"{filter_chain},ass='{_escape_subtitles_path(planned['ass_path'])}'"
        )

    command = [
        _ffmpeg_binary(),
        "-y",
        "-ss",
        f"{planned['clip_start']:.2f}",
        "-to",
        f"{planned['clip_end']:.2f}",
        "-i",
        str(input_path),
    ]

    asset = planned["audio_direction"].music.get("asset")
    if asset:
        command.extend([
            "-stream_loop",
            "-1",
            "-i",
            asset,
        ])

    command.extend([
        "-vf",
        filter_chain,
    ])

    if asset:
        ducking = planned["audio_direction"].music.get("ducking", {})
        music_volume_db = ducking.get("music_target_db", -22.0)
        ducking_threshold = ducking.get("threshold", 0.03)
        ducking_ratio = ducking.get("ratio", 8.0)
        duration = planned["clip_end"] - planned["clip_start"]
        fade_out_start = max(0.0, duration - planned["audio_direction"].fade_out)
        
        filter_complex = (
            f"[1:a]atrim=0:{duration:.2f},asetpts=N/SR/TB,volume={music_volume_db:.2f}dB,"
            f"afade=t=in:st=0:d={planned['audio_direction'].fade_in:.2f},"
            f"afade=t=out:st={fade_out_start:.2f}:d={planned['audio_direction'].fade_out:.2f}[bg];"
            f"[bg][0:a]sidechaincompress=threshold={ducking_threshold:.4f}:ratio={ducking_ratio:.2f}[ducked];"
            f"[0:a][ducked]amix=inputs=2:normalize=0[aout]"
        )
        command.extend([
            "-filter_complex",
            filter_complex,
            "-map",
            "0:v",
            "-map",
            "[aout]",
        ])
    else:
        command.extend([
            "-map",
            "0:v",
            "-map",
            "0:a",
        ])

    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(planned["output_path"]),
        ]
    )
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(f"ffmpeg render failed: {detail}")
    return planned["output_path"]


def _build_crop_filter(width: int, height: int, aspect_ratio: float = 9 / 16) -> str:
    return build_static_crop_filter(width, height, aspect_ratio)


def _write_ass(
    ass_path: Path,
    words: list[TranscriptWord],
    clip_start: float,
    clip_end: float,
    preset_name: str,
    placement: dict | None = None,
) -> None:
    repaired = repair_transcript(_sanitize_caption_words(words))
    chunks = chunk_transcript(repaired.words, clip_start, clip_end)
    preset = resolve_style_preset(preset_name)
    default_crop = SpeakerCropPlan(
        source_width=1080,
        source_height=1920,
        crop_width=1080,
        crop_height=1920,
        selected_speaker_id=None,
        tracked_faces=[],
        crop_coordinates=[{"time": 0.0, "x": 0, "y": 0, "width": 1080, "height": 1920}],
        crop_filter="crop=1080:1920:0:0",
    )
    placements = plan_caption_layout(chunks, preset, default_crop)
    if placement is not None:
        placements = [
            CaptionPlacement(
                chunk_index=item.chunk_index,
                anchor=placement.get("anchor", item.anchor),
                x=540,
                y=int(placement.get("y", item.y)),
                font_size=item.font_size,
                safe_margin_y=int(placement.get("margin_v", item.safe_margin_y)),
            )
            for item in placements
        ]
    typography = build_typography_plan(chunks)
    write_ass_subtitles(ass_path, chunks, placements, typography, preset, clip_start)


# Compatibility helper kept for tests and emergency fallback use.
def _sanitize_caption_words(words: list[TranscriptWord]) -> list[TranscriptWord]:
    cleaned: list[TranscriptWord] = []
    for word in words:
        normalized = re.sub(r"[^a-z0-9]+", "", word.text.lower())
        if not normalized:
            continue
        if normalized in CAPTION_BLOCKLIST:
            continue
        cleaned.append(word)
    if len(cleaned) <= 1:
        return []
    return cleaned


def _serialize_chunk(chunk: CaptionChunk) -> dict:
    return {
        "chunk_index": chunk.chunk_index,
        "start": chunk.start,
        "end": chunk.end,
        "text": chunk.text,
        "lines": list(chunk.lines),
        "words": [asdict(word) for word in chunk.words],
    }


def _serialize_highlighted_words(
    chunks: list[CaptionChunk],
    typography: list[TypographyPlan],
) -> list[dict]:
    highlighted_words: list[dict] = []
    for chunk, plan in zip(chunks, typography, strict=False):
        for item in plan.highlighted_words:
            word = chunk.words[item.word_index]
            highlighted_words.append(
                {
                    "chunk_index": chunk.chunk_index,
                    "word": item.word,
                    "kind": item.kind,
                    "start": word.start,
                    "end": word.end,
                }
            )
    return highlighted_words


def _serialize_placement(placement: CaptionPlacement) -> dict:
    return {
        "chunk_index": placement.chunk_index,
        "anchor": placement.anchor,
        "x": placement.x,
        "y": placement.y,
        "font_size": placement.font_size,
        "safe_margin_y": placement.safe_margin_y,
    }


def _build_zoom_events(
    chunks: list[CaptionChunk],
    typography: list[TypographyPlan],
    preset: StylePreset,
) -> list[dict]:
    events: list[dict] = []
    for chunk, plan in zip(chunks, typography, strict=False):
        if not plan.highlighted_words:
            continue
        primary = plan.highlighted_words[0]
        intensity = 1.04
        if primary.kind in {"money", "number"}:
            intensity = 1.08
        elif preset.default_animation == "bounce":
            intensity = 1.06
        events.append(
            {
                "start": round(chunk.start, 3),
                "end": round(min(chunk.end, chunk.start + 0.45), 3),
                "intensity": intensity,
                "reason": primary.kind,
            }
        )
    return events


def _build_animation_timing(
    chunks: list[CaptionChunk], preset: StylePreset, clip_start: float
) -> list[dict]:
    timing: list[dict] = []
    for chunk in chunks:
        timing.append(
            {
                "chunk_index": chunk.chunk_index,
                "animation": preset.default_animation,
                "word_timings": [
                    {
                        "word": word.text,
                        "start": round(max(0.0, word.start - clip_start), 3),
                        "end": round(max(0.0, word.end - clip_start), 3),
                    }
                    for word in chunk.words
                ],
            }
        )
    return timing


def _build_audio_filter_args(
    audio_direction: AudioDirection, duration: float
) -> list[str]:
    asset = audio_direction.music.get("asset")
    if not asset:
        return []

    ducking = audio_direction.music.get("ducking", {})
    music_volume_db = ducking.get("music_target_db", -22.0)
    ducking_threshold = ducking.get("threshold", 0.03)
    ducking_ratio = ducking.get("ratio", 8.0)

    fade_out_start = max(0.0, duration - audio_direction.fade_out)
    filter_complex = (
        f"[1:a]atrim=0:{duration:.2f},asetpts=N/SR/TB,volume={music_volume_db:.2f}dB,"
        f"afade=t=in:st=0:d={audio_direction.fade_in:.2f},"
        f"afade=t=out:st={fade_out_start:.2f}:d={audio_direction.fade_out:.2f}[bg];"
        f"[bg][0:a]sidechaincompress=threshold={ducking_threshold:.4f}:ratio={ducking_ratio:.2f}[ducked];"
        f"[0:a][ducked]amix=inputs=2:normalize=0[aout]"
    )
    return [
        "-stream_loop",
        "-1",
        "-i",
        asset,
        "-filter_complex",
        filter_complex,
        "-map",
        "0:v",
        "-map",
        "[aout]",
    ]


def _escape_subtitles_path(path: Path) -> str:
    escaped = path.as_posix().replace(":", "\\:")
    return escaped.replace("'", "\\'")


def _ffmpeg_binary() -> str:
    override = os.environ.get("FFMPEG_PATH")
    if override:
        path = Path(override)
        if path.is_dir():
            candidate = path / "ffmpeg.exe"
            if candidate.exists():
                return str(candidate)
        return str(path)
    common = Path("C:/ffmpeg/bin/ffmpeg.exe")
    if common.exists():
        return str(common)
    return "ffmpeg"
