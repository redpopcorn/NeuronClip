from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HookComponents:
    curiosity: float
    emotional: float
    storytelling: float
    educational: float
    contrarian: float

    @property
    def score(self) -> float:
        total = (
            0.25 * self.curiosity
            + 0.20 * self.emotional
            + 0.20 * self.storytelling
            + 0.20 * self.educational
            + 0.15 * self.contrarian
        )
        return max(0.0, min(100.0, total))


CURIOSITY_CUES = (
    "why",
    "how",
    "what if",
    "here's",
    "imagine",
    "secret",
    "truth",
    "the reason",
    "you won't believe",
)

EMOTIONAL_CUES = (
    "amazing",
    "shocking",
    "wild",
    "insane",
    "love",
    "hate",
    "fear",
    "angry",
    "excited",
    "scared",
)

STORY_CUES = ("when", "then", "once", "I", "we", "my", "story")

EDU_CUES = (
    "because",
    "therefore",
    "lesson",
    "framework",
    "step",
    "rule",
    "principle",
    "strategy",
)

CONTRARIAN_CUES = (
    "but",
    "however",
    "actually",
    "counterintuitive",
    "most people",
    "everyone thinks",
    "wrong",
)


def analyze_hook(text: str) -> HookComponents:
    lower = text.lower()
    curiosity = _score_hits(lower, CURIOSITY_CUES, base=45, weight=10)
    emotional = _score_hits(lower, EMOTIONAL_CUES, base=40, weight=12)
    storytelling = _score_hits(lower, STORY_CUES, base=35, weight=8)
    educational = _score_hits(lower, EDU_CUES, base=40, weight=10)
    contrarian = _score_hits(lower, CONTRARIAN_CUES, base=40, weight=12)
    return HookComponents(
        curiosity=curiosity,
        emotional=emotional,
        storytelling=storytelling,
        educational=educational,
        contrarian=contrarian,
    )


def _score_hits(text: str, cues: tuple[str, ...], base: float, weight: float) -> float:
    hits = sum(1 for cue in cues if cue in text)
    score = base + hits * weight
    if "?" in text:
        score += 5
    return max(0.0, min(100.0, score))
