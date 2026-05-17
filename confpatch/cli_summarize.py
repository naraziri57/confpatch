"""CLI command for summarizing a config file."""
from __future__ import annotations

import argparse

from confpatch.loaders import load_config
from confpatch.summarize import SummarizeError, summarize_config


def cmd_summarize(args: argparse.Namespace) -> int:
    """Print a summary of a config file."""
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading config: {exc}")
        return 1

    try:
        result = summarize_config(config)
    except SummarizeError as exc:
        print(f"Error: {exc}")
        return 1

    if args.verbose:
        print(f"File       : {args.config}")
        print(f"Top-level  : {', '.join(result.top_level_keys) or '(none)'}")
        print(f"Total keys : {result.total_keys}")
        print(f"Max depth  : {result.max_depth}")
        print("Value types:")
        for t, n in sorted(result.type_counts.items()):
            print(f"  {t}: {n}")
    else:
        print(result.summary())

    return 0


def register_summarize_commands(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    p = subparsers.add_parser("summarize", help="Summarize a config file")
    p.add_argument("config", help="Path to the config file")
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Show detailed breakdown",
    )
    p.set_defaults(func=cmd_summarize)
