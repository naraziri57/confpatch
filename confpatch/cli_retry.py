"""CLI subcommands for apply-with-retry."""

from __future__ import annotations

import argparse
import sys

from confpatch.loaders import load_config, save_config
from confpatch.patch import load_patch, apply_patch
from confpatch.retry import retry, RetryError


def cmd_apply_retry(args: argparse.Namespace) -> int:
    """Apply a patch file to a config file with automatic retries."""
    config_path = args.config
    patch_path = args.patch
    attempts = args.attempts
    delay = args.delay
    backoff = args.backoff
    fmt = getattr(args, "format", None)

    if not __import__("pathlib").Path(config_path).exists():
        print(f"error: config file not found: {config_path}", file=sys.stderr)
        return 1

    if not __import__("pathlib").Path(patch_path).exists():
        print(f"error: patch file not found: {patch_path}", file=sys.stderr)
        return 1

    def do_apply() -> None:
        config = load_config(config_path, fmt=fmt)
        patch = load_patch(patch_path)
        patched = apply_patch(config, patch)
        save_config(patched, config_path, fmt=fmt)

    try:
        result = retry(
            do_apply,
            attempts=attempts,
            delay=delay,
            backoff=backoff,
        )
        if args.verbose:
            print(result.summary())
        return 0
    except RetryError as exc:
        print(
            f"error: patch failed after {exc.attempts} attempt(s): {exc.last_error}",
            file=sys.stderr,
        )
        return 1


def register_retry_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "apply-retry",
        help="Apply a patch with automatic retry on failure",
    )
    parser.add_argument("config", help="Path to the config file")
    parser.add_argument("patch", help="Path to the patch file")
    parser.add_argument(
        "--attempts", type=int, default=3, metavar="N",
        help="Maximum number of attempts (default: 3)",
    )
    parser.add_argument(
        "--delay", type=float, default=0.5, metavar="SEC",
        help="Initial delay between retries in seconds (default: 0.5)",
    )
    parser.add_argument(
        "--backoff", type=float, default=2.0, metavar="MULT",
        help="Backoff multiplier applied to delay (default: 2.0)",
    )
    parser.add_argument(
        "--format", dest="format", default=None,
        choices=["yaml", "toml"],
        help="Force config format (auto-detected by default)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print retry summary on success",
    )
    parser.set_defaults(func=cmd_apply_retry)
