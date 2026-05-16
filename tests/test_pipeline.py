"""Tests for confpatch.pipeline."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from confpatch.pipeline import PipelineError, PipelineResult, StepResult, run_pipeline


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"app": {"port": 8080, "debug": False}, "version": "1.0"}))
    return cfg


def _write_patch(tmp_path: Path, name: str, data: dict) -> Path:
    p = tmp_path / name
    p.write_text(yaml.dump(data))
    return p


def test_run_pipeline_no_steps(config_file: Path) -> None:
    result = run_pipeline(str(config_file), steps=[])
    assert isinstance(result, PipelineResult)
    assert result.success is True
    assert result.steps == []


def test_run_pipeline_single_patch(config_file: Path, tmp_path: Path) -> None:
    patch = _write_patch(tmp_path, "p1.yaml", {"version": "2.0"})
    steps = [{"name": "bump-version", "type": "patch", "patch_file": str(patch)}]
    result = run_pipeline(str(config_file), steps=steps)
    assert result.success
    assert len(result.steps) == 1
    assert result.steps[0].name == "bump-version"
    loaded = yaml.safe_load(config_file.read_text())
    assert loaded["version"] == "2.0"


def test_run_pipeline_dry_run_does_not_write(config_file: Path, tmp_path: Path) -> None:
    original = config_file.read_text()
    patch = _write_patch(tmp_path, "p.yaml", {"version": "99.0"})
    steps = [{"name": "s", "type": "patch", "patch_file": str(patch)}]
    result = run_pipeline(str(config_file), steps=steps, dry_run=True)
    assert result.success
    assert config_file.read_text() == original


def test_run_pipeline_config_not_found(tmp_path: Path) -> None:
    with pytest.raises(PipelineError, match="Config not found"):
        run_pipeline(str(tmp_path / "missing.yaml"), steps=[])


def test_run_pipeline_unknown_step_type(config_file: Path) -> None:
    steps = [{"name": "bad", "type": "explode"}]
    result = run_pipeline(str(config_file), steps=steps)
    assert not result.success
    assert "Unknown step type" in result.steps[0].message


def test_run_pipeline_stops_on_failure(config_file: Path, tmp_path: Path) -> None:
    good = _write_patch(tmp_path, "good.yaml", {"version": "2.0"})
    steps = [
        {"name": "ok", "type": "patch", "patch_file": str(good)},
        {"name": "bad", "type": "patch", "patch_file": "/nonexistent/patch.yaml"},
        {"name": "never", "type": "patch", "patch_file": str(good)},
    ]
    result = run_pipeline(str(config_file), steps=steps)
    assert not result.success
    assert len(result.steps) == 2
    assert result.steps[1].name == "bad"


def test_step_result_str_ok() -> None:
    s = StepResult(name="x", success=True, message="done")
    assert str(s) == "[ok] x: done"


def test_step_result_str_fail() -> None:
    s = StepResult(name="y", success=False, message="oops")
    assert str(s) == "[fail] y: oops"


def test_pipeline_result_summary_contains_status(config_file: Path, tmp_path: Path) -> None:
    patch = _write_patch(tmp_path, "p.yaml", {"version": "3.0"})
    steps = [{"name": "s", "type": "patch", "patch_file": str(patch)}]
    result = run_pipeline(str(config_file), steps=steps)
    summary = result.summary()
    assert "SUCCESS" in summary
    assert str(config_file) in summary
