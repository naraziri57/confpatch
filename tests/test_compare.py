"""Tests for confpatch.compare module."""

import pytest
from pathlib import Path

from confpatch.compare import compare_configs, CompareResult, CompareError


@pytest.fixture
def config_a(tmp_path):
    f = tmp_path / "a.yaml"
    f.write_text("host: localhost\nport: 8080\ndebug: false\n")
    return f


@pytest.fixture
def config_b(tmp_path):
    f = tmp_path / "b.yaml"
    f.write_text("host: localhost\nport: 9090\ntimeout: 30\n")
    return f


@pytest.fixture
def config_identical(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("host: localhost\nport: 8080\ndebug: false\n")
    return f


def test_compare_returns_compare_result(config_a, config_b):
    result = compare_configs(config_a, config_b)
    assert isinstance(result, CompareResult)


def test_compare_detects_differences(config_a, config_b):
    result = compare_configs(config_a, config_b)
    assert result.has_differences


def test_compare_no_differences(config_a, config_identical):
    result = compare_configs(config_a, config_identical)
    assert not result.has_differences
    assert result.change_count == 0


def test_compare_change_count(config_a, config_b):
    result = compare_configs(config_a, config_b)
    assert result.change_count > 0


def test_compare_summary_no_diff(config_a, config_identical):
    result = compare_configs(config_a, config_identical)
    summary = result.summary()
    assert "No differences" in summary


def test_compare_summary_with_diff(config_a, config_b):
    result = compare_configs(config_a, config_b)
    summary = result.summary()
    assert "difference" in summary


def test_compare_format_no_diff_returns_summary(config_a, config_identical):
    result = compare_configs(config_a, config_identical)
    assert result.format() == result.summary()


def test_compare_format_with_diff_returns_string(config_a, config_b):
    result = compare_configs(config_a, config_b)
    formatted = result.format()
    assert isinstance(formatted, str)
    assert len(formatted) > 0


def test_compare_file_a_not_found(tmp_path, config_b):
    with pytest.raises(CompareError, match="File not found"):
        compare_configs(tmp_path / "missing.yaml", config_b)


def test_compare_file_b_not_found(tmp_path, config_a):
    with pytest.raises(CompareError, match="File not found"):
        compare_configs(config_a, tmp_path / "missing.yaml")


def test_compare_stores_file_paths(config_a, config_b):
    result = compare_configs(config_a, config_b)
    assert str(config_a) in result.file_a
    assert str(config_b) in result.file_b
