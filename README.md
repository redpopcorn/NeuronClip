# ClipNeuron

Free, local-first AI clipping pipeline for long-form podcasts.

## MVP-1 (current)
- Extract audio with `ffmpeg`
- Transcribe with **faster-whisper** (open-source models)
- Segment transcript into candidate moments
- Score candidates with heuristic virality signals
- Output `clips.json` with ranked candidates

## Requirements
- Python 3.10+
- `ffmpeg` installed and available in PATH
- Free open-source models (faster-whisper downloads them automatically)

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run (MVP-1)
```bash
python -m clipneuron.cli \
  --input path/to/podcast.mp4 \
  --output out/clips.json
```

## Render top clips (MVP-2)
```bash
python -m clipneuron.cli \
  --input path/to/podcast.mp4 \
  --output out/clips.json \
  --render \
  --top 5 \
  --clips-dir out/clips
```

## Notes
- This pipeline uses only free resources and open-source models.
- MVP-2 adds clip rendering, 9:16 cropping, and basic burned-in captions.
