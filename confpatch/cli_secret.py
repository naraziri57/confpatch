"""CLI commands for secret redaction preview."""

from __future__ import annotations

import argparse
import sys

from confpatch.loaders import load_config
from confpatch.secret import SecretError, redact_patch


def cmd_redact(args: argparse.Namespace) -> int:
    """Preview a patch file with sensitive values masked."""
    try:
        patch = load_config(args.patch_file)
    except FileNotFoundError:
        print(f"Error: patch file not found: {args.patch_file}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error loading patch: {exc}", file=sys.stderr)
        return 1

    try:
        redacted, result = redact_patch(patch)
    except SecretError as exc:
        print(f"Redaction error: {exc}", file=sys.stderr)
        return 1

    print("Redacted patch preview:")
    for key, value in redacted.items():
        print(f"  {key}: {value}")

    print()
    print(result.summary())
    return 0


def cmd_list_sensitive(args: argparse.Namespace) -> int:
    """List keys in a patch that would be redacted."""
    try:
        patch = load_config(args.patch_file)
    except FileNotFoundError:
        print(f"Error: patch file not found: {args.patch_file}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error loading patch: {exc}", file=sys.stderr)
        return 1

    _, result = redact_patch(patch)
    if result.redacted_keys:
        print("Sensitive keys detected:")
        for k in result.redacted_keys:
            print(f"  - {k}")
    else:
        print("No sensitive keys detected.")
    return 0


def register_secret_commands(subparsers) -> None:
    redact_parser = subparsers.add_parser("redact", help="Preview patch with secrets masked")
    redact_parser.add_argument("patch_file", help="Patch file to preview")
    redact_parser.set_defaults(func=cmd_redact)

    list_parser = subparsers.add_parser("list-sensitive", help="List sensitive keys in a patch")
    list_parser.add_argument("patch_file", help="Patch file to inspect")
    list_parser.set_defaults(func=cmd_list_sensitive)
