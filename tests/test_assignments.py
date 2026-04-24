from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.assignments import (
    ClaimRecord,
    claim_paper,
    is_claimed,
    load_assignments,
    primary_agent_for_domains,
)


def test_load_assignments_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "nope.jsonl"
    assert load_assignments(path) == []


def test_load_assignments_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "assignments.jsonl"
    claim_paper(path, paper_id="p1", agent_name="rl_systems")
    claim_paper(path, paper_id="p2", agent_name="theory")
    claims = load_assignments(path)
    assert len(claims) == 2
    assert claims[0].paper_id == "p1"
    assert claims[0].agent_name == "rl_systems"
    assert claims[1].paper_id == "p2"


def test_is_claimed_false_when_empty(tmp_path: Path) -> None:
    path = tmp_path / "assignments.jsonl"
    assert not is_claimed(path, paper_id="p1")


def test_is_claimed_true_after_claim(tmp_path: Path) -> None:
    path = tmp_path / "assignments.jsonl"
    claim_paper(path, paper_id="p1", agent_name="rl_systems")
    assert is_claimed(path, paper_id="p1")
    assert not is_claimed(path, paper_id="p2")


def test_claim_paper_returns_winning_claim_when_first(tmp_path: Path) -> None:
    path = tmp_path / "assignments.jsonl"
    claim = claim_paper(path, paper_id="p1", agent_name="rl_systems")
    assert claim.paper_id == "p1"
    assert claim.agent_name == "rl_systems"


def test_claim_paper_returns_first_claim_when_already_claimed(tmp_path: Path) -> None:
    path = tmp_path / "assignments.jsonl"
    first = claim_paper(path, paper_id="p1", agent_name="rl_systems")
    second = claim_paper(path, paper_id="p1", agent_name="theory")
    assert second.agent_name == "rl_systems"
    assert second.claimed_at == first.claimed_at
    assert len(load_assignments(path)) == 1


def test_primary_agent_for_domains_rl_first_wins() -> None:
    assert primary_agent_for_domains(["d/Reinforcement-Learning", "d/Theory"]) == "rl_systems"


def test_primary_agent_for_domains_theory_first_wins() -> None:
    assert primary_agent_for_domains(["d/Theory", "d/Deep-Learning"]) == "theory"


def test_primary_agent_for_domains_applications_fairness() -> None:
    assert primary_agent_for_domains(["d/Fairness", "d/Deep-Learning"]) == "applications"


def test_primary_agent_for_domains_healthcare() -> None:
    assert primary_agent_for_domains(["d/Healthcare"]) == "applications"


def test_primary_agent_for_domains_optimization_goes_to_rl_systems() -> None:
    assert primary_agent_for_domains(["d/Optimization"]) == "rl_systems"


def test_primary_agent_for_domains_fallback_to_baseline_a0() -> None:
    assert primary_agent_for_domains(["d/NLP", "d/Computer-Vision"]) == "baseline_a0"


def test_primary_agent_for_domains_empty_falls_back() -> None:
    assert primary_agent_for_domains([]) == "baseline_a0"
