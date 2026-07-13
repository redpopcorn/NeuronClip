from __future__ import annotations

import json
import logging
import sys
import traceback
import uuid
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

APP_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = APP_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.append(str(SRC_ROOT))

from clipneuron.config import PipelineConfig
from clipneuron.errors import PipelineStageError
from clipneuron.pipeline import run_pipeline
from clipneuron.render import render_clips

DATA_DIR = APP_ROOT / "data" / "projects"
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clipneuron.api")

app = FastAPI(title="ClipNeuron API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _project_dir(project_id: str) -> Path:
    return DATA_DIR / project_id


def _status_path(project_id: str) -> Path:
    return _project_dir(project_id) / "status.json"


def _write_status(
    project_id: str,
    status: str,
    progress: int,
    stage: str | None = None,
    error: str | None = None,
    traceback_text: str | None = None,
) -> None:
    payload = {"status": status, "progress": progress}
    if stage:
        payload["stage"] = stage
    if error:
        payload["error"] = error
    if traceback_text:
        payload["traceback"] = traceback_text
    path = _status_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _read_status(project_id: str) -> dict[str, Any]:
    path = _status_path(project_id)
    if not path.exists():
        return {"status": "processing", "progress": 0}
    return json.loads(path.read_text(encoding="utf-8"))


def _clip_id(project_id: str, filename: str) -> str:
    return f"{project_id}__{filename}"


def _parse_clip_id(clip_id: str) -> tuple[str, str]:
    if "__" not in clip_id:
        raise ValueError("Invalid clip id")
    project_id, filename = clip_id.split("__", 1)
    return project_id, filename


def _process_project(project_id: str, input_path: Path, config_overrides: dict[str, Any]) -> None:
    stage = "queued"
    try:
        stage = "transcription"
        logger.info("[%s] Stage started: %s", project_id, stage)
        _write_status(project_id, "processing", 5, stage=stage)
        output_path = _project_dir(project_id) / "clips.json"
        config = PipelineConfig(**config_overrides)
        payload, words = run_pipeline(input_path, output_path, config)
        logger.info("[%s] Stage completed: %s", project_id, stage)

        stage = "rendering"
        logger.info("[%s] Stage started: %s", project_id, stage)
        _write_status(project_id, "processing", 70, stage=stage)
        clips_dir = _project_dir(project_id) / "clips"
        rendered = render_clips(input_path, clips_dir, payload["clips"], words, config)
        logger.info("[%s] Stage completed: %s", project_id, stage)

        stage = "clips_json"
        logger.info("[%s] Stage started: %s", project_id, stage)
        if rendered:
            clips = payload.get("clips", [])
            for clip, clip_path in zip(clips, rendered, strict=False):
                clip_id = _clip_id(project_id, clip_path.name)
                clip["clip_id"] = clip_id
                clip["download_url"] = f"/clip/{clip_id}/download"
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("[%s] Stage completed: %s", project_id, stage)

        _write_status(project_id, "completed", 100, stage="completed")
    except PipelineStageError as exc:  # pragma: no cover - surfaced to status
        logger.exception("[%s] Stage failed: %s", project_id, exc.stage)
        _write_status(
            project_id,
            "failed",
            100,
            stage=exc.stage,
            error=str(exc),
            traceback_text=traceback.format_exc(),
        )
    except Exception as exc:  # pragma: no cover - surfaced to status
        logger.exception("[%s] Stage failed: %s", project_id, stage)
        _write_status(
            project_id,
            "failed",
            100,
            stage=stage,
            error=str(exc),
            traceback_text=traceback.format_exc(),
        )


@app.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    music_enabled: bool = Form(True),
    music_category: str | None = Form(None),
    music_volume_db: float = Form(-22.0),
    ducking_ratio: float = Form(8.0),
    ducking_threshold: float = Form(0.03),
    task: str = Form("transcribe"),
    crop_enabled: bool = Form(True),
):
    project_id = uuid.uuid4().hex
    project_dir = _project_dir(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    input_path = project_dir / video.filename
    with input_path.open("wb") as handle:
        handle.write(await video.read())

    # Form parameters can come in as strings depending on client, clean them up
    if isinstance(music_category, str) and (music_category.lower() == "none" or music_category == ""):
        music_category = None

    # Handle string to bool conversions from form data if needed
    def _bool(val: Any) -> bool:
        if isinstance(val, str):
            return val.lower() == "true"
        return bool(val)

    config_overrides = {
        "music_enabled": _bool(music_enabled),
        "music_category": music_category,
        "music_volume_db": float(music_volume_db),
        "ducking_ratio": float(ducking_ratio),
        "ducking_threshold": float(ducking_threshold),
        "task": task,
        "crop_enabled": _bool(crop_enabled),
    }

    _write_status(project_id, "processing", 0)
    background_tasks.add_task(_process_project, project_id, input_path, config_overrides)

    return {"project_id": project_id, "status": "processing"}


@app.get("/project/{project_id}")
def get_project(project_id: str):
    status = _read_status(project_id)
    if status.get("status") == "failed":
        return status
    return status


@app.get("/project/{project_id}/clips")
def get_clips(project_id: str):
    clips_path = _project_dir(project_id) / "clips.json"
    if not clips_path.exists():
        raise HTTPException(status_code=404, detail="Clips not ready")
    payload = json.loads(clips_path.read_text(encoding="utf-8"))
    return payload


@app.get("/clip/{clip_id}/download")
def download_clip(clip_id: str):
    try:
        project_id, filename = _parse_clip_id(clip_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    clip_path = _project_dir(project_id) / "clips" / filename
    if not clip_path.exists():
        raise HTTPException(status_code=404, detail="Clip not found")
    return FileResponse(path=clip_path, media_type="video/mp4", filename=filename)
