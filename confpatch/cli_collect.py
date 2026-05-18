"""CLI commands for the collect feature."""

from __future__ import annotations

import json
import sys

from confpatch.collect import CollectError, collect_keys
from confpatch.loaders import load_config


def cmd_collect(args) -> int:
    """Collect specific keys from a config file and print them."""
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        return 1

    if not args.keys:
        print("Error: at least one key must be specified", file=sys.stderr)
        return 1

    try:
        result = collect_keys(
            config,
            args.keys,
            skip_missing=getattr(args, "skip_missing", False),
        )
    except CollectError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.collected, indent=2))
    else:
        for key, value in result.collected.items():
            print(f"{key}: {value}")
        if result.missing:
            print(f"Missing keys: {', '.join(result.missing)}", file=sys.stderr)

    return 0


def register_collect_commands(subparsers) -> None:
    parser = subparsers.add_parser("collect", help="Collect specific keys from a config")
    parser.add_argument("config", help="Path to config file")
    parser.add_argument("keys", nargs="+", help="Keys to collect (dot notation supported)")
    parser.add_argument(
        "--skip-missing",
        action="store_true",
        default=False,
        help="Skip missing keys instead of failing",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output as JSON",
    )
    parser.set_defaults(func=cmd_collect)
