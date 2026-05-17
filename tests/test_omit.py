"""Tests for confpatch.omit."""

import pytest
from confpatch.omit import OmitError, OmitResult, omit_keys


@pytest.fixture
def config():
    return {
        "app": {
            "name": "myapp",
            "debug": True,
            "port": 8080,
        },
        "database": {
            "host": "localhost",
            "password": "secret",
        },
        "version": "1.0",
    }


def test_omit_top_level_key(config):
    result = omit_keys(config, ["version"])
    assert "version" not in result.config
    assert result.has_changes()
    assert result.count() == 1


def test_omit_nested_key(config):
    result = omit_keys(config, ["app.debug"])
    assert "debug" not in result.config["app"]
    assert result.config["app"]["name"] == "myapp"
    assert result.count() == 1


def test_omit_multiple_keys(config):
    result = omit_keys(config, ["version", "database.password"])
    assert "version" not in result.config
    assert "password" not in result.config["database"]
    assert result.count() == 2


def test_omit_does_not_mutate_original(config):
    original_version = config["version"]
    omit_keys(config, ["version"])
    assert config["version"] == original_version


def test_omit_missing_key_raises(config):
    with pytest.raises(OmitError, match="Key not found"):
        omit_keys(config, ["nonexistent"])


def test_omit_missing_key_missing_ok(config):
    result = omit_keys(config, ["nonexistent"], missing_ok=True)
    assert result.count() == 0
    assert not result.has_changes()


def test_omit_missing_nested_path_raises(config):
    with pytest.raises(OmitError):
        omit_keys(config, ["app.nonexistent.deep"])


def test_omit_missing_nested_path_missing_ok(config):
    result = omit_keys(config, ["app.nonexistent.deep"], missing_ok=True)
    assert result.count() == 0


def test_omit_non_dict_config_raises():
    with pytest.raises(OmitError, match="Config must be a dict"):
        omit_keys(["not", "a", "dict"], ["key"])


def test_omit_no_keys_returns_copy(config):
    result = omit_keys(config, [])
    assert result.config == config
    assert not result.has_changes()


def test_omit_summary_with_changes(config):
    result = omit_keys(config, ["version", "app.debug"])
    s = result.summary()
    assert "2" in s
    assert "version" in s


def test_omit_summary_no_changes(config):
    result = omit_keys(config, [], missing_ok=True)
    assert result.summary() == "No keys omitted."
