"""Build the paper inventory the theory prompt expects at /tmp/koala_papers_raw.json.

Two source modes:
- `--source koala`: live fetch from Koala via tools/koala_client.py. Needs
  KOALA_API_KEY env var (or `--api-key` flag, or auto-read from
  agent_configs/theory/.api_key). Pulls papers in `in_review` state.
- `--source eval-set`: read from a local jsonl (default
  eval_data/icml_2025_eval.jsonl). Used for dry runs and the 50-paper smoke.

Output schema (matches the theory prompt's expectation):
    [{"paper_id", "title", "abstract", "pdf_url", "domain", "accepted"|null,
      "domains" (list, optional), "state" (optional)}]

Defaults to writing to /tmp/koala_papers_raw.json. Prompt step A.0 reads
this file to enumerate the work queue.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_KEY_PATH = REPO / "agent_configs" / "theory" / ".api_key"
DEFAULT_OUTPUT = Path("/tmp/koala_papers_raw.json")


def _read_api_key(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    env = os.environ.get("KOALA_API_KEY")
    if env:
        return env
    if DEFAULT_KEY_PATH.exists():
        return DEFAULT_KEY_PATH.read_text(encoding="utf-8").strip()
    return None


def from_koala(api_key: str, limit: int) -> list[dict]:
    from tools.koala_client import KoalaClient
    client = KoalaClient(api_key=api_key)
    records = client.list_papers(limit=limit)
    out: list[dict] = []
    for r in records:
        if r.status and r.status != "in_review":
            continue
        out.append({
            "paper_id": r.paper_id,
            "title": r.title,
            "abstract": r.abstract,
            "pdf_url": r.pdf_url,
            "domain": (r.domains[0] if r.domains else None),
            "domains": list(r.domains or []),
            "state": r.status,
            "accepted": None,
        })
    return out


def from_eval_set(path: Path, limit: int) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            rows.append({
                "paper_id": r["paper_id"],
                "title": r["title"],
                "abstract": r.get("abstract", ""),
                "pdf_url": r.get("pdf_url"),
                "domain": r.get("domain"),
                "domains": [r["domain"]] if r.get("domain") else [],
                "state": "in_review",
                "accepted": r.get("accepted"),
            })
            if limit and len(rows) >= limit:
                break
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description="Build /tmp/koala_papers_raw.json for the theory agent.")
    p.add_argument("--source", choices=["koala", "eval-set"], default="koala")
    p.add_argument("--eval-set", type=Path, default=REPO / "eval_data" / "icml_2025_eval.jsonl")
    p.add_argument("--api-key", default=None, help="Override Koala API key.")
    p.add_argument("--limit", type=int, default=500, help="Cap on papers fetched.")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = p.parse_args()

    if args.source == "koala":
        api_key = _read_api_key(args.api_key)
        if not api_key:
            print(
                "ERROR: no Koala API key. Set KOALA_API_KEY, pass --api-key, "
                f"or stage one at {DEFAULT_KEY_PATH}",
                file=sys.stderr,
            )
            return 2
        rows = from_koala(api_key, args.limit)
    else:
        rows = from_eval_set(args.eval_set, args.limit)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"wrote {len(rows)} papers to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
