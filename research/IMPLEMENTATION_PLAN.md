# Implementation Plan (post‑research)

This plan converts the research findings into a concrete build path for a high‑quality, iterative clipping system that optimizes for viral performance scores. It is structured to support **continuous evaluation and improvement** of clip outputs, not just code completion.

## 0) Goals & success criteria

**Primary goal:** generate short‑form clips from 60‑minute podcasts that rival professional editors.

**Target scores**
- Overall Viral Score > 85/100
- Hook > 90
- Retention > 80
- Caption Quality > 85
- Visual Engagement > 80
- Shareability > 80

The system must **iterate on clip generation until score targets are met** or no meaningful improvement is found.

---

## 1) Core pipeline overview

1. **Ingest** 60‑minute video/audio.
2. **Transcribe & diarize** (speaker segmentation + word timestamps).
3. **Segment into candidate moments** (topic shifts, punchlines, emotional peaks).
4. **Score candidates** (multi‑signal virality model).
5. **Generate clip variants** (boundary tweaks, hook‑first trims, pacing cleanup).
6. **Caption & reframe** (animated captions, safe‑zone layout, speaker tracking).
7. **Evaluate clips** (automated scoring + heuristics).
8. **Iterate**: adjust boundaries, rewrite captions, reorder hooks, re‑rank.

---

## 2) Data & modeling components

### 2.1 Transcription + diarization
- Use high‑accuracy ASR with word‑level timestamps.
- Diarize speakers to support multi‑speaker podcasts and targeted tracking.

### 2.2 Candidate moment detection
Combine signals similar to leading tools:
- **Transcript features**: hook phrases, contrarian statements, “payoff” cues.
- **Audio features**: loudness/pitch spikes, laughter, excitement.
- **Visual features**: gesture intensity, eye contact, motion saliency (if video).
- **Narrative features**: complete thought boundaries, clear start/end.

Output: 20–40 candidate segments per episode.

### 2.3 Virality scoring (initial pass)
Create a weighted score:
- Hook strength (first 3s)
- Pacing & clarity
- Emotional intensity
- Topic relevance/novelty
- Payoff strength at end

---

## 3) Clip variant generation

For each top candidate (e.g., top 15):

1. **Boundary optimization**: expand/contract ±2–6s to find a stronger hook or cleaner ending.
2. **Hook‑first variant**: start at the highest‑impact line even if it is mid‑sentence, if coherence remains.
3. **Pacing cleanup**: remove fillers and dead air; compress silences.
4. **Length variants**: 20–30s, 35–45s, 50–65s (platform‑specific).

---

## 4) Captions & visual treatment

### 4.1 Captions
- Word‑by‑word animation with keyword highlights.
- Safe‑zone placement for TikTok/Reels/Shorts UI.
- Caption QA pass: spellcheck + domain terms.

### 4.2 Visual framing
- 9:16 vertical output.
- Active speaker tracking with smooth reframe.
- Fallback to manual subject selection or face‑based tracking in multi‑speaker scenes.

---

## 5) Evaluation loop (critical)

### 5.1 Scoring functions
Compute per‑clip scores:
- **Hook Score**: lexical surprise + audio intensity in first 3s.
- **Retention Score**: predicted watch time from pacing, entropy, and narrative coherence.
- **Caption Quality**: accuracy + formatting + keyword emphasis.
- **Visual Engagement**: face presence, movement saliency, framing stability.
- **Shareability**: presence of quotable lines, controversy/novelty, clarity in isolation.

### 5.2 Iteration rules
If any score < target:
- **Hook low** → move start time earlier/later, or reorder to strongest line.
- **Retention low** → tighten pacing, cut digressions, shorten length.
- **Caption quality low** → rewrite or re‑sync captions; remove clutter.
- **Visual engagement low** → adjust crop, face tracking sensitivity, add emphasis zoom.
- **Shareability low** → prioritize clips with clearer “stance” or insight.

Repeat for top clips until improvement plateaus.

---

## 6) MVP milestones

1. **MVP‑1 (offline evaluation):**
   - Transcription + candidate detection + scoring.
   - Generate and rank clip proposals (no rendering).

2. **MVP‑2 (rendered output):**
   - Clip generation, captions, and 9:16 reframing.
   - Initial scoring loop and reranking.

3. **MVP‑3 (iterative optimizer):**
   - Automated loop with boundary adjustments and caption rewrites.
   - Produces final set with score thresholds.

---

## 7) Metrics & QA

- Track **score deltas per iteration** to ensure improvements aren’t overfitting.
- Maintain **per‑episode leaderboards** of clips and their scores.
- Keep **human review checkpoints** for edge cases (sarcasm, context‑heavy segments).

---

## 8) Output artifacts

- `clips.json` with timestamps, scores, and clip metadata.
- Rendered MP4 clips with captions and vertical framing.
- Evaluation report summarizing scores and iterations.

---

## 9) Risks & mitigations

- **Context loss**: mitigation via “standalone clarity” score and auto‑rewrite of captions for context.
- **Over‑trimming**: maintain coherence threshold to avoid confusing hooks.
- **Multi‑speaker tracking**: introduce face‑ID or audio‑speaker matching.

---

## 10) Next step after approval

Proceed to Phase 2: build ingestion, transcription, and candidate detection modules, then implement the iterative scoring loop with clip boundary optimization.

