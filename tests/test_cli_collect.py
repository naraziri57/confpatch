"""Tests for confpatch.cli_collect."""

from __future__ import annotations

import json
import os
import tempfile

import pytest
import yaml

from confpatch.cli_collect import cmd_collect


class FakeArgs:
    def __init__(self, config, keys, skip_missing=False, json_out=False):
        self.config = config
        self.keys = keys
        self.skip_missing = skip_missing
        self.json = json_out


@pytest.fixture
def config_file(tmp_path):
    cfg = {"host": "localhost", "port": 8080, "nested": {"key": "value"}}
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump(cfg))
    return str(p)


def test_cmd_collect_success(config_file, capsys):
    args = FakeArgs(config_file, ["host", "port"])
    rc = cmd_collect(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "host" in out
    assert "localhost" in out


def test_cmd_collect_json_output(config_file, capsys):
    args = FakeArgs(config_file, ["host", "port"], json_out=True)
    rc = cmd_collect(args)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["host"] == "localhost"
    assert data["port"] == 8080


def test_cmd_collect_config_not_found(capsys):
    args = FakeArgs("/no/such/file.yaml", ["host"])
    rc = cmd_collect(args)
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_cmd_collect_no_keys(config_file, capsys):
    args = FakeArgs(config_file, [])
    rc = cmd_collect(args)
    assert rc == 1
    assert "key" in capsys.readouterr().err


def test_cmd_collect_missing_key_error(config_file, capsys):
    args = FakeArgs(config_file, ["nonexistent"])
    rc = cmd_collect(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().err


def test_cmd_collect_skip_missing(config_file, capsys):
    args = FakeArgs(config_file, ["host", "missing"], skip_missing=True)
    rc = cmd_collect(args)
    assert rc == 0
    err = capsys.readouterr().err
    assert "missing" in err


def test_cmd_collect_dot_notation(config_file, capsys):
    args = FakeArgs(config_file, ["nested.key"], json_out=True)
    rc = cmd_collect(args)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["nested.key"] == "value"
