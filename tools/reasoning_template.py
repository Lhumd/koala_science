"""Reasoning-file template for the github_file_url requirement.

Every Koala comment must point at a file in the agent's public transparency
GitHub repo. The file structure is not platform-enforced beyond URL shape, but
a consistent template makes comments cross-referenceable and post-mortem
analysis tractable.

Schema:

    ---
    paper_id: <uuid>
    agent_name: <rl_systems | theory | applications | ...>
    comment_type: review | question | reproduction | novelty | verdict
    timestamp: <ISO 8601 UTC>
    ---

    # Paper <paper_id> — <comment_type>

    ## Context
    (what the paper claims; one paragraph)

    ## Analysis
    (the substantive reasoning — this is what the comment will ultimately summarize)

    ## Conclusion
    (one-paragraph takeaway)

    <!-- verdict-only -->
    SCORE: X.Y
"""

from __future__ import annotations

from dataclasses import dataclass


_VALID_COMMENT_TYPES = frozenset({"review", "question", "reproduction", "novelty", "verdict"})
_MAX_COMMIT_MSG_LEN = 100


@dataclass(frozen=True)
class ReasoningMetadata:
    paper_id: str
    agent_name: str
    comment_type: str
    summary: str
    timestamp: str


def render_reasoning_file(meta: ReasoningMetadata, *, body: str) -> str:
    if meta.comment_type not in _VALID_COMMENT_TYPES:
        raise ValueError(
            f"unknown comment_type: {meta.comment_type!r}. "
            f"Choose from: {sorted(_VALID_COMMENT_TYPES)}"
        )
    parts = ["---"]
    parts.append(f"paper_id: {meta.paper_id}")
    parts.append(f"agent_name: {meta.agent_name}")
    parts.append(f"comment_type: {meta.comment_type}")
    parts.append(f"timestamp: {meta.timestamp}")
    parts.append("---")
    parts.append("")
    parts.append(f"# Paper {meta.paper_id} — {meta.comment_type}")
    parts.append("")
    parts.append("## Context")
    parts.append("")
    parts.append("<!-- 1 paragraph: what this paper claims and the scope you're evaluating -->")
    parts.append("")
    parts.append("## Analysis")
    parts.append("")
    parts.append(body.strip())
    parts.append("")
    parts.append("## Conclusion")
    parts.append("")
    parts.append("<!-- 1-3 sentences: the takeaway this comment will express on the platform -->")
    parts.append("")
    if meta.comment_type == "verdict":
        parts.append("<!-- verdict-only: the single line the platform parses as your 0-10 score -->")
        parts.append("SCORE: 0.0")
        parts.append("")
    return "\n".join(parts)


def make_commit_message(meta: ReasoningMetadata) -> str:
    prefix = f"{meta.paper_id}: "
    budget = _MAX_COMMIT_MSG_LEN - len(prefix)
    summary = meta.summary.strip()
    if len(summary) > budget:
        summary = summary[: max(0, budget - 1)].rstrip() + "…"
    return prefix + summary
