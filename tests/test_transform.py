"""Tests for confpatch.transform."""

import pytest
from confpatch.transform import (
    apply_transform,
    apply_transforms_to_patch,
    list_transforms,
    TransformError,
)


def test_list_transforms_returns_list():
    result = list_transforms()
    assert isinstance(result, list)
    assert "int" in result
    assert "str" in result


def test_apply_transform_int():
    assert apply_transform("42", "int") == 42


def test_apply_transform_float():
    assert apply_transform("3.14", "float") == pytest.approx(3.14)


def test_apply_transform_str():
    assert apply_transform(99, "str") == "99"


def test_apply_transform_bool_true():
    assert apply_transform("true", "bool") is True
    assert apply_transform("yes", "bool") is True
    assert apply_transform("1", "bool") is True


def test_apply_transform_bool_false():
    assert apply_transform("false", "bool") is False


def test_apply_transform_upper():
    assert apply_transform("hello", "upper") == "HELLO"


def test_apply_transform_lower():
    assert apply_transform("WORLD", "lower") == "world"


def test_apply_transform_strip():
    assert apply_transform("  hi  ", "strip") == "hi"


def test_apply_transform_null():
    assert apply_transform("anything", "null") is None


def test_apply_transform_unknown_raises():
    with pytest.raises(TransformError, match="Unknown transform"):
        apply_transform("x", "nonexistent")


def test_apply_transform_invalid_conversion_raises():
    with pytest.raises(TransformError, match="failed"):
        apply_transform("not-a-number", "int")


def test_apply_transforms_to_patch_simple():
    patch = {"port": "8080", "debug": "true"}
    transforms = {"port": "int", "debug": "bool"}
    result = apply_transforms_to_patch(patch, transforms)
    assert result["port"] == 8080
    assert result["debug"] is True


def test_apply_transforms_to_patch_nested():
    patch = {"server": {"port": "9000"}}
    transforms = {"server.port": "int"}
    result = apply_transforms_to_patch(patch, transforms)
    assert result["server"]["port"] == 9000


def test_apply_transforms_missing_key_is_noop():
    patch = {"a": "1"}
    transforms = {"b": "int"}
    result = apply_transforms_to_patch(patch, transforms)
    assert result == {"a": "1"}


def test_apply_transforms_does_not_mutate_original():
    patch = {"x": "hello"}
    transforms = {"x": "upper"}
    apply_transforms_to_patch(patch, transforms)
    assert patch["x"] == "hello"


def test_apply_transforms_non_dict_raises():
    with pytest.raises(TransformError, match="patch must be a dict"):
        apply_transforms_to_patch(["not", "a", "dict"], {})
