"""Operational tripwires for live competition agents.

Three tripwires evaluate per-agent state and fire alerts:

1. **Strike tripwire** — `strike_count` approaching the 3rd-after-free -10 karma
   cliff. Warn at 5, critical at 7.
2. **Karma tripwire** — low karma means future first-comments become rationed.
   Warn below 50, critical below 20.
3. **API-spend tripwire** — rolling 24h spend vs a per-agent daily cap.
   Warn at 80%, critical at 100%.

Input state is an `AgentMetrics` record. Source of truth is either the Koala
`GET /users/me` response (exposed as karma + strike_count) plus a locally
maintained per-agent spend log, or a JSON dump of those two written by each
agent's reva launch wrapper.

This module is pure logic + a CLI renderer; it does not fetch anything
itself. Wire the fetch in a wrapper script that calls
`evaluate_agent(AgentMetrics(...), daily_cap_usd=...)` on a schedule.
"""

from __future__ import annotations

import argparse
import enum
import json
from dataclasses import dataclass
from pathlib import Path


_STRIKE_WARN = 5
_STRIKE_CRITICAL = 7
_KARMA_WARN = 50.0
_KARMA_CRITICAL = 20.0
_SPEND_WARN_FRACTION = 0.8


class TripwireSeverity(str, enum.Enum):
    warn = "warn"
    critical = "critical"


@dataclass(frozen=True)
class AgentMetrics:
    agent_name: str
    karma: float
    strike_count: int
    spend_usd_24h: float


@dataclass(frozen=True)
class Tripwire:
    agent_name: str
    kind: str
    severity: TripwireSeverity
    message: str
    metric_value: float
    threshold: float


def check_strike(metrics: AgentMetrics) -> Tripwire | None:
    if metrics.strike_count >= _STRIKE_CRITICAL:
        return Tripwire(
            agent_name=metrics.agent_name,
            kind="strike",
            severity=TripwireSeverity.critical,
            message=f"strike_count={metrics.strike_count} — next 3rd strike cycle triggers -10 karma",
            metric_value=float(metrics.strike_count),
            threshold=float(_STRIKE_CRITICAL),
        )
    if metrics.strike_count >= _STRIKE_WARN:
        return Tripwire(
            agent_name=metrics.agent_name,
            kind="strike",
            severity=TripwireSeverity.warn,
            message=f"strike_count={metrics.strike_count} approaching -10 karma cliff",
            metric_value=float(metrics.strike_count),
            threshold=float(_STRIKE_WARN),
        )
    return None


def check_karma(metrics: AgentMetrics) -> Tripwire | None:
    if metrics.karma < _KARMA_CRITICAL:
        return Tripwire(
            agent_name=metrics.agent_name,
            kind="karma",
            severity=TripwireSeverity.critical,
            message=f"karma={metrics.karma:.1f} below critical floor — halt first-commenting",
            metric_value=metrics.karma,
            threshold=_KARMA_CRITICAL,
        )
    if metrics.karma < _KARMA_WARN:
        return Tripwire(
            agent_name=metrics.agent_name,
            kind="karma",
            severity=TripwireSeverity.warn,
            message=f"karma={metrics.karma:.1f} — throttle first-comment activity",
            metric_value=metrics.karma,
            threshold=_KARMA_WARN,
        )
    return None


def check_api_spend(metrics: AgentMetrics, *, daily_cap_usd: float) -> Tripwire | None:
    if daily_cap_usd <= 0:
        return None
    fraction = metrics.spend_usd_24h / daily_cap_usd
    if metrics.spend_usd_24h >= daily_cap_usd:
        return Tripwire(
            agent_name=metrics.agent_name,
            kind="spend",
            severity=TripwireSeverity.critical,
            message=f"spend=${metrics.spend_usd_24h:.2f} at or past daily cap ${daily_cap_usd:.2f}",
            metric_value=metrics.spend_usd_24h,
            threshold=daily_cap_usd,
        )
    if fraction >= _SPEND_WARN_FRACTION:
        return Tripwire(
            agent_name=metrics.agent_name,
            kind="spend",
            severity=TripwireSeverity.warn,
            message=f"spend=${metrics.spend_usd_24h:.2f} ({fraction:.0%} of ${daily_cap_usd:.2f} cap)",
            metric_value=metrics.spend_usd_24h,
            threshold=daily_cap_usd,
        )
    return None


def evaluate_agent(metrics: AgentMetrics, *, daily_cap_usd: float) -> list[Tripwire]:
    candidates = [
        check_strike(metrics),
        check_karma(metrics),
        check_api_spend(metrics, daily_cap_usd=daily_cap_usd),
    ]
    return [c for c in candidates if c is not None]


def render_alert_markdown(wires: list[Tripwire]) -> str:
    if not wires:
        return "# Tripwire status: OK\n\nNo alerts fired."
    lines = ["# Tripwire alerts\n"]
    lines.append("| Agent | Kind | Severity | Value | Threshold | Message |")
    lines.append("|---|---|---|---|---|---|")
    for w in wires:
        lines.append(
            f"| {w.agent_name} | {w.kind} | **{w.severity.value}** | "
            f"{w.metric_value} | {w.threshold} | {w.message} |"
        )
    return "\n".join(lines) + "\n"


def _load_metrics_file(path: Path) -> list[AgentMetrics]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        AgentMetrics(
            agent_name=row["agent_name"],
            karma=float(row["karma"]),
            strike_count=int(row["strike_count"]),
            spend_usd_24h=float(row.get("spend_usd_24h", 0.0)),
        )
        for row in payload
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate tripwires for live agents.")
    parser.add_argument(
        "--metrics",
        type=Path,
        required=True,
        help="JSON array of {agent_name, karma, strike_count, spend_usd_24h}.",
    )
    parser.add_argument(
        "--daily-cap-usd",
        type=float,
        default=50.0,
        help="Per-agent daily API spend cap in USD.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the markdown alert report.",
    )
    args = parser.parse_args()
    metrics = _load_metrics_file(args.metrics)
    all_wires: list[Tripwire] = []
    for m in metrics:
        all_wires.extend(evaluate_agent(m, daily_cap_usd=args.daily_cap_usd))
    md = render_alert_markdown(all_wires)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
