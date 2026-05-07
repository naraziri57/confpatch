"""Tests for confpatch.schema."""

from __future__ import annotations

import pytest

from confpatch.schema import SchemaError, _check_type, load_schema, validate_against_schema


# ---------------------------------------------------------------------------
# _check_type
# ---------------------------------------------------------------------------

def test_check_type_valid():
    _check_type("hello", "str", "key")
    _check_type(42, "int", "key")
    _check_type(3.14, "float", "key")
    _check_type(True, "bool", "key")
    _check_type([], "list", "key")
    _check_type({}, "dict", "key")


def test_check_type_mismatch():
    with pytest.raises(SchemaError, match="expected str"):
        _check_type(123, "str", "name")


def test_check_type_unknown():
    with pytest.raises(SchemaError, match="Unknown type"):
        _check_type("x", "bytes", "key")


# ---------------------------------------------------------------------------
# validate_against_schema
# ---------------------------------------------------------------------------

def test_validate_simple_valid():
    schema = {"name": "str", "port": "int"}
    config = {"name": "app", "port": 8080}
    validate_against_schema(config, schema)  # should not raise


def test_validate_missing_key():
    schema = {"name": "str", "port": "int"}
    config = {"name": "app"}
    with pytest.raises(SchemaError, match="Missing required key 'port'"):
        validate_against_schema(config, schema)


def test_validate_wrong_type():
    schema = {"port": "int"}
    config = {"port": "not-an-int"}
    with pytest.raises(SchemaError, match="expected int"):
        validate_against_schema(config, schema)


def test_validate_nested_valid():
    schema = {"db": {"host": "str", "port": "int"}}
    config = {"db": {"host": "localhost", "port": 5432}}
    validate_against_schema(config, schema)


def test_validate_nested_missing():
    schema = {"db": {"host": "str", "port": "int"}}
    config = {"db": {"host": "localhost"}}
    with pytest.raises(SchemaError, match="db.port"):
        validate_against_schema(config, schema)


def test_validate_schema_not_dict():
    with pytest.raises(SchemaError, match="Schema must be a dict"):
        validate_against_schema({}, "bad")


def test_validate_config_not_dict():
    with pytest.raises(SchemaError, match="Expected a dict"):
        validate_against_schema("oops", {"key": "str"})


def test_validate_invalid_rule():
    with pytest.raises(SchemaError, match="Invalid schema rule"):
        validate_against_schema({"key": 42}, {"key": 123})


# ---------------------------------------------------------------------------
# load_schema
# ---------------------------------------------------------------------------

def test_load_schema_valid(tmp_path):
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text("name: str\nport: int\n")
    schema = load_schema(str(schema_file))
    assert schema == {"name": "str", "port": "int"}


def test_load_schema_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_schema(str(tmp_path / "missing.yaml"))


def test_load_schema_non_mapping(tmp_path):
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text("- item1\n- item2\n")
    with pytest.raises(SchemaError, match="must contain a YAML mapping"):
        load_schema(str(schema_file))
