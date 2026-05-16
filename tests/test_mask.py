"""Tests for confpatch.mask."""
import pytest

from confpatch.mask import MaskError, MaskResult, _mask_value, mask_keys, mask_patch


# --- _mask_value ---

def test_mask_value_no_reveal():
    assert _mask_value("secret") == "***"


def test_mask_value_reveal_chars():
    assert _mask_value("secret", reveal_chars=2) == "se***"


def test_mask_value_reveal_exceeds_length():
    assert _mask_value("hi", reveal_chars=10) == "***"


def test_mask_value_zero_reveal():
    assert _mask_value("password123", reveal_chars=0) == "***"


def test_mask_value_non_string():
    assert _mask_value(12345) == "***"


# --- mask_keys ---

def test_mask_keys_simple():
    config = {"password": "hunter2", "host": "localhost"}
    result = mask_keys(config, ["password"])
    assert result.masked["password"] == "***"
    assert result.masked["host"] == "localhost"
    assert result.keys_masked == ["password"]


def test_mask_keys_nested():
    config = {"db": {"password": "secret", "host": "localhost"}}
    result = mask_keys(config, ["db.password"])
    assert result.masked["db"]["password"] == "***"
    assert result.masked["db"]["host"] == "localhost"
    assert "db.password" in result.keys_masked


def test_mask_keys_no_matching_keys():
    config = {"host": "localhost", "port": 5432}
    result = mask_keys(config, ["password"])
    assert result.masked == config
    assert result.keys_masked == []


def test_mask_keys_reveal_chars():
    config = {"token": "abcdef123"}
    result = mask_keys(config, ["token"], reveal_chars=3)
    assert result.masked["token"] == "abc***"


def test_mask_keys_not_dict_raises():
    with pytest.raises(MaskError):
        mask_keys("not a dict", ["key"])


def test_mask_keys_multiple_keys():
    config = {"password": "p", "token": "t", "host": "h"}
    result = mask_keys(config, ["password", "token"])
    assert result.masked["password"] == "***"
    assert result.masked["token"] == "***"
    assert result.masked["host"] == "h"
    assert result.count == 2


# --- MaskResult ---

def test_mask_result_summary_no_keys():
    r = MaskResult(masked={}, keys_masked=[])
    assert "No keys" in r.summary()


def test_mask_result_summary_with_keys():
    r = MaskResult(masked={}, keys_masked=["password", "token"])
    assert "2" in r.summary()
    assert "password" in r.summary()


def test_mask_result_count():
    r = MaskResult(masked={}, keys_masked=["a", "b", "c"])
    assert r.count == 3


# --- mask_patch ---

def test_mask_patch_simple():
    patch = {"password": "new_secret"}
    result = mask_patch(patch, ["password"])
    assert result.masked["password"] == "***"


def test_mask_patch_not_dict_raises():
    with pytest.raises(MaskError):
        mask_patch(["not", "a", "dict"], ["key"])
