"""CLI commands for the group feature."""

from __future__ import annotations

import sys

from confpatch.group import GroupError, group_keys
from confpatch.loaders import load_config, save_config


def cmd_group(args) -> None:
    import os

    if not os.path.exists(args.config):
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    if not args.keys:
        print("Error: no keys specified (use --keys KEY [KEY ...])", file=sys.stderr)
        sys.exit(1)

    if not args.group:
        print("Error: --group path is required.", file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(args.config)
        result = group_keys(
            config,
            keys=args.keys,
            group=args.group,
            overwrite=getattr(args, "overwrite", False),
        )
    except GroupError as exc:
        print(f"Group error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if args.dry_run:
        print("Dry run — no changes written.")
        return

    save_config(args.config, result.grouped)
    print(f"Saved: {args.config}")


def register_group_commands(subparsers) -> None:
    parser = subparsers.add_parser(
        "group",
        help="Move top-level keys into a nested group section.",
    )
    parser.add_argument("config", help="Config file to modify.")
    parser.add_argument(
        "--keys",
        nargs="+",
        required=True,
        metavar="KEY",
        help="Top-level keys to move into the group.",
    )
    parser.add_argument(
        "--group",
        required=True,
        metavar="PATH",
        help="Dot-separated path of the destination group (e.g. 'database.credentials').",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite keys that already exist in the target group.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Show what would change without writing.",
    )
    parser.set_defaults(func=cmd_group)
