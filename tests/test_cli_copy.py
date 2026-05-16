"""Tests for confpatch.cli_copy."""

from __future__ import annotations

import argparse

import pytest

from confpatch.cli_copy import cmd_copy
from confpatch.loaders import save_config, load_config


@pytest.fixture
def config_file(tmp_path):
    path = tmp_path / "config.yaml"
    save_config({"database": {"host": "localhost", "port": 5432}}, str(path))
    return str(path)


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "config": "config.yaml",
        "pairs": ["database.host:backup.host"],
        "overwrite": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_copy_config_not_found(tmp_path):
    args = make_args(config=str(tmp_path / "missing.yaml"))
    result = cmd_copy(args)
    assert result == 1


def test_cmd_copy_no_pairs(config_file):
    args = make_args(config=config_file, pairs=[])
    result = cmd_copy(args)
    assert result == 1


def test_cmd_copy_invalid_pair_format(config_file):
    args = make_args(config=config_file, pairs=["database.host"])
    result = cmd_copy(args)
    assert result == 1


def test_cmd_copy_success(config_file):
    args = make_args(config=config_file, pairs=["database.host:backup.host"])
    result = cmd_copy(args)
    assert result == 0
    config = load_config(config_file)
    assert config["backup"]["host"] == "localhost"


def test_cmd_copy_dry_run_does_not_write(config_file):
    args = make_args(
        config=config_file,
        pairs=["database.host:backup.host"],
        dry_run=True,
    )
    result = cmd_copy(args)
    assert result == 0
    config = load_config(config_file)
    assert "backup" not in config


def test_cmd_copy_missing_source_returns_error(config_file):
    args = make_args(config=config_file, pairs=["nonexistent.key:backup.host"])
    result = cmd_copy(args)
    assert result == 1


def test_cmd_copy_overwrite_flag(config_file):
    save_config(
        {"database": {"host": "localhost"}, "backup": {"host": "old"}},
        config_file,
    )
    args = make_args(
        config=config_file,
        pairs=["database.host:backup.host"],
        overwrite=True,
    )
    result = cmd_copy(args)
    assert result == 0
    config = load_config(config_file)
    assert config["backup"]["host"] == "localhost"
