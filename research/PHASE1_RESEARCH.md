# Phase 1 Research: AI Clipping Systems

This document summarizes publicly available information about leading clipping tools and distills their practical patterns for clip selection, captions, viral editing, speaker tracking, and retention optimization. Sources are linked inline.

## Summary of recurring patterns

- **Clip selection is score‑driven**: Most tools generate multiple candidates and rank them with a virality/engagement score derived from transcript, audio, and visual cues (e.g., hooks, emotional peaks, pacing). This matches the market’s “many shots on goal” approach (Klap, Opus, Submagic). 
- **Hook-first trimming**: Leading tools prioritize a hook in the first 1–3 seconds, often trimming or repositioning the strongest line to the front (Klap).
- **Captioning is central**: Word‑by‑word, animated captions with highlighted keywords are used to boost retention in muted viewing contexts (Klap, Submagic). 
- **Speaker tracking and smart reframing**: Tools emphasize auto‑reframing and active speaker tracking to keep faces centered in 9:16 (Opus subject tracking; Klap AI reframe).
- **Retention optimization**: Algorithms favor segments with clear narrative arcs, complete thoughts, strong openings, and a payoff in the last seconds (Opus viral moment detection; Klap patterns).

---

## Tool‑by‑tool analysis

### 1) Opus Clip

**Clip selection methods**
- Uses multi‑signal “viral moment detection” combining transcript‑level cues (hook strength, narrative arc, emotional intensity), audio dynamics (pitch, pace, laughter), and visual cues (gestures, facial expression) to score moments and rank candidates. The API supports scoring arbitrary segments or auto‑selecting top moments. Source: https://www.opus.pro/blog/viral-moment-detection-api

**Caption styles**
- Not deeply documented in the available public sources here, but Opus emphasizes short‑form‑optimized captions and vertical formatting as part of repurposing workflows. Source: https://www.opus.pro/blog/video-clipping-techniques

**Viral editing patterns**
- Focus on shortening to match short‑form attention patterns and mobile‑first consumption; clip selection based on retention‑aligned signals. Source: https://www.opus.pro/blog/video-clipping-techniques

**Speaker tracking approaches**
- Provides **subject tracking** with automatic moving speaker tracking to keep the speaker centered during reframing, plus manual tracking for other subjects. Source: https://opusclip-c3e48c12.mintlify.app/docs/article/subject-tracking

**Retention optimization techniques**
- Emphasizes watch‑time percentage, completion rate, and re‑watch frequency as the primary metrics improved by clip selection and formatting. Source: https://www.opus.pro/blog/video-clipping-techniques

---

### 2) Klap

**Clip selection methods**
- Generates 10+ candidates and assigns a **Virality Score (0–100)** based on hook strength, pacing, emotional peaks, and topic relevance. Scored clips are ranked to prioritize posting order. Source: https://klap.app/tools/ai-clip-maker

**Caption styles**
- Animated captions with keyword highlighting and styles optimized for muted viewing. Offers brand kits (fonts/colors) for consistency. Source: https://klap.app/tools/ai-clip-maker

**Viral editing patterns**
- Emphasizes: hook in first 1–2 seconds, contrarian take or surprise, emotional reaction, and payoff at end. Mentions reordering dialogue to place the hook at second zero when needed (with approval). Source: https://klap.app/tools/viral-clip-generator

**Speaker tracking approaches**
- Auto‑reframing to 9:16 with speaker tracking (“AI Reframe 2”). Source: https://klap.app/tools/ai-video-clipping-tool

**Retention optimization techniques**
- Scores clips on hook strength and pacing; promotes posting higher scores first; emphasizes retention in first seconds. Source: https://klap.app/tools/ai-clip-maker

---

### 3) Vidyo.ai (Quso)

**Clip selection methods**
- “Intelliclips” scans videos for speech peaks, topic transitions, and engagement hooks; returns ranked clip list with a virality score. Source: https://videoclipping-ai.com/

