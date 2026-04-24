from pathlib import Path

from tools.build_eval_set import (
    RawPaperRecord,
    classify_cluster,
    write_eval_jsonl,
)
from tools.eval_agents import load_eval_set


def test_classify_cluster_rl_and_robotics() -> None:
    assert classify_cluster(["RL"]) == "rl_systems"
    assert classify_cluster(["robotics"]) == "rl_systems"
    assert classify_cluster(["ML systems"]) == "rl_systems"
    assert classify_cluster(["optimization"]) == "rl_systems"


def test_classify_cluster_theory() -> None:
    assert classify_cluster(["ML theory"]) == "theory_probabilistic"
    assert classify_cluster(["bandits"]) == "theory_probabilistic"
    assert classify_cluster(["probabilistic methods"]) == "theory_probabilistic"


def test_classify_cluster_applications() -> None:
    assert classify_cluster(["healthcare"]) == "applications_trustworthy"
    assert classify_cluster(["trustworthy ML"]) == "applications_trustworthy"
    assert classify_cluster(["fairness"]) == "applications_trustworthy"
    assert classify_cluster(["evaluation benchmark"]) == "applications_trustworthy"


def test_classify_cluster_unknown_falls_back_to_general() -> None:
    assert classify_cluster(["somewhere-novel"]) == "general"
    assert classify_cluster([]) == "general"


def test_classify_cluster_prefers_first_match() -> None:
    assert classify_cluster(["RL", "theory"]) == "rl_systems"


def test_classify_cluster_substring_match() -> None:
    assert classify_cluster(["gaussian process"]) == "theory_probabilistic"
    assert classify_cluster(["causal discovery"]) == "theory_probabilistic"
    assert classify_cluster(["data poisoning attack"]) == "applications_trustworthy"
    assert classify_cluster(["multi-agent reinforcement learning"]) == "rl_systems"
    assert classify_cluster(["distributed optimization"]) == "rl_systems"
    assert classify_cluster(["differential privacy"]) == "applications_trustworthy"


def test_classify_cluster_case_insensitive() -> None:
    assert classify_cluster(["Reinforcement Learning"]) == "rl_systems"
    assert classify_cluster(["BAYESIAN INFERENCE"]) == "theory_probabilistic"


def test_write_eval_jsonl_roundtrip(tmp_path: Path) -> None:
    records = [
        RawPaperRecord(
            paper_id="icml25-001",
            title="Sample Accepted",
            abstract="An abstract.",
            pdf_url="https://example.com/a.pdf",
            raw_domains=["RL"],
            accepted=True,
        ),
        RawPaperRecord(
            paper_id="icml25-002",
            title="Sample Rejected",
            abstract="Another abstract.",
            pdf_url=None,
            raw_domains=["ML theory"],
            accepted=False,
        ),
    ]
    out_path = tmp_path / "eval.jsonl"
    write_eval_jsonl(records, out_path)

    loaded = load_eval_set(out_path)
    assert len(loaded) == 2
    assert loaded[0].paper_id == "icml25-001"
    assert loaded[0].domain == "rl_systems"
    assert loaded[0].accepted is True
    assert loaded[1].domain == "theory_probabilistic"
    assert loaded[1].pdf_url is None
    assert loaded[1].accepted is False
