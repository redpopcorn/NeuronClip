from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import PipelineConfig
from .face_detection import VideoStreamInfo, detect_faces
from .face_tracking import FaceTrack, TrackedFaceSample, track_faces
from .io_utils import get_video_dimensions

logger = logging.getLogger("clipneuron.crop_planner")


@dataclass(frozen=True)
class CropCoordinate:
    time: float
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class SpeakerCropPlan:
    source_width: int
    source_height: int
    crop_width: int
    crop_height: int
    selected_speaker_id: int | None
    tracked_faces: list[dict]
    crop_coordinates: list[dict]
    crop_filter: str


def plan_speaker_crop(
    input_path: Path,
    clip_start: float,
    clip_end: float,
    config: PipelineConfig,
) -> SpeakerCropPlan:
    """Plan a smooth vertical crop that keeps the primary face near center."""
    source_width, source_height = get_video_dimensions(input_path)
    crop_width, crop_height = _target_crop_size(
        source_width, source_height, config.crop_aspect_ratio
    )
    fallback = _build_static_plan(
        source_width=source_width,
        source_height=source_height,
        crop_width=crop_width,
        crop_height=crop_height,
        clip_duration=max(0.0, clip_end - clip_start),
    )

    detections, stream_info = detect_faces(
        input_path,
        clip_start,
        clip_end,
        config.face_detection_interval,
        config.minimum_face_size,
    )
    if not detections or stream_info is None:
        return fallback

    tracks = track_faces(
        detections,
        max_gap_s=max(config.face_detection_interval * 2.5, 0.75),
    )
    if not tracks:
        return fallback

    speaker_track = _select_primary_speaker(tracks, clip_start, clip_end)
    if speaker_track is None:
        return fallback

    sample_times = _build_sample_times(
        clip_start, clip_end, config.face_detection_interval
    )
    crop_points = _build_crop_coordinates(
        sample_times=sample_times,
        track=speaker_track,
        source_width=source_width,
        source_height=source_height,
        crop_width=crop_width,
        crop_height=crop_height,
        clip_start=clip_start,
        smoothing_factor=config.smoothing_factor,
        max_crop_velocity=config.max_crop_velocity,
    )
    if not crop_points:
        return fallback

    crop_filter = build_dynamic_crop_filter(crop_points)
    return SpeakerCropPlan(
        source_width=source_width,
        source_height=source_height,
        crop_width=crop_width,
        crop_height=crop_height,
        selected_speaker_id=speaker_track.face_id,
        tracked_faces=[_serialize_track(track) for track in tracks],
        crop_coordinates=[asdict(point) for point in crop_points],
        crop_filter=crop_filter,
    )


def build_static_crop_filter(
    width: int, height: int, aspect_ratio: float = 9 / 16
) -> str:
    crop_width, crop_height = _target_crop_size(width, height, aspect_ratio)
    x = max(0, int((width - crop_width) / 2))
    y = max(0, int((height - crop_height) / 2))
    return f"crop={crop_width}:{crop_height}:{x}:{y}"


def build_dynamic_crop_filter(crop_points: list[CropCoordinate]) -> str:
    if not crop_points:
        raise ValueError("Cannot build dynamic crop filter without crop coordinates.")
    first = crop_points[0]
    x_expr = _build_axis_expression(crop_points, "x")
    y_expr = _build_axis_expression(crop_points, "y")
    return f"crop={first.width}:{first.height}:x='{x_expr}':y='{y_expr}'"


def _build_static_plan(
    source_width: int,
    source_height: int,
    crop_width: int,
    crop_height: int,
    clip_duration: float,
) -> SpeakerCropPlan:
    x = max(0, int((source_width - crop_width) / 2))
    y = max(0, int((source_height - crop_height) / 2))
    crop_points = [
        CropCoordinate(time=0.0, x=x, y=y, width=crop_width, height=crop_height),
        CropCoordinate(
            time=round(max(0.0, clip_duration), 3),
            x=x,
            y=y,
            width=crop_width,
            height=crop_height,
        ),
    ]
    return SpeakerCropPlan(
        source_width=source_width,
        source_height=source_height,
        crop_width=crop_width,
        crop_height=crop_height,
        selected_speaker_id=None,
        tracked_faces=[],
        crop_coordinates=[asdict(point) for point in crop_points],
        crop_filter=build_dynamic_crop_filter(crop_points),
    )


def _target_crop_size(width: int, height: int, aspect_ratio: float) -> tuple[int, int]:
    aspect_ratio = max(0.1, aspect_ratio)
    current_ratio = width / max(height, 1)
    if current_ratio > aspect_ratio:
        crop_height = height
        crop_width = max(1, int(height * aspect_ratio))
    else:
        crop_width = width
        crop_height = max(1, int(width / aspect_ratio))
    return min(crop_width, width), min(crop_height, height)


def _select_primary_speaker(
    tracks: list[FaceTrack], clip_start: float, clip_end: float
) -> FaceTrack | None:
    clip_duration = max(0.1, clip_end - clip_start)
    best_track: FaceTrack | None = None
    best_score = float("-inf")
    for track in tracks:
        areas = [sample.area for sample in track.samples]
        if not areas:
            continue
        avg_area = sum(areas) / len(areas)
        max_area = max(areas)
        coverage = min(1.0, len(track.samples) / max(1.0, clip_duration))
        score = max_area + avg_area * 0.5 + coverage * 10000.0
        if score > best_score:
            best_score = score
            best_track = track
    return best_track


