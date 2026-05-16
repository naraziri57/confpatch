"""Tests for confpatch.normalize."""

import pytest

from confpatch.normalize import (
    NormalizeError,
    _to_snake,
    _to_kebab,
    normalize_keys,
    normalize_patch,
)


def test_to_snake_camel():
    assert _to_snake("camelCase") == "camel_case"


def test_to_snake_pascal():
    assert _to_snake("PascalCase") == "pascal_case"


def test_to_snake_already_snake():
    assert _to_snake("already_snake") == "already_snake"


def test_to_kebab_snake_input():
    assert _to_kebab("my_key") == "my-key"


def test_to_kebab_camel_input():
    assert _to_kebab("myKey") == "my-key"


def test_normalize_keys_snake():
    data = {"myKey": 1, "anotherKey": 2}
    result = normalize_keys(data, style="snake")
    assert result == {"my_key": 1, "another_key": 2}


def test_normalize_keys_kebab():
    data = {"myKey": "val"}
    result = normalize_keys(data, style="kebab")
    assert result == {"my-key": "val"}


def test_normalize_keys_lower():
    data = {"MyKey": True, "UPPER": False}
    result = normalize_keys(data, style="lower")
    assert result == {"mykey": True, "upper": False}


def test_normalize_keys_upper():
    data = {"mykey": 42}
    result = normalize_keys(data, style="upper")
    assert result == {"MYKEY": 42}


def test_normalize_keys_nested():
    data = {"outerKey": {"innerKey": "value"}}
    result = normalize_keys(data, style="snake")
    assert result == {"outer_key": {"inner_key": "value"}}


def test_normalize_keys_not_dict_raises():
    with pytest.raises(NormalizeError, match="Expected dict"):
        normalize_keys(["a", "b"], style="snake")  # type: ignore


def test_normalize_keys_unknown_style_raises():
    with pytest.raises(NormalizeError, match="Unknown normalization style"):
        normalize_keys({"key": 1}, style="title")


def test_normalize_keys_does_not_mutate_original():
    original = {"myKey": 1}
    normalize_keys(original, style="snake")
    assert "myKey" in original


def test_normalize_patch_returns_normalized_copy():
    patch = {"dbHost": "localhost", "dbPort": 5432}
    result = normalize_patch(patch, style="snake")
    assert result == {"db_host": "localhost", "db_port": 5432}
    assert "dbHost" in patch  # original unchanged
