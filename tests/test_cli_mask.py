"""Tests for confpatch.cli_mask."""
import argparse
import json
from pathlib import Path

import pytest

from confpatch.cli_mask import cmd_mask, register_mask_commands


def make_args(**kwargs):
    defaults = {
        "config": "",
        "keys": [],
        "reveal": 0,
        "summary": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_mask_config_not_found(tmp_path):
    args = make_args(config=str(tmp_path / "missing.yaml"), keys=["password"])
    assert cmd_mask(args) == 1


def test_cmd_mask_no_keys(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("password: secret\n")
    args = make_args(config=str(cfg), keys=[])
    assert cmd_mask(args) == 1


def test_cmd_mask_success(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("password: hunter2\nhost: localhost\n")
    args = make_args(config=str(cfg), keys=["password"])
    rc = cmd_mask(args)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out.strip())
    assert data["password"] == "***"
    assert data["host"] == "localhost"


def test_cmd_mask_reveal_chars(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("token: abcdef\n")
    args = make_args(config=str(cfg), keys=["token"], reveal=2)
    cmd_mask(args)
    out = capsys.readouterr().out
    data = json.loads(out.strip())
    assert data["token"].startswith("ab")
    assert "***" in data["token"]


def test_cmd_mask_summary(tmp_path, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("password: s3cr3t\n")
    args = make_args(config=str(cfg), keys=["password"], summary=True)
    cmd_mask(args)
    out = capsys.readouterr().out
    assert "password" in out
    assert "Masked" in out


def test_register_mask_commands():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_mask_commands(sub)
    args = parser.parse_args(["mask", "config.yaml", "--keys", "password"])
    assert args.keys == ["password"]
    assert args.reveal == 0
    assert args.summary is False
