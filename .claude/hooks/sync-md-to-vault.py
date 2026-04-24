#!/usr/bin/env python3
"""Mirror Claude Code plan files into docs/plans/ as symlinks.

With koala_science itself serving as the Obsidian vault, repo-root *.md files
don't need syncing — they're already in the vault. The only cross-tree source
still worth mirroring is plan files in ~/.claude/plans/, which live outside
the repo but should surface alongside the strategy docs in the vault.

Reads Claude Code hook stdin JSON, extracts the written/edited file path, and
symlinks `~/.claude/plans/*.md` into `docs/plans/<name>.md` as an absolute
symlink. No-op if the destination symlink already exists or the file isn't a
plan.
"""
import json
import os
import sys

REPO = "/home/lhum/Desktop/my_code/koala_science"
DOCS_PLANS = os.path.join(REPO, "docs", "plans")
PLANS_DIR = os.path.expanduser("~/.claude/plans")


def resolve_target(abs_path: str) -> tuple[str, str] | None:
    """Return (dest_symlink_path, symlink_target) or None if not a sync source."""
    parent = os.path.dirname(abs_path)
    name = os.path.basename(abs_path)
    if not name.endswith(".md"):
        return None

    if parent == PLANS_DIR:
        return os.path.join(DOCS_PLANS, name), abs_path

    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    resp = data.get("tool_response") or {}
    inp = data.get("tool_input") or {}
    path = resp.get("filePath") or inp.get("file_path")
    if not path:
        return 0

    abs_path = os.path.realpath(path)
    resolved = resolve_target(abs_path)
    if resolved is None:
        return 0

    link, target = resolved
    if os.path.lexists(link):
        return 0

    os.makedirs(os.path.dirname(link), exist_ok=True)
    os.symlink(target, link)
    return 0


if __name__ == "__main__":
    sys.exit(main())
