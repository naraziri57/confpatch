"""Tests for confpatch.template module."""

import pytest
from confpatch.template import (
    render_value,
    render_patch,
    extract_variables,
    TemplateError,
)


def test_render_string_simple():
    result = render_value("hello {{ name }}", {"name": "world"})
    assert result == "hello world"


def test_render_string_multiple_vars():
    result = render_value("{{ greeting }}, {{ name }}!", {"greeting": "Hi", "name": "Alice"})
    assert result == "Hi, Alice!"


def test_render_string_missing_var_raises():
    with pytest.raises(TemplateError, match="Undefined template variable: 'missing'"):
        render_value("{{ missing }}", {})


def test_render_value_non_string_passthrough():
    assert render_value(42, {}) == 42
    assert render_value(3.14, {}) == 3.14
    assert render_value(None, {}) is None
    assert render_value(True, {}) is True


def test_render_value_nested_dict():
    patch = {"db": {"host": "{{ host }}", "port": 5432}}
    result = render_value(patch, {"host": "localhost"})
    assert result == {"db": {"host": "localhost", "port": 5432}}


def test_render_value_list():
    result = render_value(["{{ a }}", "{{ b }}", 99], {"a": "x", "b": "y"})
    assert result == ["x", "y", 99]


def test_render_patch_returns_new_dict():
    patch = {"key": "{{ val }}"}
    rendered = render_patch(patch, {"val": "hello"})
    assert rendered == {"key": "hello"}
    assert patch == {"key": "{{ val }}"}


def test_render_patch_invalid_input():
    with pytest.raises(TemplateError, match="Patch must be a dict"):
        render_patch("not a dict", {})


def test_extract_variables_empty():
    assert extract_variables({"key": "no vars here"}) == []


def test_extract_variables_single():
    assert extract_variables({"key": "{{ env }}"}) == ["env"]


def test_extract_variables_multiple_sorted():
    patch = {"a": "{{ z_var }}", "b": "{{ a_var }}", "c": "{{ m_var }}"}
    assert extract_variables(patch) == ["a_var", "m_var", "z_var"]


def test_extract_variables_deduplicates():
    patch = {"x": "{{ name }}", "y": "{{ name }} again"}
    assert extract_variables(patch) == ["name"]


def test_extract_variables_nested():
    patch = {"outer": {"inner": "{{ deep }}"}}
    assert extract_variables(patch) == ["deep"]


def test_render_value_whitespace_in_placeholder():
    result = render_value("{{  spaced  }}", {"spaced": "ok"})
    assert result == "ok"
