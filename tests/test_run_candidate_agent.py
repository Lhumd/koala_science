from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.eval_agents import EvalPaper
from tools.run_candidate_agent import (
    build_user_message,
    parse_score,
    run_candidate_on_paper,
    run_candidate_over_eval_set,
)


def test_parse_score_basic() -> None:
    assert parse_score("SCORE: 7.5") == pytest.approx(7.5)


def test_parse_score_with_surrounding_reasoning() -> None:
    text = "Soundness: 3/4. Originality: 3/4. ... Final recommendation: Weak Accept.\nSCORE: 5.8\n"
    assert parse_score(text) == pytest.approx(5.8)


def test_parse_score_integer() -> None:
    assert parse_score("...\nSCORE: 9\n") == pytest.approx(9.0)


def test_parse_score_clamped_to_range() -> None:
    assert parse_score("SCORE: 11.5") == pytest.approx(10.0)
    assert parse_score("SCORE: -2.0") == pytest.approx(0.0)


def test_parse_score_missing_raises() -> None:
    with pytest.raises(ValueError, match="no score"):
        parse_score("I don't want to score this paper.")


def test_build_user_message_includes_fields() -> None:
    paper = EvalPaper(
        paper_id="p1",
        title="Some Paper",
        abstract="We do X.",
        pdf_url=None,
        domain="rl_systems",
        accepted=True,
    )
    msg = build_user_message(paper)
    assert "Some Paper" in msg
    assert "We do X." in msg
    assert "p1" in msg
    assert "rl_systems" in msg
    assert "SCORE:" in msg


def _backend_returning(score: float) -> MagicMock:
    backend = MagicMock()
    backend.score.return_value = score
    return backend


def test_run_candidate_on_paper_delegates_to_backend() -> None:
    backend = _backend_returning(7.2)
    paper = EvalPaper("p1", "T", "A", None, "rl_systems", True)
    score = run_candidate_on_paper(
        system_prompt="You are a reviewer.",
        paper=paper,
        backend=backend,
    )
    assert score == pytest.approx(7.2)
    assert backend.score.called
    kwargs = backend.score.call_args.kwargs
    assert kwargs["system_prompt"] == "You are a reviewer."
    assert "p1" in kwargs["user_message"]


def test_run_candidate_over_eval_set_writes_jsonl(tmp_path: Path) -> None:
    papers = [
        EvalPaper("p1", "T1", "A1", None, "rl_systems", True),
        EvalPaper("p2", "T2", "A2", None, "theory_probabilistic", False),
    ]
    backend = MagicMock()
    backend.score.side_effect = [8.1, 3.4]
    out_path = tmp_path / "predictions.jsonl"
    run_candidate_over_eval_set(
        system_prompt="sp",
        eval_set=papers,
        agent_name="testagent",
        output_path=out_path,
        backend=backend,
    )
    lines = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert '"paper_id": "p1"' in lines[0]
    assert '"agent_name": "testagent"' in lines[0]
    assert '"score": 8.1' in lines[0]
    assert '"score": 3.4' in lines[1]


def test_run_candidate_over_eval_set_skips_on_error(tmp_path: Path) -> None:
    papers = [
        EvalPaper("p1", "T1", "A1", None, "rl_systems", True),
        EvalPaper("p2", "T2", "A2", None, "theory_probabilistic", False),
    ]
    backend = MagicMock()
    backend.score.side_effect = [RuntimeError("api overloaded"), 5.0]
    out_path = tmp_path / "predictions.jsonl"
    run_candidate_over_eval_set(
        system_prompt="sp",
        eval_set=papers,
        agent_name="testagent",
        output_path=out_path,
        backend=backend,
        on_error="skip",
    )
    lines = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert '"paper_id": "p2"' in lines[0]
