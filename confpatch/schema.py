"""Schema validation for config patches using simple type/shape definitions."""

from __future__ import annotations

from typing import Any


class SchemaError(Exception):
    """Raised when a config value does not match the expected schema."""


_TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}


def _check_type(value: Any, type_name: str, path: str) -> None:
    expected = _TYPE_MAP.get(type_name)
    if expected is None:
        raise SchemaError(f"Unknown type '{type_name}' in schema at '{path}'")
    if not isinstance(value, expected):
        raise SchemaError(
            f"Key '{path}': expected {type_name}, got {type(value).__name__}"
        )


def validate_against_schema(config: dict, schema: dict, _prefix: str = "") -> None:
    """Recursively validate *config* against *schema*.

    Schema format::

        {
            "key": "str",          # type check
            "nested": {
                "port": "int"
            }
        }
    """
    if not isinstance(schema, dict):
        raise SchemaError("Schema must be a dict")
    if not isinstance(config, dict):
        raise SchemaError(f"Expected a dict at '{_prefix or 'root'}'")

    for key, rule in schema.items():
        path = f"{_prefix}.{key}" if _prefix else key
        if key not in config:
            raise SchemaError(f"Missing required key '{path}'")
        value = config[key]
        if isinstance(rule, dict):
            validate_against_schema(value, rule, _prefix=path)
        elif isinstance(rule, str):
            _check_type(value, rule, path)
        else:
            raise SchemaError(f"Invalid schema rule for '{path}': {rule!r}")


def load_schema(path: str) -> dict:
    """Load a schema definition from a YAML file."""
    import yaml  # type: ignore

    with open(path, "r") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise SchemaError(f"Schema file '{path}' must contain a YAML mapping")
    return data
