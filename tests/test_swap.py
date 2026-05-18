"""Tests for confpatch.swap."""
import pytest
from confpatch.swap import swap_keys, SwapError, SwapResult


@pytest.fixture
def config():
    return {
        "host": "localhost",
        "port": 8080,
        "db": {
            "primary": "db1",
            "replica": "db2",
        },
    }


def test_swap_top_level_keys(config):
    result = swap_keys(config, [("host", "port")])
    assert result.config["host"] == 8080
    assert result.config["port"] == "localhost"


def test_swap_does_not_mutate_original(config):
    original_host = config["host"]
    swap_keys(config, [("host", "port")])
    assert config["host"] == original_host


def test_swap_nested_keys(config):
    result = swap_keys(config, [("db.primary", "db.replica")])
    assert result.config["db"]["primary"] == "db2"
    assert result.config["db"]["replica"] == "db1"


def test_swap_multiple_pairs(config):
    result = swap_keys(config, [("host", "port"), ("db.primary", "db.replica")])
    assert result.config["host"] == 8080
    assert result.config["port"] == "localhost"
    assert result.config["db"]["primary"] == "db2"
    assert result.config["db"]["replica"] == "db1"


def test_swap_has_changes(config):
    result = swap_keys(config, [("host", "port")])
    assert result.has_changes() is True


def test_swap_no_pairs_no_changes(config):
    result = swap_keys(config, [])
    assert result.has_changes() is False
    assert result.count() == 0


def test_swap_count(config):
    result = swap_keys(config, [("host", "port"), ("db.primary", "db.replica")])
    assert result.count() == 2


def test_swap_summary_with_changes(config):
    result = swap_keys(config, [("host", "port")])
    s = result.summary()
    assert "host" in s
    assert "port" in s
    assert "<->" in s


def test_swap_summary_no_changes(config):
    result = swap_keys(config, [])
    assert result.summary() == "No keys swapped."


def test_swap_missing_key_raises(config):
    with pytest.raises(SwapError, match="Key not found"):
        swap_keys(config, [("host", "nonexistent")])


def test_swap_missing_nested_key_raises(config):
    with pytest.raises(SwapError):
        swap_keys(config, [("db.primary", "db.missing")])


def test_swap_result_config_has_all_original_keys(config):
    result = swap_keys(config, [("host", "port")])
    assert set(result.config.keys()) == set(config.keys())
