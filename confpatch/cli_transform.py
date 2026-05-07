"""CLI commands for the transform feature."""

import json
import argparse
from confpatch.transform import apply_transform, list_transforms, TransformError


def cmd_transform(args: argparse.Namespace) -> int:
    """Apply a transform to a single value and print the result."""
    try:
        result = apply_transform(args.value, args.transform)
        print(result)
        return 0
    except TransformError as exc:
        print(f"error: {exc}")
        return 1


def cmd_list_transforms(args: argparse.Namespace) -> int:  # noqa: ARG001
    """List all available transform names."""
    for name in list_transforms():
        print(name)
    return 0


def register_transform_commands(subparsers) -> None:
    """Register transform sub-commands onto an existing subparsers object."""
    p_transform = subparsers.add_parser(
        "transform",
        help="apply a named transform to a value",
    )
    p_transform.add_argument("value", help="value to transform")
    p_transform.add_argument("transform", help="transform name (e.g. int, upper, bool)")
    p_transform.set_defaults(func=cmd_transform)

    p_list = subparsers.add_parser(
        "list-transforms",
        help="list available transform names",
    )
    p_list.set_defaults(func=cmd_list_transforms)
