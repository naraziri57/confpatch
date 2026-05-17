"""Tests for confpatch.typecheck."""
from __future__ import annotations

import pytest

from confpatch.typecheck import (
    TypeCheckError,
    TypeCheckResult,
    _get_nested,
    check_types,
)


# ---------------------------------------------------------------------------
# _get_nested
# ---------------------------------------------------------------------------

def test_get_nested_top_level():
    assert _get_nested({"a": 1}, "a") == 1


def test_get_nested_dot_notation():
    assert _get_nested({"a": {"b": 42}}, "a.b") == 42


def test_get_nested_missing_raises():
    with pytest.raises(TypeCheckError):
        _get_nested({"a": 1}, "b")


def test_get_nested_missing_nested_raises():
    with pytest.raises(TypeCheckError):
        _get_nested({"a": {"b": 1}}, "a.c")


# ---------------------------------------------------------------------------
# check_types
# ---------------------------------------------------------------------------

def test_check_types_all_valid():
    config = {"name": "alice", "age": 30, "score": 9.5, "active": True}
    schema = {"name": "str", "age": "int", "score": "float", "active": "bool"}
    result = check_types(config, schema)
    assert not result.has_violations()
    assert result.count() == 0


def test_check_types_type_mismatch():
    config = {"age": "thirty"}
    schema = {"age": "int"}
    result = check_types(config, schema)
    assert result.has_violations()
    assert result.count() == 1
    assert result.violations[0]["key"] == "age"
    assert result.violations[0]["expected"] == "int"
    assert result.violations[0]["actual"] == "str"


def test_check_types_missing_key_is_violation():
    config = {"name": "bob"}
    schema = {"name": "str", "age": "int"}
    result = check_types(config, schema)
    assert result.has_violations()
    assert result.violations[0]["actual"] == "missing"


def test_check_types_dot_notation_valid():
    config = {"db": {"port": 5432}}
    schema = {"db.port": "int"}
    result = check_types(config, schema)
    assert not result.has_violations()


def test_check_types_dot_notation_mismatch():
    config = {"db": {"port": "5432"}}
    schema = {"db.port": "int"}
    result = check_types(config, schema)
    assert result.has_violations()
    assert result.violations[0]["key"] == "db.port"


def test_check_types_list_type():
    config = {"tags": ["a", "b"]}
    schema = {"tags": "list"}
    result = check_types(config, schema)
    assert not result.has_violations()


def test_check_types_dict_type():
    config = {"meta": {"key": "val"}}
    schema = {"meta": "dict"}
    result = check_types(config, schema)
    assert not result.has_violations()


def test_check_types_unknown_type_raises():
    with pytest.raises(TypeCheckError, match="Unknown type"):
        check_types({"a": 1}, {"a": "bytes"})


def test_check_types_non_dict_config_raises():
    with pytest.raises(TypeCheckError):
        check_types("not a dict", {"a": "str"})


def test_check_types_non_dict_schema_raises():
    with pytest.raises(TypeCheckError):
        check_types({"a": 1}, ["a", "str"])


def test_summary_no_violations():
    result = TypeCheckResult()
    assert "No type violations" in result.summary()


def test_summary_with_violations():
    result = TypeCheckResult(
        violations=[{"key": "age", "expected": "int", "actual": "str", "value": "old"}]
    )
    s = result.summary()
    assert "age" in s
    assert "int" in s
    assert "str" in s
