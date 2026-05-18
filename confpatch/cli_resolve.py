"""CLI commands for resolving file:// references in configs."""

from __future__ import annotations

import sys
from pathlib import Path

from confpatch.loaders import load_config, save_config
from confpatch.resolve import ResolveError, resolve_refs


def cmd_resolve(args) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        return 1

    base_dir = Path(args.base_dir) if args.base_dir else config_path.parent

    try:
        config = load_config(str(config_path))
        result = resolve_refs(config, base_dir=base_dir)
    except ResolveError as exc:
        print(f"Resolve error: {exc}", file=sys.stderr)
        return 1

    print(result.summary())

    if args.dry_run:
        print("Dry run — no changes written.")
        return 0

    if result.has_changes():
        save_config(result.resolved, str(config_path))
        print(f"Saved resolved config to {config_path}")
    else:
        print("Nothing to write.")

    return 0


def register_resolve_commands(subparsers) -> None:
    p = subparsers.add_parser(
        "resolve",
        help="Resolve file:// references in a config file.",
    )
    p.add_argument("config", help="Path to the config file.")
    p.add_argument(
        "--base-dir",
        dest="base_dir",
        default=None,
        help="Base directory for resolving relative file paths (default: config file dir).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing.",
    )
    p.set_defaults(func=cmd_resolve)
