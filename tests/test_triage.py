from tools.triage import (
    PaperTriageInput,
    TriageDecision,
    score_paper,
    select_top_papers,
)


def _paper(
    *,
    paper_id: str = "p1",
    status: str = "in_review",
    commenter_count: int = 0,
    already_commented: bool = False,
    domain_cluster: str = "rl_systems",
    hours_since_release: float = 5.0,
) -> PaperTriageInput:
    return PaperTriageInput(
        paper_id=paper_id,
        status=status,
        commenter_count=commenter_count,
        already_commented=already_commented,
        domain_cluster=domain_cluster,
        hours_since_release=hours_since_release,
    )


def test_score_paper_rejects_wrong_phase() -> None:
    d = score_paper(_paper(status="deliberating"), agent_cluster="rl_systems")
    assert not d.worth_joining
    assert "in_review" in d.reason.lower()


def test_score_paper_rejects_reviewed_phase() -> None:
    d = score_paper(_paper(status="reviewed"), agent_cluster="rl_systems")
    assert not d.worth_joining


def test_score_paper_rejects_below_threshold() -> None:
    d = score_paper(_paper(commenter_count=3), agent_cluster="rl_systems")
    assert not d.worth_joining
    assert "commenter" in d.reason.lower()


def test_score_paper_accepts_sweet_spot_5_commenters() -> None:
    d = score_paper(_paper(commenter_count=5), agent_cluster="rl_systems")
    assert d.worth_joining
    assert d.score > 0.5


def test_score_paper_accepts_sweet_spot_6_7_commenters() -> None:
    d = score_paper(_paper(commenter_count=6), agent_cluster="rl_systems")
    assert d.worth_joining
    assert d.score > 0.7


def test_score_paper_deprioritizes_20_plus_commenters() -> None:
    busy = score_paper(_paper(commenter_count=22), agent_cluster="rl_systems")
    sweet = score_paper(_paper(commenter_count=6), agent_cluster="rl_systems")
    assert sweet.score > busy.score


def test_score_paper_skips_already_commented() -> None:
    d = score_paper(
        _paper(commenter_count=6, already_commented=True),
        agent_cluster="rl_systems",
    )
    assert not d.worth_joining
    assert "already commented" in d.reason.lower()


def test_score_paper_prefers_in_cluster() -> None:
    in_cluster = score_paper(
        _paper(commenter_count=6, domain_cluster="rl_systems"),
        agent_cluster="rl_systems",
    )
    out_cluster = score_paper(
        _paper(commenter_count=6, domain_cluster="theory_probabilistic"),
        agent_cluster="rl_systems",
    )
    assert in_cluster.score > out_cluster.score


def test_score_paper_penalizes_near_in_review_deadline() -> None:
    early = score_paper(
        _paper(commenter_count=6, hours_since_release=5.0),
        agent_cluster="rl_systems",
    )
    late = score_paper(
        _paper(commenter_count=6, hours_since_release=47.0),
        agent_cluster="rl_systems",
    )
    assert early.score > late.score


def test_select_top_papers_sorts_by_score_desc_and_applies_limit() -> None:
    inputs = [
        _paper(paper_id="low", commenter_count=2),
        _paper(paper_id="sweet", commenter_count=6),
        _paper(paper_id="busy", commenter_count=25),
        _paper(paper_id="edge", commenter_count=5),
    ]
    top = select_top_papers(inputs, agent_cluster="rl_systems", limit=2)
    assert len(top) == 2
    assert top[0].paper_id in {"sweet", "edge"}
    assert top[1].paper_id in {"sweet", "edge"}
    assert "low" not in {d.paper_id for d in top}
    assert "busy" not in {d.paper_id for d in top}


def test_select_top_papers_filters_not_worth_joining() -> None:
    inputs = [
        _paper(paper_id="dont", commenter_count=2),
        _paper(paper_id="yes", commenter_count=6),
    ]
    top = select_top_papers(inputs, agent_cluster="rl_systems", limit=10)
    assert len(top) == 1
    assert top[0].paper_id == "yes"
