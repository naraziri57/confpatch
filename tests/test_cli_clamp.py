"""Tests for confpatch.cli_clamp."""

import argparse
from pathlib import Path

import pytest
import yaml

from confpatch.cli_clamp import cmd_clamp


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump({"timeout": 9999, "retries": 1, "label": "prod"}))
    return p


def make_args(**kwargs):
    defaults = {
        "config": None,
        "min": None,
        "max": None,
        "keys": None,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_clamp_config_not_found(capsys):
    args = make_args(config="/nonexistent/config.yaml", max=100)
    cmd_clamp(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_clamp_no_min_or_max(config_file, capsys):
    args = make_args(config=str(config_file))
    cmd_clamp(args)
    out = capsys.readouterr().out
    assert "at least one" in out


def test_cmd_clamp_success(config_file, capsys):
    args = make_args(config=str(config_file), max=100)
    cmd_clamp(args)
    out = capsys.readouterr().out
    assert "Clamped" in out or "Saved" in out
    data = yaml.safe_load(config_file.read_text())
    assert data["timeout"] == 100
    assert data["retries"] == 1


def test_cmd_clamp_dry_run_does_not_write(config_file, capsys):
    args = make_args(config=str(config_file), max=100, dry_run=True)
    cmd_clamp(args)
    out = capsys.readouterr().out
    assert "Dry run" in out
    data = yaml.safe_load(config_file.read_text())
    assert data["timeout"] == 9999


def test_cmd_clamp_specific_keys(config_file, capsys):
    args = make_args(config=str(config_file), max=100, keys=["timeout"])
    cmd_clamp(args)
    data = yaml.safe_load(config_file.read_text())
    assert data["timeout"] == 100
    assert data["retries"] == 1


def test_cmd_clamp_non_numeric_untouched(config_file, capsys):
    args = make_args(config=str(config_file), max=100)
    cmd_clamp(args)
    data = yaml.safe_load(config_file.read_text())
    assert data["label"] == "prod"
