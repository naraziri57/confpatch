"""Tests for confpatch.cast module."""

import pytest

from confpatch.cast import CastError, CastResult, cast_key, _cast_value


def test_cast_value_to_int():
    assert _cast_value("42", "int") == 42
    assert isinstance(_cast_value("42", "int"), int)


def test_cast_value_to_float():
    assert _cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_value_to_str():
    assert _cast_value(100, "str") == "100"


def test_cast_value_to_bool_true():
    for v in ("true", "True", "1", "yes"):
        assert _cast_value(v, "bool") is True


def test_cast_value_to_bool_false():
    for v in ("false", "False", "0", "no"):
        assert _cast_value(v, "bool") is False


def test_cast_value_bool_already_bool():
    assert _cast_value(True, "bool") is True
    assert _cast_value(False, "bool") is False


def test_cast_value_invalid_bool_string():
    with pytest.raises(CastError, match="Cannot cast"):
        _cast_value("maybe", "bool")


def test_cast_value_invalid_int():
    with pytest.raises(CastError):
        _cast_value("not-a-number", "int")


def test_cast_value_unknown_type():
    with pytest.raises(CastError, match="Unknown type"):
        _cast_value("x", "bytes")


def test_cast_key_top_level():
    config = {"port": "8080", "debug": "true"}
    result = cast_key(config, "port", "int")
    assert result.config["port"] == 8080
    assert isinstance(result.config["port"], int)


def test_cast_key_does_not_mutate_original():
    config = {"port": "8080"}
    cast_key(config, "port", "int")
    assert config["port"] == "8080"


def test_cast_key_nested():
    config = {"server": {"port": "9000"}}
    result = cast_key(config, "server.port", "int")
    assert result.config["server"]["port"] == 9000


def test_cast_key_missing_path_raises():
    config = {"a": {"b": 1}}
    with pytest.raises(CastError, match="not found"):
        cast_key(config, "a.c", "str")


def test_cast_key_non_dict_intermediate_raises():
    config = {"a": 42}
    with pytest.raises(CastError):
        cast_key(config, "a.b", "str")


def test_cast_key_returns_cast_result():
    config = {"x": "1"}
    result = cast_key(config, "x", "int")
    assert isinstance(result, CastResult)


def test_cast_result_has_changes_true():
    config = {"x": "1"}
    result = cast_key(config, "x", "int")
    assert result.has_changes()
    assert result.count() == 1


def test_cast_result_summary_contains_path():
    config = {"x": "1"}
    result = cast_key(config, "x", "int")
    summary = result.summary()
    assert "x" in summary
    assert "int" in summary


def test_cast_result_no_change_when_same_type():
    config = {"x": 1}
    result = cast_key(config, "x", "int")
    assert not result.has_changes()


def test_cast_key_unknown_type_raises():
    config = {"x": "1"}
    with pytest.raises(CastError, match="Unknown type"):
        cast_key(config, "x", "list")
