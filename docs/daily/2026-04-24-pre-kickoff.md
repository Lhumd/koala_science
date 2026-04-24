---
name: 2026-04-24 pre-kickoff
tags: [daily/koala, koala-2026]
date: 2026-04-24
---

# 2026-04-24 — pre-kickoff day

## Summary

Competition starts today at 12:00 local. Overnight preparation completed (phases A, B, D-prep, E-scaffolding, F-tests, vault scaffolding) without Anthropic API credentials available. Phase C (bakeoff) is staged as a one-command script that the user runs on wake-up once `ANTHROPIC_API_KEY` is exported.

## Artifacts ready

- 4 candidate system prompts in `agent_configs/`: `baseline_a0`, `rl_systems`, `theory`, `applications` (each ~2,000 tokens with ICML 2026 rubric, PC tone, sub-venue norms, comment workflow, karma discipline, and SCORE emission)
- Balanced 120-paper ICML 2025 eval set at `eval_data/icml_2025_eval.jsonl` (15 accepted + 15 rejected per domain cluster; rejected cluster sizes capped by OpenReview opt-in pool)
- Full ICML 2025 fetch cached at `eval_data/icml_2025_full.jsonl` (3,422 records, 3,260 accepts + 162 opt-in rejects)
- Bakeoff runner: `tools/bakeoff.sh` — single-command end-to-end
- Metrics analyzer: `tools/analyze_bakeoff.py` — picks per-cluster winners, writes `eval_data/bakeoff_analysis.md`
- 153 tests passing across the `tools/` + `cli/` codebase

## Blocked / user-gated

- **Phase C bakeoff** — needs `ANTHROPIC_API_KEY`. Will run in ~40 min on wake-up.
- **Phase E agent registration** — needs `.api_key` from `koala.science/owners` which may not open until 12pm.
- **Per-agent GitHub transparency repos** — need to exist before agent launch (one public repo per deployed agent).
- **Backend CLI** — `npm install -g @anthropic-ai/claude-code` (pinned in `pyproject.toml::tool.reva.system-deps`).

## Update — bakeoff attempted and abandoned

Added a pluggable backend abstraction (`tools/bakeoff_backends.py`) supporting:
- `api` — Anthropic SDK (requires `ANTHROPIC_API_KEY`, prompt caching)
- `claude-cli` — shells out to local `claude` CLI (uses Max subscription auth)

Selection via `bakeoff.config.yaml` or `--backend` CLI flag. 9 new tests pass; total 162.

**Kicked off bakeoff via Max-CLI backend per user request. Confirmed too slow to finish before kickoff:**

| Attempt | Duration | Preds written | Rate |
|---|---|---|---|
| First run (full 120-paper) | 22 min | 10 for baseline_a0 | ~2.2 min/call → ETA 17h |
| Second run (`--limit 25`) | 10 min | 2 for baseline_a0 | one 300s timeout → ETA ~25h |

**Root cause:** each `claude --print` invocation spawns a fresh bun + Claude Code runtime, sends the full ~17K-char system prompt with no caching (the API backend's `cache_control: ephemeral` doesn't apply through the CLI), and reasons in a single shot. Per-call latency is 3–8 minutes, sometimes exceeding the 300s timeout in `bakeoff_backends.py:23`.

Killed both runs to preserve Max quota for the competition itself. Full diagnosis and wake-up options in `eval_data/bakeoff_failure.md`.

## Update — repo-as-vault migration

Also merged `koala_vault/` (sibling directory) into the repo as `docs/`:
- `docs/project-overview.md` — Koala project summary (was `10 Projects/Koala Science/README.md`)
- `docs/koala-rules.md` — distilled platform rules digest
- `docs/plans/floating-zooming-sphinx.md` — symlink to `~/.claude/plans/floating-zooming-sphinx.md`
- `docs/daily/` — session diaries (this file)

`VAULT_PATH` in `.claude/settings.local.json` now points at the repo root. `.claude/hooks/sync-md-to-vault.py` simplified to only mirror plan files into `docs/plans/`. The `koala_vault/` sibling directory has been deleted. Open `~/Desktop/my_code/koala_science/` directly in Obsidian — everything's in one place.

## Plan for 12pm launch (revised)

1. **Read `eval_data/bakeoff_failure.md`** — explains why the bakeoff didn't finish overnight.
2. **Pick a bakeoff path (or skip it):**
   - **Fast/cheap:** export `ANTHROPIC_API_KEY`, set `BAKEOFF_BACKEND=api`, rm partial preds, run `./tools/bakeoff.sh` (~40 min, ~$10–20)
   - **Slow/Max-only:** reduce scope to `--limit 10` per candidate, accept ~4h run + noisy results
   - **Skip bakeoff:** deploy Portfolio 4 from first-principles per `AGENT_DESIGNS.md`
3. After bakeoff (if run): `uv run python -m tools.analyze_bakeoff --metrics runs/metrics.json --output eval_data/bakeoff_analysis.md`
4. Confirm Portfolio 4 specialists win their clusters or pivot per analysis.
5. Register 3 agents on `koala.science/owners`; drop Koala API keys into `agent_configs/<final_name>/.api_key`.
6. Create 3 public transparency GitHub repos and stage deploy keys / PATs.
7. Launch: `uv run reva launch --name <agent> --duration 72` for each of the 3 winners.

## Processes

- Nothing running. All bakeoff processes killed as of 2026-04-24 ~12:22.
- **Partial report available** at `eval_data/bakeoff_analysis.md` — `baseline_a0` only, n=14, Spearman −0.39 / AUC 0.27. Too small to be conclusive; specialists untested.
- Partial predictions preserved at `runs/preds_baseline_a0.jsonl` (14 rows).
- `/tmp/bakeoff.log` retains the trace for post-mortem.

See also:
- [[bakeoff_analysis]] — the partial eval readout
- [[bakeoff_failure]] — failure diagnosis from the earlier aborted Max-CLI run
- [[AGENT_DESIGNS]] — first-principles deploy justification if skipping the bakeoff
- [[RUNBOOK]] — step-by-step kickoff deployment path
