# Bakeoff failure diagnosis — 2026-04-24 overnight run

## Summary

The overnight bakeoff ran using the `claude-cli` backend (Max subscription auth) but proved **too slow to complete before kickoff**. Only 2 predictions for `baseline_a0` were written before I stopped the run to preserve Max quota and your compute for the competition itself.

## What happened

- **11:00:** First bakeoff launched via `nohup ./tools/bakeoff.sh`. 120 papers per candidate × 4 candidates = 480 calls.
- **11:22 (22 min elapsed):** Only 10 predictions written → effective rate ~2.2 min/call → full run ETA ~17 hours. Killed and restarted with `--limit 25` per candidate (100 total calls).
- **11:23:** Second bakeoff launched with `--limit 25`.
- **11:33 (10 min elapsed on second run):** Still only 2 predictions. First paper (`S22CMkkQzY`) hit the 300-second `_CLI_CALL_TIMEOUT_S` defined in `tools/bakeoff_backends.py:23` and was skipped by the `on_error="skip"` path. Subsequent calls were averaging 5–8 minutes each.
- **11:35:** Second bakeoff killed. Partial predictions preserved at `runs/preds_baseline_a0.jsonl` (2 rows).

## Root cause

Each invocation of `claude --print --append-system-prompt "<15K chars>" --model claude-sonnet-4-6 "<paper info>"`:

1. Spawns a fresh bun + Claude Code runtime (~5–15s overhead per call).
2. Sends the full ~17K-char system prompt every time — no prompt caching on the CLI path (the `api` backend's `cache_control: ephemeral` doesn't apply when you're going through the CLI).
3. Has to reason over the full paper + rubric in a single shot before returning.

Combined, a single CLI call for a competition-grade review takes 3–8 minutes, and some papers (dense theory, long abstracts) blow past the 5-minute timeout. That's an order of magnitude slower than the `api` backend with prompt caching (~10–15 sec/call).

## What still works

- **4 candidate system prompts** are written and validated: `agent_configs/{baseline_a0,rl_systems,theory,applications}/system_prompt.md` (each ~2,400 words). Full prompt assembly verified via `reva.prompt.assemble_prompt` for all four.
- **Eval set** is built: `eval_data/icml_2025_eval.jsonl` (120 balanced papers, 15 accepted + 15 rejected per cluster).
- **Bakeoff runner, backend abstraction, analysis pipeline** all tested (162 tests green).
- `bakeoff.config.yaml` still defaults to `backend: claude-cli`; set `BAKEOFF_BACKEND=api` to force the Anthropic SDK path when an API key is available.

## Recommended path on wake-up

Pick one of these three in order of preference:

### Option A — Use the Anthropic SDK (fastest, ~$10–20)

```bash
export PATH="$HOME/.local/bin:$PATH"
cd ~/Desktop/my_code/koala_science
export ANTHROPIC_API_KEY=sk-ant-...
export BAKEOFF_BACKEND=api
rm runs/preds_baseline_a0.jsonl   # wipe partial data
./tools/bakeoff.sh 2>&1 | tee /tmp/bakeoff_api.log
```

ETA ~40 minutes for the full 120-paper × 4-candidate bakeoff with prompt caching. Costs ~$10–20 in Sonnet credits. Then:

```bash
uv run python -m tools.analyze_bakeoff --metrics runs/metrics.json --output eval_data/bakeoff_analysis.md
cat eval_data/bakeoff_analysis.md
```

### Option B — Use a smaller Max-CLI run (if you really can't get an API key)

```bash
# Cut the sample hard — 10 papers per candidate = 40 calls × 6 min = ~4 hours
rm runs/preds_*.jsonl
BAKEOFF_BACKEND=claude-cli BAKEOFF_SLEEP=2.0 \
uv run python -c "
# ... same loop as tools/bakeoff.sh but with --limit 10 ...
"
```

Too slow to be truly useful (10 papers per cluster is noisy), but gives *some* signal. Only do this if no API access is coming.

### Option C — Skip the bakeoff and deploy Portfolio 4 on first principles

Per `AGENT_DESIGNS.md`, Portfolio 4 (the three domain specialists) is the recommended deployment regardless of bakeoff data. The bakeoff would only tell you which specialist wins its cluster — not whether to use specialists at all. The design rationale (PC-tone overlay, sub-venue norms, ICML 4-dim rubric) is sound even without empirical validation.

If you're tight on time and the competition is about to start:

```bash
# Register 3 agents on koala.science/owners as described in RUNBOOK.md Step 4
# Drop .api_key into each agent_configs/<name>/
# Launch:
for name in rl_systems theory applications; do
    uv run reva launch --name $name --duration 72
done
```

## Lessons for future sessions

- **`claude-cli` backend is not viable for large eval sweeps.** It works for 2–5 sample calls (verified) but not for 100+ samples. Add a warning in `bakeoff.config.yaml` comments and the runbook.
- **The `api` backend is the real production path.** Keep `backend: claude-cli` as an option for demos/single-paper experiments, not bulk evaluation.
- **Consider a raw-Anthropic-minimal backend** that bypasses Claude Code entirely — could work without API key using OAuth tokens that `claude` has already stored in its keychain. Not implemented; would need reverse-engineering of the CLI's auth persistence.

## What to do with the 2 partial predictions

`runs/preds_baseline_a0.jsonl` has 2 valid score entries. They're preserved but useless for analysis (insufficient sample for per-cluster Spearman). Delete them before re-running the bakeoff.

```bash
rm runs/preds_*.jsonl runs/all_predictions.jsonl runs/metrics.json 2>/dev/null
```

## Status of other overnight work

- ✅ `tools/bakeoff_backends.py` — pluggable backend with YAML config (9 tests)
- ✅ `tools/analyze_bakeoff.py` — winner picker + markdown renderer (4 tests)
- ✅ Repo-as-vault migration (`koala_vault/` deleted; `docs/` populated)
- ✅ `.claude/hooks/sync-md-to-vault.py` simplified
- ✅ `CLAUDE.md` "Koala vault" section rewritten for repo-as-vault layout
- ✅ `.gitignore` updated (added `papers/`, `agents/`, `domains/`, `karma/`)
- ✅ All 162 tests still green
- ❌ **Phase C bakeoff incomplete** (this doc)
- ❌ **Phase D analysis cannot run** (no metrics data to analyze)

Everything other than the bakeoff itself is ready. As soon as you run the bakeoff with the API backend (Option A), the analysis pipeline runs automatically and produces `eval_data/bakeoff_analysis.md`.
