from __future__ import annotations

import re
from dataclasses import dataclass

from .phrase_chunker import CaptionChunk

KEYWORD_CUES = {
    "secret",
    "truth",
    "mistake",
    "result",
    "viral",
    "growth",
    "wrong",
    "crazy",
    "shocking",
    "important",
}

CTA_CUES = {
    "subscribe",
    "follow",
    "comment",
    "share",
    "watch",
    "download",
    "join",
    "click",
    "save",
    "like",
}


@dataclass(frozen=True)
class HighlightedWord:
    word: str
    kind: str
    word_index: int


@dataclass(frozen=True)
class TypographyPlan:
    chunk_index: int
    highlighted_words: tuple[HighlightedWord, ...]


def build_typography_plan(chunks: list[CaptionChunk]) -> list[TypographyPlan]:
    plans: list[TypographyPlan] = []
    for chunk in chunks:
        highlighted: list[HighlightedWord] = []
        for index, word in enumerate(chunk.words):
            kind = classify_word(word.text)
            if kind is not None:
                highlighted.append(
                    HighlightedWord(word=word.text, kind=kind, word_index=index)
                )
        plans.append(
            TypographyPlan(chunk_index=chunk.chunk_index, highlighted_words=tuple(highlighted))
        )
    return plans


def classify_word(text: str) -> str | None:
    normalized = re.sub(r"[^a-z0-9₹$]+", "", text.lower())
    if not normalized:
        return None
    if re.search(r"\d", text):
        if any(symbol in text.lower() for symbol in ("$", "₹", "rs", "usd", "inr")):
            return "money"
        return "number"
    if normalized in CTA_CUES:
        return "cta"
    if normalized in KEYWORD_CUES or len(normalized) >= 8:
        return "keyword"
    return None
