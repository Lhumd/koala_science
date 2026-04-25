"""Smoke driver: run the new theory Phase A prompt against 5 papers via claude-cli.

This is a one-shot offline test: the new theory/system_prompt.md expects a full
Claude Code runtime (PDF retrieval, file I/O, MCP). claude --print is text-only,
so we (a) inline title/abstract/pdf_url into the user message, (b) tell the
model this is an offline fixture so the PDF-retrieval-failure SKIP rule does
not apply, (c) capture raw output, (d) parse the two-block json+markdown
response.

Output: runs/theory_smoke/<paper_id>.txt (raw stdout) and
runs/theory_smoke/summary.jsonl (per-paper parse results).
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROMPT_PATH = REPO / "agent_configs" / "theory" / "system_prompt.md"
PAPERS_PATH = REPO / "runs" / "theory_smoke_papers.jsonl"
OUT_DIR = REPO / "runs" / "theory_smoke"
SUMMARY_PATH = OUT_DIR / "summary.jsonl"
MODEL = "claude-sonnet-4-6"
TIMEOUT_S = 600

JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
MD_BLOCK = re.compile(r"```markdown\s*\n(.*?)\n```", re.DOTALL)


def build_user_message(paper: dict) -> str:
    return (
        "OFFLINE SMOKE FIXTURE — abstract-only Phase A.\n\n"
        "This is an owner-run smoke test. You do not have PDF access, "
        "PaperLantern, or file-write tools in this invocation. Treat the "
        "abstract below as the available fixture content. Do not SKIP for "
        "PDF-unreachable in this fixture; instead emit a best-effort Phase A "
        "structured response with a clearly low confidence (2 or 3) since "
        "you only have the abstract. Respond with the two-block "
        "json+markdown format exactly as specified in your system prompt. "
        "No SCORE: line; no other text outside the two blocks.\n\n"
        f"Paper ID: {paper['paper_id']}\n"
        f"Domain: {paper.get('domain', 'general')}\n"
        f"Title: {paper['title']}\n"
        f"PDF URL (not retrievable in this fixture): {paper.get('pdf_url', '<missing>')}\n\n"
        f"Abstract:\n{paper['abstract']}\n"
    )


def run_one(system_prompt: str, paper: dict) -> dict:
    paper_id = paper["paper_id"]
    user_message = build_user_message(paper)
    cmd = [
        "claude",
        "--print",
        "--append-system-prompt",
        system_prompt,
        "--model",
        MODEL,
        user_message,
    ]
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "paper_id": paper_id,
            "accepted": paper.get("accepted"),
            "elapsed_s": TIMEOUT_S,
            "status": "timeout",
            "score": None,
            "confidence": None,
            "comment_words": None,
            "skip_reason": None,
        }
    elapsed = time.monotonic() - t0
    raw = result.stdout
    (OUT_DIR / f"{paper_id}.txt").write_text(raw, encoding="utf-8")
    if result.stderr:
        (OUT_DIR / f"{paper_id}.stderr.txt").write_text(result.stderr, encoding="utf-8")

    skip_match = re.search(r"SKIP\s+(\S+)\s+reason=(\S+)", raw)
    if skip_match and not JSON_BLOCK.search(raw):
        return {
            "paper_id": paper_id,
            "accepted": paper.get("accepted"),
            "elapsed_s": round(elapsed, 1),
            "status": "skipped_by_model",
            "score": None,
            "confidence": None,
            "comment_words": None,
            "skip_reason": skip_match.group(2),
        }

    json_match = JSON_BLOCK.search(raw)
    md_match = MD_BLOCK.search(raw)
    score = None
    confidence = None
    parse_status = "ok"
    if json_match:
        try:
            verdict = json.loads(json_match.group(1))
            theory = verdict.get("Theory", {})
            score = theory.get("score")
            confidence = theory.get("confidence")
        except json.JSONDecodeError:
            parse_status = "json_decode_fail"
    else:
        parse_status = "no_json_block"

    comment = md_match.group(1) if md_match else None
    return {
        "paper_id": paper_id,
        "accepted": paper.get("accepted"),
        "elapsed_s": round(elapsed, 1),
        "status": parse_status if md_match else f"{parse_status}+no_md_block",
        "score": score,
        "confidence": confidence,
        "comment_words": len(comment.split()) if comment else None,
        "skip_reason": None,
        "exit_code": result.returncode,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    papers = [json.loads(line) for line in PAPERS_PATH.read_text().splitlines() if line.strip()]
    print(f"running {len(papers)} papers via claude-cli (model={MODEL}, timeout={TIMEOUT_S}s)")
    rows = []
    with SUMMARY_PATH.open("w", encoding="utf-8") as f:
        for i, paper in enumerate(papers, 1):
            print(f"[{i}/{len(papers)}] {paper['paper_id']} accepted={paper.get('accepted')}: {paper['title'][:60]}", flush=True)
            row = run_one(system_prompt, paper)
            f.write(json.dumps(row) + "\n")
            f.flush()
            rows.append(row)
            print(f"   -> {row}", flush=True)
    print("\nSUMMARY")
    for r in rows:
        print(f"  {r['paper_id']} acc={r['accepted']} status={r['status']} score={r['score']} conf={r['confidence']} elapsed={r['elapsed_s']}s")


if __name__ == "__main__":
    main()
