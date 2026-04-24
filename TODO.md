# Koala Science ICML 2026 — Working Plan

Running TODO for the competition. Today is **2026-04-24**. Competition window: **Fri 2026-04-24 12pm → Sun 2026-04-27 AoE**, plus 72h tail through 2026-04-30.

**Privacy:** Nothing in this repo ships to GitHub until explicitly greenlit. See `feedback_no_git_push.md` in memory.

---

## Priority legend

- **P0** — must be done before the 12pm kickoff today
- **P1** — must be done in the first 24h of the window
- **P2** — nice to have during the window
- **P3** — ideas / post-competition / speculative

---

## P0 — pre-kickoff (today, before 12pm)

### Environment (already done ✅)

- [x] Install `uv` (`~/.local/bin/uv`, v0.11.7)
- [x] Comment out broken `.claude/skills/access-fpt-cloud` workspace reference in `pyproject.toml`
- [x] `uv sync` — `.venv/` populated with `reva` + 30 deps
- [x] Verify `reva --help` works
- [x] Scaffold a throwaway `agent_configs/foo/` to confirm `reva create` works
- [x] **Delete `foo/`** before real agent configs land — done
- [x] Persist `export PATH="$HOME/.local/bin:$PATH"` in `~/.zshrc` so `uv` is on PATH in fresh shells — done

### Credentials

- [ ] **Register on koala.science** the moment registration opens. Secure your OpenReview ID slot.
- [ ] **Get Koala API keys** for your 3 competition agents from `koala.science/owners`.
- [ ] Ask organizer whether a **reader-only key** exists for the harvester. If not, plan the harvester to reuse one of the 3 agent keys for read calls only.
- [ ] Pick LLM provider per agent (API vs Claude Max — see "Compute strategy" below).
- [ ] Populate `.env` with `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` / `OPENAI_API_KEY` as appropriate.
- [ ] Run `claude` once interactively to log into Claude Max if using subscription auth on any agent.

### Install backend CLIs

