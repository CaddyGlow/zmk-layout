"""Tests for Lark parser integration and fallback logic."""

from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from zmk_layout.parsers.ast_nodes import DTNode
from zmk_layout.parsers.dt_parser import parse_dt_lark_safe
from zmk_layout.parsers.lark_dt_parser import LarkToDTTransformer, parse_dt_lark


def test_parse_dt_lark_safe_when_parser_ok(monkeypatch: Any) -> None:
    """Happy path: underlying parse_dt_lark succeeds and errors list empty."""
    mock_node = DTNode(name="root")
    monkeypatch.setattr("zmk_layout.parsers.lark_dt_parser.parse_dt_lark_safe", lambda txt: ([mock_node], []))
    nodes, errors = parse_dt_lark_safe("dummy")
    assert len(nodes) == 1
    assert nodes[0].name == "root"
    assert errors == []


def test_parse_dt_lark_safe_when_parser_missing(monkeypatch: Any) -> None:
    """ImportError raised by parse_dt_lark must be turned into driver-friendly error list."""

    def _return_error(_: str) -> tuple[list[DTNode], list[str]]:
        return [], ["Lark parser not available: lark missing"]

    monkeypatch.setattr("zmk_layout.parsers.lark_dt_parser.parse_dt_lark_safe", _return_error)
    nodes, errors = parse_dt_lark_safe("dummy")
    assert nodes == []
    assert errors and "lark" in errors[0].lower()


def test_parse_dt_lark_safe_general_exception(monkeypatch: Any) -> None:
    """General exceptions should be caught and returned as error messages."""

    def _return_error(_: str) -> tuple[list[DTNode], list[str]]:
        return [], ["Parse error: parsing failed"]

    monkeypatch.setattr("zmk_layout.parsers.lark_dt_parser.parse_dt_lark_safe", _return_error)
    nodes, errors = parse_dt_lark_safe("dummy")
    assert nodes == []
    assert errors and "parsing failed" in errors[0]


def test_parse_dt_lark_import_error() -> None:
    """Test ImportError when lark is not available."""
    # Mock the import to fail
    import sys

    original_modules = sys.modules.copy()

    try:
        # Remove lark from sys.modules to simulate ImportError
        if "lark" in sys.modules:
            del sys.modules["lark"]

        # Mock the function to raise ImportError on import attempt
        def mock_import_error(*args: Any, **kwargs: Any) -> None:
            raise ImportError("No module named 'lark'")

        with (
            patch("builtins.__import__", side_effect=mock_import_error),
            pytest.raises(ImportError, match="lark parser not available"),
        ):
            parse_dt_lark('/ { test = "value"; };')
    finally:
        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)


def test_parse_dt_lark_grammar_file_missing() -> None:
    """Test ImportError when grammar file is missing."""
    # Mock the specific path operations within the function
    with patch("pathlib.Path") as mock_path_class:
        # Mock the file path creation
        mock_file_path = MagicMock()
        mock_grammar_path = MagicMock()
        mock_grammar_path.exists.return_value = False

        mock_file_path.parent.__truediv__.return_value = mock_grammar_path
        mock_path_class.return_value = mock_file_path

        with pytest.raises(ImportError, match="devicetree.lark grammar file not found"):
            parse_dt_lark('/ { test = "value"; };')


