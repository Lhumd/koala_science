import pytest

from tools.reasoning_template import (
    ReasoningMetadata,
    make_commit_message,
    render_reasoning_file,
)


def _meta(**overrides) -> ReasoningMetadata:
    defaults = dict(
        paper_id="abc123",
        agent_name="rl_systems",
        comment_type="review",
        summary="underpowered ablation in Table 2",
        timestamp="2026-04-25T14:30:00Z",
    )
    defaults.update(overrides)
    return ReasoningMetadata(**defaults)


def test_render_has_frontmatter() -> None:
    out = render_reasoning_file(_meta(), body="The ablation in Table 2 uses only 3 seeds.")
    assert out.startswith("---\n")
    assert "paper_id: abc123" in out
    assert "agent_name: rl_systems" in out
    assert "comment_type: review" in out


def test_render_includes_body_verbatim() -> None:
    body = "Section 3.2 contradicts Figure 4 regarding the sample-efficiency claim."
    out = render_reasoning_file(_meta(), body=body)
    assert body in out


def test_render_sections_present_for_all_comment_types() -> None:
    for ct in ("review", "question", "reproduction", "novelty", "verdict"):
        out = render_reasoning_file(_meta(comment_type=ct), body="body text")
        assert "# Paper " in out
        assert "## Context" in out
        assert "## Analysis" in out
        assert "## Conclusion" in out


def test_render_verdict_includes_score_reminder() -> None:
    out = render_reasoning_file(_meta(comment_type="verdict"), body="verdict body")
    assert "SCORE:" in out


def test_render_non_verdict_does_not_include_score_line() -> None:
    out = render_reasoning_file(_meta(comment_type="review"), body="review body")
    assert "SCORE:" not in out


def test_render_raises_on_unknown_comment_type() -> None:
    with pytest.raises(ValueError, match="unknown comment_type"):
        render_reasoning_file(_meta(comment_type="bogus"), body="body")


def test_commit_message_formats_paper_id_and_summary() -> None:
    msg = make_commit_message(_meta(paper_id="p42", summary="unfair baseline in Sec 5"))
    assert msg.startswith("p42: ")
    assert "unfair baseline in Sec 5" in msg


def test_commit_message_truncates_long_summary() -> None:
    long = "x" * 400
    msg = make_commit_message(_meta(summary=long))
    assert len(msg) <= 100
