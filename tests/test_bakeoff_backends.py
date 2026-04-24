from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.bakeoff_backends import (
    AnthropicBackend,
    BackendConfig,
    ClaudeCLIBackend,
    build_backend,
    load_config,
)


def test_load_config_defaults_when_file_missing(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "nonexistent.yaml")
    assert cfg.backend == "api"
    assert cfg.model == "claude-sonnet-4-6"
    assert cfg.sleep_between_calls == 0.5


def test_load_config_from_yaml(tmp_path: Path) -> None:
    path = tmp_path / "bakeoff.config.yaml"
    path.write_text(
        "backend: claude-cli\nmodel: claude-opus-4-7\nsleep_between_calls: 1.0\n",
        encoding="utf-8",
    )
    cfg = load_config(path)
    assert cfg.backend == "claude-cli"
    assert cfg.model == "claude-opus-4-7"
    assert cfg.sleep_between_calls == 1.0


def test_load_config_partial_merges_with_defaults(tmp_path: Path) -> None:
    path = tmp_path / "bakeoff.config.yaml"
    path.write_text("backend: claude-cli\n", encoding="utf-8")
    cfg = load_config(path)
    assert cfg.backend == "claude-cli"
    assert cfg.model == "claude-sonnet-4-6"
    assert cfg.sleep_between_calls == 0.5


def test_build_backend_api_default() -> None:
    cfg = BackendConfig(backend="api", model="claude-sonnet-4-6", sleep_between_calls=0.5)
    fake_client = MagicMock()
    backend = build_backend(cfg, anthropic_client=fake_client)
    assert isinstance(backend, AnthropicBackend)
    assert backend.model == "claude-sonnet-4-6"


def test_build_backend_claude_cli() -> None:
    cfg = BackendConfig(backend="claude-cli", model="claude-sonnet-4-6", sleep_between_calls=0.5)
    backend = build_backend(cfg)
    assert isinstance(backend, ClaudeCLIBackend)
    assert backend.model == "claude-sonnet-4-6"


def test_build_backend_unknown_raises() -> None:
    cfg = BackendConfig(backend="bogus", model="claude-sonnet-4-6", sleep_between_calls=0.5)
    with pytest.raises(ValueError, match="unknown backend"):
        build_backend(cfg)


def test_anthropic_backend_score() -> None:
    fake_message = MagicMock()
    fake_message.content = [MagicMock(text="SCORE: 6.5")]
    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_message
    backend = AnthropicBackend(client=fake_client, model="claude-sonnet-4-6")
    score = backend.score("system text", "user message")
    assert score == pytest.approx(6.5)
    kwargs = fake_client.messages.create.call_args.kwargs
    assert kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}


def test_claude_cli_backend_score_invokes_subprocess() -> None:
    with patch("tools.bakeoff_backends.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Verdict reasoning...\nSCORE: 4.2\n", returncode=0)
        backend = ClaudeCLIBackend(model="claude-sonnet-4-6")
        score = backend.score("system text", "user message")
        assert score == pytest.approx(4.2)
        args, _ = mock_run.call_args
        cmd = args[0]
        assert cmd[0] == "claude"
        assert "--print" in cmd
        assert "--append-system-prompt" in cmd
        assert "system text" in cmd
        assert "user message" in cmd
        assert "--model" in cmd
        assert "claude-sonnet-4-6" in cmd


def test_claude_cli_backend_times_out_raises() -> None:
    import subprocess as sp

    with patch("tools.bakeoff_backends.subprocess.run") as mock_run:
        mock_run.side_effect = sp.TimeoutExpired(cmd="claude", timeout=300)
        backend = ClaudeCLIBackend(model="claude-sonnet-4-6")
        with pytest.raises(sp.TimeoutExpired):
            backend.score("system text", "user message")
