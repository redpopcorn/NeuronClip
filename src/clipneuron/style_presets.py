from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StylePreset:
    name: str
    font: str
    base_font_size: int
    min_font_size: int
    max_font_size: int
    primary_color: str
    active_color: str
    keyword_color: str
    number_color: str
    money_color: str
    cta_color: str
    outline_color: str
    back_color: str
    outline: int
    shadow: int
    bold: int
    margin_v: int
    safe_margin_x: int
    default_animation: str


STYLE_PRESETS: dict[str, StylePreset] = {
    "creator": StylePreset(
        name="creator",
        font="Arial Bold",
        base_font_size=52,
        min_font_size=40,
        max_font_size=64,
        primary_color="&H00FFFFFF",
        active_color="&H0000E6FF",
        keyword_color="&H0049F8FF",
        number_color="&H0055D6FF",
        money_color="&H0035FF7A",
        cta_color="&H0000C8FF",
        outline_color="&H00000000",
        back_color="&H00000000",
        outline=3,
        shadow=3,
        bold=1,
        margin_v=140,
        safe_margin_x=70,
        default_animation="pop",
    ),
    "podcast": StylePreset(
        name="podcast",
        font="Arial Bold",
        base_font_size=48,
        min_font_size=36,
        max_font_size=56,
        primary_color="&H00FFFFFF",
        active_color="&H00C8F0FF",
        keyword_color="&H00A3E7FF",
        number_color="&H00A9D7FF",
        money_color="&H0080FFC0",
        cta_color="&H004FE4FF",
        outline_color="&H00000000",
        back_color="&H00000000",
        outline=3,
        shadow=2,
        bold=1,
        margin_v=132,
        safe_margin_x=72,
        default_animation="fade",
    ),
    "minimal": StylePreset(
        name="minimal",
        font="Arial",
        base_font_size=44,
        min_font_size=34,
        max_font_size=52,
        primary_color="&H00FFFFFF",
        active_color="&H00F4F4F4",
        keyword_color="&H00D7D7D7",
        number_color="&H00E6E6E6",
        money_color="&H00D0FFD0",
        cta_color="&H00FFFFFF",
        outline_color="&H00000000",
        back_color="&H00000000",
        outline=2,
        shadow=1,
        bold=0,
        margin_v=128,
        safe_margin_x=74,
        default_animation="fade",
    ),
    "documentary": StylePreset(
        name="documentary",
        font="Georgia Bold",
        base_font_size=46,
        min_font_size=36,
        max_font_size=56,
        primary_color="&H00F8F4ED",
        active_color="&H00D9D0C4",
        keyword_color="&H00C5B79E",
        number_color="&H00CDBA94",
        money_color="&H00A8D0A2",
        cta_color="&H00DAC287",
        outline_color="&H00000000",
        back_color="&H00000000",
        outline=3,
        shadow=2,
        bold=1,
        margin_v=136,
        safe_margin_x=72,
        default_animation="scale",
    ),
    "gaming": StylePreset(
        name="gaming",
        font="Arial Bold",
        base_font_size=56,
        min_font_size=42,
        max_font_size=68,
        primary_color="&H00FFFFFF",
        active_color="&H0000F0FF",
        keyword_color="&H0055A0FF",
        number_color="&H0000B4FF",
        money_color="&H0036FF8B",
        cta_color="&H0000E6FF",
        outline_color="&H00000000",
        back_color="&H00000000",
        outline=4,
        shadow=4,
        bold=1,
        margin_v=148,
        safe_margin_x=68,
        default_animation="bounce",
    ),
    # Backward-compatible aliases for existing config/tests.
    "classic": StylePreset(
        name="classic",
        font="Arial",
        base_font_size=42,
        min_font_size=34,
        max_font_size=52,
        primary_color="&H00FFFFFF",
        active_color="&H0000D7FF",
        keyword_color="&H0078E6FF",
        number_color="&H0078E6FF",
        money_color="&H0060FF9B",
        cta_color="&H0000E6FF",
        outline_color="&H00000000",
        back_color="&H00000000",
        outline=3,
        shadow=2,
        bold=0,
        margin_v=120,
        safe_margin_x=74,
        default_animation="fade",
    ),
    "mrbeast": StylePreset(
        name="mrbeast",
        font="Arial Bold",
        base_font_size=58,
        min_font_size=44,
        max_font_size=72,
        primary_color="&H00FFFFFF",
        active_color="&H0000F0FF",
        keyword_color="&H0000B4FF",
        number_color="&H000096FF",
        money_color="&H0035FF7A",
        cta_color="&H0000E6FF",
        outline_color="&H00000000",
        back_color="&H00000000",
        outline=4,
        shadow=4,
        bold=1,
        margin_v=150,
        safe_margin_x=68,
        default_animation="bounce",
    ),
}


def resolve_style_preset(name: str | None) -> StylePreset:
    normalized = str(name or "creator").lower()
    return STYLE_PRESETS.get(normalized, STYLE_PRESETS["creator"])
