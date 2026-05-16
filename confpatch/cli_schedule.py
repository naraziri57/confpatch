"""CLI commands for scheduled patch execution."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from confpatch.loaders import load_config, save_config
from confpatch.patch import apply_patch, load_patch
from confpatch.schedule import ScheduleError, run_after, run_at


def _default_apply(config_file: str, patch_file: str) -> None:
    fmt = Path(config_file).suffix.lstrip(".")
    config = load_config(config_file, fmt=fmt)
    patch = load_patch(patch_file)
    updated = apply_patch(config, patch)
    save_config(updated, config_file, fmt=fmt)


def cmd_schedule(args: argparse.Namespace) -> int:
    config_file = args.config
    patch_file = args.patch

    if not Path(config_file).exists():
        print(f"error: config file not found: {config_file}")
        return 1
    if not Path(patch_file).exists():
        print(f"error: patch file not found: {patch_file}")
        return 1

    try:
        if args.after is not None:
            print(f"Waiting {args.after}s before applying patch...")
            result = run_after(args.after, config_file, patch_file, _default_apply)
        elif args.at is not None:
            target = datetime.fromisoformat(args.at)
            print(f"Waiting until {target} before applying patch...")
            result = run_at(target, config_file, patch_file, _default_apply)
        else:
            print("error: provide --after or --at")
            return 1
    except ScheduleError as exc:
        print(f"error: {exc}")
        return 1

    print(result.summary())
    return 0 if result.success else 1


def register_schedule_commands(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    p = subparsers.add_parser("schedule", help="apply a patch at a scheduled time")
    p.add_argument("config", help="config file to patch")
    p.add_argument("patch", help="patch file to apply")
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--after",
        type=float,
        metavar="SECONDS",
        help="wait N seconds before applying",
    )
    group.add_argument(
        "--at",
        metavar="DATETIME",
        help="apply at ISO datetime (e.g. 2025-06-01T14:00:00)",
    )
    p.set_defaults(func=cmd_schedule)
