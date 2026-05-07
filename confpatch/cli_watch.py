"""CLI commands for the watch feature."""

import argparse
from pathlib import Path

from confpatch.watch import watch_file, make_patch_callback, WatchError


def cmd_watch(args: argparse.Namespace) -> int:
    """
    Watch a config file and re-apply a patch whenever it changes.

    Returns exit code (0 = ok, 1 = error).
    """
    config_path = Path(args.config)
    patch_path = Path(args.patch)

    if not config_path.exists():
        print(f"error: config file not found: {config_path}")
        return 1

    if not patch_path.exists():
        print(f"error: patch file not found: {patch_path}")
        return 1

    interval = getattr(args, "interval", 1.0)

    def on_apply(path, result):
        print(f"patch applied to {path} ({len(result)} top-level keys)")

    callback = make_patch_callback(patch_path, on_apply=on_apply)

    print(f"watching {config_path} (patch: {patch_path}, interval: {interval}s) — Ctrl+C to stop")

    try:
        watch_file(config_path, callback, interval=interval)
    except WatchError as exc:
        print(f"error: {exc}")
        return 1

    return 0


def register_watch_commands(subparsers) -> None:
    """Register the 'watch' subcommand on an existing subparsers object."""
    parser = subparsers.add_parser(
        "watch",
        help="watch a config file and re-apply a patch on every change",
    )
    parser.add_argument("config", help="path to the config file to watch")
    parser.add_argument("patch", help="path to the patch file to apply")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="polling interval in seconds (default: 1.0)",
    )
    parser.set_defaults(func=cmd_watch)
