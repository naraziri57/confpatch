"""CLI commands for the extract feature."""

from __future__ import annotations

import argparse

from confpatch.extract import ExtractError, extract_from_file


def cmd_extract(args: argparse.Namespace) -> None:
    if not args.keys:
        print("Error: at least one key must be specified via --key")
        return

    try:
        result = extract_from_file(
            source=args.config,
            keys=args.keys,
            dest=args.output,
            fmt=args.format,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return
    except ExtractError as exc:
        print(f"Extract error: {exc}")
        return

    print(result.summary())
    if args.dry_run:
        print("Dry run — no file written.")
        for k, v in result.extracted.items():
            print(f"  {k}: {v!r}")
    elif args.output:
        print(f"Saved to {args.output}")


def register_extract_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("extract", help="Extract keys from a config file")
    p.add_argument("config", help="Source config file")
    p.add_argument("--key", dest="keys", action="append", default=[], metavar="KEY",
                   help="Key to extract (dot-notation, repeatable)")
    p.add_argument("--output", "-o", default=None, help="Destination file")
    p.add_argument("--format", default=None, help="File format (yaml/toml)")
    p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    p.set_defaults(func=cmd_extract)
