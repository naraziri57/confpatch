"""CLI commands for conditional patch application."""

from __future__ import annotations

import json
import sys

from confpatch.condition import ConditionError, conditional_patch
from confpatch.loaders import load_config, save_config
from confpatch.patch import load_patch, apply_patch


def cmd_apply_if(args) -> int:
    """Apply a patch only if all conditions are met."""
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        return 1

    try:
        patch = load_patch(args.patch)
    except FileNotFoundError:
        print(f"Error: patch file not found: {args.patch}", file=sys.stderr)
        return 1

    try:
        conditions = json.loads(args.conditions)
        if not isinstance(conditions, list):
            conditions = [conditions]
    except json.JSONDecodeError as exc:
        print(f"Error: invalid conditions JSON: {exc}", file=sys.stderr)
        return 1

    try:
        applied, effective_patch = conditional_patch(config, patch, conditions)
    except ConditionError as exc:
        print(f"Condition error: {exc}", file=sys.stderr)
        return 1

    if not applied:
        print("Conditions not met — patch was NOT applied.")
        return 0

    updated = apply_patch(config, effective_patch)

    if args.dry_run:
        print("Conditions met — patch would be applied (dry run).")
        return 0

    save_config(args.config, updated)
    print(f"Conditions met — patch applied to {args.config}.")
    return 0


def register_condition_commands(subparsers) -> None:
    p = subparsers.add_parser(
        "apply-if",
        help="Apply a patch only when config values satisfy given conditions",
    )
    p.add_argument("config", help="Path to the config file")
    p.add_argument("patch", help="Path to the patch file")
    p.add_argument(
        "--conditions",
        required=True,
        metavar="JSON",
        help='JSON array of condition objects, e.g. [{"key":"env","op":"eq","value":"prod"}]',
    )
    p.add_argument("--dry-run", action="store_true", help="Check conditions without writing")
    p.set_defaults(func=cmd_apply_if)
