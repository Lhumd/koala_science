"""Minimal read-only client for the Koala Science REST API.

Enough to back the harvester (list papers, get paper details). Not a general
MCP client — the competition agents reach Koala via the MCP endpoint embedded
in their backend, not through this module.

Base URL defaults to `koala_base_url()` from `reva.env`, so `KOALA_BASE_URL`
still redirects to staging when set.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

from reva.env import koala_base_url
from tools.harvester import PaperRecord


_DEFAULT_TIMEOUT_S = 30


@dataclass
class KoalaClient:
    api_key: str | None = None
    base_url: str | None = None
    timeout_s: int = _DEFAULT_TIMEOUT_S

    def _root(self) -> str:
        return self.base_url or koala_base_url()

    def _headers(self) -> dict[str, str]:
        if self.api_key:
            return {"Authorization": self.api_key}
        return {}

    def list_papers(self, *, limit: int = 500) -> list[PaperRecord]:
        url = f"{self._root()}/api/v1/papers/"
        params = {"limit": limit}
        resp = requests.get(
            url, params=params, headers=self._headers(), timeout=self.timeout_s
        )
        resp.raise_for_status()
        items = resp.json()
        return [self._to_record(raw) for raw in items]

    def _to_record(self, raw: dict) -> PaperRecord:
        github_urls: list[str] = raw.get("github_urls") or []
        legacy = raw.get("github_repo_url")
        if legacy and legacy not in github_urls:
            github_urls = [legacy, *github_urls]
        return PaperRecord(
            paper_id=raw["id"],
            title=raw.get("title", ""),
            abstract=raw.get("abstract", ""),
            status=raw.get("status", "unknown"),
            domains=raw.get("domains", []),
            github_urls=github_urls,
            pdf_url=_absolute_url(self._root(), raw.get("pdf_url")),
            released_at=raw.get("released_at", raw.get("created_at", "")),
        )


def _absolute_url(root: str, maybe_relative: str | None) -> str | None:
    if maybe_relative is None:
        return None
    if maybe_relative.startswith("http"):
        return maybe_relative
    storage_base = root.rstrip("/")
    if storage_base.endswith("/api/v1"):
        storage_base = storage_base[: -len("/api/v1")]
    if not maybe_relative.startswith("/"):
        maybe_relative = "/" + maybe_relative
    return storage_base + maybe_relative
