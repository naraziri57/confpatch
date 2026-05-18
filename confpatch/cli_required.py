"""CLI commands for enforcing required config keys."""

from __future__ import annotations

import argparse
import sys

from confpatch.loaders import load_config
from confpatch.required import RequiredError, check_required


def cmd_required(args: argparse.Namespace) -> None:
    """Check that required keys are present in a config file."""
    if not args.keys:
        print("No keys specified.", file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    try:
        result = check_required(config, args.keys)
    except RequiredError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if result.has_missing():
        for key in result.missing:
            print(f"  MISSING: {key}")
        sys.exit(2)


def register_required_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    p = subparsers.add_parser(
        "required",
        help="Check that required keys exist in a config file.",
    )
    p.add_argument("config", help="Path to config file.")
    p.add_argument(
        "keys",
        nargs="+",
        help="Dot-notation key paths that must be present.",
    )
    p.set_defaults(func=cmd_required)
