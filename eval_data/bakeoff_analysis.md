---
name: Bakeoff analysis — partial (baseline_a0 only, n=14)
tags: [eval/bakeoff, koala-2026]
date: 2026-04-24
status: partial
---

# Bakeoff analysis — partial

> ⚠️ **Partial results only.** The bakeoff was killed at 14 of a planned 100 calls. Only `baseline_a0` has predictions; `rl_systems`, `theory`, `applications` have zero. **This cannot answer the bakeoff's core question of which specialist wins each cluster.** It is a single-agent calibration spot-check on a too-small sample.

## Run context

- **Launched:** 2026-04-24 12:04 via Max-CLI backend, `--limit 25` per candidate, sequential (baseline_a0 first)
- **Killed:** 2026-04-24 ~12:22 after 18 min with only 14 preds for `baseline_a0`; all other candidates untouched
- **Reason for kill:** projected 2.8 hours to completion; user needed to preserve Max quota for the 1pm kickoff and the 6-day competition window
- **Rate observed:** ~1.85 min per `claude --print` call

## Single-agent calibration — `baseline_a0`

| Metric | Value | Reference |
|---|---|---|
| Spearman | **−0.39** | 0 = random; 0.41 = human inter-reviewer; 0.42 = Stanford paperreview.ai |
| AUC | **0.27** | 0.5 = random; 0.75 = Stanford |
| n | 14 | (9 accepted, 5 rejected) |
| Cluster coverage | 7 applications_trustworthy, 3 general, 2 theory_probabilistic, 2 rl_systems | |

The negative Spearman means `baseline_a0` gave *lower* scores to accepted papers than to rejected ones on this tiny sample — directionally anti-calibrated.

## Per-paper rankings

Sorted by score ascending:

| Score | Accepted | Domain                   | Paper ID   |
| ----- | -------- | ------------------------ | ---------- |
| 4.2   | ✅        | general                  | 6udKBHc0Mr |
| 4.2   | ✅        | applications_trustworthy | 2aKHuXdr7Q |
| 4.4   | ✅        | theory_probabilistic     | M9keJ0Jy3J |
| 4.5   | ✅        | rl_systems               | WIIfdh0GJu |
| 4.5   | ❌        | applications_trustworthy | zC0ZxjXixH |
| 4.5   | ✅        | applications_trustworthy | 9vwkmxLZVL |
| 5.2   | ✅        | applications_trustworthy | XkEp70qckE |
| 5.3   | ✅        | applications_trustworthy | kRmfzTfIGe |
| 5.3   | ❌        | applications_trustworthy | xCrgcGytLR |
| 5.4   | ❌        | general                  | 1Ct7Y3jsBx |
| 5.5   | ✅        | applications_trustworthy | S22CMkkQzY |
| 5.5   | ❌        | theory_probabilistic     | GOWRex7nOA |
| 6.8   | ❌        | general                  | OEKs42CZBJ |
| 7.0   | ✅        | rl_systems               | MQpAF3Z1YD |

## Interpretation

### What this is
A single-agent directional sanity check on 14 ICML 2025 papers with known accept/reject labels.

### What this is not
- Not a bakeoff — no cross-candidate comparison happened.
- Not statistically significant — n=14 has a 95% confidence interval on Spearman of roughly ±0.45, so the true correlation could easily be 0 or mildly positive.
- Not a cluster-specific readout — 7 of 14 papers are `applications_trustworthy`, a subfield where the generalist baseline is exactly the wrong tool (the `applications` specialist is designed to dominate there).

### Suggestive patterns (don't overindex)

**Score compression.** Scores range 4.2 → 7.0, a narrow band inside the middle buckets of the 6-point rubric. The agent is not using 0–3 or 8–10. Either the rubric mapping is biasing the agent toward the middle, or the sample happens to be mid-tier. With only n=14 it's impossible to disentangle.

**Under-scoring accepts.** Accepted papers cluster 4.2–4.5 (Weak Reject territory). Five consecutive lowest-score papers are accepted. If this holds with a bigger sample, it would indicate the baseline prompt's "6-point → 0–10" mapping is pushing too low. Worth re-reading `agent_configs/baseline_a0/system_prompt.md::ICML 2026 official rubric` if you want to sanity-check the bucket table.

**One misranked high-score.** The single 6.8 is a rejected paper (general cluster). Hard to generalize from n=1 misses in a tiny sample.

### Action implications

- **The bakeoff can't tell you anything definitive from this data.** Skip it with a clear conscience.
- **If you want to sanity-check the baseline prompt's rubric mapping,** re-read the mapping table section in `agent_configs/baseline_a0/system_prompt.md`. If it looks fine, assume the −0.39 is sampling noise.
- **Portfolio 4 specialists were NOT tested.** Deploy them based on the first-principles reasoning in `AGENT_DESIGNS.md` — their design value is specifically on subfield papers the baseline handles poorly.

## Next steps

Three options, same as before:
1. **Skip bakeoff entirely, deploy Portfolio 4** — recommended path given the kickoff timeline
2. **Tiny `--limit 5` bakeoff** (~40 min Max, ~20 calls) — directional noise, not recommended
3. **Full API bakeoff** (~40 min, $10–25) — the only high-quality empirical path, needs `ANTHROPIC_API_KEY`

See `eval_data/bakeoff_failure.md` for full discussion of each option.

## Files referenced

- `runs/preds_baseline_a0.jsonl` — 14 rows of `{paper_id, agent_name, score}`
- `runs/all_predictions.jsonl` — same content (concat of preds_*.jsonl)
- `runs/metrics.json` — auto-generated `{"overall": {"baseline_a0": {"spearman": -0.39, "auc": 0.27, "n": 14}}}`
- `eval_data/icml_2025_eval.jsonl` — the 120-paper balanced eval set the run sampled from
- `eval_data/bakeoff_failure.md` — earlier failure diagnosis from the first aborted run
