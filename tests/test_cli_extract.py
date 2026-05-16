"""Tests for confpatch.cli_extract."""

from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest
import yaml

from confpatch.cli_extract import cmd_extract, register_extract_commands
from confpatch.extract import ExtractError, ExtractResult


def make_args(**kwargs):
    defaults = {
        "config": "config.yaml",
        "keys": [],
        "output": None,
        "format": None,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_extract_no_keys(capsys):
    args = make_args(keys=[])
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "at least one key" in out


def test_cmd_extract_file_not_found(capsys):
    args = make_args(config="/no/such/file.yaml", keys=["a"])
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_extract_success(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"host": "localhost", "port": 5432}))
    args = make_args(config=str(cfg), keys=["host"])
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "Extracted" in out


def test_cmd_extract_dry_run_shows_values(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"host": "localhost"}))
    dest = tmp_path / "out.yaml"
    args = make_args(config=str(cfg), keys=["host"], output=str(dest), dry_run=True)
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "Dry run" in out
    assert not dest.exists()


def test_cmd_extract_writes_output(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"key": "value"}))
    dest = tmp_path / "out.yaml"
    args = make_args(config=str(cfg), keys=["key"], output=str(dest))
    cmd_extract(args)
    assert dest.exists()
    out = capsys.readouterr().out
    assert "Saved" in out


def test_cmd_extract_error(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"a": 1}))
    args = make_args(config=str(cfg), keys=["missing_key"])
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "Extract error" in out


def test_register_extract_commands():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_extract_commands(sub)
    args = parser.parse_args(["extract", "cfg.yaml", "--key", "a"])
    assert args.keys == ["a"]
    assert args.config == "cfg.yaml"
