"""Tests for confpatch.coerce."""
import pytest
from confpatch.coerce import (
    CoerceError,
    CoerceResult,
    _coerce_value,
    coerce_keys,
)


def test_coerce_value_to_int():
    assert _coerce_value("42", "int") == 42


def test_coerce_value_to_float():
    assert _coerce_value("3.14", "float") == pytest.approx(3.14)


def test_coerce_value_to_str():
    assert _coerce_value(99, "str") == "99"


def test_coerce_value_to_bool_true():
    assert _coerce_value("yes", "bool") is True
    assert _coerce_value("true", "bool") is True
    assert _coerce_value("1", "bool") is True


def test_coerce_value_to_bool_false():
    assert _coerce_value("no", "bool") is False
    assert _coerce_value("false", "bool") is False


def test_coerce_value_to_bool_invalid_raises():
    with pytest.raises(CoerceError):
        _coerce_value("maybe", "bool")


def test_coerce_value_to_list_from_string():
    assert _coerce_value("a, b, c", "list") == ["a", "b", "c"]


def test_coerce_value_to_list_already_list():
    assert _coerce_value([1, 2], "list") == [1, 2]


def test_coerce_value_to_null():
    assert _coerce_value("anything", "null") is None


def test_coerce_value_unknown_type_raises():
    with pytest.raises(CoerceError, match="Unknown target type"):
        _coerce_value("x", "bytes")


def test_coerce_value_int_invalid_raises():
    with pytest.raises(CoerceError):
        _coerce_value("not_a_number", "int")


def test_coerce_keys_simple():
    config = {"port": "8080", "debug": "true"}
    result = coerce_keys(config, {"port": "int", "debug": "bool"})
    assert result.coerced["port"] == 8080
    assert result.coerced["debug"] is True


def test_coerce_keys_nested():
    config = {"server": {"port": "9000"}}
    result = coerce_keys(config, {"server.port": "int"})
    assert result.coerced["server"]["port"] == 9000


def test_coerce_keys_does_not_mutate_original():
    config = {"port": "8080"}
    coerce_keys(config, {"port": "int"})
    assert config["port"] == "8080"


def test_coerce_keys_missing_path_raises():
    config = {"host": "localhost"}
    with pytest.raises(CoerceError, match="not found"):
        coerce_keys(config, {"server.port": "int"})


def test_coerce_result_has_changes():
    config = {"x": "1"}
    result = coerce_keys(config, {"x": "int"})
    assert result.has_changes()
    assert result.count() == 1


def test_coerce_result_no_changes_when_already_correct_type():
    config = {"x": 1}
    result = coerce_keys(config, {"x": "int"})
    assert not result.has_changes()


def test_coerce_result_summary_with_changes():
    config = {"port": "3000"}
    result = coerce_keys(config, {"port": "int"})
    summary = result.summary()
    assert "port" in summary
    assert "3000" in summary


def test_coerce_result_summary_no_changes():
    config = {"port": 3000}
    result = coerce_keys(config, {"port": "int"})
    assert "No values coerced" in result.summary()
