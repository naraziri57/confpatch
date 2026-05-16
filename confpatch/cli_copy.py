"""CLI commands for the copy feature."""

from __future__ import annotations

import argparse

from confpatch.copy import CopyError, copy_keys
from confpatch.loaders import load_config, save_config


def cmd_copy(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}")
        return 1

    if not args.pairs:
        print("Error: at least one SRC:DST pair required.")
        return 1

    pairs: list[tuple[str, str]] = []
    for pair in args.pairs:
        if ":" not in pair:
            print(f"Error: invalid pair format '{pair}', expected SRC:DST")
            return 1
        src, dst = pair.split(":", 1)
        pairs.append((src.strip(), dst.strip()))

    try:
        new_config, report = copy_keys(config, pairs, overwrite=args.overwrite)
    except CopyError as exc:
        print(f"Error: {exc}")
        return 1

    if args.dry_run:
        print("[dry-run] " + report.summary())
        return 0

    save_config(new_config, args.config)
    print(report.summary())
    return 0


def register_copy_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("copy", help="Copy keys within a config file")
    p.add_argument("config", help="Path to the config file")
    p.add_argument(
        "pairs",
        nargs="+",
        metavar="SRC:DST",
        help="Key pairs to copy, e.g. database.host:backup.host",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite destination key if it already exists",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing",
    )
    p.set_defaults(func=cmd_copy)
