"""CLI commands for cast module."""

from __future__ import annotations

import argparse

from confpatch.cast import CAST_TYPES, CastError, cast_key
from confpatch.loaders import load_config, save_config


def cmd_cast(args: argparse.Namespace) -> None:
    if not args.pairs:
        print("No key:type pairs provided.")
        return

    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
        return

    result_config = config
    all_changes = []

    for pair in args.pairs:
        if ":" not in pair:
            print(f"Invalid pair format {pair!r}. Expected key:type")
            return
        key_path, to_type = pair.split(":", 1)
        try:
            result = cast_key(result_config, key_path.strip(), to_type.strip())
            result_config = result.config
            all_changes.extend(result.changes)
        except CastError as e:
            print(f"Cast error: {e}")
            return

    if not all_changes:
        print("No values changed.")
        return

    for path, old, new in all_changes:
        print(f"  {path}: {old!r} -> {new!r} ({type(new).__name__})")

    if args.dry_run:
        print("Dry run — no changes written.")
        return

    save_config(result_config, args.config)
    print(f"Saved: {args.config}")


def register_cast_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("cast", help="Cast config values to a target type")
    p.add_argument("config", help="Path to config file")
    p.add_argument(
        "pairs",
        nargs="+",
        metavar="key:type",
        help=f"Key path and target type pairs (types: {', '.join(CAST_TYPES)})",
    )
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=cmd_cast)
