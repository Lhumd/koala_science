"""Render a human-readable analysis of the bakeoff metrics.

Consumes runs/metrics.json produced by `tools.eval_agents --per-domain`,
picks the per-cluster winner (highest Spearman within cluster, falling back
to overall if cluster subset is empty), and writes a markdown summary to
eval_data/bakeoff_analysis.md.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BakeoffSummary:
    overall: dict[str, dict[str, float]]
    per_domain: dict[str, dict[str, dict[str, float]]]


def load_metrics(metrics_path: Path) -> BakeoffSummary:
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    return BakeoffSummary(
        overall=payload["overall"],
        per_domain=payload.get("per_domain", {}),
    )


def pick_winners(summary: BakeoffSummary) -> dict[str, str]:
    winners: dict[str, str] = {}
    for cluster, per_agent in summary.per_domain.items():
        if not per_agent:
            winners[cluster] = _best_by_spearman(summary.overall)
            continue
        winners[cluster] = _best_by_spearman(per_agent)
    return winners


def _best_by_spearman(per_agent: dict[str, dict[str, float]]) -> str:
    return max(per_agent.items(), key=lambda pair: pair[1]["spearman"])[0]


def render_analysis_markdown(summary: BakeoffSummary, winners: dict[str, str]) -> str:
    lines: list[str] = []
    lines.append("# Bakeoff analysis — ICML 2025 labeled eval set")
    lines.append("")
    lines.append(
        "Per-candidate and per-cluster Spearman + ROC-AUC against the held-out "
        "ICML 2025 accept/reject labels. Winners are picked by cluster-Spearman."
    )
    lines.append("")

    lines.append("## Overall (all eval papers)")
    lines.append("")
    lines.append("| Candidate | Spearman | AUC | n |")
    lines.append("|---|---|---|---|")
    for name, m in sorted(
        summary.overall.items(), key=lambda pair: pair[1]["spearman"], reverse=True
    ):
        lines.append(
            f"| {name} | {m['spearman']:.4f} | {m['auc']:.4f} | {int(m['n'])} |"
        )
    lines.append("")

    lines.append("## Per-cluster")
    lines.append("")
    for cluster in sorted(summary.per_domain.keys()):
        per_agent = summary.per_domain[cluster]
        if not per_agent:
            lines.append(f"### {cluster} (no papers in this cluster — winner from overall)")
            lines.append("")
            continue
        lines.append(f"### {cluster}")
        lines.append("")
        lines.append("| Candidate | Spearman | AUC | n |")
        lines.append("|---|---|---|---|")
        for name, m in sorted(
            per_agent.items(), key=lambda pair: pair[1]["spearman"], reverse=True
        ):
            lines.append(
                f"| {name} | {m['spearman']:.4f} | {m['auc']:.4f} | {int(m['n'])} |"
            )
        lines.append("")

    lines.append("## Winners by cluster")
    lines.append("")
    lines.append("| Cluster | Winning candidate |")
    lines.append("|---|---|")
    for cluster in sorted(winners.keys()):
        lines.append(f"| {cluster} | **{winners[cluster]}** |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Portfolio 4 is vindicated if each specialist (`rl_systems`, `theory`, "
        "`applications`) wins its own cluster. If `baseline_a0` wins a cluster, "
        "deploy it instead of that specialist for the competition. If "
        "`baseline_a0` wins two or more clusters, pivot to Portfolio 2 "
        "(three calibrated generalists)."
    )
    lines.append("")

    lines.append("## Baselines to compare against")
    lines.append("")
    lines.append("- Stanford paperreview.ai (ICLR 2025): Spearman 0.42 / AUC 0.75")
    lines.append("- Human inter-reviewer (ICLR 2025): Spearman 0.41")
    lines.append("- DeepReviewer (ICLR 2025): Spearman 0.40")
    lines.append("")
    lines.append(
        "Any candidate above 0.30 is a live deploy; above 0.40 is competitive "
        "with the published state of the art."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render bakeoff analysis markdown.")
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary = load_metrics(args.metrics)
    winners = pick_winners(summary)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_analysis_markdown(summary, winners),
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    print(f"winners: {winners}")


if __name__ == "__main__":
    main()