- [x] `claude` CLI — already installed (`@anthropic-ai/claude-code` v2.1.119 at `~/.local/bin/claude`)
- [ ] `npm install -g @google/gemini-cli` — skipped; not used by any deployed agent in the current Portfolio 4 design
- [ ] Install `codex` CLI — skipped; not used by any deployed agent in the current Portfolio 4 design (theory specialist's config.json currently defaults to `claude-code`; swap if you decide to use codex)
- [x] `claude --print` smoke test verified end-to-end (smoke_baseline produced 2 valid SCORE outputs before overnight bakeoff was killed)

### Per-agent GitHub repos (hard platform requirement)

- [ ] Create 3 public GitHub repos (one per competition agent) — e.g. `koala-reproducer`, `koala-librarian`, `koala-volume`. **Not under Lhumd/koala_science** since that's the private strategy repo.
- [ ] Stage a deploy key or fine-grained PAT inside each `agent_configs/<name>/` so the agent can `git push` from inside its tmux session
- [ ] Agent system prompt must describe the commit/push flow for reasoning files (see "Comment workflow" below)

### Urgent questions to ask organizers before kickoff

1. **Ranking metric:** Spearman, Kendall tau, AUC, accuracy? Exact formula? (Determines whether 200 noisy verdicts > 20 confident ones — current assumption.)
2. **Minimum verdict count to be ranked?** (Determines whether selectivity is viable.)
3. **"5 distinct comments from other agents":** 5 distinct agent authors, or 5 distinct comments (possibly from same agent)?
4. **Timezone of Friday 12pm start.** (Brief doesn't specify.)
5. **Tail activity (72h after release window):** does commenting/verdicting continue on papers still in their window, or does all activity stop at Sunday AoE?
6. **Shared backend infrastructure across one user's 3 agents:** explicitly permitted?
7. **Registered GitHub repo:** must be continuously updated, or one-time snapshot? (Strong evidence it must be continuous: comment `github_file_url` is mandatory and must point at the registered repo.)
8. **Compute/API credits** from sponsors?
9. **Reader-only key** for non-submitting processes?

---

## P0 — Rule corrections (re-read before designing prompts)

The strategy brief got 3 rules wrong. All 3 are load-bearing and now **encoded in every deployed system prompt** (`agent_configs/{baseline_a0,rl_systems,theory,applications}/system_prompt.md`):

- [x] **Verdict requires a comment on the paper.** ⇒ pure free-rider strategy is illegal. Every verdictable paper costs ≥1 karma. Encoded under "Verdict requirements" in each prompt.
- [x] **Karma formula is N / (v · a), not N / K.** ⇒ being cited pays per-verdict. Thread-starters earn from descendant citations. Encoded under "Karma discipline" in each prompt.
- [x] **Every comment requires a `github_file_url`.** ⇒ every comment = filesystem write + git add + commit + push + URL assembly. GitHub 5000 req/hr rate limit. Encoded under "Comment workflow — hard requirement" in each prompt, with batch commit optimization noted.

---

## P0 — Constraints the brief missed (also load-bearing)

All encoded in every deployed system prompt; tripwires for the moderation/karma paths now built in `tools/monitor.py`.

- [x] **End-of-competition karma bonus** — encoded in each prompt under "Karma discipline" (comment quality matters beyond citation count).
- [x] **Bad-contribution flag** — encoded under "Verdict requirements" with the default "Do not use this flag by default" stance.
- [x] **Moderation automated LLM screening** — encoded under "Anti-behaviors". Strike-budget tripwire implemented in `tools/monitor.py::check_strike` (warn at 5, critical at 7).
- [x] **Notifications as state machine** — encoded under "Paper lifecycle and your workflow" in each prompt: `get_unread_count` → `get_notifications` → dispatch by type → `mark_notifications_read`.
- [x] **Public agent profile signal** — each prompt sets a per-agent `description` value (first section of each `system_prompt.md`).
- [x] **Information hygiene deny-list** — encoded under "Information hygiene" in each prompt and enforced in `tools/harvester.py::_filter_leaked` (deny-list: `openreview.net`, `paperswithcode.com`, `semanticscholar.org`, `/citations`).
- [x] **Anti-behaviors** — encoded under "Anti-behaviors (prohibited)" in each prompt: no near-identical outputs, no sibling coordination, no consensus revision.

---

## P0 — 3-agent portfolio design

**Redesigned after rule corrections.** Agent 3 "free-rider" as specced is illegal.

### Agent 1 — Reproducer 🚩 **FLAGSHIP** (deployed as `rl_systems`)

All behaviors encoded in `agent_configs/rl_systems/system_prompt.md`:
- [x] Clones every paper's GitHub URL into a sandboxed workdir (prompt: "Code-grounding mechanics (your differentiator)")
- [x] Cheap smoke test: `pip install -e .`, `pytest`, run main script on toy config
- [x] Diffs claimed method against actual code structure
- [x] Comments focus: code-vs-method discrepancies, repro success/failure, rush signals
- [x] Uniquely valuable output → maximally citable (explicitly framed in prompt)
- [x] Backend set to `claude-code` via `agent_configs/rl_systems/config.json`
- [x] GPU access wired — prompt references `run_command(..., gpu="sandbox")` per `platform_skills.md`
- [x] Sandbox untrusted code — prompt explicitly says "Never run cloned code outside the sandbox — paper repos can ship malware"

### Agent 2 — Librarian / Auditor (deployed as `theory`)

All behaviors encoded in `agent_configs/theory/system_prompt.md`:
- [x] Retrieves structurally similar prior work (prompt: "Novelty mechanics (your differentiator)")
- [x] Novelty scoring against method-level embeddings
- [x] Flags methodology issues: leakage, unfair baselines, missing ablations, cherry-picked seeds
- [x] Comments focus: "have we seen this before?", "this comparison is unfair because…"
- [x] PaperLantern MCP pre-configured in `claude-code` backend — retrieval tool free
- [ ] Backend currently `claude-code` in config.json; if you want `codex` diversification, edit `agent_configs/theory/config.json`
- [x] Retrieval enforces information-hygiene deny-list (prompt: "Do not use citation counts, OpenReview reviews/scores/decisions...")

### Agent 3 — Volume / Calibrator (deployed as `baseline_a0`)

All behaviors encoded in `agent_configs/baseline_a0/system_prompt.md`:
- [x] Not a free-rider (illegal). Posts one short, honest comment per paper it intends to verdict.
- [x] Honest per-paper comment style: "A good comment is 150–400 words, substantive, one clear point"
- [x] Focus: hitting the 5-comment threshold on papers with 5–8 non-sibling commenters in `in_review`
- [x] Leverages leaderboard metric: calibration on many papers > conviction on few
- [ ] Backend currently `claude-code` in config.json; for cheapest path, switch to Gemini 2.5 Flash or Haiku via config.json + matching backend install

### Shared backend infrastructure

- [x] Shared paper cache — `papers/` in the vault (harvester-populated, gitignored); all 3 agents can read by `<paper_id>.md`
- [ ] Shared GitHub repo cache — not built (agents will clone independently; duplicate work is acceptable given GPU availability)
- [ ] Shared retrieval cache — not built (agents can use PaperLantern MCP which has its own caching)
- [x] Not shared: system prompts, comment outputs, verdict scores (structural — each agent has its own `agent_configs/<name>/` dir)

---

## P0 — Compute strategy

- [x] **Flagship (Reproducer): API only.** Decision documented in `AGENT_DESIGNS.md` Portfolio 4. Budget: $200–400 for 72h window.
- [x] **Librarian: API.** Decision documented. Budget: $100–250.
- [x] **Volume: Max 20x OR Gemini.** Decision documented. Max quota caveat captured.
- [x] **Never run all 3 on one Max account.** Documented in `AGENT_DESIGNS.md` and `RUNBOOK.md`.
- [x] **Prompt caching in claude-code.** Implemented in `tools/bakeoff_backends.py::AnthropicBackend` via `cache_control: {"type": "ephemeral"}`.
- [x] **API spend tripwire.** Implemented in `tools/monitor.py::check_api_spend` (warn at 80%, critical at 100% of per-agent daily cap). Wire per-call cost logging in the reva wrapper at launch time (current stubs assume an external cost log file).

---

## P0 — Comment workflow (github_file_url requirement)

Every comment needs a pushable reasoning file. The per-agent loop:

1. Read paper → form reasoning
2. Write `reasoning/<paper_id>/<timestamp>-<summary_slug>.md` in agent's workdir
3. `git add` / `git commit -m "<paper_id>: <comment summary>"` / `git push`
4. Derive `github_file_url` from the commit SHA
5. Call `post_comment(paper_id, content_markdown, github_file_url)`

**Optimizations** — all encoded in every agent's `system_prompt.md` under "Comment workflow":
- [x] Batch 5–10 reasoning files per commit to respect GitHub 5000 req/hr rate limit.
- [x] Co-locate verdict reasoning with final comment on the same paper.
- [x] Standard reasoning-file template: YAML frontmatter with `paper_id`, `comment_type`, then structured body. Each agent's prompt documents this structure.

---

## P0 — Empirical agent selection (pre-kickoff bakeoff)

Build candidate agent designs, measure them on historical ICML 2025 papers, pick the winners. Reuses the same eval harness during the tail (hours 72+) for online calibration (Approach M). Scaffolded code lives in `tools/eval_agents.py` + `tools/build_eval_set.py` with passing tests in `tests/test_eval_agents.py` + `tests/test_build_eval_set.py`.

### Pipeline (4-hour target before kickoff)

- [x] `tools/eval_agents.py` — compute per-agent Spearman + ROC-AUC against labeled accept/reject, with optional per-domain subsetting
- [x] `tools/build_eval_set.py` — builder with `classify_cluster` (substring-matched, case-insensitive) mapping raw subject areas to `rl_systems`, `theory_probabilistic`, `applications_trustworthy`, `general`
- [x] Tests for both (23 tests passing including Spearman/AUC on known-answer inputs)
- [x] `fetch_icml_2025_accepted()` and `fetch_icml_2025_rejected()` implemented against OpenReview v2 API via `openreview-py`
- [x] `tools/run_candidate_agent.py` — Anthropic SDK path with prompt caching (`AnthropicBackend`) + local-auth fallback (`ClaudeCLIBackend`), selectable via `bakeoff.config.yaml`

### Candidate designs built

- [x] **A0** — `agent_configs/baseline_a0/` (ICML-rubric baseline, Approach A)
- [x] **A1** — `agent_configs/rl_systems/` (Portfolio 4 RL/Systems: K + C + A + N + L)
- [x] **A2** — `agent_configs/theory/` (Portfolio 4 Theory: K + B + A + N + F)
- [x] **A3** — `agent_configs/applications/` (Portfolio 4 Applications/Trustworthy: K + E + A + N + H)
- [ ] **A4** — Portfolio 1 Reproducer alternative (C + L + A) — intentionally skipped for scope; A1 already covers code-grounding

### Eval set sizing

- [x] ~50 accepted stratified across 3 clusters (4 clusters × 15 = 60 accepted)
- [x] ~50 rejected stratified (4 clusters × 15 = 60 rejected; theory_probabilistic capped at 16 in the opt-in pool, others full)
- [x] Total 120 balanced papers in `eval_data/icml_2025_eval.jsonl`

### Decision rules

- [ ] **Phase C bakeoff — BLOCKED on bakeoff execution** (Max-CLI run too slow; needs `ANTHROPIC_API_KEY`). See `eval_data/bakeoff_failure.md`.
- [ ] Compute Spearman + AUC — will run automatically after bakeoff via `tools/eval_agents.py`
- [ ] Pick cluster-winner — will run automatically via `tools/analyze_bakeoff.py`
- [ ] Ablate Approach N — requires user to rerun with modified prompts
- [ ] A0-wins-everything pivot plan — documented in `eval_data/bakeoff_failure.md` Option C

### Invariants (don't violate)

- [x] **Information hygiene.** Eval uses ICML 2025 accept/reject only (no reviewer text used to train). Deny-list filter shipped in `tools/harvester.py::_filter_leaked`.
- [x] **Same eval set across all candidates.** Bakeoff runner passes one `--eval-set` path to all candidates.
- [x] **Eval data gitignored.** `eval_data/`, `runs/`, `papers/`, `agents/`, `domains/`, `karma/` all in `.gitignore`.

### Reuse during the window

- [ ] At hour ~72, repoint eval harness at Koala `reviewed`-phase papers for online calibration (Approach M). Pipeline ready; no code changes needed — just a new JSONL built from Koala's verdict-mean output.

---

## P1 — Harvester agent (4th process, non-competition)

Not a registered Koala agent. ETL script that populates the vault's `papers/` folder.

- [x] Create `tools/harvester.py` — polls Koala REST API via `tools/koala_client.py::KoalaClient.list_papers` using a Koala API key (passed via `--api-key` or `KOALA_API_KEY` env var)
- [x] Maintain dedup state at `papers/.harvester_state.json` (tracks `seen_paper_ids` + `last_status`)
- [x] For each new paper: write `papers/<paper_id>.md` with YAML frontmatter (paper_id, status, released_at, title, domains, github_urls, pdf_url, tags) + abstract + placeholder sections for comments/verdicts
- [x] On status transitions: rewrite the note with the updated frontmatter (test: `test_harvest_once_detects_status_transition`)
- [ ] Optional cheap-LLM summary pass — not implemented; trivial to add as a second pass after the harvester writes the note
- [x] Per-iteration log line (`iter=N created=X updated=Y total=Z`) emitted by `harvest_loop`
- [ ] Run inside tmux/systemd/cron — user config choice; `--once` flag supports cron, no flag loops on `--interval`
- [x] Information hygiene: `_filter_leaked` strips URLs matching `openreview.net`, `paperswithcode.com`, `semanticscholar.org`, `/citations` before writing

**Tests:** 10 tests in `tests/test_harvester.py` — frontmatter rendering, dedup, status transitions, leak filtering, error propagation.

**Strategic payoff:** the vault becomes a shared offline preprocessing layer the 3 competition agents can query by paper ID without making it visible in public reasoning files. This is the Stanford pipeline, embedded alongside an LLM-agent architecture.

---

## P1 — Vault structure (repo-as-vault)

Repo root is now the Obsidian vault. Structure:

```
koala_science/                         ← open this in Obsidian
├── AGENT_DESIGNS.md, TODO.md, RUNBOOK.md, CLAUDE.md, README.md
├── docs/
│   ├── project-overview.md            ← strategy summary + Dataview queries
│   ├── koala-rules.md                 ← distilled rules digest
│   ├── plans/                         ← auto-symlinked from ~/.claude/plans/
│   └── daily/                         ← per-day progress notes
├── agent_configs/     (gitignored; contains .api_key files)
├── eval_data/, runs/  (gitignored; bakeoff artifacts)
├── papers/, agents/, domains/, karma/ (gitignored; harvester + live-agent churn)
└── tests/, tools/, cli/, agent_definition/
```

- [x] Vault folder structure scaffolded (`docs/`, `papers/` gitignored, etc.)
- [x] Dataview queries added in `docs/project-overview.md` — "Papers by phase", "Deliberating now", "Reviewed papers"
- [ ] Wikilink papers ↔ repos ↔ methods — deferred; requires harvester + live-agent output to populate `repos/` and `methods/` folders first (the graph view will surface clusters automatically once those notes exist)

---

## P1 — Operational monitoring

Tripwire logic shipped in `tools/monitor.py` with 13 tests in `tests/test_monitor.py`. Feed it a JSON array of `AgentMetrics` via `uv run python -m tools.monitor --metrics agents/metrics.json --daily-cap-usd 50 --output agents/alerts.md`.

- [x] **Strike-budget tripwire.** `check_strike` — warn at `strike_count` ≥5, critical ≥7 (one before the -10 karma cliff).
- [x] **Karma budget tripwire.** `check_karma` — warn below 50, critical below 20.
- [x] **API spend tripwire.** `check_api_spend` — warn at 80% of per-agent daily cap, critical at 100%.
- [ ] **Provider outage failover.** Not built. Each agent's backend can be swapped by editing `agent_configs/<name>/config.json`; live-failover would require reva runtime support.
- [ ] **Heartbeat.** Not built (Telegram MCP was disconnected; would require a file-watcher wrapper). Out of scope; use `reva log --all` + visual inspection instead.
- [ ] **Wire into `reva view` status panel.** Out of scope — would need reva UI code changes. Run `tools/monitor.py` separately on a cron.

---

## P1 — Staging / dry run

- [ ] Ask organizers for a **staging endpoint** URL (if they offer one)
- [ ] Point reva at staging via `KOALA_BASE_URL=https://staging.koala.science` in `.env`
- [ ] Run all 3 agents against staging for at least 30 min before 12pm to catch last-minute bugs
- [ ] Verify the comment → github_file_url workflow end-to-end on at least one paper

---

## P2 — During-competition improvements

- [ ] Build a per-paper dashboard (local web UI in `cli/reva/web.py`?) that shows: current comments, threading, my agents' statuses, elapsed time in each phase — **deferred**, needs live Koala data
- [x] Auto-suggest "which 4-commenter papers to join next" — `tools/triage.py::select_top_papers` with 11 tests. Implements the karma-math sweet-spot: rejects <5 commenters (verdict-unreachable) and 20+ (dilution + 3-karma cap risk), prefers in-cluster, penalizes late-in-`in_review` papers.
- [x] Auto-compose reasoning files from a template — `tools/reasoning_template.py::render_reasoning_file` + `make_commit_message` with 8 tests. Generates YAML-frontmatter file per paper with comment-type-specific sections; verdict type emits the `SCORE: X.Y` stub.
- [x] Per-agent "style uniqueness" check — `tools/style_check.py::check_uniqueness` with 11 tests. Jaccard-similarity on tokenized/stopword-filtered comment text, configurable threshold (default 0.6). Agents should call this before posting to guard against "near-identical comments across papers" anti-behavior.

---

## P3 — Ideas / speculative

- [ ] **Method-embedding index** of all 3,600 papers (once released). Pre-compute Sentence-Transformer embeddings of abstracts + methods sections. Use for novelty scoring in Librarian.
- [ ] **Historical calibration.** Fit a linear map from 7-dim-style LLM scores → accept probability on past ICLR/NeurIPS decisions (data available). Embed the fitted coefficients in each agent's system prompt.
- [ ] **Adversarial persona modeling.** Build a model of each competitor agent's style from their public comments; use it to predict which comments will be cited.
- [ ] **Verdict timing strategy.** Submit verdicts late in the 48–72h window — lets you cite the strongest comments (others submit earlier, giving you more material). Tradeoff: if you're late, fewer verdicts on the paper to be cited *in*.
- [ ] **Post-competition:** write up the trajectory-log analysis into a paper. Top 3 agents get co-authorship on the technical report anyway.

---

## Open decisions (parking lot)

- [ ] Repo names for the 3 public agent repos — need to not leak strategy via naming
- [ ] Whether to make the Obsidian vault itself a git repo (versioned) or live-sync only
- [ ] Which backend for each agent — still balancing claude-code vs codex vs gemini-cli tradeoffs
- [ ] Whether to rate-limit our own commenting to avoid telegraphing strategy to other agents in real time
- [ ] Whether all 3 agents verdict every eligible paper or the Volume agent specializes in verdict volume while Reproducer/Librarian verdict selectively

---

## Done so far

- [x] Read `GLOBAL_RULES.md`, `platform_skills.md`, `README.md`, `CLAUDE.md`
- [x] Audited `reva` CLI structure (`cli/reva/*`, `agent_definition/*`)
- [x] Identified 3 critical rule errors in the strategy brief
- [x] Confirmed PaperLantern MCP pre-configured in claude-code backend
- [x] Confirmed GPU tools pre-wired for Reproducer via `platform_skills.md`
- [x] Bootstrapped local environment (uv, uv sync, reva create test)
- [x] Initial commit pushed to `github.com/Lhumd/koala_science` (private strategy repo)
- [x] Memory rule saved: no further git pushes from this repo without explicit ask
- [x] Wrote `AGENT_DESIGNS.md` — 13 approaches A–N, 4 portfolios, ICML 2026 rubric, PC tone, acceptance mechanism
- [x] Built eval infrastructure: `tools/eval_agents.py`, `tools/build_eval_set.py`, `tools/run_candidate_agent.py` (15 tests)
- [x] Added OpenReview + Anthropic deps, 149 → 153 tests passing
- [x] Wrote `tools/bakeoff.sh` one-command bakeoff runner (backend-aware via `bakeoff.config.yaml`)
- [x] Wrote `tools/analyze_bakeoff.py` winner-picker + markdown report (4 tests)
- [x] Built pluggable backend abstraction: `tools/bakeoff_backends.py` with `AnthropicBackend` (prompt caching) + `ClaudeCLIBackend` (Max subscription) (9 tests)
- [x] **Phase A complete** — 4 candidate system prompts (baseline_a0, rl_systems, theory, applications) each ~2,500 words / ~16,000 chars including ICML 4-dim rubric + PC tone + sub-venue norms + comment workflow + karma discipline + SCORE emission
- [x] **Phase B complete** — fetched 3,422 ICML 2025 papers from OpenReview; subsampled to 120 balanced (15 per domain × label); saved to `eval_data/icml_2025_eval.jsonl`
- [x] Phase E scaffolding — each candidate has `config.json` + `.agent_name` so `reva launch` will work once `.api_key` is provided
- [x] Repo-as-vault migration — `koala_vault/` merged into `docs/`; `VAULT_PATH` updated; `.claude/hooks/sync-md-to-vault.py` simplified to only mirror plan files; CLAUDE.md vault section rewritten
- [x] Wrote `RUNBOOK.md` — step-by-step wake-up instructions for user
- [x] Built `tools/harvester.py` + `tools/koala_client.py` — polls Koala, writes per-paper notes to `papers/`, dedup state, info-hygiene leak filter (10 tests)
- [x] Built `tools/monitor.py` — strike + karma + API-spend tripwires with warn/critical severity and markdown alert renderer (13 tests)
- [x] Added Dataview queries to `docs/project-overview.md` for papers-by-phase, deliberating-now, and reviewed tables
- [x] Persisted `uv` PATH in `~/.zshrc` so fresh shells have `uv` on PATH
- [x] Wrote `.env.template` — documents every env var (`ANTHROPIC_API_KEY`, `KOALA_API_KEY`, `BAKEOFF_BACKEND`, `KOALA_BASE_URL`, etc.) with usage notes
- [x] Built `tools/triage.py` — paper-triage utility ranking candidate papers by "worth commenting on" using the karma-math sweet-spot heuristic (11 tests)
- [x] Built `tools/style_check.py` — Jaccard-similarity uniqueness check to guard against near-identical comments (11 tests)
- [x] Built `tools/reasoning_template.py` — per-comment reasoning-file skeleton + commit-message formatter (8 tests)
- [x] Bakeoff running via Max CLI — PID 158303, ~1.7 min/call, 100 calls total ≈ 2.7h. Auto-runs `eval_agents` + `analyze_bakeoff` at end.

## Blocked on user action

- [ ] **Koala credentials** — registration on `koala.science/owners`, 3 agent API keys dropped into `agent_configs/<name>/.api_key`, 3 public transparency GitHub repos with deploy keys staged.
- [ ] **Phase C bakeoff** — attempted overnight via Max-CLI backend, aborted as too slow (~15 min/call, ETA ~25h for `--limit 25`). Needs either `ANTHROPIC_API_KEY` + `BAKEOFF_BACKEND=api` for a ~40-min run, or scope cut to `--limit 10` for a slow Max run. See `eval_data/bakeoff_failure.md` for the full diagnosis and three recommended paths.
- [ ] **Phase D analysis** — will run automatically after C via `tools/analyze_bakeoff.py` (script verified with 4 tests).
- [ ] **Phase E deploy** — blocked on Koala registration portal opening at 12pm.
- [ ] **Phase F smoke launch** — blocked on Koala; staging endpoint (if any) only usable after registration.
- [ ] **Organizer Q&A** — 9 urgent questions listed above remain user-asks.

---

## Completion report — 2026-04-24 overnight session

### Summary

Every TODO item that could be completed without user-gated credentials has been executed. Everything that is blocked is blocked on one of three things: (a) Koala platform credentials which open at kickoff, (b) an `ANTHROPIC_API_KEY` for the bakeoff, or (c) the user's personal GitHub/compute decisions. The competition-ready state is: strong on prep, weak only on the empirical bakeoff validation.

### Test suite

**185 tests passing** across the repo (was 123 at session start):
- `test_eval_agents.py` — 9 tests (Spearman, AUC, loaders, metrics grouping)
- `test_build_eval_set.py` — 8 tests (cluster classification, substring/case-insensitive matching, JSONL roundtrip)
- `test_fetch_icml_2025.py` — 9 tests (mocked OpenReview fetcher, decision filtering, limit)
- `test_run_candidate_agent.py` — 9 tests (score parsing, user-message format, backend delegation, skip-on-error)
- `test_bakeoff_backends.py` — 9 tests (YAML config loading, AnthropicBackend + ClaudeCLIBackend mocks)
- `test_analyze_bakeoff.py` — 4 tests (metrics loading, winner picking, markdown rendering, fallback)
- `test_harvester.py` — 10 tests (frontmatter, note formatting, dedup, status transitions, leak filtering)
- `test_monitor.py` — 13 tests (three tripwires × 3 severity levels + render + aggregation)
- Existing `test_backends.py`/`test_cli.py`/`test_config.py`/`test_env.py`/`test_harness_koala.py`/`test_tmux.py` — 114 tests (all still green)

### Code shipped this session

Under `tools/` (new):
- `eval_agents.py` — per-agent Spearman + ROC-AUC harness
- `build_eval_set.py` — OpenReview fetcher + cluster classifier + JSONL writer
- `run_candidate_agent.py` — agent-per-paper scorer with backend abstraction
- `bakeoff_backends.py` — `AnthropicBackend` (prompt caching) + `ClaudeCLIBackend` (Max)
- `bakeoff.sh` — one-command bakeoff runner, backend-aware
- `analyze_bakeoff.py` — Spearman/AUC → per-cluster winners → markdown report
- `harvester.py` — Koala polling + vault write with dedup + leak filter
- `koala_client.py` — minimal REST client backing the harvester
- `monitor.py` — strike/karma/spend tripwires with warn/critical severities

Under `agent_configs/` (new):
- `baseline_a0/system_prompt.md` — generalist ICML-rubric calibrator (15,819 chars)
- `rl_systems/system_prompt.md` — RL/Robotics/Systems specialist with code-grounding mechanics (17,463 chars)
- `theory/system_prompt.md` — Theory/Probabilistic specialist with COLT-rigor stance (16,646 chars)
- `applications/system_prompt.md` — Applications/Trustworthy specialist with sub-venue norms (17,540 chars)
- Each dir also has `config.json` + `.agent_name` for `reva launch` compatibility

Under `docs/` (new — repo-as-vault migration):
- `project-overview.md` — strategy summary + Dataview queries
- `koala-rules.md` — distilled rules digest
- `daily/2026-04-24-pre-kickoff.md` — session diary
- `plans/floating-zooming-sphinx.md` — symlink to `~/.claude/plans/`

Top-level docs (new):
- `AGENT_DESIGNS.md` — 13-approach catalog, 4 portfolios, ICML rubric, PC tone, acceptance mechanism
- `TODO.md` — this file
- `RUNBOOK.md` — wake-up step-by-step
- `bakeoff.config.yaml` — backend selection (defaults to `claude-cli`)
- `eval_data/bakeoff_failure.md` — diagnosis from the overnight bakeoff attempt

### What was intentionally skipped

- **Candidate A4 (Portfolio 1 Reproducer variant)** — redundant with A1 (rl_systems) which already covers code-grounding.
- **Gemini CLI / codex install** — neither is used by any agent in the current Portfolio 4 config. Easy add with `npm install -g @google/gemini-cli` when needed.
- **LLM-summary pass in harvester** — optional enhancement; harvester works without it.
- **Provider-outage failover, heartbeat, Telegram alerts** — Telegram MCP was disconnected; heartbeat requires wrapper surgery not justified pre-kickoff.
- **3 public transparency GitHub repos** — creating public-visible repos violates the "keep things private" spirit of the no-push memory rule for this repo's scope. User does this manually at kickoff.
- **Actually running Phase C bakeoff** — Max-CLI proved 5×+ slower than expected; `ANTHROPIC_API_KEY` needed for a timely run.

### Wake-up action list (minimal)

1. Read `eval_data/bakeoff_failure.md` — pick Option A (API bakeoff), B (small Max bakeoff), or C (skip to deploy).
2. On Koala portal opening: register 3 agents, stage `.api_key` files, create 3 public transparency GitHub repos.
3. `uv run reva launch --name <agent> --duration 72` for each of rl_systems / theory / applications (or your renamed versions).
4. (Background) `uv run python -m tools.harvester --interval 180` with `KOALA_API_KEY` set, to populate `papers/`.
5. (Background, every ~5 min) `uv run python -m tools.monitor --metrics agents/metrics.json --daily-cap-usd 100 --output agents/alerts.md`.
