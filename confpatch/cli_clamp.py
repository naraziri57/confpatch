"""CLI commands for the clamp feature."""

from __future__ import annotations

import argparse

from confpatch.clamp import ClampError, clamp_config
from confpatch.loaders import load_config, save_config


def cmd_clamp(args: argparse.Namespace) -> None:
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}")
        return

    keys = args.keys if args.keys else None
    min_val = args.min
    max_val = args.max

    if min_val is None and max_val is None:
        print("Error: at least one of --min or --max must be specified.")
        return

    try:
        result = clamp_config(config, min_val=min_val, max_val=max_val, keys=keys)
    except ClampError as e:
        print(f"Clamp error: {e}")
        return

    print(result.summary())

    if args.dry_run:
        print("Dry run: no changes written.")
        return

    if result.has_changes():
        save_config(result.clamped, args.config)
        print(f"Saved: {args.config}")


def register_clamp_commands(subparsers) -> None:
    p = subparsers.add_parser("clamp", help="Clamp numeric values in a config file")
    p.add_argument("config", help="Path to config file")
    p.add_argument("--min", type=float, default=None, help="Minimum allowed value")
    p.add_argument("--max", type=float, default=None, help="Maximum allowed value")
    p.add_argument("--keys", nargs="+", default=None, help="Specific keys to clamp (dot notation)")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=cmd_clamp)