**Caption styles**
- Provides multiple caption styles and templates; reviews note strong subtitle styling control and brand templates. Source: https://raixs.com/vidyo-ai

**Viral editing patterns**
- Emphasizes reducing filler and dead air, scene detection, and clipping at complete sentences to keep shorts natural. Source: https://videoclipping-ai.com/

**Speaker tracking approaches**
- Reviews cite reliable speaker tracking and smart framing for interviews. Source: https://raixs.com/vidyo-ai

**Retention optimization techniques**
- Focuses on practical clipping and template control; less explicit “viral” optimization compared to some competitors. Source: https://raixs.com/vidyo-ai

---

### 4) Submagic

**Clip selection methods**
- “Magic Clips” generates multiple short clips from long videos with a virality score per clip, plus transcript‑based editing. Source: https://care.submagic.co/en/article/how-to-use-magic-clips-step-by-step-guide-15mve5q/

**Caption styles**
- Heavy emphasis on animated captions (highlight/bounce/fade), 48+ languages, 98–99% accuracy claims, brand kit support. Source: https://www.submagic.co/ai-caption

**Viral editing patterns**
- Auto‑edit features include removing silences and filler words, adding zooms, and auto‑generated B‑roll that matches transcript. Source: https://www.submagic.co/features/auto-video-editor

**Speaker tracking approaches**
- Magic Clips API supports face tracking; default enabled. Source: https://docs.submagic.co/api-reference/magic-clips

**Retention optimization techniques**
- Emphasizes caption animations and pacing cleanup to improve watch time; encourages hook titles and visual effects. Sources: https://care.submagic.co/en/article/how-to-use-magic-clips-step-by-step-guide-15mve5q/, https://www.submagic.co/features/auto-video-editor

---

### 5) Captions.ai

**Clip selection methods**
- “Long to Short” workflow extracts multiple clips from long recordings, with guidance to keep clips that stand alone and start strong. Source: https://captions.ai/help/guides/creators/repurpose-long-recording

**Caption styles**
- AI Edit applies style templates with animated captions, B‑roll, music, and motion graphics; 95+ styles. Source: https://captions.ai/help/docs/project/ai-edit

**Viral editing patterns**
- AI Edit auto‑adds transitions, sound effects, B‑roll, and motion graphics; co‑editor enables iterative refinements via natural language. Source: https://captions.ai/help/docs/project/ai-edit

**Speaker tracking approaches**
- Guidance indicates best performance with single speaker and vertical footage; less emphasis on multi‑speaker tracking compared to others. Sources: https://captions.ai/help/guides/creators/ai-edit-workflow, https://captions.ai/help/guides/edit-faster/no-timeline-edit

**Retention optimization techniques**
- Emphasis on strong hooks, clean endings, and short clips (60–90 seconds) for tighter edits and better retention. Source: https://captions.ai/help/guides/creators/repurpose-long-recording

---

## Practical takeaways for our system

1. **Generate many candidates, rank them aggressively** using a “virality score” driven by transcript hooks, emotional peaks, pacing, and visual saliency. 
2. **Hook‑first strategy**: position the strongest line at t=0–1s, even if it means trimming lead‑in or re‑ordering (when safe and coherent).
3. **Tighten pacing**: remove filler and dead air; prefer complete thoughts and clear endings.
4. **Captions are part of the clip**: use animated, word‑by‑word captions with keyword emphasis and safe‑zone placement for mobile UI.
5. **Smart reframe with active speaker tracking** in 9:16 to keep attention on the face/gesture.
6. **Retention‑aware endings**: ensure a payoff or “button” in the last 2–3 seconds.

---

## Notes & limitations

- Many claims in vendor marketing are directional, not audited. We should treat them as hypotheses to be tested in our own scoring and evaluation loop.
- The strongest evidence of *how* models work is from Opus’ public API documentation, which outlines specific signal categories.

