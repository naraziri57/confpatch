"""Tests for confpatch.split."""

import pytest
from pathlib import Path

from confpatch.split import split_config, SplitError, SplitResult


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("database:\n  host: localhost\n  port: 5432\napp:\n  debug: true\nlogging:\n  level: info\n")
    return p


def test_split_all_keys(config_file, tmp_path):
    out = tmp_path / "out"
    result = split_config(str(config_file), str(out))
    assert result.has_output()
    assert result.count() == 3
    assert set(result.keys_split) == {"database", "app", "logging"}


def test_split_creates_files(config_file, tmp_path):
    out = tmp_path / "out"
    result = split_config(str(config_file), str(out))
    for p in result.files_written:
        assert Path(p).exists()


def test_split_specific_keys(config_file, tmp_path):
    out = tmp_path / "out"
    result = split_config(str(config_file), str(out), keys=["app"])
    assert result.count() == 1
    assert result.keys_split == ["app"]
    assert (out / "app.yaml").exists()


def test_split_dry_run_does_not_write(config_file, tmp_path):
    out = tmp_path / "out"
    result = split_config(str(config_file), str(out), dry_run=True)
    assert result.dry_run is True
    assert result.has_output()
    assert not out.exists()


def test_split_file_not_found(tmp_path):
    with pytest.raises(SplitError, match="not found"):
        split_config(str(tmp_path / "missing.yaml"), str(tmp_path / "out"))


def test_split_missing_key_raises(config_file, tmp_path):
    with pytest.raises(SplitError, match="Keys not found"):
        split_config(str(config_file), str(tmp_path / "out"), keys=["nonexistent"])


def test_split_file_content_correct(config_file, tmp_path):
    out = tmp_path / "out"
    split_config(str(config_file), str(out), keys=["database"])
    from confpatch.loaders import load_config
    data = load_config(str(out / "database.yaml"))
    assert data == {"database": {"host": "localhost", "port": 5432}}


def test_split_result_summary_dry_run(config_file, tmp_path):
    out = tmp_path / "out"
    result = split_config(str(config_file), str(out), keys=["app"], dry_run=True)
    assert "dry run" in result.summary()
    assert "app" in result.summary()


def test_split_result_summary_no_keys():
    result = SplitResult()
    assert result.summary() == "No keys to split."


def test_split_non_dict_config(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("- item1\n- item2\n")
    with pytest.raises(SplitError, match="mapping"):
        split_config(str(p), str(tmp_path / "out"))


def test_split_creates_output_dir_if_missing(config_file, tmp_path):
    out = tmp_path / "deep" / "nested" / "out"
    assert not out.exists()
    split_config(str(config_file), str(out), keys=["logging"])
    assert out.exists()
