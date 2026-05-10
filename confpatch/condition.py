"""Conditional patch application — apply patches only when config values match conditions."""

from __future__ import annotations

from typing import Any


class ConditionError(Exception):
    pass


OPERATORS = ("eq", "ne", "gt", "lt", "gte", "lte", "contains", "exists")


def _get_nested(config: dict, key: str) -> Any:
    """Resolve a dot-notation key from a nested dict."""
    parts = key.split(".")
    current = config
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(key)
        current = current[part]
    return current


def evaluate_condition(config: dict, condition: dict) -> bool:
    """Evaluate a single condition dict against a config.

    Condition format:
        {"key": "some.key", "op": "eq", "value": "expected"}
    """
    if not isinstance(condition, dict):
        raise ConditionError(f"Condition must be a dict, got {type(condition).__name__}")

    key = condition.get("key")
    op = condition.get("op", "eq")
    expected = condition.get("value")

    if not key:
        raise ConditionError("Condition must include a 'key' field")
    if op not in OPERATORS:
        raise ConditionError(f"Unknown operator '{op}'. Valid: {OPERATORS}")

    try:
        actual = _get_nested(config, key)
        exists = True
    except KeyError:
        actual = None
        exists = False

    if op == "exists":
        return exists
    if not exists:
        return False
    if op == "eq":
        return actual == expected
    if op == "ne":
        return actual != expected
    if op == "gt":
        return actual > expected
    if op == "lt":
        return actual < expected
    if op == "gte":
        return actual >= expected
    if op == "lte":
        return actual <= expected
    if op == "contains":
        return expected in actual
    return False


def evaluate_all(config: dict, conditions: list[dict]) -> bool:
    """Return True only if ALL conditions are satisfied."""
    return all(evaluate_condition(config, c) for c in conditions)


def conditional_patch(config: dict, patch: dict, conditions: list[dict]) -> tuple[bool, dict]:
    """Return (applied, patch) — patch is returned unchanged; applied indicates if conditions passed."""
    if evaluate_all(config, conditions):
        return True, patch
    return False, {}
