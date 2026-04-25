#!/usr/bin/env bash
# Preflight checks for `reva launch --name theory`.
#
# Since the user is reusing the koala_science repo as the public transparency
# repo, no separate repo setup is needed. This script verifies everything is
# wired correctly before going live.
#
# Run from repo root:
#   ./tools/setup_transparency_repo.sh
#
# Exit code 0 = ready for reva launch. Non-zero = something to fix.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0
warn=0

ok()    { printf '  \033[32m✓\033[0m %s\n' "$1"; }
nope()  { printf '  \033[31m✗\033[0m %s\n' "$1"; fail=$((fail+1)); }
warn_() { printf '  \033[33m!\033[0m %s\n' "$1"; warn=$((warn+1)); }

echo "== 1/8 — agent dir + .api_key =="
if [[ -f agent_configs/theory/.api_key ]]; then
    perm=$(stat -c '%a' agent_configs/theory/.api_key)
    if [[ "$perm" == "600" ]]; then
        ok "agent_configs/theory/.api_key (mode 0600)"
    else
        warn_ ".api_key has mode $perm; recommend chmod 600"
    fi
else
    nope "agent_configs/theory/.api_key missing — needed for reva launch"
fi

echo "== 2/8 — git remote points to koala_science =="
remote_url=$(git remote get-url origin 2>/dev/null || echo "")
case "$remote_url" in
    *Lhumd/koala_science*) ok "origin -> $remote_url" ;;
    "")                     nope "no git remote 'origin' configured" ;;
    *)                      warn_ "origin -> $remote_url (not Lhumd/koala_science; you may have a different transparency repo wired up)" ;;
esac

echo "== 3/8 — koala_science is public =="
if command -v gh >/dev/null 2>&1; then
    is_priv=$(gh repo view Lhumd/koala_science --json isPrivate -q .isPrivate 2>/dev/null || echo "unknown")
    case "$is_priv" in
        false)   ok "Lhumd/koala_science is public (Koala readers can fetch github_file_url)" ;;
        true)    nope "Lhumd/koala_science is private — Koala cannot resolve github_file_url" ;;
        *)       warn_ "could not determine repo visibility (gh auth?)" ;;
    esac
else
    warn_ "gh CLI not installed; skipping visibility check"
fi

echo "== 4/8 — push credentials work =="
if git push --dry-run origin HEAD:main >/dev/null 2>&1; then
    ok "git push --dry-run succeeds"
else
    nope "git push --dry-run failed — fix ssh key or PAT before reva launch"
fi

echo "== 5/8 — gitignore allows transparency artifacts =="
sample_paths=(
    "agent_configs/theory/scratch/__test__.md"
    "agent_configs/theory/reports/__test__.md"
    "agent_configs/theory/full_reports/__test__.md"
    "agent_configs/theory/reasoning/__test__/x.md"
    "agent_configs/theory/triage_phase_a.md"
    "agents/assignments.jsonl"
    "papers/__test__/shared_reasoning.md"
)
gi_fail=0
for p in "${sample_paths[@]}"; do
    if git check-ignore -q "$p" 2>/dev/null; then
        nope "transparency path is gitignored: $p"
        gi_fail=1
    fi
done
[[ $gi_fail -eq 0 ]] && ok "transparency carveouts active for all required paths"

echo "== 6/8 — claude CLI installed =="
if command -v claude >/dev/null 2>&1; then
    ok "claude $(claude --version 2>&1 | head -1)"
else
    nope "claude CLI not on PATH; install via npm i -g @anthropic-ai/claude-code"
fi

echo "== 7/8 — PaperLantern MCP reachable =="
mcp_url="https://mcp.paperlantern.ai/chat/mcp"
http=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 "$mcp_url" 2>/dev/null || echo "fail")
case "$http" in
    200|400|401|403|405|406) ok "PaperLantern MCP responds ($http)" ;;
    *)                       warn_ "PaperLantern MCP returned $http; verify offline before launch" ;;
esac

echo "== 8/8 — pypdf + urllib (PDF retrieval) =="
if uv run python -c "import pypdf, urllib.request" 2>/dev/null; then
    ok "pypdf importable"
else
    nope "pypdf import failed; uv add pypdf"
fi

echo
if [[ $fail -gt 0 ]]; then
    echo "✗ $fail blocker(s), $warn warning(s) — fix before reva launch."
    exit 1
fi
if [[ $warn -gt 0 ]]; then
    echo "✓ no blockers; $warn warning(s) — review then launch."
    exit 0
fi
echo "✓ all checks pass; reva launch --name theory --duration 72 is online-ready."
