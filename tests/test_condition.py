"""Tests for confpatch.condition."""

import pytest

from confpatch.condition import (
    ConditionError,
    evaluate_condition,
    evaluate_all,
    conditional_patch,
)


CONFIG = {
    "env": "production",
    "version": 3,
    "database": {
        "host": "db.example.com",
        "port": 5432,
    },
    "tags": ["web", "api"],
}


def test_evaluate_eq_true():
    assert evaluate_condition(CONFIG, {"key": "env", "op": "eq", "value": "production"}) is True


def test_evaluate_eq_false():
    assert evaluate_condition(CONFIG, {"key": "env", "op": "eq", "value": "staging"}) is False


def test_evaluate_ne():
    assert evaluate_condition(CONFIG, {"key": "env", "op": "ne", "value": "staging"}) is True


def test_evaluate_gt():
    assert evaluate_condition(CONFIG, {"key": "version", "op": "gt", "value": 2}) is True


def test_evaluate_lt():
    assert evaluate_condition(CONFIG, {"key": "version", "op": "lt", "value": 10}) is True


def test_evaluate_gte():
    assert evaluate_condition(CONFIG, {"key": "version", "op": "gte", "value": 3}) is True


def test_evaluate_lte():
    assert evaluate_condition(CONFIG, {"key": "version", "op": "lte", "value": 3}) is True


def test_evaluate_contains():
    assert evaluate_condition(CONFIG, {"key": "tags", "op": "contains", "value": "api"}) is True


def test_evaluate_exists_true():
    assert evaluate_condition(CONFIG, {"key": "env", "op": "exists"}) is True


def test_evaluate_exists_false():
    assert evaluate_condition(CONFIG, {"key": "missing_key", "op": "exists"}) is False


def test_evaluate_nested_key():
    assert evaluate_condition(CONFIG, {"key": "database.port", "op": "eq", "value": 5432}) is True


def test_evaluate_missing_key_returns_false():
    assert evaluate_condition(CONFIG, {"key": "nope", "op": "eq", "value": "x"}) is False


def test_evaluate_unknown_operator_raises():
    with pytest.raises(ConditionError, match="Unknown operator"):
        evaluate_condition(CONFIG, {"key": "env", "op": "regex", "value": "prod"})


def test_evaluate_missing_key_field_raises():
    with pytest.raises(ConditionError, match="'key' field"):
        evaluate_condition(CONFIG, {"op": "eq", "value": "x"})


def test_evaluate_non_dict_raises():
    with pytest.raises(ConditionError):
        evaluate_condition(CONFIG, "env == production")


def test_evaluate_all_all_pass():
    conditions = [
        {"key": "env", "op": "eq", "value": "production"},
        {"key": "version", "op": "gte", "value": 1},
    ]
    assert evaluate_all(CONFIG, conditions) is True


def test_evaluate_all_one_fails():
    conditions = [
        {"key": "env", "op": "eq", "value": "production"},
        {"key": "version", "op": "gt", "value": 100},
    ]
    assert evaluate_all(CONFIG, conditions) is False


def test_conditional_patch_applied():
    patch = {"env": "staging"}
    conditions = [{"key": "env", "op": "eq", "value": "production"}]
    applied, result = conditional_patch(CONFIG, patch, conditions)
    assert applied is True
    assert result == patch


def test_conditional_patch_not_applied():
    patch = {"env": "staging"}
    conditions = [{"key": "env", "op": "eq", "value": "staging"}]
    applied, result = conditional_patch(CONFIG, patch, conditions)
    assert applied is False
    assert result == {}
