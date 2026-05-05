"""Tests for confpatch.report module."""

import pytest
from confpatch.report import ApplyReport


ORIGINAL = {"host": "localhost", "port": 5432, "debug": False}
PATCHED = {"host": "remotehost", "port": 5432, "debug": False, "timeout": 30}


def make_report(**kwargs) -> ApplyReport:
    defaults = dict(
        source_file="config.yaml",
        patch_file="patch.yaml",
        original=ORIGINAL,
        patched=PATCHED,
    )
    defaults.update(kwargs)
    return ApplyReport(**defaults)


def test_report_has_changes():
    r = make_report()
    assert r.has_changes is True


def test_report_change_count():
    r = make_report()
    assert r.change_count == 2  # host changed + timeout added


def test_report_no_changes():
    r = make_report(original=ORIGINAL, patched=ORIGINAL)
    assert r.has_changes is False
    assert r.change_count == 0


def test_report_summary_contains_filenames():
    r = make_report()
    summary = r.summary()
    assert "config.yaml" in summary
    assert "patch.yaml" in summary


def test_report_summary_contains_diff():
    r = make_report()
    summary = r.summary()
    assert "host" in summary
    assert "timeout" in summary


def test_report_summary_no_changes_text():
    r = make_report(original=ORIGINAL, patched=ORIGINAL)
    summary = r.summary()
    assert "(no changes)" in summary


def test_report_to_dict_keys():
    r = make_report()
    d = r.to_dict()
    assert set(d.keys()) == {"source_file", "patch_file", "change_count", "changes"}


def test_report_to_dict_values():
    r = make_report()
    d = r.to_dict()
    assert d["source_file"] == "config.yaml"
    assert d["change_count"] == r.change_count
    assert isinstance(d["changes"], list)


def test_report_summary_color_flag():
    r = make_report()
    colored = r.summary(color=True)
    plain = r.summary(color=False)
    # colored output should contain ANSI escape codes
    assert "\033[" in colored
    assert "\033[" not in plain
