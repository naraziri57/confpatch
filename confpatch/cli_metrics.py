"""CLI commands for viewing patch metrics."""

from __future__ import annotations

import json
from pathlib import Path

from confpatch.metrics import MetricsError, load_metrics, summarize_metrics


def cmd_metrics_show(args) -> int:
    """Show recorded metrics for a config file."""
    if not Path(args.config).exists():
        print(f"Error: config file not found: {args.config}")
        return 1
    try:
        entries = load_metrics(args.config)
    except MetricsError as exc:
        print(f"Error: {exc}")
        return 1

    if not entries:
        print(f"No metrics recorded for {args.config}")
        return 0

    for e in entries[-args.limit:]:
        status = "OK" if e.success else "FAIL"
        print(f"[{status}] {e.patch_file} -> {e.config_file}  "
              f"keys={e.keys_changed}  {e.duration_ms:.1f}ms")
    return 0


def cmd_metrics_summary(args) -> int:
    """Print a summary of metrics for a config file."""
    if not Path(args.config).exists():
        print(f"Error: config file not found: {args.config}")
        return 1
    try:
        summary = summarize_metrics(args.config)
    except MetricsError as exc:
        print(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Config:          {args.config}")
        print(f"Total patches:   {summary['total']}")
        print(f"Successful:      {summary['successful']}")
        print(f"Failed:          {summary['failed']}")
        print(f"Avg duration:    {summary['avg_duration_ms']} ms")
        print(f"Keys changed:    {summary['total_keys_changed']}")
    return 0


def register_metrics_commands(subparsers) -> None:
    p_show = subparsers.add_parser("metrics-show", help="Show recent patch metrics")
    p_show.add_argument("config", help="Path to config file")
    p_show.add_argument("--limit", type=int, default=20, help="Max entries to show")
    p_show.set_defaults(func=cmd_metrics_show)

    p_summary = subparsers.add_parser("metrics-summary", help="Summarize patch metrics")
    p_summary.add_argument("config", help="Path to config file")
    p_summary.add_argument("--json", action="store_true", help="Output as JSON")
    p_summary.set_defaults(func=cmd_metrics_summary)
