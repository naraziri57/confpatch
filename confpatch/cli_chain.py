"""CLI commands for patch chaining."""

from __future__ import annotations

import argparse

from confpatch.chain import apply_chain, ChainError


def cmd_chain(args: argparse.Namespace) -> None:
    """Apply multiple patch files in sequence."""
    if not args.patches:
        print("No patch files specified.")
        return

    try:
        result = apply_chain(
            config_path=args.config,
            patch_paths=args.patches,
            fmt=getattr(args, "format", None),
            stop_on_error=not args.keep_going,
            dry_run=args.dry_run,
        )
    except ChainError as exc:
        print(f"Error: {exc}")
        return

    print(result.summary())

    for patch in result.patches_applied:
        print(f"  [ok]   {patch}")

    for patch, reason in result.patches_failed:
        print(f"  [fail] {patch}: {reason}")

    if args.dry_run:
        print("(dry-run: no changes written)")


def register_chain_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "chain",
        help="Apply multiple patch files in sequence to a config",
    )
    parser.add_argument("config", help="Path to the config file")
    parser.add_argument(
        "patches",
        nargs="+",
        help="Patch files to apply in order",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "toml"],
        default=None,
        help="Force config format",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        default=False,
        help="Continue applying remaining patches even if one fails",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing to disk",
    )
    parser.set_defaults(func=cmd_chain)
