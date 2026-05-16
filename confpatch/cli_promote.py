"""CLI commands for the promote feature."""
from __future__ import annotations

import argparse
from pathlib import Path

from confpatch.loaders import load_config, save_config
from confpatch.promote import PromoteError, promote_key


def cmd_promote(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1

    try:
        config = load_config(str(config_path))
    except Exception as exc:
        print(f"Error loading config: {exc}")
        return 1

    try:
        result = promote_key(
            config,
            args.path,
            remove_source=args.remove_source,
            overwrite=args.overwrite,
        )
    except PromoteError as exc:
        print(f"Promote error: {exc}")
        return 1

    if args.dry_run:
        print(result.summary())
        for key, val in result.promoted.items():
            print(f"  {key}: {val}")
        return 0

    save_config(str(config_path), result.config)
    print(result.summary())
    return 0


def register_promote_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("promote", help="Promote nested keys to top level")
    p.add_argument("config", help="Path to config file")
    p.add_argument("path", help="Dot-separated path to nested dict to promote")
    p.add_argument(
        "--remove-source",
        action="store_true",
        default=False,
        help="Remove the source key after promotion",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing top-level keys",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing",
    )
    p.set_defaults(func=cmd_promote)
