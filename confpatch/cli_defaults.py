"""CLI commands for applying defaults to config files."""

from __future__ import annotations

import argparse
import sys

from confpatch.defaults import DefaultsError, apply_defaults
from confpatch.loaders import load_config, save_config


def cmd_defaults(args: argparse.Namespace) -> int:
    """Apply default values to missing/null keys in a config file."""
    config_path = args.config

    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print(f"error: config file not found: {config_path}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: could not load config: {exc}", file=sys.stderr)
        return 1

    if not args.set:
        print("error: no defaults provided (use --set key=value)", file=sys.stderr)
        return 1

    defaults: dict = {}
    for item in args.set:
        if "=" not in item:
            print(f"error: invalid format {item!r}, expected key=value", file=sys.stderr)
            return 1
        key, _, raw_value = item.partition("=")
        # Attempt numeric coercion
        value: object = raw_value
        try:
            value = int(raw_value)
        except ValueError:
            try:
                value = float(raw_value)
            except ValueError:
                if raw_value.lower() in ("true", "false"):
                    value = raw_value.lower() == "true"
        defaults[key.strip()] = value

    try:
        new_config, result = apply_defaults(
            config, defaults, overwrite_null=not args.no_overwrite_null
        )
    except DefaultsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary())

    if args.dry_run:
        print("(dry run — no changes written)")
        return 0

    if result.has_changes():
        save_config(new_config, config_path)

    return 0


def register_defaults_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    p = subparsers.add_parser(
        "defaults",
        help="Apply default values to missing or null config keys",
    )
    p.add_argument("config", help="Path to config file")
    p.add_argument(
        "--set",
        metavar="KEY=VALUE",
        action="append",
        help="Default key=value pair (repeatable)",
    )
    p.add_argument(
        "--no-overwrite-null",
        action="store_true",
        default=False,
        help="Skip keys that exist but are null",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would change without writing",
    )
    p.set_defaults(func=cmd_defaults)
