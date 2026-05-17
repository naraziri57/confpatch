"""CLI commands for type checking config values."""
from __future__ import annotations

import argparse
import json
import sys

from confpatch.loaders import load_config
from confpatch.typecheck import TypeCheckError, check_types


def cmd_typecheck(args: argparse.Namespace) -> None:
    config_path = args.config
    schema_path = args.schema

    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print(f"Error: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"Error: schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in schema file: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(schema, dict):
        print("Error: schema must be a JSON object mapping keys to type names.", file=sys.stderr)
        sys.exit(1)

    try:
        result = check_types(config, schema)
    except TypeCheckError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if result.has_violations():
        sys.exit(2)


def register_typecheck_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    p = subparsers.add_parser(
        "typecheck",
        help="Check config value types against a JSON schema.",
    )
    p.add_argument("config", help="Path to the config file (YAML or TOML).")
    p.add_argument(
        "schema",
        help="Path to a JSON file mapping dot-notation keys to expected types.",
    )
    p.set_defaults(func=cmd_typecheck)
