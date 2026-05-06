"""Tests for core patch application logic."""

import pytest
from confpatch.patch import apply_patch, load_patch


def test_load_patch_valid():
    patch = {"key": "value"}
    assert load_patch(patch) == patch


def test_load_patch_invalid_type():
    with pytest.raises(TypeError, match="Patch must be a dict"):
        load_patch(["not", "a", "dict"])


def test_apply_patch_simple():
    config = {"host": "localhost", "port": 5432}
    patch = {"port": 9999}
    result = apply_patch(config, patch)
    assert result["port"] == 9999
    assert result["host"] == "localhost"


def test_apply_patch_does_not_mutate_original():
    config = {"host": "localhost"}
    patch = {"host": "remotehost"}
    result = apply_patch(config, patch)
    assert config["host"] == "localhost"
    assert result["host"] == "remotehost"


def test_apply_patch_dot_notation():
    config = {"database": {"host": "localhost", "port": 5432}}
    patch = {"database.host": "db.example.com"}
    result = apply_patch(config, patch)
    assert result["database"]["host"] == "db.example.com"
    assert result["database"]["port"] == 5432


def test_apply_patch_creates_nested_keys():
    config = {}
    patch = {"server.host": "0.0.0.0", "server.port": 8080}
    result = apply_patch(config, patch)
    assert result["server"]["host"] == "0.0.0.0"
    assert result["server"]["port"] == 8080


def test_apply_patch_disallow_new_keys_raises():
    config = {"existing": "value"}
    patch = {"new_key": "something"}
    with pytest.raises(KeyError, match="new_key"):
        apply_patch(config, patch, allow_new_keys=False)


def test_apply_patch_disallow_new_keys_existing_ok():
    config = {"port": 80}
    patch = {"port": 443}
    result = apply_patch(config, patch, allow_new_keys=False)
    assert result["port"] == 443


def test_apply_patch_deep_nested():
    config = {"a": {"b": {"c": 1}}}
    patch = {"a.b.c": 42}
    result = apply_patch(config, patch)
    assert result["a"]["b"]["c"] == 42


def test_apply_patch_empty_patch():
    """Applying an empty patch should return a copy of the original config unchanged."""
    config = {"host": "localhost", "port": 5432}
    result = apply_patch(config, {})
    assert result == config
    assert result is not config


def test_apply_patch_disallow_new_keys_dot_notation_raises():
    """Dot-notation keys that would create new nested paths should also raise when allow_new_keys=False."""
    config = {"database": {"host": "localhost"}}
    patch = {"database.port": 5432}
    with pytest.raises(KeyError, match="port"):
        apply_patch(config, patch, allow_new_keys=False)
