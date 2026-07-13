from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringWeights:
    hook: float = 0.30
    retention: float = 0.25
    caption_quality: float = 0.15
    visual_engagement: float = 0.15
    shareability: float = 0.15


@dataclass(frozen=True)
class PipelineConfig:
    min_clip_s: float = 5.0
    max_clip_s: float = 60.0
    target_candidates: int = 30
    hook_window_s: float = 3.0
    silence_threshold: float = 0.02
    energy_window_s: float = 0.5
    sample_rate: int = 16000
    model_size: str = "base"
    fallback_model_size: str | None = None
    language: str | None = None
    caption_preset: str = "creator"
    crop_aspect_ratio: float = 9 / 16
    face_detection_interval: float = 0.5
    smoothing_factor: float = 0.35
    max_crop_velocity: float = 240.0
    minimum_face_size: int = 48
    weights: ScoringWeights = ScoringWeights()
    hook_inspect_s: float = 10.0
    ending_inspect_s: float = 10.0
    hook_recovery_window_s: float = 15.0
    punchline_recovery_window_s: float = 15.0
    max_sentence_shift: int = 2
    min_hook_score: float = 60.0
    filler_ratio_threshold: float = 0.06
    filler_penalty_weight: float = 1.0
    improvement_threshold_pct: float = 2.0
    improvement_target_rate: float = 0.70
    music_enabled: bool = True
    music_category: str | None = None
    music_volume_db: float = -22.0
    ducking_ratio: float = 8.0
    ducking_threshold: float = 0.03
    task: str = "transcribe"
    crop_enabled: bool = True
