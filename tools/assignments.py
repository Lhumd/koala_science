"""Paper-claim assignment log for multi-agent coordination.

Siblings under one OpenReview ID must not duplicate-comment. `agents/assignments.jsonl`
is an append-only log where each sibling claims papers before first-commenting.
First claim wins; subsequent attempts on the same paper are no-ops. Uses `fcntl.flock`
to serialize writes from concurrent agents.

Usage from an agent's Bash loop:

    result = claim_paper(Path("agents/assignments.jsonl"), paper_id, agent_name)
    if result.agent_name != agent_name:
        # sibling already claimed; skip first-commenting, contribute to shared_reasoning instead
        ...

Domain-routing helper:

    primary = primary_agent_for_domains(paper.domains)
    if primary != my_agent_name:
        # defer to sibling; don't even attempt to claim
        ...
"""

from __future__ import annotations

import fcntl
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ClaimRecord:
    paper_id: str
    agent_name: str
    claimed_at: str


_DOMAIN_ROUTING: list[tuple[str, tuple[str, ...]]] = [
    ("applications", (
        "d/Trustworthy-ML", "d/Fairness", "d/Privacy", "d/Safety",
        "d/Healthcare", "d/Climate", "d/Social-Sciences",
        "d/Biosciences", "d/Physical-Sciences", "d/Medical",
    )),
    ("theory", (
        "d/Theory", "d/Probabilistic-Methods", "d/Bandits",
        "d/Statistical-Learning", "d/Learning-Theory",
    )),
    ("rl_systems", (
        "d/Reinforcement-Learning", "d/Robotics", "d/Optimization",
        "d/ML-Systems", "d/Distributed-Systems", "d/Control",
    )),
]


def load_assignments(path: Path) -> list[ClaimRecord]:
    if not path.exists():
        return []
    records: list[ClaimRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        records.append(
            ClaimRecord(
                paper_id=payload["paper_id"],
                agent_name=payload["agent_name"],
                claimed_at=payload["claimed_at"],
            )
        )
    return records


def is_claimed(path: Path, *, paper_id: str) -> bool:
    for claim in load_assignments(path):
        if claim.paper_id == paper_id:
            return True
    return False


def claim_paper(path: Path, *, paper_id: str, agent_name: str) -> ClaimRecord:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.seek(0)
            for line in f:
                if not line.strip():
                    continue
                payload = json.loads(line)
                if payload["paper_id"] == paper_id:
                    return ClaimRecord(
                        paper_id=payload["paper_id"],
                        agent_name=payload["agent_name"],
                        claimed_at=payload["claimed_at"],
                    )
            claimed_at = datetime.now(timezone.utc).isoformat()
            new_record = ClaimRecord(
                paper_id=paper_id, agent_name=agent_name, claimed_at=claimed_at
            )
            f.write(
                json.dumps(
                    {
                        "paper_id": new_record.paper_id,
                        "agent_name": new_record.agent_name,
                        "claimed_at": new_record.claimed_at,
                    }
                )
                + "\n"
            )
            f.flush()
            return new_record
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def primary_agent_for_domains(domains: list[str]) -> str:
    if not domains:
        return "baseline_a0"
    for d in domains:
        for agent, owned in _DOMAIN_ROUTING:
            if d in owned:
                return agent
    return "baseline_a0"
