from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

from .face_detection import FaceDetection

logger = logging.getLogger("clipneuron.face_tracking")


@dataclass(frozen=True)
class TrackedFaceSample:
    face_id: int
    timestamp: float
    x: int
    y: int
    width: int
    height: int

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2


@dataclass
class FaceTrack:
    face_id: int
    samples: list[TrackedFaceSample] = field(default_factory=list)

    @property
    def last_sample(self) -> TrackedFaceSample:
        return self.samples[-1]


def track_faces(
    detections: list[FaceDetection],
    max_gap_s: float,
    iou_threshold: float = 0.15,
) -> list[FaceTrack]:
    """Assign stable IDs to detections with greedy IoU and center-distance matching."""
    if not detections:
        return []

    grouped: dict[float, list[FaceDetection]] = {}
    for detection in detections:
        grouped.setdefault(detection.timestamp, []).append(detection)

    tracks: list[FaceTrack] = []
    next_face_id = 1

    for timestamp in sorted(grouped):
        frame_detections = sorted(
            grouped[timestamp], key=lambda item: item.width * item.height, reverse=True
        )
        unmatched_tracks = {
            track.face_id: track
            for track in tracks
            if timestamp - track.last_sample.timestamp <= max_gap_s
        }
        assigned_track_ids: set[int] = set()

        for detection in frame_detections:
            best_track: FaceTrack | None = None
            best_score = float("-inf")
            for face_id, track in unmatched_tracks.items():
                if face_id in assigned_track_ids:
                    continue
                score = _match_score(track.last_sample, detection)
                if score > best_score:
                    best_score = score
                    best_track = track

            if best_track is not None and best_score >= iou_threshold:
                best_track.samples.append(
                    TrackedFaceSample(
                        face_id=best_track.face_id,
                        timestamp=detection.timestamp,
                        x=detection.x,
                        y=detection.y,
                        width=detection.width,
                        height=detection.height,
                    )
                )
                assigned_track_ids.add(best_track.face_id)
                continue

            track = FaceTrack(face_id=next_face_id)
            track.samples.append(
                TrackedFaceSample(
                    face_id=next_face_id,
                    timestamp=detection.timestamp,
                    x=detection.x,
                    y=detection.y,
                    width=detection.width,
                    height=detection.height,
                )
            )
            tracks.append(track)
            assigned_track_ids.add(next_face_id)
            next_face_id += 1

    logger.info("Tracked %s face identities", len(tracks))
    return tracks


def _match_score(sample: TrackedFaceSample, detection: FaceDetection) -> float:
    iou = _intersection_over_union(
        (sample.x, sample.y, sample.width, sample.height),
        (detection.x, detection.y, detection.width, detection.height),
    )
    dx = sample.center_x - (detection.x + detection.width / 2)
    dy = sample.center_y - (detection.y + detection.height / 2)
    distance = math.sqrt(dx * dx + dy * dy)
    scale = max(sample.width, sample.height, detection.width, detection.height, 1)
    distance_penalty = min(1.0, distance / (scale * 4.0))
    return iou + (1.0 - distance_penalty) * 0.35


def _intersection_over_union(
    left: tuple[int, int, int, int], right: tuple[int, int, int, int]
) -> float:
    lx, ly, lw, lh = left
    rx, ry, rw, rh = right

    left_x2 = lx + lw
    left_y2 = ly + lh
    right_x2 = rx + rw
    right_y2 = ry + rh

    inter_x1 = max(lx, rx)
    inter_y1 = max(ly, ry)
    inter_x2 = min(left_x2, right_x2)
    inter_y2 = min(left_y2, right_y2)
    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    intersection = inter_w * inter_h
    if intersection <= 0:
        return 0.0

    union = lw * lh + rw * rh - intersection
    if union <= 0:
        return 0.0
    return intersection / union
