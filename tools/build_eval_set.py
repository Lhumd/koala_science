"""Build a labeled ICML 2025 eval set for comparing candidate agents.

This script produces a JSONL file compatible with `tools.eval_agents.load_eval_set`:
each line is an `EvalPaper` with `accepted: true | false`. The file is used to
measure per-agent Spearman/AUC before deploying into the Koala competition.

Data sources (pick whichever is accessible to you; the fetchers below are stubs
you fill in):

- **Accepted papers:** public ICML 2025 accepted-paper list on `icml.cc/Conferences/2025`
  or mirrored on Paper Copilot (https://papercopilot.com/statistics/icml-statistics/).
- **Rejected papers:** harder — ICML does not publish the reject list. Options:
  (a) arXiv papers tagged "submitted to ICML 2025" that do not appear in the
      accepted list (heuristic, noisy);
  (b) OpenReview for years ICML used it (ICML 2020-ish and later withdrawals
      are partial);
  (c) manual curation from researcher-shared lists.

The domain clustering maps raw subject-area strings onto the three Portfolio 4
clusters (`rl_systems`, `theory_probabilistic`, `applications_trustworthy`)
plus a `general` fallback for uncategorizable papers.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RawPaperRecord:
    paper_id: str
    title: str
    abstract: str
    pdf_url: str | None
    raw_domains: list[str]
    accepted: bool


_RL_SYSTEMS_TERMS = (
    "rl",
    "reinforcement learning",
    "robot",
    "control",
    "planning",
    "ml systems",
    "scalability",
    "hardware",
    "distributed",
    "federated",
    "optimization",
    "convex",
    "non-convex",
    "nonconvex",
    "stochastic gradient",
    "sgd",
    "efficient training",
    "parallel",
)

_THEORY_PROBABILISTIC_TERMS = (
    "theory",
    "theoretical",
    "learning theory",
    "statistical learning",
    "bandit",
    "game theor",
    "decision theor",
    "probabilistic",
    "bayesian",
    "graphical model",
    "monte carlo",
    "gaussian process",
    "causal",
    "information theor",
    "regret",
    "pac",
    "sample complexity",
    "minimax",
)

_APPLICATIONS_TRUSTWORTHY_TERMS = (
    "trustworthy",
    "fairness",
    "fair ml",
    "interpretability",
    "explainability",
    "privacy",
    "differential privacy",
    "robust",
    "safety",
    "alignment",
    "healthcare",
    "medical",
    "bioscience",
    "biology",
    "physical science",
    "chemistry",
    "social science",
    "sustainability",
    "climate",
    "evaluation benchmark",
    "meta-stud",
    "replicabil",
    "reproducib",
    "poisoning",
    "adversarial",
    "hallucination",
    "out-of-distribution",
    "ood",
    "uncertainty quantif",
)


def _matches_any(norm: str, terms: tuple[str, ...]) -> bool:
    return any(term in norm for term in terms)


def classify_cluster(raw_domains: list[str]) -> str:
    """Map a paper's raw subject-area tags onto a Portfolio 4 cluster.

    Returns one of: 'rl_systems', 'theory_probabilistic', 'applications_trustworthy',
    or 'general' for unmatched inputs. First match wins so ordering in the input
    list matters — put the paper's primary domain first. Substring match on
    lowercased input, so "Reinforcement Learning" and "distributed optimization"
    both resolve correctly.
    """
    for d in raw_domains:
        norm = d.strip().lower()
        if _matches_any(norm, _RL_SYSTEMS_TERMS):
            return "rl_systems"
        if _matches_any(norm, _THEORY_PROBABILISTIC_TERMS):
            return "theory_probabilistic"
        if _matches_any(norm, _APPLICATIONS_TRUSTWORTHY_TERMS):
            return "applications_trustworthy"
    return "general"


def write_eval_jsonl(records: list[RawPaperRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for r in records:
            row = {
                "paper_id": r.paper_id,
                "title": r.title,
                "abstract": r.abstract,
                "pdf_url": r.pdf_url,
                "domain": classify_cluster(r.raw_domains),
                "accepted": r.accepted,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


_OPENREVIEW_API_URL = "https://api2.openreview.net"
_ICML_2025_SUBMISSION_INVITATION = "ICML.cc/2025/Conference/-/Submission"
_OPENREVIEW_PDF_BASE = "https://openreview.net"


def _decision_from_replies(direct_replies: list[dict]) -> str | None:
    for reply in direct_replies:
        content = reply.get("content") or {}
        decision = content.get("decision")
        if decision is None:
            continue
        if isinstance(decision, dict):
            return decision.get("value")
        return decision
    return None


def _note_to_raw_record(note: object, *, accepted: bool) -> RawPaperRecord:
    content = note.content
    pdf_ref = content.get("pdf", {}).get("value") if isinstance(content.get("pdf"), dict) else None
    pdf_url = f"{_OPENREVIEW_PDF_BASE}{pdf_ref}" if pdf_ref else None
    keywords = content.get("keywords", {})
    raw_domains = keywords.get("value", []) if isinstance(keywords, dict) else []
    return RawPaperRecord(
        paper_id=note.id,
        title=content["title"]["value"],
        abstract=content["abstract"]["value"],
        pdf_url=pdf_url,
        raw_domains=list(raw_domains),
        accepted=accepted,
    )


def _build_default_client() -> object:
    import openreview

    return openreview.api.OpenReviewClient(baseurl=_OPENREVIEW_API_URL)


def _fetch_icml_2025_by_decision(
    *,
    accept: bool,
    client: object | None,
    limit: int | None,
) -> list[RawPaperRecord]:
    active_client = client if client is not None else _build_default_client()
    notes = active_client.get_all_notes(
        invitation=_ICML_2025_SUBMISSION_INVITATION,
        details="directReplies",
    )
    records: list[RawPaperRecord] = []
    for note in notes:
        direct_replies = note.details.get("directReplies", [])
        decision_text = _decision_from_replies(direct_replies)
        if decision_text is None:
            continue
        is_accept = decision_text.lower().startswith("accept")
        if is_accept != accept:
            continue
        records.append(_note_to_raw_record(note, accepted=accept))
        if limit is not None and len(records) >= limit:
            break
    return records


def fetch_icml_2025_accepted(
    *,
    client: object | None = None,
    limit: int | None = None,
) -> list[RawPaperRecord]:
    """Fetch ICML 2025 accepted submissions from OpenReview.

    Decisions are attached as replies with content.decision like 'Accept (Poster)'
    or 'Accept (Oral)'. Pass an existing `openreview.api.OpenReviewClient` if you
    want to share authentication or customize `baseurl`.
    """
    return _fetch_icml_2025_by_decision(accept=True, client=client, limit=limit)


def fetch_icml_2025_rejected(
    *,
    client: object | None = None,
    limit: int | None = None,
) -> list[RawPaperRecord]:
    """Fetch ICML 2025 rejected submissions from OpenReview (opt-in only).

    Not all rejected authors opt into public release, so the rejected set is
    smaller than the accepted set. OpenReview returns only the releasable
    subset; we filter on `content.decision == 'Reject'`.
    """
    return _fetch_icml_2025_by_decision(accept=False, client=client, limit=limit)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a labeled ICML 2025 eval set.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--accepted-jsonl",
        type=Path,
        help="Pre-built JSONL of accepted papers (skip the fetcher stub).",
    )
    parser.add_argument(
        "--rejected-jsonl",
        type=Path,
        help="Pre-built JSONL of rejected papers (skip the fetcher stub).",
    )
    args = parser.parse_args()

    if args.accepted_jsonl and args.rejected_jsonl:
        accepted = _read_raw_jsonl(args.accepted_jsonl, accepted=True)
        rejected = _read_raw_jsonl(args.rejected_jsonl, accepted=False)
    else:
        accepted = fetch_icml_2025_accepted()
        rejected = fetch_icml_2025_rejected()

    all_records = accepted + rejected
    write_eval_jsonl(all_records, args.output)
    print(f"wrote {len(all_records)} records to {args.output}")


def _read_raw_jsonl(path: Path, *, accepted: bool) -> list[RawPaperRecord]:
    records: list[RawPaperRecord] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            payload = json.loads(line)
            records.append(
                RawPaperRecord(
                    paper_id=payload["paper_id"],
                    title=payload["title"],
                    abstract=payload["abstract"],
                    pdf_url=payload.get("pdf_url"),
                    raw_domains=payload.get("raw_domains", []),
                    accepted=accepted,
                )
            )
    return records


if __name__ == "__main__":
    main()
