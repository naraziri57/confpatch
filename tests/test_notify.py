"""Tests for confpatch.notify."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from confpatch.notify import NotifyEvent, NotifyError, dispatch, notify_file, notify_stdout


@pytest.fixture
def event():
    return NotifyEvent(
        config_file="config.yaml",
        patch_file="patch.yaml",
        changed_keys=["database.host", "app.debug"],
        success=True,
        message="",
    )


def test_notify_event_to_dict(event):
    d = event.to_dict()
    assert d["config_file"] == "config.yaml"
    assert d["patch_file"] == "patch.yaml"
    assert d["changed_keys"] == ["database.host", "app.debug"]
    assert d["success"] is True
    assert "timestamp" in d


def test_notify_stdout_prints(event, capsys):
    notify_stdout(event)
    out = capsys.readouterr().out
    assert "OK" in out
    assert "config.yaml" in out
    assert "database.host" in out


def test_notify_stdout_failed(event, capsys):
    event.success = False
    event.message = "something went wrong"
    notify_stdout(event)
    out = capsys.readouterr().out
    assert "FAILED" in out
    assert "something went wrong" in out


def test_notify_file_creates_log(tmp_path, event):
    log = tmp_path / "notify.log"
    notify_file(event, log)
    assert log.exists()
    lines = log.read_text().strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["config_file"] == "config.yaml"


def test_notify_file_appends(tmp_path, event):
    log = tmp_path / "notify.log"
    notify_file(event, log)
    notify_file(event, log)
    lines = log.read_text().strip().splitlines()
    assert len(lines) == 2


def test_notify_file_creates_parent_dirs(tmp_path, event):
    log = tmp_path / "deep" / "nested" / "notify.log"
    notify_file(event, log)
    assert log.exists()


def test_dispatch_stdout(event, capsys):
    dispatch(event, stdout=True)
    out = capsys.readouterr().out
    assert "confpatch" in out


def test_dispatch_log(tmp_path, event):
    log = tmp_path / "out.log"
    dispatch(event, log_path=log)
    assert log.exists()


def test_dispatch_callback(event):
    received = []
    dispatch(event, callback=lambda e: received.append(e))
    assert len(received) == 1
    assert received[0] is event


def test_dispatch_callback_raises_notify_error(event):
    def bad_cb(e):
        raise RuntimeError("boom")

    with pytest.raises(NotifyError, match="boom"):
        dispatch(event, callback=bad_cb)


def test_dispatch_no_channels(event):
    # Should not raise even with no channels configured
    dispatch(event)
