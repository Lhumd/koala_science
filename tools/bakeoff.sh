#!/usr/bin/env bash
set -euo pipefail

# Run the full pre-kickoff bakeoff: 4 candidates × 120 papers on ICML 2025.
#
# Backend selection (api vs. claude-cli) comes from:
#   1. BAKEOFF_BACKEND env var (if set), or
#   2. bakeoff.config.yaml file in the repo root (if present), or
#   3. default "api" backend.
#
# The `api` backend uses the Anthropic SDK and needs ANTHROPIC_API_KEY exported.
# The `claude-cli` backend uses the local `claude` command (Max subscription or
# whatever auth is configured) — no API key required.
#
# Writes:
#   runs/preds_<candidate>.jsonl   — per-candidate predictions
#   runs/all_predictions.jsonl     — concatenated
#   runs/metrics.json              — per-agent + per-domain Spearman + AUC
#
# Expected runtime: ~40 min (api, Sonnet with caching) to ~90 min (claude-cli
# headless; slower because each call spawns a fresh CLI session).

export PATH="$HOME/.local/bin:$PATH"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

EVAL_SET="eval_data/icml_2025_eval.jsonl"
CANDIDATES=(baseline_a0 rl_systems theory applications)
CONFIG_FILE="${BAKEOFF_CONFIG:-bakeoff.config.yaml}"
MODEL="${BAKEOFF_MODEL:-}"
SLEEP="${BAKEOFF_SLEEP:-}"
BACKEND="${BAKEOFF_BACKEND:-}"

if [[ ! -f "$EVAL_SET" ]]; then
    echo "ERROR: eval set not found at $EVAL_SET."
    echo "Run: uv run python -m tools.build_eval_set --output eval_data/icml_2025_full.jsonl"
    echo "Then subsample it (see RUNBOOK.md)."
    exit 1
fi

# Soft check: if backend is (or defaults to) 'api' and ANTHROPIC_API_KEY is
# missing, warn but don't abort — user may have .env or apiKeyHelper wired up.
effective_backend="$BACKEND"
if [[ -z "$effective_backend" && -f "$CONFIG_FILE" ]]; then
    effective_backend=$(grep -E '^backend:' "$CONFIG_FILE" | head -1 | awk '{print $2}' || true)
fi
if [[ -z "$effective_backend" ]]; then
    effective_backend="api"
fi
if [[ "$effective_backend" == "api" && -z "${ANTHROPIC_API_KEY:-}" && ! -f .env ]]; then
    echo "WARN: backend=api but ANTHROPIC_API_KEY is unset and no .env found."
    echo "      Either export ANTHROPIC_API_KEY, create .env, or use BAKEOFF_BACKEND=claude-cli."
fi

mkdir -p runs

echo "== bakeoff: ${#CANDIDATES[@]} candidates × $(wc -l < "$EVAL_SET") papers, backend=$effective_backend =="

extra_flags=()
[[ -n "$BACKEND" ]] && extra_flags+=(--backend "$BACKEND")
[[ -n "$MODEL" ]] && extra_flags+=(--model "$MODEL")
[[ -n "$SLEEP" ]] && extra_flags+=(--sleep-between-calls "$SLEEP")
[[ -f "$CONFIG_FILE" ]] && extra_flags+=(--config "$CONFIG_FILE")

for candidate in "${CANDIDATES[@]}"; do
    prompt_file="agent_configs/$candidate/system_prompt.md"
    out_file="runs/preds_${candidate}.jsonl"
    echo
    echo "== [$candidate] $(date '+%H:%M:%S') starting =="
    uv run python -m tools.run_candidate_agent \
        --system-prompt "$prompt_file" \
        --eval-set "$EVAL_SET" \
        --agent-name "$candidate" \
        --output "$out_file" \
        "${extra_flags[@]}"
    echo "== [$candidate] $(date '+%H:%M:%S') done; wrote $(wc -l < "$out_file") rows =="
done

cat runs/preds_*.jsonl > runs/all_predictions.jsonl
echo
echo "== aggregating metrics =="
uv run python -m tools.eval_agents \
    --eval-set "$EVAL_SET" \
    --predictions runs/all_predictions.jsonl \
    --output runs/metrics.json \
    --per-domain

echo
echo "== DONE =="
echo "See runs/metrics.json for per-candidate and per-domain Spearman + AUC."
echo "Next: uv run python -m tools.analyze_bakeoff --metrics runs/metrics.json --output eval_data/bakeoff_analysis.md"
