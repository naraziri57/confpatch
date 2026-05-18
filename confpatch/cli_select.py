"""CLI commands for the select feature."""

from __future__ import annotations

import json
import sys

from confpatch.loaders import load_config, save_config
from confpatch.select import SelectError, select_keys


def cmd_select(args) -> int:
    """Select specific keys from a config file and write or print the result."""
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        return 1

    if not args.keys:
        print("Error: at least one key must be provided via --keys", file=sys.stderr)
        return 1

    try:
        result = select_keys(config, args.keys, strict=args.strict)
    except SelectError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.selected, indent=2))
        return 0

    if args.dry_run:
        print(result.summary())
        for key, val in result.selected.items():
            print(f"  {key}: {val!r}")
        if result.missing:
            print(f"  (missing: {', '.join(result.missing)})")
        return 0

    if args.output:
        save_config(result.selected, args.output)
        print(f"Wrote {result.count()} key(s) to {args.output}")
    else:
        print(result.summary())
        for key, val in result.selected.items():
            print(f"  {key}: {val!r}")

    return 0


def register_select_commands(subparsers) -> None:
    parser = subparsers.add_parser("select", help="Select specific keys from a config")
    parser.add_argument("config", help="Path to config file")
    parser.add_argument(
        "--keys", nargs="+", metavar="KEY", help="Keys to select (dot-notation supported)"
    )
    parser.add_argument(
        "--output", metavar="FILE", help="Write selected keys to this file"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Fail if any key is missing"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without writing"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    parser.set_defaults(func=cmd_select)
