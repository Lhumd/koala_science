"""Evaluate candidate agent designs against a labeled historical paper set.

Usage:
    python -m tools.eval_agents \\
        --eval-set data/icml_2025_eval.jsonl \\
        --predictions runs/predictions.jsonl \\
        --output runs/metrics.json

The eval harness takes predictions that some upstream pipeline generated
(one score per (agent, paper) pair) and computes per-agent Spearman and
ROC-AUC against the accept/reject labels. Optionally subsets by domain
so you can see each specialist's performance on its own cluster.

Wiring a candidate agent to produce predictions is left to the caller
(see run_agent_on_paper stub below) because the binding depends on which
backend and prompt you're testing.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvalPaper:
    paper_id: str
    title: str
    abstract: str
    pdf_url: str | None
    domain: str | None
    accepted: bool


@dataclass(frozen=True)
class AgentPrediction:
    paper_id: str
    agent_name: str
    score: float


def load_eval_set(path: Path) -> list[EvalPaper]:
    with path.open(encoding="utf-8") as f:
        return [EvalPaper(**json.loads(line)) for line in f if line.strip()]


def load_predictions(path: Path) -> list[AgentPrediction]:
    with path.open(encoding="utf-8") as f:
        return [AgentPrediction(**json.loads(line)) for line in f if line.strip()]


def spearman(x: list[float], y: list[float]) -> float:
    if len(x) != len(y):
        raise ValueError(f"length mismatch: {len(x)} vs {len(y)}")
    if len(x) < 2:
        raise ValueError("need at least 2 points for correlation")
    rx = _ranks(x)
    ry = _ranks(y)
    n = len(rx)
    mean_x = sum(rx) / n
    mean_y = sum(ry) / n
    num = sum((rx[i] - mean_x) * (ry[i] - mean_y) for i in range(n))
    denom_x = sum((r - mean_x) ** 2 for r in rx) ** 0.5
    denom_y = sum((r - mean_y) ** 2 for r in ry) ** 0.5
    if denom_x == 0 or denom_y == 0:
        return 0.0
    return num / (denom_x * denom_y)


def _ranks(values: list[float]) -> list[float]:
    """Average-rank assignment; handles ties by averaging positional ranks."""
    indexed = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def auc(scores: list[float], labels: list[int]) -> float:
    """ROC-AUC via the Mann–Whitney U interpretation."""
    positives = [scores[i] for i in range(len(labels)) if labels[i] == 1]
    negatives = [scores[i] for i in range(len(labels)) if labels[i] == 0]
    if not positives or not negatives:
        raise ValueError("AUC requires at least one positive and one negative label")
    total = 0.0
    for p in positives:
        for n in negatives:
            if p > n:
                total += 1.0
            elif p == n:
                total += 0.5
    return total / (len(positives) * len(negatives))


def compute_metrics(
    predictions: list[AgentPrediction],
    eval_set: list[EvalPaper],
    *,
    domain: str | None = None,
) -> dict[str, dict[str, float]]:
    paper_index = {p.paper_id: p for p in eval_set}
    per_agent: dict[str, list[tuple[float, int]]] = {}
    for pred in predictions:
        paper = paper_index.get(pred.paper_id)
        if paper is None:
            continue
        if domain is not None and paper.domain != domain:
            continue
        per_agent.setdefault(pred.agent_name, []).append(
            (pred.score, 1 if paper.accepted else 0)
        )
    results: dict[str, dict[str, float]] = {}
    for agent_name, scored in per_agent.items():
        scores = [s for s, _ in scored]
        labels = [a for _, a in scored]
        results[agent_name] = {
            "spearman": spearman(scores, [float(a) for a in labels]),
            "auc": auc(scores, labels),
            "n": float(len(scored)),
        }
    return results


def run_agent_on_paper(agent_config_dir: Path, paper: EvalPaper) -> float:
    """Produce a 0–10 verdict score from a candidate agent for one paper.

    Wire this to whatever runtime you use — direct Anthropic SDK call with
    the agent's system prompt, a subprocess invocation of claude-code, or
    reva's own launch infrastructure. The signature is stable so you can
    swap implementations while keeping the eval harness identical.
    """
    raise NotImplementedError(
        "wire this to your backend (Anthropic SDK / claude-code subprocess / reva launch)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate candidate agents.")
    parser.add_argument("--eval-set", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--per-domain",
        action="store_true",
        help="Also report metrics split by eval-set domain.",
    )
    args = parser.parse_args()

    eval_set = load_eval_set(args.eval_set)
    predictions = load_predictions(args.predictions)

    report: dict[str, object] = {"overall": compute_metrics(predictions, eval_set)}
    if args.per_domain:
        domains = sorted({p.domain for p in eval_set if p.domain is not None})
        report["per_domain"] = {
            d: compute_metrics(predictions, eval_set, domain=d) for d in domains
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
