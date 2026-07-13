from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TranscriptWord:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class Sentence:
    start: float
    end: float
    text: str
    words: tuple[TranscriptWord, ...]


HOOK_PHRASES = (
    "here's why",
    "the truth is",
    "you won't believe",
    "the secret",
    "most people",
    "the reason",
    "the biggest mistake",
    "what nobody tells you",
    "this is why",
    "listen to this",
)


PUNCTUATION = {".", "?", "!"}


def words_to_sentences(
    words: Iterable[TranscriptWord], pause_s: float = 1.0
) -> list[Sentence]:
    words = list(words)
    if not words:
        return []

    sentences: list[Sentence] = []
    current: list[TranscriptWord] = [words[0]]
    for prev, word in zip(words, words[1:]):
        gap = word.start - prev.end
        current.append(word)
        if gap >= pause_s or prev.text.endswith(tuple(PUNCTUATION)):
            sentences.append(_build_sentence(current))
            current = []
    if current:
        sentences.append(_build_sentence(current))
    return sentences


def generate_candidates(
    sentences: list[Sentence],
    min_s: float,
    max_s: float,
    target: int,
) -> list[Sentence]:
    candidates: list[Sentence] = []
    for i, sentence in enumerate(sentences):
        start = sentence.start
        end = sentence.end
        words: list[TranscriptWord] = list(sentence.words)
        text_parts = [sentence.text]
        j = i + 1
        while end - start < max_s and j < len(sentences):
            if end - start >= min_s:
                candidates.append(
                    Sentence(
                        start=start,
                        end=end,
                        text=" ".join(text_parts),
                        words=tuple(words),
                    )
                )
            next_sentence = sentences[j]
            end = next_sentence.end
            words.extend(next_sentence.words)
            text_parts.append(next_sentence.text)
            j += 1
        if end - start >= min_s and end - start <= max_s:
            candidates.append(
                Sentence(
                    start=start, end=end, text=" ".join(text_parts), words=tuple(words)
                )
            )

    if len(candidates) <= target:
        return candidates
    # keep early diverse candidates by stride
    stride = max(1, len(candidates) // target)
    return candidates[::stride][:target]


def _build_sentence(words: list[TranscriptWord]) -> Sentence:
    start = words[0].start
    end = words[-1].end
    text = " ".join(word.text for word in words).strip()
    return Sentence(start=start, end=end, text=text, words=tuple(words))
