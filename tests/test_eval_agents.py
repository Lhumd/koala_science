from pathlib import Path

import pytest

from tools.eval_agents import (
    AgentPrediction,
    EvalPaper,
    auc,
    compute_metrics,
    load_eval_set,
    spearman,
)


def test_spearman_perfect_monotonic() -> None:
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert spearman(x, y) == pytest.approx(1.0)


def test_spearman_perfect_anticorrelation() -> None:
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [50.0, 40.0, 30.0, 20.0, 10.0]
    assert spearman(x, y) == pytest.approx(-1.0)


def test_spearman_zero_correlation() -> None:
    x = [1.0, 2.0, 3.0, 4.0]
    y = [3.0, 1.0, 4.0, 2.0]
    assert spearman(x, y) == pytest.approx(0.0, abs=1e-9)


def test_auc_perfect_separation() -> None:
    scores = [0.1, 0.2, 0.8, 0.9]
    labels = [0, 0, 1, 1]
    assert auc(scores, labels) == pytest.approx(1.0)


def test_auc_inverse_separation() -> None:
    scores = [0.9, 0.8, 0.2, 0.1]
    labels = [0, 0, 1, 1]
    assert auc(scores, labels) == pytest.approx(0.0)


def test_auc_random() -> None:
    scores = [0.5, 0.5, 0.5, 0.5]
    labels = [0, 0, 1, 1]
    assert auc(scores, labels) == pytest.approx(0.5)


def test_load_eval_set(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "eval.jsonl"
    jsonl_path.write_text(
        '{"paper_id":"p1","title":"A","abstract":"a","pdf_url":"u1","domain":"RL","accepted":true}\n'
        '{"paper_id":"p2","title":"B","abstract":"b","pdf_url":null,"domain":"Theory","accepted":false}\n',
        encoding="utf-8",
    )
    papers = load_eval_set(jsonl_path)
    assert len(papers) == 2
    assert papers[0].paper_id == "p1"
    assert papers[0].accepted is True
    assert papers[0].domain == "RL"
    assert papers[1].pdf_url is None
    assert papers[1].accepted is False


def _make_eval_set() -> list[EvalPaper]:
    return [
        EvalPaper("p1", "t1", "a1", None, "RL", True),
        EvalPaper("p2", "t2", "a2", None, "RL", False),
        EvalPaper("p3", "t3", "a3", None, "Theory", True),
        EvalPaper("p4", "t4", "a4", None, "Theory", False),
    ]


def test_compute_metrics_per_agent() -> None:
    eval_set = _make_eval_set()
    predictions = [
        AgentPrediction("p1", "agent_good", 9.0),
        AgentPrediction("p2", "agent_good", 2.0),
        AgentPrediction("p3", "agent_good", 8.0),
        AgentPrediction("p4", "agent_good", 3.0),
        AgentPrediction("p1", "agent_bad", 1.0),
        AgentPrediction("p2", "agent_bad", 9.0),
        AgentPrediction("p3", "agent_bad", 2.0),
        AgentPrediction("p4", "agent_bad", 8.0),
    ]
    results = compute_metrics(predictions, eval_set)
    assert results["agent_good"]["spearman"] > 0.8
    assert results["agent_good"]["auc"] == pytest.approx(1.0)
    assert results["agent_good"]["n"] == 4
    assert results["agent_bad"]["spearman"] < -0.8
    assert results["agent_bad"]["auc"] == pytest.approx(0.0)


def test_compute_metrics_per_domain_filter() -> None:
    eval_set = _make_eval_set()
    predictions = [
        AgentPrediction("p1", "agent_good", 9.0),
        AgentPrediction("p2", "agent_good", 2.0),
        AgentPrediction("p3", "agent_good", 1.0),
        AgentPrediction("p4", "agent_good", 8.0),
    ]
    rl_only = compute_metrics(predictions, eval_set, domain="RL")
    theory_only = compute_metrics(predictions, eval_set, domain="Theory")
    assert rl_only["agent_good"]["auc"] == pytest.approx(1.0)
    assert theory_only["agent_good"]["auc"] == pytest.approx(0.0)
    assert rl_only["agent_good"]["n"] == 2
    assert theory_only["agent_good"]["n"] == 2
