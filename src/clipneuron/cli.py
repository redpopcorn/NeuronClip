from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import PipelineConfig
from .pipeline import run_pipeline
from .render import render_clips


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ClipNeuron pipeline")
    parser.add_argument("--input", required=True, help="Path to input video/audio")
    parser.add_argument("--output", required=True, help="Path to output clips.json")
    parser.add_argument("--model", default="small", help="Whisper model size")
    parser.add_argument(
        "--fallback-model",
        default=None,
        help="Optional heavier fallback Whisper model for low-quality audio",
    )
    parser.add_argument("--language", default=None, help="Optional language code")
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render top clips to MP4 with burned-in captions",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top clips to render",
    )
    parser.add_argument(
        "--clips-dir",
        default=None,
        help="Directory for rendered clips (defaults to output directory)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        config = PipelineConfig(
            model_size=args.model,
            fallback_model_size=args.fallback_model,
            language=args.language,
        )
        payload, words = run_pipeline(Path(args.input), Path(args.output), config)
        if args.render:
            clips_dir = (
                Path(args.clips_dir) if args.clips_dir else Path(args.output).parent
            )
            render_clips(
                Path(args.input),
                clips_dir,
                payload["clips"],
                words,
                config,
                top=args.top,
            )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
