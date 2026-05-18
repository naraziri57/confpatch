"""CLI commands for placeholder resolution."""

from __future__ import annotations

import sys

from confpatch.loaders import load_config, save_config
from confpatch.placeholder import PlaceholderError, resolve_placeholders


def cmd_placeholder(args) -> None:
    """Resolve <token> placeholders in a config file."""
    from pathlib import Path

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    if not args.set:
        print("Error: at least one --set TOKEN=VALUE is required.", file=sys.stderr)
        sys.exit(1)

    mapping: dict[str, str] = {}
    for item in args.set:
        if "=" not in item:
            print(f"Error: invalid --set format (expected TOKEN=VALUE): {item}", file=sys.stderr)
            sys.exit(1)
        token, _, value = item.partition("=")
        mapping[token.strip()] = value

    config = load_config(str(config_path))

    try:
        result = resolve_placeholders(
            config,
            mapping=mapping,
            keys=args.keys or None,
            strict=not args.no_strict,
        )
    except PlaceholderError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if args.dry_run:
        print("Dry run — no changes written.")
        return

    save_config(str(config_path), result.resolved)


def register_placeholder_commands(subparsers) -> None:
    p = subparsers.add_parser(
        "placeholder",
        help="Resolve <token> placeholders in config values.",
    )
    p.add_argument("config", help="Path to the config file.")
    p.add_argument(
        "--set",
        metavar="TOKEN=VALUE",
        action="append",
        default=[],
        help="Provide a token replacement (repeatable).",
    )
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Limit replacement to these top-level keys.",
    )
    p.add_argument(
        "--no-strict",
        action="store_true",
        help="Leave unresolved placeholders in place instead of raising.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing.",
    )
    p.set_defaults(func=cmd_placeholder)
