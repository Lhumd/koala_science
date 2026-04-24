# Wake-up runbook — Koala ICML 2026 competition

Everything staged overnight. Competition kicks off **2026-04-24 at 12:00 local**. This runbook gets you from "just woke up" to "3 agents launched" in ~60 minutes.

## State summary (as left by overnight run)

✅ 4 candidate system prompts written in `agent_configs/{baseline_a0,rl_systems,theory,applications}/`
✅ ICML 2025 eval set built and subsampled to 120 balanced papers (`eval_data/icml_2025_eval.jsonl`)
✅ Bakeoff runner staged: `tools/bakeoff.sh`
✅ Analysis generator staged: `tools/analyze_bakeoff.py`
✅ Competition vault scaffolded at `~/Desktop/my_code/koala_vault/`
✅ 153 tests passing
⚠️ **Blocked on your action:** `ANTHROPIC_API_KEY` (Phase C bakeoff), Koala API keys (Phase E deploy), per-agent transparency GitHub repos

## Step 1 — Pick your bakeoff backend (~2 min)

The bakeoff runner supports two backends, selected via `bakeoff.config.yaml` or the `--backend` flag:

- **`claude-cli` (default in committed `bakeoff.config.yaml`)** — uses the local `claude` CLI, your Max subscription or whatever auth is configured. **No API key needed.** ~90–180 min wall-clock, burns Max weekly quota (~2–5%).
- **`api`** — Anthropic SDK with prompt caching. Requires `ANTHROPIC_API_KEY`. ~40 min wall-clock, ~$7–25 in API credits.

To flip backends, edit `bakeoff.config.yaml` or set `BAKEOFF_BACKEND=api` / `BAKEOFF_BACKEND=claude-cli` in the env before running the script. If you want API and have a key:

```bash
export PATH="$HOME/.local/bin:$PATH"
cd ~/Desktop/my_code/koala_science
export ANTHROPIC_API_KEY=sk-ant-...
# or persist in .env:
cat > .env <<EOF
ANTHROPIC_API_KEY=sk-ant-...
EOF
export BAKEOFF_BACKEND=api
```

## Step 2 — Run the bakeoff

```bash
./tools/bakeoff.sh 2>&1 | tee runs/bakeoff.log
```

This runs 4 candidates × 120 papers = 480 calls. Expected output: `runs/preds_*.jsonl` + `runs/metrics.json`.

If you hit rate limits (429 / quota alerts), bump the sleep:

```bash
BAKEOFF_SLEEP=2.0 ./tools/bakeoff.sh
```

**Note for Max backend:** the bakeoff may already be running when you wake up — an overnight invocation started one using `claude-cli`. Check `/tmp/bakeoff.log` and `runs/preds_*.jsonl` to see progress. If it completed while you slept, skip to Step 3. If it's still running or failed, restart with whatever backend fits your quota state.

## Step 3 — Analyze and pick winners (~5 min)

```bash
uv run python -m tools.analyze_bakeoff \
    --metrics runs/metrics.json \
    --output eval_data/bakeoff_analysis.md
cat eval_data/bakeoff_analysis.md
```

Expected result: Portfolio 4 specialists each win their own cluster. If any specialist loses to `baseline_a0` on its own cluster, deploy `baseline_a0` in place of that specialist. If `baseline_a0` wins 2+ clusters, pivot to Portfolio 2 (three generalists) — use three variations of `baseline_a0` with different personas.

## Step 4 — Register agents on Koala (~15 min, partly blocked on registration opening)

Go to `koala.science/owners` and register 3 agents. For each:

1. Create the agent on Koala (it issues an API key once — save immediately).
2. Create a public transparency GitHub repo (e.g. `koala-rl-systems`, `koala-theory`, `koala-applications`) — **not** under `Lhumd/koala_science` (that's your private strategy repo).
3. Stage the Koala API key:
   ```bash
   echo 'cs_your_koala_key' > agent_configs/rl_systems/.api_key
   echo 'cs_your_koala_key' > agent_configs/theory/.api_key
   echo 'cs_your_koala_key' > agent_configs/applications/.api_key
   chmod 600 agent_configs/*/.api_key
   ```
4. Stage a deploy key or fine-grained PAT in each agent's workdir so it can `git push` reasoning files at runtime.
5. Set the Koala profile `description` per each agent's system prompt (first section of the prompt has the copy).

## Step 5 — Install backend CLI (~2 min)

```bash
npm install -g @anthropic-ai/claude-code   # if not already installed
claude --version                            # confirm
```

## Step 6 — Final smoke check (~5 min)

```bash
# Confirm tests still green
uv run pytest

# Confirm no agents stale
uv run reva status

# Confirm gitignore protects secrets
git status | grep -E '\.api_key|eval_data|runs|koala_vault' || echo "clean"

# Dry-run assembly for each agent (confirms the prompt sections concatenate)
for name in rl_systems theory applications; do
    echo "=== $name ==="
    uv run python -c "
from pathlib import Path
from reva.prompt import assemble_prompt
prompt = assemble_prompt(
    global_rules_path=Path('agent_definition/GLOBAL_RULES.md'),
    platform_skills_path=Path('agent_definition/platform_skills.md'),
    agent_prompt_path=Path(f'agent_configs/$name/system_prompt.md'),
)
print(f'{len(prompt)} chars total')
    " 2>&1 | head -3
done
```

## Step 7 — Launch (~5 min)

At or after 12:00:

```bash
# For each winning agent (use names from your Koala registration):
uv run reva launch --name rl_systems   --duration 72
uv run reva launch --name theory       --duration 72
uv run reva launch --name applications --duration 72
```

Each runs in its own tmux session named `reva_<name>`. Auto-restarts on exit.

Watch them:

```bash
uv run reva view                       # interactive TUI
uv run reva log --all                  # stream all agents
```

## If something breaks

- **Agent keeps failing on `github_file_url`** → check deploy-key auth in its workdir; `git push` from inside the tmux session to debug.
- **Agent hits `402 Payment Required`** → karma exhausted; stop it, recalibrate its first-commenter selectivity.
- **Agent hits repeated `422` moderation rejections** → strike count approaching the -10 karma cliff; kill and review its recent comment style.
- **Quota exhausted on API** → switch to a different backend (`--backend codex` or `--backend gemini-cli`) for the affected agent.
- **All agents silent** → check tmux sessions exist (`tmux ls | grep reva_`), Anthropic API status, Koala platform status.

## References

- Strategy and design catalog: `AGENT_DESIGNS.md`
- Full pre-kickoff plan: `~/.claude/plans/floating-zooming-sphinx.md`
- High-level TODO: `TODO.md`
- Vault: `~/Desktop/my_code/koala_vault/10 Projects/Koala Science/README.md`
- Authoritative platform rules: [koala.science/skill.md](https://koala.science/skill.md)
