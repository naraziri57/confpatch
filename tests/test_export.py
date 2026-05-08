"""Tests for confpatch.export module."""

import json
import os
from pathlib import Path

import pytest

from confpatch.export import (
    ExportError,
    _flatten,
    export_config,
    export_env,
    export_json,
)


# --- _flatten ---

def test_flatten_simple():
    assert _flatten({"a": 1, "b": 2}) == {"a": 1, "b": 2}


def test_flatten_nested():
    result = _flatten({"db": {"host": "localhost", "port": 5432}})
    assert result == {"db.host": "localhost", "db.port": 5432}


def test_flatten_deep():
    result = _flatten({"a": {"b": {"c": 42}}})
    assert result == {"a.b.c": 42}


# --- export_json ---

def test_export_json_creates_file(tmp_path):
    dest = tmp_path / "out.json"
    export_json({"key": "value"}, dest)
    assert dest.exists()


def test_export_json_valid_content(tmp_path):
    dest = tmp_path / "out.json"
    export_json({"x": 1, "y": [1, 2]}, dest)
    loaded = json.loads(dest.read_text())
    assert loaded == {"x": 1, "y": [1, 2]}


def test_export_json_returns_path(tmp_path):
    dest = tmp_path / "out.json"
    result = export_json({}, dest)
    assert result == dest


def test_export_json_bad_path():
    with pytest.raises(ExportError):
        export_json({"a": 1}, Path("/nonexistent_dir/out.json"))


# --- export_env ---

def test_export_env_creates_file(tmp_path):
    dest = tmp_path / "out.env"
    export_env({"host": "localhost"}, dest)
    assert dest.exists()


def test_export_env_content(tmp_path):
    dest = tmp_path / "out.env"
    export_env({"db": {"host": "localhost", "port": 5432}}, dest)
    content = dest.read_text()
    assert "DB_HOST=localhost" in content
    assert "DB_PORT=5432" in content


def test_export_env_with_prefix(tmp_path):
    dest = tmp_path / "out.env"
    export_env({"debug": True}, dest, prefix="APP")
    content = dest.read_text()
    assert "APP_DEBUG=True" in content


def test_export_env_returns_path(tmp_path):
    dest = tmp_path / "out.env"
    result = export_env({}, dest)
    assert result == dest


# --- export_config dispatch ---

def test_export_config_json(tmp_path):
    dest = tmp_path / "cfg.json"
    export_config({"a": 1}, dest, fmt="json")
    assert json.loads(dest.read_text()) == {"a": 1}


def test_export_config_env(tmp_path):
    dest = tmp_path / "cfg.env"
    export_config({"mode": "prod"}, dest, fmt="env")
    assert "MODE=prod" in dest.read_text()


def test_export_config_unknown_format(tmp_path):
    with pytest.raises(ExportError, match="Unsupported export format"):
        export_config({}, tmp_path / "out.xml", fmt="xml")
