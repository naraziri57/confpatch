"""CLI commands for pipeline execution."""
from __future__ import annotations

import json
import sys

from confpatch.pipeline import PipelineError, run_pipeline


def cmd_pipeline(args) -> int:
    """Run a pipeline defined in a JSON steps file against a config."""
    try:
        with open(args.steps_file) as fh:
            steps = json.load(fh)
    except FileNotFoundError:
        print(f"error: steps file not found: {args.steps_file}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in steps file: {exc}", file=sys.stderr)
        return 1

    if not isinstance(steps, list):
        print("error: steps file must contain a JSON array", file=sys.stderr)
        return 1

    try:
        result = run_pipeline(
            config_path=args.config,
            steps=steps,
            dry_run=getattr(args, "dry_run", False),
        )
    except PipelineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary())
    return 0 if result.success else 1


def register_pipeline_commands(subparsers) -> None:
    p = subparsers.add_parser("pipeline", help="run a multi-step pipeline on a config")
    p.add_argument("config", help="path to config file")
    p.add_argument("steps_file", help="JSON file defining pipeline steps")
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="simulate pipeline without writing changes",
    )
    p.set_defaults(func=cmd_pipeline)
