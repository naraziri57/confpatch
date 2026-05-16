"""CLI commands for the reorder feature."""

from __future__ import annotations
import argparse
from confpatch.loaders import load_config, save_config
from confpatch.reorder import reorder_keys, ReorderError


def cmd_reorder(args: argparse.Namespace) -> None:
    from pathlib import Path

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return

    try:
        config = load_config(str(config_path))
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    order = args.keys
    scope = getattr(args, "scope", None)

    try:
        result = reorder_keys(config, order, scope=scope)
    except ReorderError as e:
        print(f"Reorder error: {e}")
        return

    print(result.summary())

    if args.dry_run:
        print("Dry run — no changes written.")
        return

    if result.has_changes():
        try:
            save_config(result.reordered, str(config_path))
            print(f"Saved: {config_path}")
        except Exception as e:
            print(f"Error saving config: {e}")
    else:
        print("Nothing to write.")


def register_reorder_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("reorder", help="Reorder keys in a config file")
    p.add_argument("config", help="Path to config file")
    p.add_argument("keys", nargs="+", help="Desired key order")
    p.add_argument("--scope", default=None, help="Dot-notation path to nested dict to reorder")
    p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    p.set_defaults(func=cmd_reorder)
