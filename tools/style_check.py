"""Style-uniqueness check — guards against the "near-identical comments" anti-behavior.

Koala's `GLOBAL_RULES.md` prohibits "submitting near-identical comments or verdicts
across multiple papers". The platform's auto-moderator may flag them, and even if
it doesn't, cross-paper similarity patterns are observable signals competitors can
exploit.

This module compares a candidate comment against the agent's previous N outputs
using token-level Jaccard similarity and flags the comment as non-unique if any
prior comment exceeds a configurable threshold (default 0.6). Rough but cheap.

For more sensitive detection (semantic near-duplicates that survive light
paraphrasing) an embedding-based check is a natural upgrade — not implemented
here because it would need a model call per comparison. Jaccard catches the
common failure mode where an agent reuses the same skeleton across papers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

_STOPWORDS = frozenset({
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "by",
    "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its",
    "and", "or", "but", "nor", "so", "yet",
    "as", "if", "then", "than",
    "do", "does", "did", "doing", "done",
    "have", "has", "had", "having",
    "will", "would", "shall", "should", "may", "might", "can", "could",
    "not", "no", "yes",
    "i", "we", "you", "he", "she", "they", "them", "their",
    "from", "about", "into", "through", "over", "under",
    "more", "most", "some", "any", "all", "both",
    "up", "down", "out", "off",
})


@dataclass(frozen=True)
class StyleCheckResult:
    is_unique: bool
    max_similarity: float
    most_similar_index: int | None
    threshold: float


def tokenize(text: str) -> list[str]:
    lowered = text.lower()
    tokens = _TOKEN_PATTERN.findall(lowered)
    return [t for t in tokens if t not in _STOPWORDS]


def jaccard_similarity(a: str, b: str) -> float:
    sa = set(tokenize(a))
    sb = set(tokenize(b))
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    intersection = sa & sb
    union = sa | sb
    return len(intersection) / len(union)


def check_uniqueness(
    candidate: str,
    prior_comments: list[str],
    *,
    threshold: float = 0.6,
) -> StyleCheckResult:
    if not prior_comments:
        return StyleCheckResult(
            is_unique=True, max_similarity=0.0, most_similar_index=None, threshold=threshold
        )
    sims = [jaccard_similarity(candidate, prior) for prior in prior_comments]
    max_sim = max(sims)
    most_similar_index = sims.index(max_sim)
    return StyleCheckResult(
        is_unique=max_sim < threshold,
        max_similarity=max_sim,
        most_similar_index=most_similar_index,
        threshold=threshold,
    )
