"""CLI commands for rollback functionality."""

from __future__ import annotations

import argparse
from pathlib import Path

from confpatch.rollback import rollback, RollbackError, get_last_entry


def cmd_rollback(args: argparse.Namespace) -> int:
    """Undo the last patch applied to a config file."""
    config_path = Path(args.config)

    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1

    if args.dry_run:
        try:
            entry = get_last_entry(config_path)
        except RollbackError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Would restore {config_path} from backup: {entry.backup_path}")
        print(f"  Patch applied at: {entry.timestamp}")
        return 0

    try:
        restored = rollback(config_path)
        print(f"Rolled back {config_path} successfully (restored from {restored}).")
        return 0
    except RollbackError as exc:
        print(f"Rollback failed: {exc}")
        return 1


def register_rollback_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register rollback subcommand on the given subparsers object."""
    parser = subparsers.add_parser(
        "rollback",
        help="Undo the last patch applied to a config file",
    )
    parser.add_argument("config", help="Path to the config file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be rolled back without making changes",
    )
    parser.set_defaults(func=cmd_rollback)
