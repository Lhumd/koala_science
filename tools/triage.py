"""Paper-triage heuristic — score candidate papers by "worth commenting on" for a given agent.

Implements the karma-math insight from AGENT_DESIGNS.md:

- 5-comment threshold gates verdicts; papers below that are wasted karma
- 6–8 commenters is the sweet spot (enough to cite; still room to be early-ancestor)
- 20+ commenter papers have diluted `N/(v·a)` returns and are likely over the 3-karma cap
- In-cluster papers produce higher-value comments than out-of-cluster
- Late-in-`in_review` papers (hours_since_release ≥ 40) have reduced citation runway

Usage (during the competition, from an agent's loop):

    inputs = [PaperTriageInput(...) for p in koala_papers]
    top = select_top_papers(inputs, agent_cluster="rl_systems", limit=5)
    # comment on top[0..N].paper_id
"""

from __future__ import annotations

from dataclasses import dataclass


_MIN_COMMENTERS_FOR_VERDICT = 5
_SWEET_SPOT_MIN = 5
_SWEET_SPOT_MAX = 10
_BUSY_COMMENTER_THRESHOLD = 20
_IN_REVIEW_PHASE_DURATION_H = 48.0
_LATE_DEADLINE_PENALTY_START_H = 40.0


@dataclass(frozen=True)
class PaperTriageInput:
    paper_id: str
    status: str
    commenter_count: int
    already_commented: bool
    domain_cluster: str
    hours_since_release: float


@dataclass(frozen=True)
class TriageDecision:
    paper_id: str
    worth_joining: bool
    score: float
    reason: str


def score_paper(paper: PaperTriageInput, *, agent_cluster: str) -> TriageDecision:
    if paper.status != "in_review":
        return TriageDecision(
            paper_id=paper.paper_id,
            worth_joining=False,
            score=0.0,
            reason=f"not in_review (status={paper.status})",
        )
    if paper.already_commented:
        return TriageDecision(
            paper_id=paper.paper_id,
            worth_joining=False,
            score=0.0,
            reason="already commented on this paper",
        )
    if paper.commenter_count < _MIN_COMMENTERS_FOR_VERDICT - 1:
        return TriageDecision(
            paper_id=paper.paper_id,
            worth_joining=False,
            score=0.0,
            reason=f"too few commenters ({paper.commenter_count} < {_MIN_COMMENTERS_FOR_VERDICT - 1}); verdict unreachable",
        )

    score = 0.0
    reasons: list[str] = []

    if _SWEET_SPOT_MIN <= paper.commenter_count <= _SWEET_SPOT_MAX:
        score += 0.7
        reasons.append(f"sweet spot ({paper.commenter_count} commenters)")
    elif paper.commenter_count == _MIN_COMMENTERS_FOR_VERDICT - 1:
        score += 0.5
        reasons.append(f"you'd unlock verdict threshold ({paper.commenter_count}+1=5)")
    elif paper.commenter_count < _BUSY_COMMENTER_THRESHOLD:
        score += 0.4
        reasons.append(f"well-populated ({paper.commenter_count} commenters)")
    else:
        score += 0.15
        reasons.append(
            f"busy ({paper.commenter_count} commenters; karma dilution + 3-karma cap risk)"
        )

    if paper.domain_cluster == agent_cluster:
        score += 0.3
        reasons.append("in-cluster")
    else:
        reasons.append(f"out-of-cluster ({paper.domain_cluster}≠{agent_cluster})")

    if paper.hours_since_release >= _LATE_DEADLINE_PENALTY_START_H:
        remaining = max(0.0, _IN_REVIEW_PHASE_DURATION_H - paper.hours_since_release)
        penalty = min(0.4, (paper.hours_since_release - _LATE_DEADLINE_PENALTY_START_H) / 8.0 * 0.4)
        score -= penalty
        reasons.append(f"late ({remaining:.0f}h left in in_review, -{penalty:.2f})")

    score = max(0.0, min(1.0, score))
    return TriageDecision(
        paper_id=paper.paper_id,
        worth_joining=score >= 0.4,
        score=score,
        reason="; ".join(reasons),
    )


def select_top_papers(
    papers: list[PaperTriageInput],
    *,
    agent_cluster: str,
    limit: int,
) -> list[TriageDecision]:
    decisions = [score_paper(p, agent_cluster=agent_cluster) for p in papers]
    worth = [d for d in decisions if d.worth_joining]
    worth.sort(key=lambda d: d.score, reverse=True)
    return worth[:limit]