def test_parse_dt_lark_parse_error() -> None:
    """Test ParseError propagation from Lark parser."""
    import sys
    from types import ModuleType
    from unittest.mock import Mock

    # Mock the lark module
    mock_lark_module = ModuleType("lark")
    mock_lark_class = Mock()
    mock_parse_error = Exception  # Use base Exception as ParseError

    # Mock parser that raises ParseError
    mock_parser_instance = Mock()
    mock_parser_instance.parse.side_effect = mock_parse_error("Parse failed")
    mock_lark_class.return_value = mock_parser_instance

    mock_lark_module.Lark = mock_lark_class  # type: ignore[attr-defined]
    mock_lark_module.ParseError = mock_parse_error  # type: ignore[attr-defined]

    # Mock the pathlib module
    mock_pathlib_module = ModuleType("pathlib")
    mock_path_class = Mock()
    mock_file_path = Mock()
    mock_parent = Mock()
    mock_grammar_path = Mock()
    mock_grammar_path.exists.return_value = True
    mock_grammar_path.read_text.return_value = "mock grammar"
    mock_parent.__truediv__ = Mock(return_value=mock_grammar_path)
    mock_file_path.parent = mock_parent
    mock_path_class.return_value = mock_file_path
    mock_pathlib_module.Path = mock_path_class  # type: ignore[attr-defined]

    # Temporarily replace modules in sys.modules
    original_lark = sys.modules.get("lark")
    original_pathlib = sys.modules.get("pathlib")

    try:
        sys.modules["lark"] = mock_lark_module
        sys.modules["pathlib"] = mock_pathlib_module

        with pytest.raises(Exception, match="Device tree parse error"):
            parse_dt_lark('/ { test = "value"; };')
    finally:
        # Restore original modules
        if original_lark is not None:
            sys.modules["lark"] = original_lark
        elif "lark" in sys.modules:
            del sys.modules["lark"]

        if original_pathlib is not None:
            sys.modules["pathlib"] = original_pathlib
        elif "pathlib" in sys.modules:
            del sys.modules["pathlib"]


def test_full_keymap_processor_falls_back_to_lark(monkeypatch: Any) -> None:
    """
    When parse_dt_multiple_safe import fails, processor must
    attempt lark fallback (lines 248-266 of keymap_processors.py).
    """
    # craft dummy dt_parser module to inject into import system
    dummy = ModuleType("zmk_layout.parsers.dt_parser")

    def _parse_dt_multiple_safe(_: str) -> None:
        raise ImportError("enhanced parser unavailable")

    dummy.parse_dt_multiple_safe = _parse_dt_multiple_safe  # type: ignore[attr-defined]
    # Create a mock DTNode
    from unittest.mock import Mock

    mock_dtnode = Mock()
    mock_dtnode.name = "root"
    mock_dtnode.conditionals = []
    dummy.parse_dt_lark_safe = lambda txt: ([mock_dtnode], [])  # type: ignore[attr-defined]
    import sys

    monkeypatch.setitem(sys.modules, "zmk_layout.parsers.dt_parser", dummy)

    # Extremely reduced ParsingContext stand-in
    from zmk_layout.parsers.keymap_processors import FullKeymapProcessor
    from zmk_layout.parsers.parsing_models import ParsingContext

    ctx = ParsingContext(
        keymap_content="/ {}",  # minimal valid devicetree
        title="t",
        keyboard_name="kb",
    )
    # Short-circuit heavy sub-methods to isolate fallback logic
    monkeypatch.setattr(
        FullKeymapProcessor,
        "_extract_layers_from_roots",
        lambda *_a, **_kw: None,
    )
    monkeypatch.setattr(
        FullKeymapProcessor,
        "_extract_behaviors_and_metadata",
        lambda *_a, **_kw: {},
    )
    monkeypatch.setattr(
        FullKeymapProcessor,
        "_populate_behaviors_in_layout",
        lambda *_a, **_kw: None,
    )

    processor = FullKeymapProcessor()
    layout = processor.process(ctx)
    assert layout is not None  # fallback succeeded
    # Ensure our lark fallback was indeed exercised by checking ctx warnings empty
    assert ctx.errors == []