def _build_sample_times(
    clip_start: float, clip_end: float, interval_s: float
) -> list[float]:
    interval_s = max(0.1, interval_s)
    times: list[float] = [clip_start]
    current = clip_start + interval_s
    while current < clip_end:
        times.append(round(current, 3))
        current += interval_s
    if clip_end not in times:
        times.append(round(clip_end, 3))
    return times


def _build_crop_coordinates(
    sample_times: list[float],
    track: FaceTrack,
    source_width: int,
    source_height: int,
    crop_width: int,
    crop_height: int,
    clip_start: float,
    smoothing_factor: float,
    max_crop_velocity: float,
) -> list[CropCoordinate]:
    coordinates: list[CropCoordinate] = []
    previous_x: float | None = None
    previous_y: float | None = None
    previous_time: float | None = None

    for absolute_time in sample_times:
        sample = _interpolate_track_sample(track, absolute_time)
        target_center_x = source_width / 2
        target_center_y = source_height / 2
        if sample is not None:
            target_center_x = sample.center_x
            target_center_y = sample.center_y

        target_x = _clamp(
            target_center_x - crop_width / 2, 0, source_width - crop_width
        )
        target_y = _clamp(
            target_center_y - crop_height / 2, 0, source_height - crop_height
        )

        if previous_x is None or previous_y is None:
            smoothed_x = target_x
            smoothed_y = target_y
        else:
            alpha = min(1.0, max(0.0, smoothing_factor))
            smoothed_x = previous_x + (target_x - previous_x) * alpha
            smoothed_y = previous_y + (target_y - previous_y) * alpha
            if previous_time is not None:
                dt = max(0.001, absolute_time - previous_time)
                max_delta = max_crop_velocity * dt
                smoothed_x = _limit_delta(previous_x, smoothed_x, max_delta)
                smoothed_y = _limit_delta(previous_y, smoothed_y, max_delta)

        smoothed_x = _clamp(smoothed_x, 0, source_width - crop_width)
        smoothed_y = _clamp(smoothed_y, 0, source_height - crop_height)
        coordinates.append(
            CropCoordinate(
                time=round(max(0.0, absolute_time - clip_start), 3),
                x=int(round(smoothed_x)),
                y=int(round(smoothed_y)),
                width=crop_width,
                height=crop_height,
            )
        )
        previous_x = smoothed_x
        previous_y = smoothed_y
        previous_time = absolute_time

    return _dedupe_coordinates(coordinates)


def _interpolate_track_sample(
    track: FaceTrack, timestamp: float
) -> TrackedFaceSample | None:
    if not track.samples:
        return None
    if timestamp <= track.samples[0].timestamp:
        return track.samples[0]
    if timestamp >= track.samples[-1].timestamp:
        return track.samples[-1]

    for left, right in zip(track.samples, track.samples[1:]):
        if left.timestamp <= timestamp <= right.timestamp:
            span = max(0.001, right.timestamp - left.timestamp)
            ratio = (timestamp - left.timestamp) / span
            return TrackedFaceSample(
                face_id=track.face_id,
                timestamp=timestamp,
                x=int(round(left.x + (right.x - left.x) * ratio)),
                y=int(round(left.y + (right.y - left.y) * ratio)),
                width=int(round(left.width + (right.width - left.width) * ratio)),
                height=int(round(left.height + (right.height - left.height) * ratio)),
            )
    return track.samples[-1]


def _serialize_track(track: FaceTrack) -> dict:
    return {
        "face_id": track.face_id,
        "sample_count": len(track.samples),
        "samples": [
            {
                "time": sample.timestamp,
                "bbox": {
                    "x": sample.x,
                    "y": sample.y,
                    "width": sample.width,
                    "height": sample.height,
                },
            }
            for sample in track.samples
        ],
    }


def _build_axis_expression(
    crop_points: list[CropCoordinate],
    axis: str,
) -> str:
    if len(crop_points) == 1:
        return str(getattr(crop_points[0], axis))

    segments: list[str] = []
    for left, right in zip(crop_points, crop_points[1:]):
        left_value = getattr(left, axis)
        right_value = getattr(right, axis)
        duration = max(0.001, right.time - left.time)
        segment_expression = f"{left_value}+({right_value}-{left_value})*(t-{left.time:.3f})/{duration:.3f}"
        condition = f"lt(t\\,{right.time:.3f})"
        segments.append(f"if({condition}\\,{segment_expression}\\,")

    expression = (
        "".join(segments) + str(getattr(crop_points[-1], axis)) + (")" * len(segments))
    )
    return expression


def _dedupe_coordinates(points: list[CropCoordinate]) -> list[CropCoordinate]:
    if not points:
        return []
    deduped = [points[0]]
    for point in points[1:]:
        previous = deduped[-1]
        if (
            point.x == previous.x
            and point.y == previous.y
            and point.time != points[-1].time
        ):
            continue
        deduped.append(point)
    if deduped[-1].time != points[-1].time:
        deduped.append(points[-1])
    return deduped


def _limit_delta(previous: float, current: float, max_delta: float) -> float:
    delta = current - previous
    if delta > max_delta:
        return previous + max_delta
    if delta < -max_delta:
        return previous - max_delta
    return current


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))
