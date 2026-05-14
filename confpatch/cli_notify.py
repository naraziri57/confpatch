"""CLI integration for confpatch notify — log apply events to a file."""

from __future__ import annotations

import argparse
from pathlib import Path

from confpatch.loaders import load_config, save_config
from confpatch.patch import load_patch, apply_patch
from confpatch.diff import compute_diff
from confpatch.notify import NotifyEvent, dispatch


def cmd_apply_notify(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    patch_path = Path(args.patch)
    log_path = Path(args.log) if args.log else None

    if not config_path.exists():
        print(f"Error: config file not found: {config_path}")
        return 1
    if not patch_path.exists():
        print(f"Error: patch file not found: {patch_path}")
        return 1

    try:
        config = load_config(config_path)
        patch = load_patch(patch_path)
        updated = apply_patch(config, patch)
        diff = compute_diff(config, updated)
        changed_keys = [entry["key"] for entry in diff]

        if not args.dry_run:
            save_config(updated, config_path)

        event = NotifyEvent(
            config_file=str(config_path),
            patch_file=str(patch_path),
            changed_keys=changed_keys,
            success=True,
            message="dry-run" if args.dry_run else "",
        )
        dispatch(event, stdout=args.verbose, log_path=log_path)
        return 0

    except Exception as e:
        event = NotifyEvent(
            config_file=str(config_path),
            patch_file=str(patch_path),
            changed_keys=[],
            success=False,
            message=str(e),
        )
        dispatch(event, stdout=True, log_path=log_path)
        return 1


def register_notify_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("apply-notify", help="Apply patch and emit notifications")
    p.add_argument("config", help="Target config file")
    p.add_argument("patch", help="Patch file to apply")
    p.add_argument("--log", default=None, help="Path to notification log file")
    p.add_argument("--dry-run", action="store_true", help="Do not write changes")
    p.add_argument("--verbose", action="store_true", help="Print notification to stdout")
    p.set_defaults(func=cmd_apply_notify)
