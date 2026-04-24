from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.harvester import (
    HarvesterState,
    PaperRecord,
    format_paper_note,
    harvest_once,
    load_state,
    render_frontmatter,
    save_state,
)


def _paper(
    id: str = "p1",
    title: str = "Title",
    abstract: str = "Abstract",
    status: str = "in_review",
    domains: list[str] | None = None,
    github_urls: list[str] | None = None,
    pdf_url: str | None = "https://example/p1.pdf",
    released_at: str = "2026-04-24T12:00:00Z",
) -> PaperRecord:
    return PaperRecord(
        paper_id=id,
        title=title,
        abstract=abstract,
        status=status,
        domains=domains or ["d/RL"],
        github_urls=github_urls or [],
        pdf_url=pdf_url,
        released_at=released_at,
    )


def test_render_frontmatter_includes_required_fields() -> None:
    p = _paper()
    fm = render_frontmatter(p)
    assert "paper_id: p1" in fm
    assert "status: in_review" in fm
    assert "released_at:" in fm
    assert "tags:" in fm


def test_format_paper_note_has_frontmatter_and_sections() -> None:
    p = _paper(github_urls=["https://github.com/a/b"])
    note = format_paper_note(p)
    assert note.startswith("---\n")
    assert "paper_id: p1" in note
    assert "## Abstract" in note
    assert "Abstract" in note
    assert "## GitHub" in note
    assert "https://github.com/a/b" in note


def test_format_paper_note_without_github_omits_section() -> None:
    p = _paper(github_urls=[])
    note = format_paper_note(p)
    assert "## GitHub" not in note


def test_load_state_missing_returns_empty(tmp_path: Path) -> None:
    state = load_state(tmp_path / "nope.json")
    assert state == HarvesterState(seen_paper_ids=set(), last_status={})


def test_state_roundtrip(tmp_path: Path) -> None:
    state = HarvesterState(
        seen_paper_ids={"p1", "p2"},
        last_status={"p1": "in_review", "p2": "deliberating"},
    )
    path = tmp_path / "state.json"
    save_state(path, state)
    loaded = load_state(path)
    assert loaded.seen_paper_ids == state.seen_paper_ids
    assert loaded.last_status == state.last_status


def test_harvest_once_writes_new_papers(tmp_path: Path) -> None:
    papers = [_paper("p1"), _paper("p2", status="deliberating")]
    client = MagicMock()
    client.list_papers.return_value = papers
    vault_papers = tmp_path / "papers"
    state_path = tmp_path / "state.json"
    stats = harvest_once(
        client=client, vault_papers_dir=vault_papers, state_path=state_path
    )
    assert stats["created"] == 2
    assert stats["updated"] == 0
    assert (vault_papers / "p1.md").exists()
    assert (vault_papers / "p2.md").exists()


def test_harvest_once_deduplicates_on_second_pass(tmp_path: Path) -> None:
    papers = [_paper("p1")]
    client = MagicMock()
    client.list_papers.return_value = papers
    vault_papers = tmp_path / "papers"
    state_path = tmp_path / "state.json"
    first = harvest_once(
        client=client, vault_papers_dir=vault_papers, state_path=state_path
    )
    assert first["created"] == 1
    second = harvest_once(
        client=client, vault_papers_dir=vault_papers, state_path=state_path
    )
    assert second["created"] == 0
    assert second["updated"] == 0


def test_harvest_once_detects_status_transition(tmp_path: Path) -> None:
    client = MagicMock()
    vault_papers = tmp_path / "papers"
    state_path = tmp_path / "state.json"
    client.list_papers.return_value = [_paper("p1", status="in_review")]
    harvest_once(client=client, vault_papers_dir=vault_papers, state_path=state_path)
    client.list_papers.return_value = [_paper("p1", status="deliberating")]
    stats = harvest_once(
        client=client, vault_papers_dir=vault_papers, state_path=state_path
    )
    assert stats["created"] == 0
    assert stats["updated"] == 1
    content = (vault_papers / "p1.md").read_text(encoding="utf-8")
    assert "status: deliberating" in content


def test_harvest_once_skips_leaked_source_urls(tmp_path: Path) -> None:
    p = _paper(
        "p1",
        github_urls=[
            "https://github.com/real/repo",
            "https://openreview.net/forum?id=abc",
        ],
    )
    client = MagicMock()
    client.list_papers.return_value = [p]
    vault_papers = tmp_path / "papers"
    state_path = tmp_path / "state.json"
    harvest_once(client=client, vault_papers_dir=vault_papers, state_path=state_path)
    text = (vault_papers / "p1.md").read_text(encoding="utf-8")
    assert "https://github.com/real/repo" in text
    assert "openreview.net" not in text


def test_harvest_once_raises_when_client_fails(tmp_path: Path) -> None:
    client = MagicMock()
    client.list_papers.side_effect = RuntimeError("api down")
    with pytest.raises(RuntimeError, match="api down"):
        harvest_once(
            client=client,
            vault_papers_dir=tmp_path / "papers",
            state_path=tmp_path / "state.json",
        )
