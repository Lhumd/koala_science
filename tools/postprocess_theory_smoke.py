"""Split raw smoke outputs into the canonical Phase A artifacts.

Reads runs/theory_smoke/<paper_id>.txt (the raw two-block agent response) and
runs/theory_smoke/summary.jsonl, and produces:

- agents/theory/reports/<paper_id>.md  — comment body (markdown block only)
- docs/verdicts.jsonl                  — append-only verdict log (one line per
                                         scored paper, dim=Theory)
- agents/theory/triage_phase_a.md      — shortlist of top-5 by
                                         (10 - theory) * conf**2 after the
                                         gate confidence >= 4 AND theory <= 3

Scratch files (agents/theory/scratch/<paper_id>.md) are NOT written by this
postprocess: the smoke run had no tool use, so no real theorem/assumption
inventory was produced. Faking scratch content would falsify the audit trail
the new prompt explicitly demands.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SMOKE_DIR = REPO / "runs" / "theory_smoke"
SUMMARY_PATH = SMOKE_DIR / "summary.jsonl"
REPORTS_DIR = REPO / "agents" / "theory" / "reports"
SCRATCH_NOTE = REPO / "agents" / "theory" / "scratch" / "README.md"
VERDICTS_PATH = REPO / "docs" / "verdicts.jsonl"
TRIAGE_PATH = REPO / "agents" / "theory" / "triage_phase_a.md"

JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
MD_BLOCK = re.compile(r"```markdown\s*\n(.*?)\n```", re.DOTALL)


def main() -> None:
    rows = [json.loads(line) for line in SUMMARY_PATH.read_text().splitlines() if line.strip()]
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH_NOTE.parent.mkdir(parents=True, exist_ok=True)
    VERDICTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    SCRATCH_NOTE.write_text(
        "Scratch files would normally live at "
        "`agents/theory/scratch/<paper_id>.md` (theorem inventory, "
        "assumption inventory, load-bearing lemma list, appendix cross-check, "
        "score rationale). The 2026-04-25 smoke run was abstract-only with "
        "no tool use, so no real scratch artifacts were produced. Phase A "
        "in production must populate this directory via the agent's tool use.\n",
        encoding="utf-8",
    )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    verdict_lines: list[str] = []
    triage_candidates: list[dict] = []

    for row in rows:
        paper_id = row["paper_id"]
        if row["status"] != "ok":
            continue
        raw = (SMOKE_DIR / f"{paper_id}.txt").read_text(encoding="utf-8")

        md_match = MD_BLOCK.search(raw)
        if md_match:
            (REPORTS_DIR / f"{paper_id}.md").write_text(
                md_match.group(1).rstrip() + "\n", encoding="utf-8"
            )

        score = row["score"]
        confidence = row["confidence"]
        if score is None or confidence is None:
            continue

        verdict_lines.append(
            json.dumps(
                {
                    "paper_id": paper_id,
                    "dim": "Theory",
                    "score": score,
                    "confidence": confidence,
                    "agent_name": "theory",
                    "ts": ts,
                }
            )
        )
        triage_candidates.append(
            {
                "paper_id": paper_id,
                "score": score,
                "confidence": confidence,
                "priority": (10 - score) * (confidence ** 2),
                "passes_gate": confidence >= 4 and score <= 3,
            }
        )

    if verdict_lines:
        with VERDICTS_PATH.open("a", encoding="utf-8") as f:
            for line in verdict_lines:
                f.write(line + "\n")

    triage_candidates.sort(key=lambda r: r["priority"], reverse=True)
    survivors = [c for c in triage_candidates if c["passes_gate"]][:5]

    triage_md_lines = [
        "# Theory Phase A — triage shortlist (smoke run)",
        "",
        f"Generated {ts} from {SUMMARY_PATH.relative_to(REPO)}.",
        "",
        "Gate: `confidence >= 4 AND theory_score <= 3`. "
        "Priority: `(10 - theory_score) * confidence ** 2`.",
        "",
    ]
    if survivors:
        triage_md_lines.append("| paper_id | score | conf | priority |")
        triage_md_lines.append("|---|---|---|---|")
        for c in survivors:
            triage_md_lines.append(
                f"| {c['paper_id']} | {c['score']} | {c['confidence']} | "
                f"{c['priority']:.1f} |"
            )
    else:
        triage_md_lines.append(
            "**No papers pass the Phase B gate from this batch.** "
            "All 5 papers landed at confidence 2 because the smoke "
            "fixture only provided abstracts. With full PDF access, "
            "the gate is expected to admit a non-empty shortlist."
        )
    triage_md_lines.append("")
    triage_md_lines.append("## All scored candidates")
    triage_md_lines.append("")
    triage_md_lines.append("| paper_id | score | conf | priority | passes gate |")
    triage_md_lines.append("|---|---|---|---|---|")
    for c in triage_candidates:
        triage_md_lines.append(
            f"| {c['paper_id']} | {c['score']} | {c['confidence']} | "
            f"{c['priority']:.1f} | {'✅' if c['passes_gate'] else '❌'} |"
        )
    triage_md_lines.append("")
    TRIAGE_PATH.write_text("\n".join(triage_md_lines), encoding="utf-8")

    print(f"Wrote {len([r for r in rows if r['status']=='ok'])} comments to {REPORTS_DIR.relative_to(REPO)}/")
    print(f"Appended {len(verdict_lines)} verdict lines to {VERDICTS_PATH.relative_to(REPO)}")
    print(f"Wrote shortlist to {TRIAGE_PATH.relative_to(REPO)} ({len(survivors)} survivors)")


if __name__ == "__main__":
    main()
