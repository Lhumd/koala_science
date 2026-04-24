import json
from pathlib import Path

from tools.analyze_bakeoff import (
    BakeoffSummary,
    load_metrics,
    pick_winners,
    render_analysis_markdown,
)


def _make_metrics(tmp_path: Path, metrics: dict) -> Path:
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")
    return path


def test_load_metrics(tmp_path: Path) -> None:
    metrics = {
        "overall": {"baseline_a0": {"spearman": 0.3, "auc": 0.7, "n": 100}},
        "per_domain": {
            "rl_systems": {"baseline_a0": {"spearman": 0.35, "auc": 0.72, "n": 30}}
        },
    }
    path = _make_metrics(tmp_path, metrics)
    summary = load_metrics(path)
    assert summary.overall["baseline_a0"]["spearman"] == 0.3
    assert summary.per_domain["rl_systems"]["baseline_a0"]["auc"] == 0.72


def test_pick_winners_per_cluster() -> None:
    summary = BakeoffSummary(
        overall={
            "baseline_a0": {"spearman": 0.30, "auc": 0.70, "n": 120},
            "rl_systems": {"spearman": 0.25, "auc": 0.68, "n": 120},
            "theory": {"spearman": 0.40, "auc": 0.78, "n": 120},
            "applications": {"spearman": 0.28, "auc": 0.69, "n": 120},
        },
        per_domain={
            "rl_systems": {
                "baseline_a0": {"spearman": 0.20, "auc": 0.62, "n": 30},
                "rl_systems": {"spearman": 0.45, "auc": 0.80, "n": 30},
                "theory": {"spearman": 0.15, "auc": 0.58, "n": 30},
                "applications": {"spearman": 0.22, "auc": 0.63, "n": 30},
            },
            "theory_probabilistic": {
                "baseline_a0": {"spearman": 0.30, "auc": 0.70, "n": 30},
                "rl_systems": {"spearman": 0.20, "auc": 0.62, "n": 30},
                "theory": {"spearman": 0.55, "auc": 0.85, "n": 30},
                "applications": {"spearman": 0.25, "auc": 0.65, "n": 30},
            },
            "applications_trustworthy": {
                "baseline_a0": {"spearman": 0.25, "auc": 0.65, "n": 30},
                "rl_systems": {"spearman": 0.15, "auc": 0.58, "n": 30},
                "theory": {"spearman": 0.20, "auc": 0.62, "n": 30},
                "applications": {"spearman": 0.40, "auc": 0.78, "n": 30},
            },
            "general": {
                "baseline_a0": {"spearman": 0.35, "auc": 0.74, "n": 30},
                "rl_systems": {"spearman": 0.30, "auc": 0.71, "n": 30},
                "theory": {"spearman": 0.28, "auc": 0.69, "n": 30},
                "applications": {"spearman": 0.26, "auc": 0.68, "n": 30},
            },
        },
    )
    winners = pick_winners(summary)
    assert winners["rl_systems"] == "rl_systems"
    assert winners["theory_probabilistic"] == "theory"
    assert winners["applications_trustworthy"] == "applications"
    assert winners["general"] == "baseline_a0"


def test_render_analysis_markdown_includes_key_sections() -> None:
    summary = BakeoffSummary(
        overall={"baseline_a0": {"spearman": 0.3, "auc": 0.7, "n": 100}},
        per_domain={
            "rl_systems": {"baseline_a0": {"spearman": 0.35, "auc": 0.72, "n": 30}}
        },
    )
    md = render_analysis_markdown(summary, winners={"rl_systems": "baseline_a0"})
    assert "# Bakeoff analysis" in md
    assert "Overall" in md
    assert "baseline_a0" in md
    assert "rl_systems" in md
    assert "Winners by cluster" in md


def test_pick_winners_falls_back_to_overall_if_cluster_empty() -> None:
    summary = BakeoffSummary(
        overall={
            "baseline_a0": {"spearman": 0.30, "auc": 0.70, "n": 120},
            "theory": {"spearman": 0.40, "auc": 0.78, "n": 120},
        },
        per_domain={"rl_systems": {}},
    )
    winners = pick_winners(summary)
    assert winners["rl_systems"] == "theory"
