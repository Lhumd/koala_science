"""Pluggable LLM backend for the bakeoff runner.

Two backends today:

- `AnthropicBackend` — uses the Anthropic Python SDK with prompt caching.
  Requires `ANTHROPIC_API_KEY`. Default for production and cost-controlled
  evaluation.

- `ClaudeCLIBackend` — shells out to the `claude` CLI (Claude Code). Uses
  whatever auth the CLI is configured with locally (OAuth/Max subscription,
  `apiKeyHelper`, or `ANTHROPIC_API_KEY`). Useful if the user has a Max
  subscription and wants to exercise the bakeoff without burning API credit.

Selection happens via a `BackendConfig` which is either constructed
programmatically or loaded from a YAML file. Example `bakeoff.config.yaml`:

    backend: claude-cli
    model: claude-sonnet-4-6
    sleep_between_calls: 0.5
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import yaml

from tools.run_candidate_agent import parse_score


_DEFAULT_MODEL = "claude-sonnet-4-6"
_DEFAULT_SLEEP = 0.5
_DEFAULT_BACKEND = "api"
_CLI_CALL_TIMEOUT_S = 300


@dataclass(frozen=True)
class BackendConfig:
    backend: str
    model: str
    sleep_between_calls: float


def load_config(path: Path) -> BackendConfig:
    defaults = {
        "backend": _DEFAULT_BACKEND,
        "model": _DEFAULT_MODEL,
        "sleep_between_calls": _DEFAULT_SLEEP,
    }
    if not path.exists():
        return BackendConfig(**defaults)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        raw = {}
    merged = {**defaults, **raw}
    return BackendConfig(
        backend=str(merged["backend"]),
        model=str(merged["model"]),
        sleep_between_calls=float(merged["sleep_between_calls"]),
    )


class LLMBackend(Protocol):
    model: str

    def score(self, system_prompt: str, user_message: str) -> float: ...


class AnthropicBackend:
    def __init__(self, client: object, model: str, max_tokens: int = 2048) -> None:
        self.client = client
        self.model = model
        self.max_tokens = max_tokens

    def score(self, system_prompt: str, user_message: str) -> float:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        )
        return parse_score(message.content[0].text)


class ClaudeCLIBackend:
    def __init__(self, model: str, timeout_s: int = _CLI_CALL_TIMEOUT_S) -> None:
        self.model = model
        self.timeout_s = timeout_s

    def score(self, system_prompt: str, user_message: str) -> float:
        cmd = [
            "claude",
            "--print",
            "--append-system-prompt",
            system_prompt,
            "--model",
            self.model,
            user_message,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout_s,
            check=True,
        )
        return parse_score(result.stdout)


def build_backend(
    config: BackendConfig,
    *,
    anthropic_client: object | None = None,
) -> LLMBackend:
    if config.backend == "api":
        client = anthropic_client if anthropic_client is not None else _default_anthropic_client()
        return AnthropicBackend(client=client, model=config.model)
    if config.backend == "claude-cli":
        return ClaudeCLIBackend(model=config.model)
    raise ValueError(
        f"unknown backend: {config.backend!r}. "
        f"Choose 'api' (Anthropic SDK, needs ANTHROPIC_API_KEY) or "
        f"'claude-cli' (Claude Code CLI, uses local auth / Max)."
    )


def _default_anthropic_client() -> object:
    import anthropic

    return anthropic.Anthropic()
