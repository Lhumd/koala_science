"""Koala paper harvester — populates the `papers/` vault folder with one .md per paper.

Polls the Koala platform for all known papers, writes/updates one frontmatter-rich
markdown note per paper to `<VAULT>/papers/<paper_id>.md`, and tracks dedup state
in `<VAULT>/papers/.harvester_state.json`. Gitignored by default (see `.gitignore`).

Not a registered competition agent. Uses a Koala API key (any agent's key will do
for read-only operations) to list papers. Runs on an interval via a tmux /
systemd / cron wrapper outside this file.

Information hygiene: strips any retrieved URLs that match a deny-list of
leaked-future-information sources (OpenReview, citation counts on the exact
paper) before writing the note.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


_LEAKED_SOURCE_PATTERNS = (
    "openreview.net",
    "paperswithcode.com",
    "semanticscholar.org",
    "/citations",
)


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    abstract: str
    status: str
    domains: list[str]
    github_urls: list[str]
    pdf_url: str | None
    released_at: str


@dataclass
class HarvesterState:
    seen_paper_ids: set[str] = field(default_factory=set)
    last_status: dict[str, str] = field(default_factory=dict)


def load_state(path: Path) -> HarvesterState:
    if not path.exists():
        return HarvesterState()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return HarvesterState(
        seen_paper_ids=set(payload.get("seen_paper_ids", [])),
        last_status=dict(payload.get("last_status", {})),
    )


def save_state(path: Path, state: HarvesterState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "seen_paper_ids": sorted(state.seen_paper_ids),
        "last_status": state.last_status,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _filter_leaked(urls: list[str]) -> list[str]:
    return [u for u in urls if not any(pat in u for pat in _LEAKED_SOURCE_PATTERNS)]


def render_frontmatter(paper: PaperRecord) -> str:
    lines = ["---"]
    lines.append(f"paper_id: {paper.paper_id}")
    lines.append(f"status: {paper.status}")
    lines.append(f"released_at: {paper.released_at}")
    safe_title = paper.title.replace('"', "'")
    lines.append(f'title: "{safe_title}"')
    lines.append(f"domains: {json.dumps(paper.domains)}")
    safe_github = _filter_leaked(paper.github_urls)
    lines.append(f"github_urls: {json.dumps(safe_github)}")
    lines.append(f"pdf_url: {json.dumps(paper.pdf_url)}")
    lines.append("tags:")
    lines.append("  - paper/koala")
    lines.append("  - koala-2026")
    lines.append(f"  - status/{paper.status}")
    for d in paper.domains:
        lines.append(f"  - domain/{d.replace('/', '_')}")
    lines.append("---")
    return "\n".join(lines)


def format_paper_note(paper: PaperRecord) -> str:
    parts = [render_frontmatter(paper), ""]
    parts.append(f"# {paper.title}")
    parts.append("")
    if paper.pdf_url:
        parts.append(f"[PDF]({paper.pdf_url})")
        parts.append("")
    parts.append("## Abstract")
    parts.append("")
    parts.append(paper.abstract)
    parts.append("")
    safe_github = _filter_leaked(paper.github_urls)
    if safe_github:
        parts.append("## GitHub")
        for url in safe_github:
            parts.append(f"- {url}")
        parts.append("")
    parts.append("## Comments")
    parts.append("")
    parts.append("<!-- harvested comments will be appended here during the competition -->")
    parts.append("")
    parts.append("## Verdicts")
    parts.append("")
    parts.append("<!-- published verdicts will be appended here after the 72h close -->")
    parts.append("")
    return "\n".join(parts)


def harvest_once(
    *,
    client,
    vault_papers_dir: Path,
    state_path: Path,
) -> dict[str, int]:
    papers: list[PaperRecord] = client.list_papers()
    state = load_state(state_path)
    vault_papers_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    updated = 0
    for paper in papers:
        target = vault_papers_dir / f"{paper.paper_id}.md"
        previous_status = state.last_status.get(paper.paper_id)
        is_new = paper.paper_id not in state.seen_paper_ids
        status_changed = previous_status is not None and previous_status != paper.status
        if is_new or status_changed:
            target.write_text(format_paper_note(paper), encoding="utf-8")
            if is_new:
                created += 1
            else:
                updated += 1
        state.seen_paper_ids.add(paper.paper_id)
        state.last_status[paper.paper_id] = paper.status
    save_state(state_path, state)
    return {"created": created, "updated": updated, "total": len(papers)}


def harvest_loop(
    *,
    client,
    vault_papers_dir: Path,
    state_path: Path,
    interval_s: int,
    max_iterations: int | None = None,
) -> None:
    i = 0
    while max_iterations is None or i < max_iterations:
        i += 1
        try:
            stats = harvest_once(
                client=client, vault_papers_dir=vault_papers_dir, state_path=state_path
            )
            print(
                f"[harvester] iter={i} created={stats['created']} "
                f"updated={stats['updated']} total={stats['total']}"
            )
        except Exception as exc:
            print(f"[harvester] iter={i} error: {exc}")
        time.sleep(interval_s)


def _build_default_client(api_key: str | None):
    from tools.koala_client import KoalaClient

    return KoalaClient(api_key=api_key)


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll Koala and mirror papers into the vault.")
    parser.add_argument(
        "--vault-papers-dir",
        type=Path,
        default=Path("papers"),
        help="Directory under the repo/vault to write <paper_id>.md files to.",
    )
    parser.add_argument(
        "--state",
        type=Path,
        default=Path("papers/.harvester_state.json"),
    )
    parser.add_argument("--interval", type=int, default=180, help="Seconds between polls.")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single poll and exit (useful for cron).",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Koala API key. If omitted, reads from KOALA_API_KEY env var.",
    )
    args = parser.parse_args()

    import os
    api_key = args.api_key or os.environ.get("KOALA_API_KEY")
    client = _build_default_client(api_key)
    if args.once:
        stats = harvest_once(
            client=client,
            vault_papers_dir=args.vault_papers_dir,
            state_path=args.state,
        )
        print(json.dumps(stats))
    else:
        harvest_loop(
            client=client,
            vault_papers_dir=args.vault_papers_dir,
            state_path=args.state,
            interval_s=args.interval,
        )


if __name__ == "__main__":
    main()
