from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

try:  # pragma: no cover - runtime dependency may be absent in tests
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None

logger = logging.getLogger("clipneuron.face_detection")


@dataclass(frozen=True)
class FaceDetection:
    timestamp: float
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0


@dataclass(frozen=True)
class VideoStreamInfo:
    width: int
    height: int
    fps: float


def detect_faces(
    input_path: Path,
    clip_start: float,
    clip_end: float,
    interval_s: float,
    minimum_face_size: int,
) -> tuple[list[FaceDetection], VideoStreamInfo | None]:
    """Sample frames at a fixed interval and return all detected faces."""
    if cv2 is None:
        logger.warning(
            "OpenCV is unavailable; speaker-focused cropping will use fallback"
        )
        return [], None

    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        logger.warning("Unable to open video for face detection: %s", input_path)
        return [], None

    try:
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        stream_info = VideoStreamInfo(width=width, height=height, fps=fps)
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        if cascade.empty():
            logger.warning("OpenCV face cascade could not be loaded")
            return [], stream_info

        detections: list[FaceDetection] = []
        interval_s = max(0.1, interval_s)
        timestamp = max(0.0, clip_start)
        final_timestamp = max(timestamp, clip_end)

        while timestamp <= final_timestamp + 0.001:
            capture.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000.0)
            ok, frame = capture.read()
            if not ok or frame is None:
                timestamp += interval_s
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(minimum_face_size, minimum_face_size),
            )
            for x, y, w, h in faces:
                detections.append(
                    FaceDetection(
                        timestamp=round(timestamp, 3),
                        x=int(x),
                        y=int(y),
                        width=int(w),
                        height=int(h),
                    )
                )
            timestamp += interval_s

        return detections, stream_info
    except Exception:
        logger.exception("Face detection failed for %s", input_path)
        return [], None
    finally:
        capture.release()
