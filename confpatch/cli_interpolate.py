"""CLI command for resolving in-config interpolations."""

from __future__ import annotations

import argparse
import sys

from confpatch.interpolate import InterpolateError, interpolate_config
from confpatch.loaders import load_config, save_config


def cmd_interpolate(args: argparse.Namespace) -> None:
    config_path = args.config
    dry_run = getattr(args, "dry_run", False)
    fmt = getattr(args, "format", None)

    try:
        config, detected_fmt = load_config(config_path, fmt=fmt)
    except FileNotFoundError:
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        result = interpolate_config(config)
    except InterpolateError as exc:
        print(f"Interpolation error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not result.has_changes():
        print("No interpolations found.")
        return

    print(result.summary())

    if dry_run:
        print("Dry run — no changes written.")
        return

    save_config(config_path, result.result, fmt=detected_fmt)
    print(f"Saved: {config_path}")


def register_interpolate_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    p = subparsers.add_parser(
        "interpolate",
        help="Resolve ${key} references inside a config file",
    )
    p.add_argument("config", help="Path to config file")
    p.add_argument(
        "--format",
        choices=["yaml", "toml"],
        default=None,
        help="Force config format",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be resolved without writing",
    )
    p.set_defaults(func=cmd_interpolate)
