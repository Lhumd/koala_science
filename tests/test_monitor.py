from dataclasses import dataclass
from pathlib import Path

import pytest

from tools.monitor import (
    AgentMetrics,
    Tripwire,
    TripwireSeverity,
    check_api_spend,
    check_karma,
    check_strike,
    evaluate_agent,
    render_alert_markdown,
)


def _metrics(
    *,
    karma: float = 100.0,
    strike_count: int = 0,
    spend_usd_24h: float = 0.0,
) -> AgentMetrics:
    return AgentMetrics(
        agent_name="test",
        karma=karma,
        strike_count=strike_count,
        spend_usd_24h=spend_usd_24h,
    )


def test_strike_tripwire_below_threshold_returns_nothing() -> None:
    wire = check_strike(_metrics(strike_count=2))
    assert wire is None


def test_strike_tripwire_warns_at_5() -> None:
    wire = check_strike(_metrics(strike_count=5))
    assert wire is not None
    assert wire.severity == TripwireSeverity.warn
    assert "strike" in wire.message.lower()


def test_strike_tripwire_critical_at_7() -> None:
    wire = check_strike(_metrics(strike_count=7))
    assert wire is not None
    assert wire.severity == TripwireSeverity.critical


def test_karma_tripwire_above_threshold_returns_nothing() -> None:
    assert check_karma(_metrics(karma=80.0)) is None


def test_karma_tripwire_warn_at_50() -> None:
    wire = check_karma(_metrics(karma=49.0))
    assert wire is not None
    assert wire.severity == TripwireSeverity.warn
    assert "karma" in wire.message.lower()


def test_karma_tripwire_critical_at_20() -> None:
    wire = check_karma(_metrics(karma=18.0))
    assert wire is not None
    assert wire.severity == TripwireSeverity.critical


def test_api_spend_tripwire_below_threshold_returns_nothing() -> None:
    assert check_api_spend(_metrics(spend_usd_24h=50.0), daily_cap_usd=100.0) is None


def test_api_spend_tripwire_warn_at_80_percent() -> None:
    wire = check_api_spend(_metrics(spend_usd_24h=85.0), daily_cap_usd=100.0)
    assert wire is not None
    assert wire.severity == TripwireSeverity.warn


def test_api_spend_tripwire_critical_at_cap() -> None:
    wire = check_api_spend(_metrics(spend_usd_24h=120.0), daily_cap_usd=100.0)
    assert wire is not None
    assert wire.severity == TripwireSeverity.critical


def test_evaluate_agent_returns_all_fired_tripwires() -> None:
    m = _metrics(karma=15.0, strike_count=8, spend_usd_24h=120.0)
    wires = evaluate_agent(m, daily_cap_usd=100.0)
    severities = {w.severity for w in wires}
    assert TripwireSeverity.critical in severities
    assert len(wires) == 3


def test_evaluate_agent_returns_empty_when_healthy() -> None:
    m = _metrics(karma=90.0, strike_count=1, spend_usd_24h=10.0)
    assert evaluate_agent(m, daily_cap_usd=100.0) == []


def test_render_alert_markdown_formats_tripwires() -> None:
    wires = [
        Tripwire(
            agent_name="flagship",
            kind="karma",
            severity=TripwireSeverity.warn,
            message="karma 45 < 50 warn threshold",
            metric_value=45.0,
            threshold=50.0,
        )
    ]
    md = render_alert_markdown(wires)
    assert "flagship" in md
    assert "karma" in md.lower()
    assert "45" in md


def test_render_alert_markdown_empty_returns_ok() -> None:
    md = render_alert_markdown([])
    assert "OK" in md or "no alerts" in md.lower()
