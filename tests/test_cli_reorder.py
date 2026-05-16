"""Tests for confpatch.cli_reorder."""

import argparse
import pytest
from pathlib import Path
from confpatch.cli_reorder import cmd_reorder
from confpatch.loaders import save_config, load_config


@pytest.fixture
def config_file(tmp_path):
    path = tmp_path / "config.yaml"
    save_config({"b": 2, "a": 1, "c": 3}, str(path))
    return path


def make_args(**kwargs):
    defaults = {
        "config": "config.yaml",
        "keys": ["a", "b", "c"],
        "scope": None,
        "dry_run": False,
    }
    defaults.update(kwargs)
    ns = argparse.Namespace(**defaults)
    return ns


def test_cmd_reorder_config_not_found(tmp_path, capsys):
    args = make_args(config=str(tmp_path / "missing.yaml"))
    cmd_reorder(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_reorder_success(config_file, capsys):
    args = make_args(config=str(config_file), keys=["a", "b", "c"])
    cmd_reorder(args)
    out = capsys.readouterr().out
    assert "Reordered" in out or "Saved" in out
    loaded = load_config(str(config_file))
    assert list(loaded.keys()) == ["a", "b", "c"]


def test_cmd_reorder_dry_run_does_not_write(config_file, capsys):
    args = make_args(config=str(config_file), keys=["a", "b", "c"], dry_run=True)
    cmd_reorder(args)
    out = capsys.readouterr().out
    assert "Dry run" in out
    loaded = load_config(str(config_file))
    # original order preserved
    assert list(loaded.keys()) == ["b", "a", "c"]


def test_cmd_reorder_with_scope(tmp_path, capsys):
    path = tmp_path / "cfg.yaml"
    save_config({"db": {"port": 5432, "host": "localhost"}}, str(path))
    args = make_args(config=str(path), keys=["host", "port"], scope="db")
    cmd_reorder(args)
    loaded = load_config(str(path))
    assert list(loaded["db"].keys()) == ["host", "port"]


def test_cmd_reorder_bad_scope(config_file, capsys):
    args = make_args(config=str(config_file), keys=["x"], scope="nonexistent")
    cmd_reorder(args)
    out = capsys.readouterr().out
    assert "error" in out.lower()
