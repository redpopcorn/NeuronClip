from __future__ import annotations

from pathlib import Path

from .caption_layout import CaptionPlacement
from .phrase_chunker import CaptionChunk
from .style_presets import StylePreset
from .typography_engine import TypographyPlan

HIGHLIGHT_KIND_TO_COLOR = {
    "keyword": "keyword_color",
    "number": "number_color",
    "money": "money_color",
    "cta": "cta_color",
}


def write_ass_subtitles(
    ass_path: Path,
    chunks: list[CaptionChunk],
    placements: list[CaptionPlacement],
    typography: list[TypographyPlan],
    preset: StylePreset,
    clip_start: float,
) -> list[dict]:
    animation_timing: list[dict] = []
    ass_path.parent.mkdir(parents=True, exist_ok=True)
    with ass_path.open("w", encoding="utf-8") as handle:
        handle.write(_ass_header(preset))
        handle.write("\n[Events]\n")
        handle.write(
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )
        for chunk, placement, type_plan in zip(chunks, placements, typography, strict=False):
            entries, timing = _chunk_to_ass(
                chunk,
                placement,
                type_plan,
                preset,
                clip_start,
            )
            for entry in entries:
                handle.write(entry + "\n")
            animation_timing.append(timing)
    return animation_timing


def _chunk_to_ass(
    chunk: CaptionChunk,
    placement: CaptionPlacement,
    type_plan: TypographyPlan,
    preset: StylePreset,
    clip_start: float,
) -> tuple[list[str], dict]:
    entries: list[str] = []
    highlight_map = {item.word_index: item.kind for item in type_plan.highlighted_words}
    word_timings: list[dict] = []
    for active_index, word in enumerate(chunk.words):
        start = max(0.0, word.start - clip_start)
        end = max(start + 0.06, word.end - clip_start)
        word_timings.append({"word": word.text, "start": start, "end": end})
        entries.append(
            "Dialogue: 0,"
            f"{_format_ass_time(start)},{_format_ass_time(end)},Default,,0,0,0,,"
            f"{{{_placement_tags(placement)}{_style_tags(placement, preset)}}}"
            f"{_render_chunk_text(chunk, active_index, highlight_map, preset)}"
        )
    return entries, {
        "chunk_index": chunk.chunk_index,
        "animation": preset.default_animation,
        "word_timings": word_timings,
    }


def _render_chunk_text(
    chunk: CaptionChunk,
    active_index: int,
    highlight_map: dict[int, str],
    preset: StylePreset,
) -> str:
    rendered_lines: list[str] = []
    consumed = 0
    line_lengths = [len(line.split()) for line in chunk.lines]
    for line_length in line_lengths:
        line_words = chunk.words[consumed : consumed + line_length]
        parts: list[str] = []
        for offset, word in enumerate(line_words):
            index = consumed + offset
            token = _escape_ass_text(word.text)
            if index == active_index:
                parts.append(
                    f"{{{_active_word_animation(preset)}}}{token}"
                )
            elif index in highlight_map:
                color_key = HIGHLIGHT_KIND_TO_COLOR.get(highlight_map[index], "keyword_color")
                parts.append(f"{{\\c{getattr(preset, color_key)}\\b1}}{token}")
            else:
                parts.append(token)
        rendered_lines.append(" ".join(parts))
        consumed += line_length
    return r"\N".join(rendered_lines)


def _placement_tags(placement: CaptionPlacement) -> str:
    align = "\\an8" if placement.anchor == "top" else "\\an2"
    return f"{align}\\pos({placement.x},{placement.y})"


def _style_tags(placement: CaptionPlacement, preset: StylePreset) -> str:
    return f"\\fs{placement.font_size}\\bord{preset.outline}\\shad{preset.shadow}"


def _active_word_animation(preset: StylePreset) -> str:
    if preset.default_animation == "bounce":
        return f"\\c{preset.active_color}\\b1\\fscx128\\fscy128\\t(0,120,\\fscx94\\fscy94)\\t(120,220,\\fscx100\\fscy100)"
    if preset.default_animation == "scale":
        return f"\\c{preset.active_color}\\b1\\fscx118\\fscy118\\t(0,120,\\fscx100\\fscy100)"
    if preset.default_animation == "fade":
        return f"\\c{preset.active_color}\\b1\\fad(60,60)"
    return f"\\c{preset.active_color}\\b1\\fscx122\\fscy122\\t(0,140,\\fscx100\\fscy100)"


def _ass_header(preset: StylePreset) -> str:
    return (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "WrapStyle: 2\n"
        "ScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{preset.font},{preset.base_font_size},{preset.primary_color},{preset.active_color},{preset.outline_color},{preset.back_color},{preset.bold},0,0,0,100,100,0,0,1,{preset.outline},{preset.shadow},2,{preset.safe_margin_x},{preset.safe_margin_x},{preset.margin_v},1\n"
    )


def _format_ass_time(seconds: float) -> str:
    total_centiseconds = max(0, int(round(seconds * 100)))
    hours = total_centiseconds // 360000
    minutes = (total_centiseconds % 360000) // 6000
    secs = (total_centiseconds % 6000) // 100
    cs = total_centiseconds % 100
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def _escape_ass_text(text: str) -> str:
    return text.replace("{", r"\{").replace("}", r"\}")
