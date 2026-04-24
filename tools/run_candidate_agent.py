"""Run a candidate agent design against an eval set and write predictions.

Backend selection is controlled by `tools/bakeoff_backends.py`. Default is the
Anthropic SDK backend (needs `ANTHROPIC_API_KEY`). A YAML config file can flip
the backend to the local `claude` CLI (Max subscription / local auth).

Usage:
    # API backend (default, needs ANTHROPIC_API_KEY):
    python -m tools.run_candidate_agent \\
        --system-prompt agent_configs/rl_systems/system_prompt.md \\
        --eval-set eval_data/icml_2025_eval.jsonl \\
        --agent-name rl_systems \\
        --output runs/preds_rl_systems.jsonl

    # Claude CLI backend (uses local auth / Max):
    python -m tools.run_candidate_agent --backend claude-cli \\
        --system-prompt agent_configs/rl_systems/system_prompt.md \\
        --eval-set eval_data/icml_2025_eval.jsonl \\
        --agent-name rl_systems \\
        --output runs/preds_rl_systems.jsonl

    # Or via YAML config:
    python -m tools.run_candidate_agent --config bakeoff.config.yaml ...
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from tools.eval_agents import EvalPaper, load_eval_set

_DEFAULT_MODEL = "claude-sonnet-4-6"
_SCORE_PATTERN = re.compile(r"SCORE:\s*(-?\d+(?:\.\d+)?)")


def build_user_message(paper: EvalPaper) -> str:
    pdf_line = f"\nPDF: {paper.pdf_url}" if paper.pdf_url else ""
    return (
        f"Paper ID: {paper.paper_id}\n"
        f"Domain cluster: {paper.domain or 'general'}\n"
        f"Title: {paper.title}\n"
        f"{pdf_line}\n"
        f"Abstract:\n{paper.abstract}\n\n"
        "Review this paper according to your system prompt. At the end, emit a single "
        "line of the form `SCORE: X.Y` where X.Y is your 0-10 Koala verdict (float)."
    )


def parse_score(text: str) -> float:
    match = _SCORE_PATTERN.search(text)
    if match is None:
        raise ValueError(f"no score found in response (tail 200 chars): {text[-200:]!r}")
    value = float(match.group(1))
    if value > 10.0:
        return 10.0
    if value < 0.0:
        return 0.0
    return value


def run_candidate_on_paper(
    *,
    system_prompt: str,
    paper: EvalPaper,
    backend,
) -> float:
    return backend.score(system_prompt=system_prompt, user_message=build_user_message(paper))


def run_candidate_over_eval_set(
    *,
    system_prompt: str,
    eval_set: list[EvalPaper],
    agent_name: str,
    output_path: Path,
    backend,
    sleep_between_calls_s: float = 0.0,
    on_error: str = "skip",
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for paper in eval_set:
            try:
                score = run_candidate_on_paper(
                    system_prompt=system_prompt, paper=paper, backend=backend
                )
            except Exception as exc:
                if on_error == "raise":
                    raise
                print(f"[{agent_name}] skipping {paper.paper_id}: {exc}")
                continue
            row = {
                "paper_id": paper.paper_id,
                "agent_name": agent_name,
                "score": score,
            }
            f.write(json.dumps(row) + "\n")
            f.flush()
            if sleep_between_calls_s > 0:
                time.sleep(sleep_between_calls_s)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a candidate agent against an eval set.")
    parser.add_argument("--system-prompt", type=Path, required=True)
    parser.add_argument("--eval-set", type=Path, required=True)
    parser.add_argument("--agent-name", type=str, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("bakeoff.config.yaml"),
        help="YAML config with backend/model/sleep (missing file → defaults).",
    )
    parser.add_argument(
        "--backend",
        choices=["api", "claude-cli"],
        default=None,
        help="Override the backend from the config file.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the model from the config file.",
    )
    parser.add_argument(
        "--sleep-between-calls",
        type=float,
        default=None,
        help="Override the inter-call sleep from the config file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max papers to score (for debugging / cheap dry runs).",
    )
    args = parser.parse_args()

    from tools.bakeoff_backends import BackendConfig, build_backend, load_config

    cfg = load_config(args.config)
    cfg = BackendConfig(
        backend=args.backend or cfg.backend,
        model=args.model or cfg.model,
        sleep_between_calls=(
            args.sleep_between_calls if args.sleep_between_calls is not None else cfg.sleep_between_calls
        ),
    )
    print(f"[{args.agent_name}] backend={cfg.backend} model={cfg.model} sleep={cfg.sleep_between_calls}s")
    backend = build_backend(cfg)

    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    eval_set = load_eval_set(args.eval_set)
    if args.limit is not None:
        eval_set = eval_set[: args.limit]

    run_candidate_over_eval_set(
        system_prompt=system_prompt,
        eval_set=eval_set,
        agent_name=args.agent_name,
        output_path=args.output,
        backend=backend,
        sleep_between_calls_s=cfg.sleep_between_calls,
    )
    print(f"wrote predictions to {args.output}")


if __name__ == "__main__":
    main()
