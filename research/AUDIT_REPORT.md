# ClipNeuron Audit Report (Phase 1)

Date: 2026-07-04

## Scope
Full audit of current codebase with a focus on runtime errors, edge cases, silent failures, invalid timestamps, and ffmpeg/ffprobe failures.

## Findings (prior to fixes)

1. **No input validation**
   - Missing file, empty file, or non-file path were not handled.

2. **Dependency checks missing**
   - `ffmpeg`/`ffprobe` assumed available; missing binaries would crash without context.

3. **Transcript validation missing**
   - Empty transcripts or invalid word timestamps could proceed silently.

4. **Candidate validation missing**
   - Candidates could include invalid timestamps or durations outside min/max.

5. **Overlapping clip boundaries**
   - Ranked candidates overlapped by design; no non-overlap selection enforced.

6. **ffmpeg/ffprobe error handling**
   - Command failures raised generic exceptions without stderr context.

7. **Caption timing edge cases**
   - Word selection excluded words overlapping clip boundaries, risking empty captions.
   - Subtitle timing not clamped to clip window.

8. **Overall score weights hardcoded**
   - Configurable weights were ignored, risking inconsistent scores.

## Fixes applied

- Added dependency checks for `ffmpeg` and `ffprobe` with clear error messages.
- Added input file validation (existence, file type, non-zero length).
- Added transcript validation (non-empty, valid timestamps, non-empty text).
- Added candidate validation with warnings and enforcement of valid durations.
- Enforced non-overlapping clip selection in final output.
- Added error context for ffmpeg/ffprobe failures.
- Improved caption word selection for boundary overlaps and clamped SRT timing.
- Applied configurable scoring weights consistently.

## Remaining risk areas

- Rendering requires video streams; audio-only inputs with `--render` will still fail at ffprobe stage. Needs explicit video stream validation if audio-only inputs are supported for rendering.
- No automated tests yet (Phase 9).

