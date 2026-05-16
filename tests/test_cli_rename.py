"""Tests for confpatch.cli_rename."""

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from confpatch.cli_rename import cmd_rename


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump({"host": "localhost", "port": 8080}))
    return p


def make_args(config, rename, dry_run=False, skip_missing=False):
    ns = argparse.Namespace()
    ns.config = config
    ns.rename = rename
    ns.dry_run = dry_run
    ns.skip_missing = skip_missing
    return ns


def test_cmd_rename_config_not_found(tmp_path):
    args = make_args(tmp_path / "missing.yaml", ["host:hostname"])
    assert cmd_rename(args) == 1


def test_cmd_rename_success(config_file):
    args = make_args(config_file, ["host:hostname"])
    rc = cmd_rename(args)
    assert rc == 0
    data = yaml.safe_load(config_file.read_text())
    assert "hostname" in data
    assert "host" not in data


def test_cmd_rename_dry_run_does_not_write(config_file):
    original = config_file.read_text()
    args = make_args(config_file, ["host:hostname"], dry_run=True)
    rc = cmd_rename(args)
    assert rc == 0
    assert config_file.read_text() == original


def test_cmd_rename_invalid_spec(config_file):
    args = make_args(config_file, ["badspec"])
    assert cmd_rename(args) == 1


def test_cmd_rename_missing_key_no_skip(config_file):
    args = make_args(config_file, ["nonexistent:new"])
    assert cmd_rename(args) == 1


def test_cmd_rename_missing_key_with_skip(config_file):
    args = make_args(config_file, ["host:hostname", "nonexistent:new"], skip_missing=True)
    rc = cmd_rename(args)
    assert rc == 0
    data = yaml.safe_load(config_file.read_text())
    assert "hostname" in data


def test_cmd_rename_no_renames(config_file):
    args = make_args(config_file, [])
    assert cmd_rename(args) == 1
