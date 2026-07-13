from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from .segmenter import TranscriptWord

logger = logging.getLogger("clipneuron.transcript_repair")

FILLER_WORDS = {
    "um",
    "uh",
    "hmm",
    "erm",
    "like",
    "basically",
    "literally",
    "matlab",
    "toh",
    "haan",
    "hmmm",
}

SENTENCE_BREAK_WORDS = {
    "but",
    "because",
    "kyunki",
    "lekin",
    "par",
    "toh",
    "then",
    "so",
    "aur",
}


@dataclass(frozen=True)
class TranscriptRepairReport:
    removed_fillers: list[str]
    merged_words: list[dict]
    punctuation_restorations: list[dict]


@dataclass(frozen=True)
class RepairedTranscript:
    words: list[TranscriptWord]
    report: TranscriptRepairReport


def repair_transcript(words: list[TranscriptWord]) -> RepairedTranscript:
    repaired: list[TranscriptWord] = []
    removed_fillers: list[str] = []
    merged_words: list[dict] = []
    punctuation_restorations: list[dict] = []

    for word in words:
        token = _normalize_spacing(word.text)
        if not token:
            continue
        normalized = _normalize_token(token)
        if normalized in FILLER_WORDS and len(words) > 3:
            removed_fillers.append(token)
            continue

        current = TranscriptWord(start=word.start, end=word.end, text=token)
        if repaired and _should_merge(repaired[-1], current):
            previous = repaired.pop()
            merged_text = _merge_tokens(previous.text, current.text)
            merged_words.append(
                {
                    "from": [previous.text, current.text],
                    "to": merged_text,
                    "start": previous.start,
                    "end": current.end,
                }
            )
            repaired.append(
                TranscriptWord(
                    start=previous.start,
                    end=current.end,
                    text=merged_text,
                )
            )
            continue

        repaired.append(current)

    repaired = _restore_punctuation(repaired, punctuation_restorations)
    repaired = _capitalize_sentences(repaired)
    logger.info(
        "Transcript repaired: %s words, %s fillers removed, %s merges",
        len(repaired),
        len(removed_fillers),
        len(merged_words),
    )
    return RepairedTranscript(
        words=repaired,
        report=TranscriptRepairReport(
            removed_fillers=removed_fillers,
            merged_words=merged_words,
            punctuation_restorations=punctuation_restorations,
        ),
    )


def _normalize_spacing(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9₹$]+", "", text.lower())


def _should_merge(left: TranscriptWord, right: TranscriptWord) -> bool:
    if right.start - left.end > 0.12:
        return False
    left_norm = _normalize_token(left.text)
    right_norm = _normalize_token(right.text)
    if not left_norm or not right_norm:
        return False
    if any(char.isdigit() for char in left_norm + right_norm):
        return False
    if left.text.endswith(('.', '!', '?', ',')):
        return False
    return len(left_norm) <= 4 and len(right_norm) <= 5


def _merge_tokens(left: str, right: str) -> str:
    if left.endswith('-'):
        return f"{left[:-1]}{right}"
    return f"{left}{right}"


def _restore_punctuation(
    words: list[TranscriptWord],
    restorations: list[dict],
) -> list[TranscriptWord]:
    if not words:
        return []
    restored: list[TranscriptWord] = []
    for index, word in enumerate(words):
        token = word.text
        pause_after = 0.0
        if index + 1 < len(words):
            pause_after = max(0.0, words[index + 1].start - word.end)
        normalized = _normalize_token(token)
        punctuation = ""
        if pause_after >= 0.7 or normalized in SENTENCE_BREAK_WORDS:
            punctuation = "."
        elif pause_after >= 0.35:
            punctuation = ","
        if punctuation and not token.endswith((".", "!", "?", ",")):
            token = f"{token}{punctuation}"
            restorations.append({"word": word.text, "punctuation": punctuation})
        restored.append(TranscriptWord(start=word.start, end=word.end, text=token))
    if restored and not restored[-1].text.endswith((".", "!", "?")):
        restorations.append({"word": restored[-1].text, "punctuation": "."})
        last = restored[-1]
        restored[-1] = TranscriptWord(start=last.start, end=last.end, text=f"{last.text}.")
    return restored


def _capitalize_sentences(words: list[TranscriptWord]) -> list[TranscriptWord]:
    capitalized: list[TranscriptWord] = []
    should_capitalize = True
    for word in words:
        text = word.text
        if should_capitalize and text:
            text = text[0].upper() + text[1:]
        capitalized.append(TranscriptWord(start=word.start, end=word.end, text=text))
        should_capitalize = text.endswith((".", "!", "?"))
    return capitalized