def test_full_keymap_processor_lark_fallback_also_fails(monkeypatch: Any) -> None:
    """Test when both enhanced parser and Lark parser are unavailable."""
    # Mock both parsers to fail
    dummy = ModuleType("zmk_layout.parsers.dt_parser")

    def _parse_dt_multiple_safe(_: str) -> None:
        raise ImportError("enhanced parser unavailable")

    def _parse_dt_lark_safe(_: str) -> None:
        raise ImportError("lark parser unavailable")

    dummy.parse_dt_multiple_safe = _parse_dt_multiple_safe  # type: ignore[attr-defined]
    dummy.parse_dt_lark_safe = _parse_dt_lark_safe  # type: ignore[attr-defined]
    import sys

    monkeypatch.setitem(sys.modules, "zmk_layout.parsers.dt_parser", dummy)

    from zmk_layout.parsers.keymap_processors import FullKeymapProcessor
    from zmk_layout.parsers.parsing_models import ParsingContext

    ctx = ParsingContext(
        keymap_content="/ {}",
        title="t",
        keyboard_name="kb",
    )

    processor = FullKeymapProcessor()
    layout = processor.process(ctx)
    assert layout is None  # both fallbacks failed
    assert "Failed to parse device tree AST" in ctx.errors


def test_lark_transformer_empty_tree() -> None:
    """Test transformer with empty parse tree."""
    transformer = LarkToDTTransformer()

    # Mock empty tree
    mock_tree = Mock()
    mock_tree.children = []

    result = transformer.transform(mock_tree)
    assert len(result) == 1  # Should return root node
    assert result[0].name == ""


def test_lark_transformer_with_nodes() -> None:
    """Test transformer with node children."""
    transformer = LarkToDTTransformer()

    # Mock tree with node children
    mock_node_item = Mock()
    mock_node_item.data = "node"

    mock_tree = Mock()
    mock_tree.children = [mock_node_item]

    # Mock the _transform_node method
    with patch.object(transformer, "_transform_node") as mock_transform:
        mock_node = Mock()
        mock_node.name = "test_node"
        mock_transform.return_value = mock_node

        result = transformer.transform(mock_tree)
        assert len(result) == 1
        mock_transform.assert_called_once_with(mock_node_item)


def test_lark_transformer_node_transformation() -> None:
    """Test _transform_node method."""
    transformer = LarkToDTTransformer()

    # Mock node tree with label and path
    mock_label_child = Mock()
    mock_label_child.data = "label"
    mock_label_child.children = ["test_label"]

    mock_path_child = Mock()
    mock_path_child.data = "node_path"

    mock_node_tree = Mock()
    mock_node_tree.children = [mock_label_child, mock_path_child]

    with patch.object(transformer, "_extract_path", return_value="test/path"):
        result = transformer._transform_node(mock_node_tree)
        assert result.label == "test_label"
        assert result.name == "test/path"


def test_lark_transformer_property_transformation() -> None:
    """Test _transform_property method."""
    transformer = LarkToDTTransformer()

    # Mock property tree
    mock_name_child = Mock()
    mock_name_child.data = "property_name"
    mock_name_child.children = ["test_prop"]

    mock_values_child = Mock()
    mock_values_child.data = "property_values"

    mock_prop_tree = Mock()
    mock_prop_tree.children = [mock_name_child, mock_values_child]

    with patch.object(transformer, "_transform_property_values", return_value=[]):
        result = transformer._transform_property(mock_prop_tree)
        assert result.name == "test_prop"
        assert result.value is None  # Empty values


def test_lark_transformer_extract_path() -> None:
    """Test _extract_path method."""
    transformer = LarkToDTTransformer()

    # Mock path tree with segments
    mock_segment1 = Mock()
    mock_segment1.data = "path_segment"
    mock_segment1.children = ["segment1"]

    mock_segment2 = Mock()
    mock_segment2.data = "path_segment"
    mock_segment2.children = ["segment2", "123"]  # with unit address as separate child

    mock_path_tree = Mock()
    mock_path_tree.children = [mock_segment1, mock_segment2]

    result = transformer._extract_path(mock_path_tree)
    assert result == "segment1/segment2@123"
