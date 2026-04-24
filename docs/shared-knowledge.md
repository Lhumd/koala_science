---
name: Shared knowledge — multi-agent protocol, karma math, coordination
tags: [reference/koala, koala-2026, shared]
---

# Shared knowledge for all Koala competition agents

This doc is the single source of truth for **multi-agent coordination rules** across `rl_systems`, `theory`, `applications` (and `baseline_a0` if deployed). Consult this before every first-comment decision.

## Why coordination matters

All sibling agents share one OpenReview ID. Platform rule (`skill.md`):
- **Sibling agents cannot cite each other in verdicts** (400 error).
- **Sibling-agent coordination on the platform is prohibited** — no cross-citations, no synchronized postings.

The owner-level assignment of "which agent reviews which paper" is normal operation, not platform-level coordination. Agents don't talk to each other at runtime; they consult a shared assignment log and a shared reasoning pool, both maintained under the owner's workspace.

**The waste to avoid:** if two siblings both first-comment on the same paper, each spends 1 karma, neither can earn citation karma from the other's verdict, and the thread ancestry splits — costing both the 3-karma-per-paper cap advantage. Pure loss.

## Commenting is a karma COST with narrow ROI

Commenting on a paper spends karma (1.0 first; 0.1 subsequent). The karma-positive scenarios are:

1. **Seed your own thread** in an unclaimed high-fit paper — you become the ancestor of every descendant citation on that thread. Up to +3 karma per paper (capped).
2. **Defend your own thread** against a challenge (someone replied claiming your observation is wrong). Reply costs 0.1 and preserves citation value for anyone who later cites your thread. Cheap.
3. **Verdict eligibility** — you must have commented on a paper to verdict it. Combine this with #1: your first-comment both seeds a thread and unlocks verdict eligibility.

The karma-negative scenarios (avoid):

- Commenting on a paper a sibling already claimed (0 citation return from siblings; the paper is already covered).
- Replying to another (non-sibling) agent's thread — makes you a descendant, not ancestor. You only earn if your specific reply is cited, not the whole thread.
- First-commenting papers at 20+ commenters — karma dilution past the 3-karma cap; others hit it first.
- First-commenting papers under 4 commenters with no sibling claim — high verdict-unreachable risk; waste if the paper stays below 5.

## Assignment protocol — one sibling per paper

**Assignment file:** `agents/assignments.jsonl`. Append-only JSONL, one record per claim:

```json
{"paper_id": "abc123", "agent_name": "rl_systems", "claimed_at": "2026-04-25T14:23:00Z"}
```

**Before you first-comment on paper P:**
1. Read `agents/assignments.jsonl`. If any record matches `paper_id == P`, a sibling has claimed it. **Skip** first-commenting. You may still contribute via shared reasoning (below).
2. Otherwise, append a claim record for P with your agent_name, then first-comment.

**Conflict resolution:** if two siblings race on the same paper (claim within the same second), the one with the lexicographically smaller `claimed_at` wins; the loser skips.

**Atomicity:** agents use an advisory file lock pattern — read-append-fsync via `tools/assignments.py::claim_paper` (or Bash equivalent with `flock`). If that utility is unavailable, append the claim and then re-read; if your claim is not first, skip.

## Domain routing — which agent is primary for a paper

Use Koala's `paper.domains` field (e.g. `d/RL`, `d/Theory`, `d/Trustworthy-ML`).

| Agent | Primary domains |
|---|---|
| `rl_systems` | d/Reinforcement-Learning, d/Robotics, d/Optimization, d/Deep-Learning (systems/scale subset) |
| `theory` | d/Theory, d/Probabilistic-Methods, d/Bandits, d/Statistical-Learning |
| `applications` | d/Trustworthy-ML, d/Fairness, d/Privacy, d/Safety, d/Healthcare, d/Climate, d/Social-Sciences, d/Biosciences, d/Physical-Sciences |
| `baseline_a0` (if deployed) | anything uncategorized / `d/General` / overlapping domains |

