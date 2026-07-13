from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def extract_audio(input_path: Path, output_wav: Path, sample_rate: int) -> None:
    ensure_parent(output_wav)
    command = [
        _ffmpeg_binary(),
        "-y",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-vn",
        str(output_wav),
    ]
    _run_command(command, "ffmpeg failed to extract audio")


def enhance_audio_for_transcription(
    input_wav: Path, output_wav: Path, sample_rate: int
) -> None:
    ensure_parent(output_wav)
    command = [
        _ffmpeg_binary(),
        "-y",
        "-i",
        str(input_wav),
        "-af",
        "highpass=f=120,lowpass=f=7000,afftdn=nf=-25,dynaudnorm=f=150:g=15",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        str(output_wav),
    ]
    _run_command(command, "ffmpeg failed to enhance transcription audio")


def write_json(path: Path, payload: dict) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def get_media_duration(input_path: Path) -> float:
    command = [
        _ffprobe_binary(),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_path),
    ]
    result = _run_command(command, "ffprobe failed to read media duration")
    output = result.stdout.strip()
    if not output:
        raise ValueError("Unable to read media duration via ffprobe.")
    return float(output)


def get_video_dimensions(input_path: Path) -> tuple[int, int]:
    command = [
        _ffprobe_binary(),
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=p=0:s=x",
        str(input_path),
    ]
    result = _run_command(command, "ffprobe failed to read video dimensions")
    output = result.stdout.strip()
    if "x" not in output:
        raise ValueError("Unable to read video dimensions via ffprobe.")
    width_str, height_str = output.split("x", maxsplit=1)
    return int(width_str), int(height_str)


def _run_command(
    command: list[str], error_message: str
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or "Unknown error"
        raise RuntimeError(f"{error_message}: {detail}")
    return result


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


def _ffprobe_binary() -> str:
    override = os.environ.get("FFPROBE_PATH")
    if override:
        path = Path(override)
        if path.is_dir():
            candidate = path / "ffprobe.exe"
            if candidate.exists():
                return str(candidate)
        return str(path)
    common = Path("C:/ffmpeg/bin/ffprobe.exe")
    if common.exists():
        return str(common)
    return "ffprobe"
