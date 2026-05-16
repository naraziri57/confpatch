"""CLI commands for renaming config keys."""

from __future__ import annotations

import argparse
import sys

from confpatch.loaders import load_config, save_config
from confpatch.rename import RenameError, rename_keys


def cmd_rename(args: argparse.Namespace) -> int:
    if not args.config.exists():
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        return 1

    try:
        config = load_config(args.config)
    except Exception as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    renames: dict[str, str] = {}
    for pair in args.rename:
        if ":" not in pair:
            print(f"Error: invalid rename spec (expected old:new): {pair!r}", file=sys.stderr)
            return 1
        old, new = pair.split(":", 1)
        renames[old.strip()] = new.strip()

    if not renames:
        print("No renames specified.", file=sys.stderr)
        return 1

    try:
        new_config, report = rename_keys(config, renames, skip_missing=args.skip_missing)
    except RenameError as exc:
        print(f"Rename error: {exc}", file=sys.stderr)
        return 1

    print(report.summary())

    if args.dry_run:
        print("Dry run — no changes written.")
        return 0

    try:
        save_config(args.config, new_config)
    except Exception as exc:
        print(f"Error saving config: {exc}", file=sys.stderr)
        return 1

    return 0


def register_rename_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("rename", help="Rename keys in a config file")
    p.add_argument("config", type=__import__("pathlib").Path, help="Config file path")
    p.add_argument(
        "rename",
        nargs="+",
        metavar="OLD:NEW",
        help="Key rename spec in old.path:new_name format",
    )
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.add_argument("--skip-missing", action="store_true", help="Skip keys that don't exist")
    p.set_defaults(func=cmd_rename)