**Overlap rules:**
- Multi-domain papers: the agent whose primary domain appears FIRST in `paper.domains` wins.
- Pure `d/Deep-Learning` without a specialist match: applications agent takes it if it touches reliability/OOD/safety themes in abstract; theory agent takes it if it's primarily theoretical; rl_systems takes it if it's about training efficiency or scaling.
- Ambiguous: first-come-first-claim from whichever agent gets there first (usually harmless; only one agent ends up claiming).

## Shared reasoning pool — consolidate insights without duplicate comments

When a sibling has claimed paper P, **you do not post a comment** — but you *may* contribute findings to the shared pool.

**Shared reasoning file:** `papers/<paper_id>/shared_reasoning.md`. Any sibling appends sections tagged with their agent name:

```markdown
## [theory — 2026-04-25T14:30Z] Novelty check vs. prior work

The Lie-algebraic framing overlaps significantly with [Grazzi et al. 2024]
theorem 3.2. See their section 5 for the commutativity bound.
```

The sibling who **claimed** the paper reads the shared pool when composing their comment or verdict, and may incorporate the contributed observations into their single comment (or reply if they've already commented). Consolidation improves the comment's substance without spending extra karma.

**Karma math for sharing:** the primary agent spends 1 karma for the first-comment; siblings spend 0 on the shared file (local file write; no platform action). If the thread gets cited, only the primary agent earns (the siblings contributed offline).

## Reply policy (threads)

- **Your own thread:** reply freely at 0.1 karma when it's strategically valuable (defending a challenged observation, adding a clarification that strengthens citation value). Reply sparingly; each reply is a karma cost that has to pay back via citation.
- **Another agent's thread (non-sibling):** never. You cannot first-comment for free on a paper whose first-thread isn't yours, and replying to their thread makes you a descendant rather than an ancestor — terrible karma ROI.
- **Another sibling's thread:** never. Siblings can't cite each other, so replying to a sibling is pure waste.

## Verdict policy

- **Every sibling verdicts every eligible paper.** Verdicts are free and one-per-agent, and your individual ranking depends on verdict-vs-outcome correlation. If you commented on a paper, verdict it.
- **Don't wait for sibling verdicts.** Each of your verdicts is your own calibration; siblings' verdicts can't influence yours and can't be cited by yours.
- **Citing in verdicts:** you may only cite non-sibling, non-self comments. When composing, read the full comment tree and pick the 5 most substantive non-sibling citations that support your final recommendation.

## Critical-observation comment style

(Cross-reference: each agent's own prompt has a "Citation-karma strategy" section with domain-specific critical-observation catalogs.)

Core principle: every comment you post leads with the sharpest evidence-based weakness you've found. Positive observations are less citable — reject verdicts need 5 specific weakness-citations each, and reject verdicts outnumber accept verdicts ~3:1 in ICML's ~27% accept rate.

Frame criticisms as precise questions, not conclusions:
- ✅ *"Does Theorem 2's bound remain tight when assumption A3 is relaxed?"*
- ❌ *"The assumption is too strong."*

## Comment–verdict split (never violate)

Comments lean sharp and critical → citation optimization.
Verdicts stay honestly calibrated to the ICML 4-dim rubric → leaderboard optimization.

A Strong Accept paper still gets a Strong Accept verdict even if your comment raises one valid critique. Do not lower verdict scores to match critical comment tone. Koala's leaderboard ranks on Spearman/AUC — **calibration**, not severity.

## Information hygiene (enforced for all agents)

Never use these sources for the exact paper being reviewed:
- OpenReview reviews/scores/decisions
- Citation counts / trajectory
- Blog posts, social media, news
- Post-publication commentary

You may use: the paper itself, its references, author-provided code artifacts, PaperLantern MCP retrieval, and prior work predating the paper.

## Anti-behaviors (platform-enforced)

- Near-identical comments/verdicts across papers → moderation flag + anti-behavior violation
- Sibling coordination on the platform → rule violation
- Stance revision to match consensus → anti-behavior
- Ad hominem / off-topic / low-effort content → moderation strike

## Optional strategy — selective echo-replies (NOT ENABLED BY DEFAULT)

> ⚠️ **Currently disabled.** This strategy is parked here pending an organizer clarification on the karma rule wording. Do NOT act on it until the owner explicitly enables it in each agent's system prompt.

### The idea

When you've first-commented paper P, you could *selectively* reply to 1–2 other agents' threads on the same paper with substantive add-ons (0.1 karma per reply). If skill.md's rule *"anyone whose earlier comments appear in the same threads as the citations"* is the canonical interpretation, you'd then earn karma when those threads get cited — beyond what your own thread earns alone.

### Why "selective", not blanket

- **3-karma-per-paper cap** clamps upside. If your own thread alone is likely to hit the cap (high citation-magnetic first-comment), the echo-replies are 0.1 karma each for zero return.
- **Moderation risk** on blanket echoing ("I agree with X") — auto-flagged as `low_effort` or `spam_or_nonsense`. Each reply must be substantive and add a specific, verifiable point.
- **Anti-behavior risk** if echoes are templated across papers — "near-identical comments" is explicitly prohibited.
- **Opportunity cost:** 0.1 karma spent here is 0.1 karma not spent on first-commenting another paper.

### Numerical example (skill.md interpretation, best case)

Paper P: 10 distinct commenters by hour 48; 5 verdicts during hours 48–72; average verdict cites 5 comments; 3-karma-per-paper cap.

| Strategy | Spent | Earned (uncapped) | Earned (capped) | **Net** |
|---|---|---|---|---|
| Bare: only your own thread | 1.0 | 2.0 | 2.0 | **+1.0** |
| Blanket hack: your thread + 4 echo-replies | 1.4 | 3.5 | 3.0 | **+1.6** |
| Selective hack: your thread + 1 targeted reply | 1.1 | 2.5 | 2.5 | **+1.4** |
| Selective hack: your thread + 2 targeted replies | 1.2 | 3.0 | 3.0 | **+1.8** |

Selective (+1 or +2 replies) captures most of the blanket upside at a fraction of the moderation/anti-behavior risk.

### Gate conditions for activating it

An agent should post an echo-reply only if **all** of these hold:

1. Paper P is already commented on by the agent (first-comment done, so subsequent replies cost 0.1).
2. The other thread's first-commenter has credibility signal (>60 karma, 0 recent strikes, clearly in-cluster expertise) — use `get_my_profile` on the other agent's id to check.
3. That thread's first comment has a citation-magnetic observation — sharp, specific, non-obvious.
4. Your own thread is unlikely to hit the 3-karma cap on its own — use it as a heuristic that your first-comment is less differentiated than usual.
5. You have a substantive add-on to offer (a specific section/figure reference that extends the other agent's point, not a bare echo).
6. Reply count on paper P so far for you ≤ 1 — do not exceed 2 echo-replies per paper total.

### Skill.md vs competition-page ambiguity

- `skill.md`: "authors it directly cites plus anyone whose earlier comments appear in the same threads as the citations" → hack works.
- `koala.science/competition`: "agents cited (excluding verdict author and any flagged agent)" → hack has ~zero EV.

Until this is clarified with organizers, **assume the hack is ~0 EV** and do not enable it.

### To enable later

Add a new "Selective echo-reply gate" paragraph to each agent's `system_prompt.md` that references this section and restates the 6 gate conditions. Do not enable for all agents simultaneously — start with one (probably `theory`, which has the smallest pool of comparable-quality commenters and therefore gains most from cross-thread karma diversification).

## Tooling pointers

- **Triage:** `tools/triage.py::select_top_papers(candidates, agent_cluster=...)` ranks candidate papers by join-worthiness using the 5-commenter sweet-spot heuristic. Call before committing to a claim.
- **Style uniqueness:** `tools/style_check.py::check_uniqueness(new, prior)` compares Jaccard similarity vs your prior comments to guard against near-identical-text anti-behavior. Call before posting.
- **Reasoning template:** `tools/reasoning_template.py::render_reasoning_file(meta, body)` generates the per-comment markdown with correct frontmatter for github_file_url.
- **Monitor tripwires:** `tools/monitor.py::evaluate_agent(metrics, daily_cap_usd=...)` flags strike/karma/spend issues. The owner runs this externally; agents don't need to invoke it.
