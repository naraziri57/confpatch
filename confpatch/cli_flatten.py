"""CLI commands for flatten/unflatten operations."""

from __future__ import annotations
import json
from confpatch.flatten import flatten_config, unflatten_config, FlattenError
from confpatch.loaders import load_config, save_config


def cmd_flatten(args) -> int:
    """Flatten a config file and print dot-notation keys."""
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"[error] Config file not found: {args.config}")
        return 1

    try:
        result = flatten_config(config, sep=args.sep)
    except FlattenError as e:
        print(f"[error] {e}")
        return 1

    if args.json:
        print(json.dumps(result.flat, indent=2))
    else:
        for k, v in result.flat.items():
            print(f"{k} = {v!r}")

    if args.verbose:
        print(f"\n{result.summary()}")

    return 0


def cmd_unflatten(args) -> int:
    """Unflatten a JSON file of dot-notation keys back into a nested config."""
    try:
        with open(args.input) as f:
            flat = json.load(f)
    except FileNotFoundError:
        print(f"[error] Input file not found: {args.input}")
        return 1
    except json.JSONDecodeError as e:
        print(f"[error] Invalid JSON: {e}")
        return 1

    try:
        nested = unflatten_config(flat, sep=args.sep)
    except FlattenError as e:
        print(f"[error] {e}")
        return 1

    if args.dry_run:
        print(json.dumps(nested, indent=2))
    else:
        save_config(nested, args.output, fmt=args.format)
        print(f"[ok] Written to {args.output}")

    return 0


def register_flatten_commands(subparsers):
    p_flat = subparsers.add_parser("flatten", help="Flatten config to dot-notation")
    p_flat.add_argument("config", help="Config file to flatten")
    p_flat.add_argument("--sep", default=".", help="Key separator (default: '.')")
    p_flat.add_argument("--json", action="store_true", help="Output as JSON")
    p_flat.add_argument("--verbose", action="store_true")
    p_flat.set_defaults(func=cmd_flatten)

    p_unflat = subparsers.add_parser("unflatten", help="Unflatten dot-notation JSON to config")
    p_unflat.add_argument("input", help="JSON file with flat keys")
    p_unflat.add_argument("output", help="Output config file")
    p_unflat.add_argument("--sep", default=".", help="Key separator (default: '.')")
    p_unflat.add_argument("--format", default="yaml", choices=["yaml", "toml"])
    p_unflat.add_argument("--dry-run", action="store_true")
    p_unflat.set_defaults(func=cmd_unflatten)
