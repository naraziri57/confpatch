"""CLI commands for type coercion of config values."""
from __future__ import annotations

import argparse
import sys

from confpatch.coerce import coerce_keys, CoerceError
from confpatch.loaders import load_config, save_config


def cmd_coerce(args: argparse.Namespace) -> None:
    if not args.config.exists():
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    if not args.coerce:
        print("No coercions specified. Use --coerce key=type.", file=sys.stderr)
        sys.exit(1)

    coercions: dict[str, str] = {}
    for item in args.coerce:
        if "=" not in item:
            print(f"Error: invalid coercion spec {item!r}, expected key=type", file=sys.stderr)
            sys.exit(1)
        key, _, target_type = item.partition("=")
        coercions[key.strip()] = target_type.strip()

    try:
        config = load_config(args.config)
        result = coerce_keys(config, coercions)
    except CoerceError as e:
        print(f"Coerce error: {e}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if args.dry_run:
        print("Dry run — no changes written.")
        return

    save_config(args.config, result.coerced)
    print(f"Saved: {args.config}")


def register_coerce_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("coerce", help="Coerce config values to specified types")
    p.add_argument("config", type=__import__("pathlib").Path, help="Config file to modify")
    p.add_argument(
        "--coerce",
        metavar="KEY=TYPE",
        nargs="+",
        help="One or more key=type coercions (e.g. port=int debug=bool)",
    )
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=cmd_coerce)
