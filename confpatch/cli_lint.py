"""CLI commands for the lint feature."""

from __future__ import annotations

import argparse
import sys

from confpatch.lint import lint_patch
from confpatch.patch import load_patch


def cmd_lint(args: argparse.Namespace) -> int:
    """Lint a patch file and report issues."""
    try:
        patch = load_patch(args.patch)
    except Exception as exc:
        print(f"Error loading patch: {exc}", file=sys.stderr)
        return 1

    result = lint_patch(patch)
    print(result.summary())

    if not result.ok:
        return 2

    if result.warnings and args.strict:
        print("Strict mode: warnings treated as errors.", file=sys.stderr)
        return 2

    return 0


def register_lint_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "lint",
        help="Check a patch file for common issues",
    )
    parser.add_argument("patch", help="Path to the patch file (YAML/TOML)")
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Treat warnings as errors",
    )
    parser.set_defaults(func=cmd_lint)
