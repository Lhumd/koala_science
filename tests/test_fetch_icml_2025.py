from unittest.mock import MagicMock

from tools.build_eval_set import (
    RawPaperRecord,
    _decision_from_replies,
    _note_to_raw_record,
    fetch_icml_2025_accepted,
    fetch_icml_2025_rejected,
)


class _FakeNote:
    def __init__(self, id: str, content: dict, direct_replies: list[dict]):
        self.id = id
        self.content = content
        self.details = {"directReplies": direct_replies}


def _make_accepted_note(id: str, title: str, abstract: str, keywords: list[str]) -> _FakeNote:
    return _FakeNote(
        id=id,
        content={
            "title": {"value": title},
            "abstract": {"value": abstract},
            "keywords": {"value": keywords},
            "pdf": {"value": f"/pdf/{id}.pdf"},
        },
        direct_replies=[{"content": {"decision": {"value": "Accept (Poster)"}}}],
    )


def _make_rejected_note(id: str, title: str, abstract: str, keywords: list[str]) -> _FakeNote:
    return _FakeNote(
        id=id,
        content={
            "title": {"value": title},
            "abstract": {"value": abstract},
            "keywords": {"value": keywords},
            "pdf": {"value": None},
        },
        direct_replies=[{"content": {"decision": {"value": "Reject"}}}],
    )


def test_decision_from_replies_accept() -> None:
    replies = [{"content": {"decision": {"value": "Accept (Oral)"}}}]
    assert _decision_from_replies(replies) == "Accept (Oral)"


def test_decision_from_replies_reject() -> None:
    replies = [{"content": {"decision": {"value": "Reject"}}}]
    assert _decision_from_replies(replies) == "Reject"


def test_decision_from_replies_no_decision() -> None:
    replies = [{"content": {"review": {"value": "some review text"}}}]
    assert _decision_from_replies(replies) is None


def test_decision_from_replies_empty() -> None:
    assert _decision_from_replies([]) is None


def test_note_to_raw_record_accepted() -> None:
    note = _make_accepted_note("p1", "Title A", "Abstract A", ["RL", "robotics"])
    record = _note_to_raw_record(note, accepted=True)
    assert record.paper_id == "p1"
    assert record.title == "Title A"
    assert record.abstract == "Abstract A"
    assert record.pdf_url == "https://openreview.net/pdf/p1.pdf"
    assert record.raw_domains == ["RL", "robotics"]
    assert record.accepted is True


def test_note_to_raw_record_rejected_no_pdf() -> None:
    note = _make_rejected_note("p2", "Title B", "Abstract B", ["theory"])
    record = _note_to_raw_record(note, accepted=False)
    assert record.paper_id == "p2"
    assert record.pdf_url is None
    assert record.accepted is False


def test_fetch_icml_2025_accepted_filters_by_decision() -> None:
    fake_client = MagicMock()
    fake_client.get_all_notes.return_value = [
        _make_accepted_note("a1", "Accepted 1", "Abs 1", ["RL"]),
        _make_rejected_note("r1", "Rejected 1", "Abs 2", ["theory"]),
        _make_accepted_note("a2", "Accepted 2", "Abs 3", ["fairness"]),
    ]
    records = fetch_icml_2025_accepted(client=fake_client, limit=None)
    assert len(records) == 2
    assert {r.paper_id for r in records} == {"a1", "a2"}
    assert all(r.accepted is True for r in records)


def test_fetch_icml_2025_rejected_filters_by_decision() -> None:
    fake_client = MagicMock()
    fake_client.get_all_notes.return_value = [
        _make_accepted_note("a1", "Accepted 1", "Abs 1", ["RL"]),
        _make_rejected_note("r1", "Rejected 1", "Abs 2", ["theory"]),
        _make_rejected_note("r2", "Rejected 2", "Abs 3", ["fairness"]),
    ]
    records = fetch_icml_2025_rejected(client=fake_client, limit=None)
    assert len(records) == 2
    assert {r.paper_id for r in records} == {"r1", "r2"}
    assert all(r.accepted is False for r in records)


def test_fetch_icml_2025_accepted_respects_limit() -> None:
    fake_client = MagicMock()
    fake_client.get_all_notes.return_value = [
        _make_accepted_note(f"a{i}", f"t{i}", f"abs{i}", ["RL"]) for i in range(10)
    ]
    records = fetch_icml_2025_accepted(client=fake_client, limit=3)
    assert len(records) == 3
