"""CLI commands for template variable handling."""

import argparse
import json
import sys

from confpatch.template import extract_variables, render_patch, TemplateError
from confpatch.patch import load_patch


def cmd_render(args: argparse.Namespace) -> int:
    """Render a patch file with provided variables and print the result."""
    try:
        patch = load_patch(args.patch)
    except Exception as exc:
        print(f"Error loading patch: {exc}", file=sys.stderr)
        return 1

    variables: dict = {}
    for item in args.var or []:
        if "=" not in item:
            print(f"Invalid variable format (expected key=value): {item}", file=sys.stderr)
            return 1
        k, v = item.split("=", 1)
        variables[k.strip()] = v.strip()

    try:
        rendered = render_patch(patch, variables)
    except TemplateError as exc:
        print(f"Template error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(rendered, indent=2))
    return 0


def cmd_list_vars(args: argparse.Namespace) -> int:
    """List all template variables used in a patch file."""
    try:
        patch = load_patch(args.patch)
    except Exception as exc:
        print(f"Error loading patch: {exc}", file=sys.stderr)
        return 1

    variables = extract_variables(patch)
    if not variables:
        print("No template variables found.")
    else:
        print(f"Template variables in '{args.patch}':")
        for var in variables:
            print(f"  - {var}")
    return 0


def register_template_commands(subparsers) -> None:
    """Register template-related CLI subcommands."""
    render_p = subparsers.add_parser("render", help="Render a patch template with variables")
    render_p.add_argument("patch", help="Path to the patch file")
    render_p.add_argument(
        "--var", action="append", metavar="KEY=VALUE",
        help="Template variable (can be repeated)"
    )
    render_p.set_defaults(func=cmd_render)

    list_p = subparsers.add_parser("list-vars", help="List template variables in a patch file")
    list_p.add_argument("patch", help="Path to the patch file")
    list_p.set_defaults(func=cmd_list_vars)
