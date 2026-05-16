"""Tests for confpatch.indent module."""

import pytest
from confpatch.indent import IndentError, IndentResult, normalize_indent


def test_normalize_indent_no_multiline_strings():
    config = {"key": "simple", "num": 42}
    result = normalize_indent(config)
    assert isinstance(result, IndentResult)
    assert not result.has_changes()
    assert result.count() == 0
    assert result.normalized == config


def test_normalize_indent_single_multiline_string():
    config = {"msg": "line1\n    line2\n    line3"}
    result = normalize_indent(config, indent=2)
    assert result.has_changes()
    assert "msg" in result.changes
    lines = result.normalized["msg"].splitlines()
    assert lines[1] == "  line2"
    assert lines[2] == "  line3"


def test_normalize_indent_no_change_when_already_correct():
    config = {"msg": "line1\n  line2"}
    result = normalize_indent(config, indent=2)
    assert not result.has_changes()


def test_normalize_indent_nested_dict():
    config = {"outer": {"inner": "a\n        b"}}
    result = normalize_indent(config, indent=4)
    assert result.has_changes()
    assert "outer.inner" in result.changes
    lines = result.normalized["outer"]["inner"].splitlines()
    assert lines[1] == "    b"


def test_normalize_indent_list_of_strings():
    config = {"items": ["x\n    y", "plain"]}
    result = normalize_indent(config, indent=2)
    assert result.has_changes()
    assert "items[0]" in result.changes
    assert "items[1]" not in result.changes


def test_normalize_indent_use_tabs():
    config = {"msg": "line1\n    line2"}
    result = normalize_indent(config, use_tabs=True)
    assert result.normalized["msg"] == "line1\n\tline2"


def test_normalize_indent_does_not_mutate_original():
    config = {"msg": "a\n    b"}
    original_value = config["msg"]
    normalize_indent(config, indent=2)
    assert config["msg"] == original_value


def test_normalize_indent_not_a_dict_raises():
    with pytest.raises(IndentError, match="Expected a dict"):
        normalize_indent(["not", "a", "dict"])  # type: ignore


def test_normalize_indent_invalid_indent_raises():
    with pytest.raises(IndentError, match="indent must be >= 1"):
        normalize_indent({"k": "v"}, indent=0)


def test_normalize_indent_summary_with_changes():
    config = {"msg": "a\n    b"}
    result = normalize_indent(config, indent=2)
    assert "1" in result.summary()


def test_normalize_indent_summary_no_changes():
    config = {"key": "no newlines here"}
    result = normalize_indent(config)
    assert result.summary() == "No indentation changes."


def test_normalize_indent_single_line_string_unchanged():
    config = {"greeting": "hello world"}
    result = normalize_indent(config)
    assert result.normalized["greeting"] == "hello world"
    assert not result.has_changes()
