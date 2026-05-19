import pytest
from confpatch.uppercase import uppercase_keys, UppercaseError, UppercaseResult


@pytest.fixture
def config():
    return {
        "name": "alice",
        "role": "admin",
        "meta": {
            "region": "us-east",
            "tier": "free",
        },
        "count": 42,
    }


def test_uppercase_single_key(config):
    result = uppercase_keys(config, ["name"])
    assert result.config["name"] == "ALICE"
    assert result.has_changes()
    assert result.count() == 1


def test_uppercase_multiple_keys(config):
    result = uppercase_keys(config, ["name", "role"])
    assert result.config["name"] == "ALICE"
    assert result.config["role"] == "ADMIN"
    assert result.count() == 2


def test_uppercase_nested_key(config):
    result = uppercase_keys(config, ["meta.region"])
    assert result.config["meta"]["region"] == "US-EAST"
    assert result.has_changes()


def test_uppercase_non_string_passthrough(config):
    result = uppercase_keys(config, ["count"])
    assert result.config["count"] == 42
    assert not result.has_changes()


def test_uppercase_does_not_mutate_original(config):
    original_name = config["name"]
    uppercase_keys(config, ["name"])
    assert config["name"] == original_name


def test_uppercase_missing_key_raises(config):
    with pytest.raises(UppercaseError, match="Key not found"):
        uppercase_keys(config, ["nonexistent"])


def test_uppercase_missing_nested_key_raises(config):
    with pytest.raises(UppercaseError, match="Key not found"):
        uppercase_keys(config, ["meta.missing"])


def test_uppercase_not_a_dict_raises():
    with pytest.raises(UppercaseError, match="Config must be a dict"):
        uppercase_keys(["not", "a", "dict"], ["key"])


def test_uppercase_no_keys_returns_unchanged(config):
    result = uppercase_keys(config, [])
    assert not result.has_changes()
    assert result.config == config


def test_uppercase_summary_with_changes(config):
    result = uppercase_keys(config, ["name"])
    assert "name" in result.summary()
    assert "1" in result.summary()


def test_uppercase_summary_no_changes(config):
    result = uppercase_keys(config, [])
    assert "No string values" in result.summary()


def test_uppercase_already_uppercase_no_change(config):
    config["name"] = "ALICE"
    result = uppercase_keys(config, ["name"])
    assert not result.has_changes()
