"""End-to-end Theory Phase A + Phase B smoke pipeline for 5 new papers.

Deviations from the production runtime (claude-cli has no file-write tool, no
PaperLantern MCP, no real Koala API):

- Scratch + verdict + comment are emitted as a 3-block envelope in one call,
  instead of via tool-driven file writes.
- Phase B emits full_report + reconciled comment as a 2-block envelope.
- "Submission" is a JSON payload written to disk, not a real post_comment call.
- Novelty-retrieval-dependent critiques are hedged per the prompt's
  hallucination guard (line 223).

Outputs:
- agents/theory/scratch/<id>.md
- agents/theory/reports/<id>.md       (Phase A draft, overwritten if Phase B rewrites)
- agents/theory/full_reports/<id>.md  (Phase B only)
- docs/verdicts.jsonl                 (append per scored paper)
- agents/theory/triage_phase_a.md     (shortlist + gate decision)
- runs/theory_pipeline/<id>_phaseA.txt, <id>_phaseB.txt  (raw model outputs)
- runs/theory_pipeline/submissions.jsonl  (simulated post_comment payloads)
- runs/theory_pipeline/summary.json
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROMPT_PATH = REPO / "agent_configs" / "theory" / "system_prompt.md"
PAPERS_PATH = REPO / "runs" / "theory_pipeline_papers.jsonl"
PDF_DIR = Path("/tmp/koala_pdfs")
OUT_DIR = REPO / "runs" / "theory_pipeline"
AGENT_DIR = REPO / "agent_configs" / "theory"
SCRATCH_DIR = AGENT_DIR / "scratch"
REPORTS_DIR = AGENT_DIR / "reports"
FULL_REPORTS_DIR = AGENT_DIR / "full_reports"
TRIAGE_PATH = AGENT_DIR / "triage_phase_a.md"
VERDICTS_PATH = REPO / "docs" / "verdicts.jsonl"
SUBMISSIONS_PATH = OUT_DIR / "submissions.jsonl"
SUMMARY_PATH = OUT_DIR / "summary.json"
GH_USER_REPO = "Lhumd/koala_science"
GH_FULL_REPORT_PATH_PREFIX = "agent_configs/theory/full_reports"

MODEL = "claude-sonnet-4-6"
PHASE_A_TIMEOUT_S = 900
PHASE_B_TIMEOUT_S = 1200
PDF_MAX_PAGES = 30

GATE_SCORE_MAX = 3
GATE_CONF_MIN = 4
PHASE_B_DEMO_FALLBACK_TOPK = 5

PHASE_A_BLOCK = re.compile(r"```(scratch|json|markdown)\s*\n(.*?)\n```", re.DOTALL)
PHASE_B_BLOCK = re.compile(r"```(full_report|markdown)\s*\n(.*?)\n```", re.DOTALL)


_CTRL_CHARS = "".join(chr(c) for c in range(32) if chr(c) not in "\t\n\r")
_CTRL_TABLE = str.maketrans({c: " " for c in _CTRL_CHARS})


def fetch_pdf_text(paper: dict) -> str:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = PDF_DIR / f"{paper['paper_id']}.pdf"
    if not pdf_path.exists():
        urllib.request.urlretrieve(paper["pdf_url"], pdf_path)
    from pypdf import PdfReader
    reader = PdfReader(str(pdf_path))
    pages = reader.pages[:PDF_MAX_PAGES]
    raw = "\n".join(page.extract_text() or "" for page in pages)
    return raw.translate(_CTRL_TABLE)


def call_claude(system_prompt: str, user_message: str, timeout_s: int) -> tuple[str, str, int]:
    cmd = [
        "claude",
        "--print",
        "--append-system-prompt",
        system_prompt,
        "--model",
        MODEL,
        user_message,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    return result.stdout, result.stderr, result.returncode


def build_phase_a_user_message(paper: dict, pdf_text: str) -> str:
    return (
        "## OPERATING NOTICE — smoke harness override\n\n"
        "You are running Phase A in an offline smoke harness invoked by the "
        "owner. The runtime cannot execute tool calls (no file writes, no "
        "MCP, no PDF retrieval). The full PDF text has been extracted and is "
        "inlined below — treat it as your `pdf_url` read.\n\n"
        "Because file writes are unavailable, emit your scratch + verdict + "
        "comment as THREE consecutive fenced blocks in this exact order, "
        "with no other text:\n\n"
        "1. ```scratch — body of `agents/theory/scratch/<short_id>.md` per "
        "step 2 of your prompt (theorem inventory, assumption inventory, "
        "load-bearing lemmas, appendix proof location, score rationale). "
        "Must be >500 chars and theory-grounded.\n"
        "2. ```json — `{\"Theory\": {\"score\": <1-10>, \"confidence\": "
        "<2-5>}}`\n"
        "3. ```markdown — the 80–400 word publishable comment per step 5.\n\n"
        "All other rules of your prompt apply unchanged: stay in the Theory "
        "lane, hallucination guard on novelty (PaperLantern unavailable), "
        "epistemic discipline on absence claims. Confidence 1 does not "
        "exist; if you genuinely cannot read the paper, emit a `SKIP` line "
        "as your only output (no fenced blocks).\n\n"
        f"## Paper metadata\n\n"
        f"- paper_id: `{paper['paper_id']}`\n"
        f"- title: {paper['title']}\n"
        f"- domain: {paper.get('domain', 'general')}\n"
        f"- pdf_url: {paper.get('pdf_url')}\n\n"
        f"## Abstract\n\n{paper['abstract']}\n\n"
        f"## Full PDF text (extracted via pypdf)\n\n{pdf_text}\n"
    )


def build_phase_b_user_message(paper: dict, pdf_text: str, phase_a: dict) -> str:
    return (
        "## OPERATING NOTICE — smoke harness, Phase B\n\n"
        "You are running Phase B for this paper in the same smoke harness "
        "as Phase A. The harness has no file-write tool and no Koala API. "
        "Emit Phase B output as TWO consecutive fenced blocks in this exact "
        "order, with no other text:\n\n"
        "1. ```full_report — body of `agents/theory/full_reports/<short_id>.md` "
        "per Phase B step 2: headline claim, proof walk-through, "
        "counter-example attempt, prior-work diff (hedged if you cannot "
        "name a specific prior theorem), all weaknesses with severity, "
        "defense paragraph.\n"
        "2. ```markdown — the FINAL reconciled comment that will be submitted "
        "to Koala as `post_comment.content_markdown`. If the deep-dive "
        "confirmed the Phase A draft, you may submit it verbatim; if the "
        "deep-dive invalidated any part, rewrite it. The reconciled comment "
        "must be consistent with the full_report.\n\n"
        "PaperLantern is unavailable in this harness — apply the "
        "hallucination guard: do not invent prior theorems for a non-novelty "
        "claim; pivot the comment angle if needed.\n\n"
        f"## Paper metadata\n\n"
        f"- paper_id: `{paper['paper_id']}`\n"
        f"- title: {paper['title']}\n\n"
        f"## Phase A verdict (your own)\n\n"
        f"```json\n{json.dumps(phase_a['verdict'])}\n```\n\n"
        f"## Phase A scratch (your own)\n\n{phase_a['scratch']}\n\n"
        f"## Phase A draft comment (your own)\n\n{phase_a['comment']}\n\n"
        f"## Full PDF text (re-read for Phase B)\n\n{pdf_text}\n"
    )


def parse_phase_a(raw: str) -> dict:
    blocks = {label: body for label, body in PHASE_A_BLOCK.findall(raw)}
    if "SKIP" in raw and not blocks:
        skip = re.search(r"SKIP\s+(\S+)\s+reason=(\S+)", raw)
        return {"status": "skipped", "reason": skip.group(2) if skip else "unknown"}
    if not all(k in blocks for k in ("scratch", "json", "markdown")):
        return {"status": "parse_fail", "missing": [k for k in ("scratch","json","markdown") if k not in blocks]}
    try:
        verdict = json.loads(blocks["json"])
    except json.JSONDecodeError as e:
        return {"status": "json_decode_fail", "error": str(e)}
    return {
        "status": "ok",
        "scratch": blocks["scratch"],
        "comment": blocks["markdown"],
        "verdict": verdict,
        "score": verdict["Theory"]["score"],
        "confidence": verdict["Theory"]["confidence"],
    }


def parse_phase_b(raw: str) -> dict:
    blocks = {label: body for label, body in PHASE_B_BLOCK.findall(raw)}
    if not all(k in blocks for k in ("full_report", "markdown")):
        return {"status": "parse_fail", "missing": [k for k in ("full_report","markdown") if k not in blocks]}
    return {
        "status": "ok",
        "full_report": blocks["full_report"],
        "final_comment": blocks["markdown"],
    }


def write_phase_a_artifacts(paper_id: str, result: dict, ts: str) -> None:
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    VERDICTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    (SCRATCH_DIR / f"{paper_id}.md").write_text(result["scratch"].rstrip() + "\n", encoding="utf-8")
    (REPORTS_DIR / f"{paper_id}.md").write_text(result["comment"].rstrip() + "\n", encoding="utf-8")
    with VERDICTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "paper_id": paper_id,
            "dim": "Theory",
            "score": result["score"],
            "confidence": result["confidence"],
            "agent_name": "theory",
            "ts": ts,
        }) + "\n")


def write_phase_b_artifacts(paper_id: str, result: dict) -> None:
    FULL_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (FULL_REPORTS_DIR / f"{paper_id}.md").write_text(result["full_report"].rstrip() + "\n", encoding="utf-8")
    (REPORTS_DIR / f"{paper_id}.md").write_text(result["final_comment"].rstrip() + "\n", encoding="utf-8")


def write_triage(phase_a_results: list[dict]) -> tuple[list[dict], list[dict]]:
    candidates = []
    for paper_id, r in phase_a_results:
        if r["status"] != "ok":
            continue
        candidates.append({
            "paper_id": paper_id,
            "score": r["score"],
            "confidence": r["confidence"],
            "priority": (10 - r["score"]) * (r["confidence"] ** 2),
            "passes_gate": r["confidence"] >= GATE_CONF_MIN and r["score"] <= GATE_SCORE_MAX,
        })
    candidates.sort(key=lambda c: c["priority"], reverse=True)
    survivors = [c for c in candidates if c["passes_gate"]][:5]
    fallback = []
    if not survivors:
        fallback = candidates[:PHASE_B_DEMO_FALLBACK_TOPK]
    lines = [
        "# Theory Phase A — triage shortlist (full pipeline run)",
        "",
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}.",
        "",
        f"Gate: `confidence >= {GATE_CONF_MIN} AND theory_score <= {GATE_SCORE_MAX}`. "
        "Priority: `(10 - theory_score) * confidence ** 2`.",
        "",
    ]
    if survivors:
        lines.append(f"**{len(survivors)} paper(s) pass the gate** — running Phase B on these.")
    else:
        lines.append(f"**No papers pass the gate.** Demo override: running Phase B on top-{PHASE_B_DEMO_FALLBACK_TOPK} by priority.")
    lines.append("")
    lines.append("| paper_id | score | conf | priority | passes gate | phase B |")
    lines.append("|---|---|---|---|---|---|")
    phase_b_set = {c["paper_id"] for c in (survivors or fallback)}
    for c in candidates:
        lines.append(
            f"| {c['paper_id']} | {c['score']} | {c['confidence']} | "
            f"{c['priority']:.1f} | {'✅' if c['passes_gate'] else '❌'} | "
            f"{'✅' if c['paper_id'] in phase_b_set else '—'} |"
        )
    lines.append("")
    TRIAGE_PATH.write_text("\n".join(lines), encoding="utf-8")
    return survivors, fallback


def build_submission_payload(paper_id: str, final_comment: str) -> dict:
    raw_url = (
        f"https://raw.githubusercontent.com/{GH_USER_REPO}/main/"
        f"{GH_FULL_REPORT_PATH_PREFIX}/{paper_id}.md"
    )
    return {
        "paper_id": paper_id,
        "content_markdown": final_comment,
        "github_file_url": raw_url,
        "_note": "simulated — no real Koala API call made",
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    papers = [json.loads(line) for line in PAPERS_PATH.read_text().splitlines() if line.strip()]
    print(f"=== Theory full pipeline: {len(papers)} papers ===", flush=True)

    phase_a_results: list[tuple[str, dict]] = []
    for i, paper in enumerate(papers, 1):
        pid = paper["paper_id"]
        print(f"\n[Phase A {i}/{len(papers)}] {pid} ({'acc' if paper.get('accepted') else 'rej'}): {paper['title'][:60]}", flush=True)
        try:
            pdf_text = fetch_pdf_text(paper)
        except Exception as e:
            print(f"  PDF fetch failed: {e}", flush=True)
            phase_a_results.append((pid, {"status": "pdf_fail", "error": str(e)}))
            continue
        print(f"  PDF: {len(pdf_text)} chars", flush=True)
        user_msg = build_phase_a_user_message(paper, pdf_text)
        t0 = time.monotonic()
        try:
            stdout, stderr, rc = call_claude(system_prompt, user_msg, PHASE_A_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT after {PHASE_A_TIMEOUT_S}s", flush=True)
            phase_a_results.append((pid, {"status": "timeout"}))
            continue
        elapsed = time.monotonic() - t0
        (OUT_DIR / f"{pid}_phaseA.txt").write_text(stdout, encoding="utf-8")
        if stderr:
            (OUT_DIR / f"{pid}_phaseA.stderr.txt").write_text(stderr, encoding="utf-8")
        result = parse_phase_a(stdout)
        result["elapsed_s"] = round(elapsed, 1)
        result["exit_code"] = rc
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if result["status"] == "ok":
            write_phase_a_artifacts(pid, result, ts)
            print(f"  -> score={result['score']} conf={result['confidence']} comment_words={len(result['comment'].split())} elapsed={elapsed:.1f}s", flush=True)
        else:
            print(f"  -> status={result['status']} elapsed={elapsed:.1f}s", flush=True)
        phase_a_results.append((pid, result))

    survivors, fallback = write_triage(phase_a_results)
    phase_b_targets = survivors or fallback
    print(f"\n=== Triage: {len(survivors)} survivors, {len(fallback)} fallback ===", flush=True)

    paper_by_id = {p["paper_id"]: p for p in papers}
    submissions: list[dict] = []

    SUBMISSIONS_PATH.write_text("", encoding="utf-8")
    for j, cand in enumerate(phase_b_targets, 1):
        pid = cand["paper_id"]
        paper = paper_by_id[pid]
        phase_a = dict(phase_a_results)[pid]
        print(f"\n[Phase B {j}/{len(phase_b_targets)}] {pid}", flush=True)
        try:
            pdf_text = fetch_pdf_text(paper)
        except Exception as e:
            print(f"  PDF re-fetch failed: {e}", flush=True)
            continue
        user_msg = build_phase_b_user_message(paper, pdf_text, phase_a)
        t0 = time.monotonic()
        try:
            stdout, stderr, rc = call_claude(system_prompt, user_msg, PHASE_B_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT after {PHASE_B_TIMEOUT_S}s", flush=True)
            continue
        elapsed = time.monotonic() - t0
        (OUT_DIR / f"{pid}_phaseB.txt").write_text(stdout, encoding="utf-8")
        if stderr:
            (OUT_DIR / f"{pid}_phaseB.stderr.txt").write_text(stderr, encoding="utf-8")
        result = parse_phase_b(stdout)
        if result["status"] != "ok":
            print(f"  -> Phase B parse failed: {result}", flush=True)
            continue
        write_phase_b_artifacts(pid, result)
        payload = build_submission_payload(pid, result["final_comment"])
        submissions.append(payload)
        with SUBMISSIONS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        print(f"  -> full_report_words={len(result['full_report'].split())} final_comment_words={len(result['final_comment'].split())} elapsed={elapsed:.1f}s", flush=True)

    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "phase_a": [
            {"paper_id": pid, **{k: v for k, v in r.items() if k not in ("scratch", "comment")}}
            for pid, r in phase_a_results
        ],
        "survivors": survivors,
        "fallback": fallback,
        "phase_b_run_on": [s["paper_id"] for s in submissions],
        "submissions": submissions,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\n=== Final summary ===", flush=True)
    print(f"Phase A scored: {sum(1 for _, r in phase_a_results if r['status']=='ok')}/{len(phase_a_results)}", flush=True)
    print(f"Survivors (gate): {len(survivors)}; Fallback (top-{PHASE_B_DEMO_FALLBACK_TOPK}): {len(fallback)}", flush=True)
    print(f"Phase B submissions written: {len(submissions)}", flush=True)
    print(f"Summary at {SUMMARY_PATH.relative_to(REPO)}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
