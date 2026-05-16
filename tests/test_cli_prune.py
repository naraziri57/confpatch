"""Tests for confpatch.cli_prune."""
import pytest
import yaml
from pathlib import Path
from confpatch.cli_prune import cmd_prune


def make_args(config, empty=False, dry_run=False):
    import argparse
    args = argparse.Namespace(config=config, empty=empty, dry_run=dry_run)
    return args


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump({"host": "localhost", "token": None, "port": 8080}))
    return str(p)


def test_cmd_prune_config_not_found(capsys):
    args = make_args("/nonexistent/config.yaml")
    cmd_prune(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_prune_success(config_file, capsys):
    args = make_args(config_file)
    cmd_prune(args)
    out = capsys.readouterr().out
    assert "Pruned" in out or "Saved" in out
    data = yaml.safe_load(Path(config_file).read_text())
    assert "token" not in data
    assert data["host"] == "localhost"


def test_cmd_prune_dry_run_does_not_write(config_file, capsys):
    original = Path(config_file).read_text()
    args = make_args(config_file, dry_run=True)
    cmd_prune(args)
    out = capsys.readouterr().out
    assert "Dry run" in out
    assert Path(config_file).read_text() == original


def test_cmd_prune_nothing_to_prune(tmp_path, capsys):
    p = tmp_path / "clean.yaml"
    p.write_text(yaml.dump({"a": 1, "b": "ok"}))
    args = make_args(str(p))
    cmd_prune(args)
    out = capsys.readouterr().out
    assert "Nothing to prune" in out or "No keys pruned" in out


def test_cmd_prune_empty_flag(tmp_path, capsys):
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump({"name": "app", "tags": [], "desc": ""}))
    args = make_args(str(p), empty=True)
    cmd_prune(args)
    data = yaml.safe_load(p.read_text())
    assert "tags" not in data
    assert "desc" not in data
    assert data["name"] == "app"
