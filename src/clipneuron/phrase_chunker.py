from __future__ import annotations

from dataclasses import dataclass

from .segmenter import TranscriptWord


@dataclass(frozen=True)
class CaptionChunk:
    chunk_index: int
    start: float
    end: float
    words: tuple[TranscriptWord, ...]
    text: str
    lines: tuple[str, ...]


def chunk_transcript(
    words: list[TranscriptWord],
    clip_start: float,
    clip_end: float,
    min_words: int = 2,
    max_words: int = 5,
    pause_threshold: float = 0.45,
) -> list[CaptionChunk]:
    filtered = [word for word in words if word.start < clip_end and word.end > clip_start]
    if not filtered:
        return []

    groups: list[list[TranscriptWord]] = []
    current: list[TranscriptWord] = []
    for word in filtered:
        if current:
            gap = max(0.0, word.start - current[-1].end)
            if _should_break(current, word, gap, max_words, pause_threshold):
                groups.append(current)
                current = []
        current.append(word)
    if current:
        groups.append(current)

    groups = _merge_short_groups(groups, min_words, max_words)
    return [
        CaptionChunk(
            chunk_index=index,
            start=group[0].start,
            end=group[-1].end,
            words=tuple(group),
            text=" ".join(word.text for word in group),
            lines=tuple(balance_lines(group)),
        )
        for index, group in enumerate(groups, start=1)
    ]


def balance_lines(words: list[TranscriptWord]) -> list[str]:
    tokens = [word.text for word in words]
    if len(tokens) <= 3:
        return [" ".join(tokens)]

    char_lengths = [len(token) for token in tokens]
    total = sum(char_lengths)
    split_index = len(tokens)
    running = 0
    for index, length in enumerate(char_lengths, start=1):
        running += length
        if running >= total / 2:
            split_index = index
            break

    split_index = max(2, min(len(tokens) - 1, split_index))
    left = tokens[:split_index]
    right = tokens[split_index:]
    if len(right) == 1 and len(left) > 2:
        right.insert(0, left.pop())
    return [" ".join(left), " ".join(right)]


def _should_break(
    current: list[TranscriptWord],
    candidate: TranscriptWord,
    gap: float,
    max_words: int,
    pause_threshold: float,
) -> bool:
    if gap >= pause_threshold:
        return True
    if len(current) >= max_words:
        return True
    if current[-1].text.endswith((".", "!", "?")):
        return True
    if current[-1].text.endswith(",") and len(current) >= 2:
        return True
    return False


def _merge_short_groups(
    groups: list[list[TranscriptWord]], min_words: int, max_words: int
) -> list[list[TranscriptWord]]:
    if not groups:
        return []
    merged: list[list[TranscriptWord]] = []
    index = 0
    while index < len(groups):
        group = groups[index]
        if len(group) < min_words and index + 1 < len(groups):
            candidate = group + groups[index + 1]
            if len(candidate) <= max(max_words, min_words + 1):
                merged.append(candidate)
                index += 2
                continue
        if len(group) < min_words and merged and len(merged[-1]) + len(group) <= max_words:
            merged[-1].extend(group)
            index += 1
            continue
        merged.append(group)
        index += 1
    return merged
