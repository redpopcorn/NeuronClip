from __future__ import annotations

from clipneuron.config import PipelineConfig
from clipneuron.crop_planner import (
    CropCoordinate,
    build_dynamic_crop_filter,
    build_static_crop_filter,
)
from clipneuron.face_detection import FaceDetection
from clipneuron.face_tracking import track_faces


def test_track_faces_assigns_stable_ids() -> None:
    detections = [
        FaceDetection(timestamp=0.0, x=100, y=100, width=120, height=120),
        FaceDetection(timestamp=0.0, x=500, y=120, width=110, height=110),
        FaceDetection(timestamp=0.5, x=108, y=104, width=122, height=122),
        FaceDetection(timestamp=0.5, x=508, y=126, width=108, height=108),
    ]

    tracks = track_faces(detections, max_gap_s=1.0)

    assert len(tracks) == 2
    assert len(tracks[0].samples) == 2
    assert len(tracks[1].samples) == 2
    assert {track.face_id for track in tracks} == {1, 2}


def test_build_static_crop_filter_uses_center_crop() -> None:
    crop = build_static_crop_filter(1920, 1080, aspect_ratio=9 / 16)

    assert crop == "crop=607:1080:656:0"


def test_build_dynamic_crop_filter_contains_time_expression() -> None:
    filter_text = build_dynamic_crop_filter(
        [
            CropCoordinate(time=0.0, x=100, y=0, width=607, height=1080),
            CropCoordinate(time=1.0, x=200, y=0, width=607, height=1080),
        ]
    )

    assert "crop=607:1080:" in filter_text
    assert "lt(t\\,1.000)" in filter_text


def test_pipeline_config_exposes_crop_controls() -> None:
    config = PipelineConfig()

    assert config.crop_aspect_ratio == 9 / 16
    assert config.face_detection_interval > 0
    assert 0 <= config.smoothing_factor <= 1
    assert config.max_crop_velocity > 0
    assert config.minimum_face_size > 0
