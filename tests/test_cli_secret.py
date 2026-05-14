"""Tests for confpatch.cli_secret."""

import argparse
from unittest.mock import patch, MagicMock
import pytest

from confpatch.cli_secret import cmd_redact, cmd_list_sensitive, register_secret_commands


def make_args(**kwargs):
    ns = argparse.Namespace()
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_cmd_redact_file_not_found(tmp_path):
    args = make_args(patch_file=str(tmp_path / "missing.yaml"))
    result = cmd_redact(args)
    assert result == 1


def test_cmd_redact_success(tmp_path):
    patch_file = tmp_path / "patch.yaml"
    patch_file.write_text("username: admin\npassword: secret\n")
    args = make_args(patch_file=str(patch_file))
    result = cmd_redact(args)
    assert result == 0


def test_cmd_redact_shows_masked_value(tmp_path, capsys):
    patch_file = tmp_path / "patch.yaml"
    patch_file.write_text("password: hunter2\n")
    args = make_args(patch_file=str(patch_file))
    cmd_redact(args)
    captured = capsys.readouterr()
    assert "***" in captured.out
    assert "hunter2" not in captured.out


def test_cmd_list_sensitive_file_not_found(tmp_path):
    args = make_args(patch_file=str(tmp_path / "nope.yaml"))
    result = cmd_list_sensitive(args)
    assert result == 1


def test_cmd_list_sensitive_detects_keys(tmp_path, capsys):
    patch_file = tmp_path / "patch.yaml"
    patch_file.write_text("api_key: abc123\nhost: localhost\n")
    args = make_args(patch_file=str(patch_file))
    result = cmd_list_sensitive(args)
    assert result == 0
    out = capsys.readouterr().out
    assert "api_key" in out


def test_cmd_list_sensitive_no_sensitive_keys(tmp_path, capsys):
    patch_file = tmp_path / "patch.yaml"
    patch_file.write_text("host: localhost\nport: 5432\n")
    args = make_args(patch_file=str(patch_file))
    result = cmd_list_sensitive(args)
    assert result == 0
    out = capsys.readouterr().out
    assert "No sensitive" in out


def test_register_secret_commands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_secret_commands(subparsers)
    args = parser.parse_args(["redact", "some_file.yaml"])
    assert args.patch_file == "some_file.yaml"
    assert callable(args.func)
