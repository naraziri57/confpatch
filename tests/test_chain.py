"""Tests for confpatch.chain."""

from __future__ import annotations

import pytest
import yaml
from pathlib import Path

from confpatch.chain import apply_chain, ChainError, ChainResult


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"name": "alice", "version": 1, "debug": False}))
    return cfg


def _write_patch(tmp_path: Path, name: str, data: dict) -> Path:
    p = tmp_path / name
    p.write_text(yaml.dump(data))
    return p


def test_apply_chain_single_patch(config_file, tmp_path):
    patch = _write_patch(tmp_path, "p1.yaml", {"version": 2})
    result = apply_chain(config_file, [patch])
    assert result.success
    assert result.final_config["version"] == 2
    assert len(result.patches_applied) == 1


def test_apply_chain_multiple_patches(config_file, tmp_path):
    p1 = _write_patch(tmp_path, "p1.yaml", {"version": 2})
    p2 = _write_patch(tmp_path, "p2.yaml", {"debug": True})
    result = apply_chain(config_file, [p1, p2])
    assert result.success
    assert result.final_config["version"] == 2
    assert result.final_config["debug"] is True
    assert len(result.patches_applied) == 2


def test_apply_chain_config_not_found(tmp_path):
    with pytest.raises(ChainError, match="not found"):
        apply_chain(tmp_path / "missing.yaml", [])


def test_apply_chain_bad_patch_stop_on_error(config_file, tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("[not a dict]")
    p2 = _write_patch(tmp_path, "p2.yaml", {"debug": True})
    result = apply_chain(config_file, [bad, p2], stop_on_error=True)
    assert not result.success
    assert len(result.patches_failed) == 1
    assert len(result.patches_applied) == 0


def test_apply_chain_keep_going(config_file, tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("[not a dict]")
    p2 = _write_patch(tmp_path, "p2.yaml", {"debug": True})
    result = apply_chain(config_file, [bad, p2], stop_on_error=False)
    assert not result.success
    assert len(result.patches_failed) == 1
    assert len(result.patches_applied) == 1


def test_apply_chain_dry_run_does_not_write(config_file, tmp_path):
    original = config_file.read_text()
    patch = _write_patch(tmp_path, "p1.yaml", {"version": 99})
    result = apply_chain(config_file, [patch], dry_run=True)
    assert result.final_config["version"] == 99
    assert config_file.read_text() == original


def test_chain_result_summary():
    r = ChainResult(
        config_file="cfg.yaml",
        patches_applied=["a.yaml", "b.yaml"],
        patches_failed=[("c.yaml", "oops")],
    )
    s = r.summary()
    assert "2 applied" in s
    assert "1 failed" in s


def test_chain_result_success_flag():
    r = ChainResult(config_file="x.yaml", patches_applied=["a.yaml"])
    assert r.success is True
    r.patches_failed.append(("b.yaml", "err"))
    assert r.success is False
