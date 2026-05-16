"""CLI commands for pruning null/empty values from config files."""
from __future__ import annotations
import argparse
from confpatch.loaders import load_config, save_config
from confpatch.prune import prune_config, PruneError


def cmd_prune(args: argparse.Namespace) -> None:
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}")
        return

    try:
        result = prune_config(config, prune_empty=args.empty)
    except PruneError as e:
        print(f"Prune error: {e}")
        return

    print(result.summary())

    if args.dry_run:
        print("Dry run — no changes written.")
        return

    if result.has_removals():
        save_config(result.pruned, args.config)
        print(f"Saved pruned config to {args.config}")
    else:
        print("Nothing to prune.")


def register_prune_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("prune", help="Remove null/empty values from a config file")
    p.add_argument("config", help="Path to config file")
    p.add_argument(
        "--empty",
        action="store_true",
        default=False,
        help="Also prune empty strings, lists, and dicts",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing",
    )
    p.set_defaults(func=cmd_prune)
