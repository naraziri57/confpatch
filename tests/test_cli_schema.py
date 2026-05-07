"""Tests for confpatch.cli_schema."""

from __future__ import annotations

import argparse

import pytest

from confpatch.cli_schema import cmd_validate, register_schema_commands


def make_args(config: str, schema: str) -> argparse.Namespace:
    return argparse.Namespace(config=config, schema=schema)


def test_cmd_validate_success(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("name: myapp\nport: 9000\n")
    sch = tmp_path / "schema.yaml"
    sch.write_text("name: str\nport: int\n")
    result = cmd_validate(make_args(str(cfg), str(sch)))
    assert result == 0


def test_cmd_validate_config_not_found(tmp_path):
    sch = tmp_path / "schema.yaml"
    sch.write_text("name: str\n")
    result = cmd_validate(make_args(str(tmp_path / "missing.yaml"), str(sch)))
    assert result == 1


def test_cmd_validate_schema_not_found(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("name: app\n")
    result = cmd_validate(make_args(str(cfg), str(tmp_path / "missing_schema.yaml")))
    assert result == 1


def test_cmd_validate_validation_failure(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("name: 42\nport: 9000\n")
    sch = tmp_path / "schema.yaml"
    sch.write_text("name: str\nport: int\n")
    result = cmd_validate(make_args(str(cfg), str(sch)))
    assert result == 2


def test_cmd_validate_missing_key(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("name: app\n")
    sch = tmp_path / "schema.yaml"
    sch.write_text("name: str\nport: int\n")
    result = cmd_validate(make_args(str(cfg), str(sch)))
    assert result == 2


def test_register_schema_commands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_schema_commands(subparsers)
    args = parser.parse_args(["validate-schema", "cfg.yaml", "schema.yaml"])
    assert args.config == "cfg.yaml"
    assert args.schema == "schema.yaml"
    assert callable(args.func)
