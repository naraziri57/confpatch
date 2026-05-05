"""Tests for confpatch.validator module."""

import pytest

from confpatch.validator import (
    PatchValidationError,
    validate_format,
    validate_keys,
    validate_patch_structure,
)


# --- validate_patch_structure ---

def test_validate_patch_structure_valid():
    validate_patch_structure({"key": "value"})  # should not raise


def test_validate_patch_structure_not_dict():
    with pytest.raises(PatchValidationError, match="mapping"):
        validate_patch_structure(["key", "value"])


def test_validate_patch_structure_empty_dict():
    with pytest.raises(PatchValidationError, match="empty"):
        validate_patch_structure({})


def test_validate_patch_structure_none():
    with pytest.raises(PatchValidationError, match="mapping"):
        validate_patch_structure(None)


# --- validate_keys ---

def test_validate_keys_valid():
    validate_keys({"a": 1, "b.c": 2})  # should not raise


def test_validate_keys_non_string_key():
    with pytest.raises(PatchValidationError, match="strings"):
        validate_keys({1: "value"})


def test_validate_keys_dot_notation_disallowed():
    with pytest.raises(PatchValidationError, match="Dot-notation"):
        validate_keys({"a.b": 1}, allow_dot_notation=False)


def test_validate_keys_dot_notation_allowed():
    validate_keys({"a.b": 1}, allow_dot_notation=True)  # should not raise


def test_validate_keys_empty_key():
    with pytest.raises(PatchValidationError, match="empty"):
        validate_keys({"": "value"})


def test_validate_keys_whitespace_key():
    with pytest.raises(PatchValidationError, match="empty"):
        validate_keys({"   ": "value"})


# --- validate_format ---

def test_validate_format_yaml():
    validate_format("yaml")  # should not raise


def test_validate_format_toml():
    validate_format("toml")  # should not raise


def test_validate_format_unsupported():
    with pytest.raises(PatchValidationError, match="Unsupported"):
        validate_format("json")


def test_validate_format_empty_string():
    with pytest.raises(PatchValidationError, match="Unsupported"):
        validate_format("")
