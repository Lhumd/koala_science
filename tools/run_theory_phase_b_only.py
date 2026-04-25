"""Run Phase B on a single already-scored paper, reusing the Phase A artifacts.

Used to validate that the Phase B deep-dive either confirms or principled-
rewrites the Phase A draft on a paper that didn't make the original top-1.

Usage: uv run python -m tools.run_theory_phase_b_only <paper_id>
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from tools.run_theory_full_pipeline import (
    PROMPT_PATH,
    PAPERS_PATH,
    OUT_DIR,
    REPORTS_DIR,
    FULL_REPORTS_DIR,
    SUBMISSIONS_PATH,
    SCRATCH_DIR,
    PHASE_B_TIMEOUT_S,
    REPO,
    build_phase_b_user_message,
    call_claude,
    fetch_pdf_text,
    parse_phase_b,
    write_phase_b_artifacts,
    build_submission_payload,
)


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: run_theory_phase_b_only <paper_id>", file=sys.stderr)
        sys.exit(2)
    pid = sys.argv[1]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    papers = {
        json.loads(line)["paper_id"]: json.loads(line)
        for line in PAPERS_PATH.read_text().splitlines() if line.strip()
    }
    if pid not in papers:
        print(f"paper {pid} not found in {PAPERS_PATH}", file=sys.stderr)
        sys.exit(2)
    paper = papers[pid]

    scratch = (SCRATCH_DIR / f"{pid}.md").read_text(encoding="utf-8")
    draft = (REPORTS_DIR / f"{pid}.md").read_text(encoding="utf-8")
    verdict = None
    for line in (REPO / "docs" / "verdicts.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec["paper_id"] == pid and rec["dim"] == "Theory":
            verdict = rec
    if verdict is None:
        print(f"no Theory verdict for {pid} in docs/verdicts.jsonl", file=sys.stderr)
        sys.exit(2)
    phase_a = {
        "scratch": scratch,
        "comment": draft,
        "verdict": {"Theory": {"score": verdict["score"], "confidence": verdict["confidence"]}},
        "score": verdict["score"],
        "confidence": verdict["confidence"],
    }

    print(f"=== Phase B re-run for {pid} ({'acc' if paper.get('accepted') else 'rej'}) ===", flush=True)
    print(f"Phase A: score={phase_a['score']} conf={phase_a['confidence']} draft_words={len(draft.split())}", flush=True)
    pdf_text = fetch_pdf_text(paper)
    print(f"PDF: {len(pdf_text)} chars", flush=True)
    user_msg = build_phase_b_user_message(paper, pdf_text, phase_a)

    t0 = time.monotonic()
    stdout, stderr, rc = call_claude(system_prompt, user_msg, PHASE_B_TIMEOUT_S)
    elapsed = time.monotonic() - t0
    (OUT_DIR / f"{pid}_phaseB.txt").write_text(stdout, encoding="utf-8")
    if stderr:
        (OUT_DIR / f"{pid}_phaseB.stderr.txt").write_text(stderr, encoding="utf-8")

    result = parse_phase_b(stdout)
    if result["status"] != "ok":
        print(f"parse failed: {result}", flush=True)
        sys.exit(1)

    write_phase_b_artifacts(pid, result)
    payload = build_submission_payload(pid, result["final_comment"])
    with SUBMISSIONS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")

    final_words = len(result["final_comment"].split())
    full_words = len(result["full_report"].split())
    confirmed = result["final_comment"].strip() == draft.strip()
    print(
        f"Phase B done: full_report_words={full_words} final_comment_words={final_words} "
        f"elapsed={elapsed:.1f}s rewrote={'no' if confirmed else 'yes'}",
        flush=True,
    )


if __name__ == "__main__":
    sys.exit(main())
