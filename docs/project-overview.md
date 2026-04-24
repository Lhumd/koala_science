---
name: Koala Science ICML 2026
tags: [project/koala, koala-2026]
status: pre-kickoff
kickoff: 2026-04-24T12:00
---

# Koala Science — ICML 2026 Agent Review Competition

> 72h competition window followed by a 72h tail. ~3,600 ICML 2026 submissions released at ~1 per 2 minutes. Leaderboard ranks each agent by correlation of its 0–10 verdicts with actual ICML 2026 accept/reject decisions. Top 3 agents get co-authorship on the technical report.

## Quick links

- **Strategy source** — `~/Desktop/my_code/koala_science/AGENT_DESIGNS.md` (13 approaches A–N; 4 portfolios; ICML 2026 rubric; PC tilt; acceptance mechanism notes)
- **TODO** — `~/Desktop/my_code/koala_science/TODO.md` (P0 / P1 / P2 / P3 plan)
- **Runbook** — `~/Desktop/my_code/koala_science/RUNBOOK.md` (exact wake-up commands)
- **Plan file (this cycle)** — `~/.claude/plans/floating-zooming-sphinx.md`
- **Authoritative rules** — [koala.science/skill.md](https://koala.science/skill.md)

## Deployment

Three competition agents, each a domain specialist calibrated to the ICML 2026 Program Chair team (Tong Zhang, Alekh Agarwal, Miroslav Dudik, Sharon Li, Martin Jaggi):

- **rl_systems** — RL / Robotics / Systems / Optimization (flagship; `claude-code` on API; GPU access via FPT Cloud + McGill)
- **theory** — ML theory / probabilistic / optimization theory (`codex` on GPT-5 API)
- **applications** — Applications / Trustworthy ML / Evaluation (`claude-code` on Sonnet API)

One baseline candidate (`baseline_a0`) is used for bakeoff comparison only, not deployed.

## Folder structure

```
papers/     ← harvester-written, one file per Koala paper
repos/      ← reproducer-written, one file per GitHub URL per paper
methods/    ← librarian-written, method→prior-work links
domains/    ← domain tags (RL/Theory/Applications/…)
daily/      ← per-day progress notes (YYYY-MM-DD.md)
```

Papers are populated by `tools/harvester.py` (needs a Koala API key in `KOALA_API_KEY` or `--api-key`). Run once: `uv run python -m tools.harvester --once`. Loop: `uv run python -m tools.harvester --interval 180` (poll every 3 min). Repos, methods, and domain tags are populated by the live competition agents.

## Paper tracker (Dataview)

Requires the Obsidian Dataview community plugin. Harvester output lands in `papers/` as gitignored notes with `paper_id`, `status`, `domains`, and `tags` frontmatter — these queries surface them live.

### Papers by phase

````
```dataview
TABLE paper_id AS "ID", status, domains
FROM "papers"
WHERE paper_id
SORT status ASC, file.name ASC
```
````

### Deliberating now (verdict window open)

````
```dataview
LIST paper_id + " — " + title
FROM "papers"
WHERE status = "deliberating"
SORT file.mtime DESC
```
````

### Reviewed papers (final scores public)

````
```dataview
TABLE title, domains
FROM "papers"
WHERE status = "reviewed"
SORT file.mtime DESC
LIMIT 50
```
````

## Competition rules digest (distilled from koala.science/skill.md)

- **Karma economy** — start with 100. Your first comment on a paper = 1.0 karma; subsequent = 0.1 each. Per-paper earning cap = 3 karma via N/(v·a) ancestor-chain citation.
- **Verdict prerequisites** — paper in `deliberating` phase; you commented during `in_review`; cite ≥5 distinct non-sibling other agents inline; body includes `SCORE: X.Y` line for your 0–10.
- **Hard platform requirement** — every comment needs `github_file_url` to a file in your public transparency GitHub repo (one per agent, not under `Lhumd/koala_science`).
- **Moderation** — automated LLM screening; 3 free strikes, then -10 karma per 3rd strike.
- **Forbidden sources for the same paper** — OpenReview reviews/scores/decisions, citation counts, blog posts, social media, news, post-publication commentary.
- **Sibling agents cannot cite each other's comments** (same OpenReview ID → same bloc).

## ICML 2026 rubric (official)

Four dims, 1–4 each: Soundness, Presentation, Significance, Originality. Then 6-point overall (1=Strong Reject → 6=Strong Accept). Map to Koala 0–10:

| Rec | Koala | Rec | Koala |
|---|---|---|---|
| 1 (SR) | 0.5–1.5 | 4 (WA) | 5.0–6.0 |
| 2 (R)  | 2.5–3.5 | 5 (A)  | 6.5–7.5 |
| 3 (WR) | 4.0–5.0 | 6 (SA) | 8.5–9.5 |

Use fractional values to preserve within-bucket ordering.

## Acceptance mechanism

ICML uses **merit-based acceptance**, not per-subfield quotas. If robotics is weak this year, ICML accepts fewer robotics papers rather than lowering the bar. Target: ~26–28% overall acceptance, but subfield rates vary with submission-pool strength and PC emphasis.
