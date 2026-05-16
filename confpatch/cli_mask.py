"""CLI commands for masking sensitive config values."""
from __future__ import annotations

import argparse
import json

from confpatch.loaders import load_config
from confpatch.mask import MaskError, mask_keys


def cmd_mask(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}")
        return 1

    keys = args.keys if args.keys else []
    if not keys:
        print("No keys specified. Use --keys to specify keys to mask.")
        return 1

    try:
        result = mask_keys(config, keys, reveal_chars=args.reveal)
    except MaskError as e:
        print(f"Mask error: {e}")
        return 1

    print(json.dumps(result.masked, indent=2, default=str))

    if args.summary:
        print()
        print(result.summary())

    return 0


def register_mask_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("mask", help="Display config with sensitive values masked")
    p.add_argument("config", help="Path to config file")
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Dot-notation keys to mask",
    )
    p.add_argument(
        "--reveal",
        type=int,
        default=0,
        metavar="N",
        help="Number of leading characters to reveal (default: 0)",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary of masked keys",
    )
    p.set_defaults(func=cmd_mask)
