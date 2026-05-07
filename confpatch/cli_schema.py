"""CLI commands for schema validation."""

from __future__ import annotations

import argparse
import sys

from confpatch.loaders import load_config
from confpatch.schema import SchemaError, load_schema, validate_against_schema


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a config file against a schema."""
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    try:
        schema = load_schema(args.schema)
    except FileNotFoundError:
        print(f"Error: schema file not found: {args.schema}", file=sys.stderr)
        return 1
    except SchemaError as exc:
        print(f"Schema error: {exc}", file=sys.stderr)
        return 1

    try:
        validate_against_schema(config, schema)
    except SchemaError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 2

    print(f"Config '{args.config}' is valid against schema '{args.schema}'.")
    return 0


def register_schema_commands(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """Register schema sub-commands onto *subparsers*."""
    p = subparsers.add_parser(
        "validate-schema",
        help="Validate a config file against a schema definition",
    )
    p.add_argument("config", help="Path to the config file")
    p.add_argument("schema", help="Path to the schema YAML file")
    p.set_defaults(func=cmd_validate)
