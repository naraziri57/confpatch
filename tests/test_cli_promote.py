"""Tests for confpatch.cli_promote."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest
import yaml

from confpatch.cli_promote import cmd_promote


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump({"app": {"host": "localhost", "port": 8080}, "debug": True}))
    return p


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "config": "",
        "path": "app",
        "remove_source": False,
        "overwrite": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_promote_config_not_found(tmp_path):
    args = make_args(config=str(tmp_path / "missing.yaml"))
    assert cmd_promote(args) == 1


def test_cmd_promote_success(config_file):
    args = make_args(config=str(config_file), path="app")
    rc = cmd_promote(args)
    assert rc == 0
    data = yaml.safe_load(config_file.read_text())
    assert data["host"] == "localhost"
    assert data["port"] == 8080


def test_cmd_promote_dry_run_does_not_write(config_file):
    original = config_file.read_text()
    args = make_args(config=str(config_file), path="app", dry_run=True)
    rc = cmd_promote(args)
    assert rc == 0
    assert config_file.read_text() == original


def test_cmd_promote_remove_source(config_file):
    args = make_args(config=str(config_file), path="app", remove_source=True)
    cmd_promote(args)
    data = yaml.safe_load(config_file.read_text())
    assert "app" not in data


def test_cmd_promote_conflict_returns_error(config_file):
    # inject a conflicting top-level key
    data = yaml.safe_load(config_file.read_text())
    data["host"] = "conflict"
    config_file.write_text(yaml.dump(data))
    args = make_args(config=str(config_file), path="app")
    assert cmd_promote(args) == 1


def test_cmd_promote_overwrite_resolves_conflict(config_file):
    data = yaml.safe_load(config_file.read_text())
    data["host"] = "conflict"
    config_file.write_text(yaml.dump(data))
    args = make_args(config=str(config_file), path="app", overwrite=True)
    assert cmd_promote(args) == 0
    result = yaml.safe_load(config_file.read_text())
    assert result["host"] == "localhost"
