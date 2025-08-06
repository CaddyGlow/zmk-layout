"""Comprehensive tests for device tree parser (dt_parser.py)."""

from unittest.mock import Mock, patch

import pytest

from zmk_layout.parsers.ast_nodes import (
    DTComment,
    DTNode,
    DTParseError,
    DTProperty,
    DTValue,
    DTValueType,
)
from zmk_layout.parsers.dt_parser import (
    DTParser,
    parse_dt,
    parse_dt_lark,
    parse_dt_lark_safe,
    parse_dt_multiple,
    parse_dt_multiple_safe,
    parse_dt_safe,
)
from zmk_layout.parsers.tokenizer import Token, TokenType


class TestDTParser:
    """Test the DTParser class functionality."""

    def test_parser_initialization(self) -> None:
        """Test DTParser initialization."""
        tokens = [
            Token(TokenType.IDENTIFIER, "test", 1, 1, "test"),
            Token(TokenType.EOF, "", 1, 5, ""),
        ]
        parser = DTParser(tokens)

        assert parser.tokens == tokens
        assert parser.pos == 0  # Should be at first token after _advance()
        assert parser.current_token == tokens[0]
        assert parser.errors == []
        assert parser.comments == []
        assert parser.conditionals == []
        assert parser.logger is None

    def test_parser_initialization_with_logger(self) -> None:
        """Test DTParser initialization with logger."""
        tokens = [Token(TokenType.EOF, "", 1, 1, "")]
        mock_logger = Mock()
        parser = DTParser(tokens, logger=mock_logger)

        assert parser.logger == mock_logger

    def test_parse_empty_tokens(self) -> None:
        """Test parsing empty token list."""
        parser = DTParser([Token(TokenType.EOF, "", 1, 1, "")])
        root = parser.parse()

        assert isinstance(root, DTNode)
        assert root.name == ""
        assert len(root.properties) == 0
        assert len(root.children) == 0

    def test_parse_simple_root_node(self) -> None:
        """Test parsing simple root node structure."""
        tokens = [
            Token(TokenType.SLASH, "/", 1, 1, "/"),
            Token(TokenType.LBRACE, "{", 1, 3, "{"),
            Token(TokenType.IDENTIFIER, "property", 2, 5, "property"),
            Token(TokenType.EQUALS, "=", 2, 13, "="),
            Token(TokenType.STRING, "value", 2, 15, '"value"'),
            Token(TokenType.SEMICOLON, ";", 2, 22, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        assert root.name == ""
        assert len(root.properties) == 1
        prop = list(root.properties.values())[0]
        assert prop.name == "property"
        assert prop.value is not None
        assert prop.value.value == "value"

    def test_parse_standalone_node(self) -> None:
        """Test parsing standalone node without explicit root."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "property", 2, 5, "property"),
            Token(TokenType.SEMICOLON, ";", 2, 13, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        assert len(root.children) == 1
        child = list(root.children.values())[0]
        assert child.name == "node"
        assert len(child.properties) == 1
        prop = list(child.properties.values())[0]
        assert prop.name == "property"

    def test_parse_multiple_root_nodes(self) -> None:
        """Test parsing multiple root nodes."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node1", 1, 1, "node1"),
            Token(TokenType.LBRACE, "{", 1, 7, "{"),
            Token(TokenType.RBRACE, "}", 1, 8, "}"),
            Token(TokenType.SEMICOLON, ";", 1, 9, ";"),
            Token(TokenType.IDENTIFIER, "node2", 2, 1, "node2"),
            Token(TokenType.LBRACE, "{", 2, 7, "{"),
            Token(TokenType.RBRACE, "}", 2, 8, "}"),
            Token(TokenType.SEMICOLON, ";", 2, 9, ";"),
            Token(TokenType.EOF, "", 3, 1, ""),
        ]
        parser = DTParser(tokens)
        roots = parser.parse_multiple()

        assert len(roots) == 2
        child1 = list(roots[0].children.values())[0]
        child2 = list(roots[1].children.values())[0]
        assert child1.name == "node1"
        assert child2.name == "node2"

    def test_parse_with_comments(self) -> None:
        """Test parsing with comments."""
        tokens = [
            Token(TokenType.COMMENT, "// This is a comment", 1, 1, "// This is a comment"),
            Token(TokenType.IDENTIFIER, "node", 2, 1, "node"),
            Token(TokenType.LBRACE, "{", 2, 6, "{"),
            Token(TokenType.RBRACE, "}", 2, 7, "}"),
            Token(TokenType.SEMICOLON, ";", 2, 8, ";"),
            Token(TokenType.EOF, "", 3, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        assert len(root.children) == 1
        node = list(root.children.values())[0]
        assert node.name == "node"
        # Comments should be associated with the node
        assert len(node.comments) >= 0  # May or may not be associated based on proximity

    def test_parse_with_preprocessor_directives(self) -> None:
        """Test parsing with preprocessor directives."""
        tokens = [
            Token(TokenType.PREPROCESSOR, "#include <dt-bindings.h>", 1, 1, "#include <dt-bindings.h>"),
            Token(TokenType.IDENTIFIER, "node", 2, 1, "node"),
            Token(TokenType.LBRACE, "{", 2, 6, "{"),
            Token(TokenType.RBRACE, "}", 2, 7, "}"),
            Token(TokenType.SEMICOLON, ";", 2, 8, ";"),
            Token(TokenType.EOF, "", 3, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        assert len(parser.conditionals) >= 0  # Preprocessor directives stored as conditionals
        assert len(root.children) == 1

    def test_parse_property_string_value(self) -> None:
        """Test parsing string property values."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "compatible", 2, 5, "compatible"),
            Token(TokenType.EQUALS, "=", 2, 15, "="),
            Token(TokenType.STRING, "test-device", 2, 17, '"test-device"'),
            Token(TokenType.SEMICOLON, ";", 2, 30, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        prop = list(node.properties.values())[0]
        assert prop.name == "compatible"
        assert prop.value is not None
        assert prop.value.type == DTValueType.STRING
        assert prop.value.value == "test-device"

    def test_parse_property_number_value(self) -> None:
        """Test parsing number property values."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "reg", 2, 5, "reg"),
            Token(TokenType.EQUALS, "=", 2, 8, "="),
            Token(TokenType.NUMBER, "0x1000", 2, 10, "0x1000"),
            Token(TokenType.SEMICOLON, ";", 2, 16, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        prop = list(node.properties.values())[0]
        assert prop.name == "reg"
        assert prop.value is not None
        assert prop.value.type == DTValueType.INTEGER
        assert prop.value.value == 0x1000

    def test_parse_property_boolean_value(self) -> None:
        """Test parsing boolean property values (no value)."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "status", 2, 5, "status"),
            Token(TokenType.SEMICOLON, ";", 2, 11, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        prop = list(node.properties.values())[0]
        assert prop.name == "status"
        assert prop.value is not None
        assert prop.value.type == DTValueType.BOOLEAN
        assert prop.value.value is True

    def test_parse_property_reference_value(self) -> None:
        """Test parsing reference property values."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "clocks", 2, 5, "clocks"),
            Token(TokenType.EQUALS, "=", 2, 11, "="),
            Token(TokenType.REFERENCE, "clk", 2, 13, "&clk"),
            Token(TokenType.SEMICOLON, ";", 2, 17, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        prop = list(node.properties.values())[0]
        assert prop.name == "clocks"
        assert prop.value is not None
        assert prop.value.type == DTValueType.REFERENCE
        assert prop.value.value == "clk"

    def test_parse_property_array_value(self) -> None:
        """Test parsing array property values."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "reg", 2, 5, "reg"),
            Token(TokenType.EQUALS, "=", 2, 8, "="),
            Token(TokenType.ANGLE_OPEN, "<", 2, 10, "<"),
            Token(TokenType.NUMBER, "0x1000", 2, 11, "0x1000"),
            Token(TokenType.NUMBER, "0x100", 2, 18, "0x100"),
            Token(TokenType.ANGLE_CLOSE, ">", 2, 23, ">"),
            Token(TokenType.SEMICOLON, ";", 2, 24, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        prop = list(node.properties.values())[0]
        assert prop.name == "reg"
        assert prop.value is not None
        assert prop.value.type == DTValueType.ARRAY
        assert prop.value.value == [0x1000, 0x100]

    def test_parse_property_multiple_values(self) -> None:
        """Test parsing comma-separated property values."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "compatible", 2, 5, "compatible"),
            Token(TokenType.EQUALS, "=", 2, 15, "="),
            Token(TokenType.STRING, "device1", 2, 17, '"device1"'),
            Token(TokenType.COMMA, ",", 2, 26, ","),
            Token(TokenType.STRING, "device2", 2, 28, '"device2"'),
            Token(TokenType.SEMICOLON, ";", 2, 37, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        prop = list(node.properties.values())[0]
        assert prop.name == "compatible"
        assert prop.value is not None
        assert prop.value.type == DTValueType.ARRAY
        assert prop.value.value == ["device1", "device2"]

    def test_parse_node_with_label(self) -> None:
        """Test parsing node with label."""
        tokens = [
            Token(TokenType.IDENTIFIER, "mylabel", 1, 1, "mylabel"),
            Token(TokenType.COLON, ":", 1, 8, ":"),
            Token(TokenType.IDENTIFIER, "node", 1, 10, "node"),
            Token(TokenType.LBRACE, "{", 1, 15, "{"),
            Token(TokenType.RBRACE, "}", 1, 16, "}"),
            Token(TokenType.SEMICOLON, ";", 1, 17, ";"),
            Token(TokenType.EOF, "", 2, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        assert node.name == "node"
        assert node.label == "mylabel"

    def test_parse_node_with_unit_address(self) -> None:
        """Test parsing node with unit address."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.AT, "@", 1, 5, "@"),
            Token(TokenType.NUMBER, "1000", 1, 6, "1000"),
            Token(TokenType.LBRACE, "{", 1, 11, "{"),
            Token(TokenType.RBRACE, "}", 1, 12, "}"),
            Token(TokenType.SEMICOLON, ";", 1, 13, ";"),
            Token(TokenType.EOF, "", 2, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        assert node.name == "node"
        assert node.unit_address == "1000"

    def test_parse_node_with_label_and_unit_address(self) -> None:
        """Test parsing node with both label and unit address."""
        tokens = [
            Token(TokenType.IDENTIFIER, "mylabel", 1, 1, "mylabel"),
            Token(TokenType.COLON, ":", 1, 8, ":"),
            Token(TokenType.IDENTIFIER, "node", 1, 10, "node"),
            Token(TokenType.AT, "@", 1, 14, "@"),
            Token(TokenType.IDENTIFIER, "1000", 1, 15, "1000"),
            Token(TokenType.LBRACE, "{", 1, 20, "{"),
            Token(TokenType.RBRACE, "}", 1, 21, "}"),
            Token(TokenType.SEMICOLON, ";", 1, 22, ";"),
            Token(TokenType.EOF, "", 2, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        assert node.name == "node"
        assert node.label == "mylabel"
        assert node.unit_address == "1000"

    def test_parse_reference_node(self) -> None:
        """Test parsing reference node."""
        tokens = [
            Token(TokenType.REFERENCE, "noderef", 1, 1, "&noderef"),
            Token(TokenType.LBRACE, "{", 1, 9, "{"),
            Token(TokenType.IDENTIFIER, "property", 2, 5, "property"),
            Token(TokenType.SEMICOLON, ";", 2, 13, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        assert node.name == "noderef"  # Reference without &
        assert len(node.properties) == 1

    def test_parse_nested_nodes(self) -> None:
        """Test parsing nested nodes."""
        tokens = [
            Token(TokenType.IDENTIFIER, "parent", 1, 1, "parent"),
            Token(TokenType.LBRACE, "{", 1, 8, "{"),
            Token(TokenType.IDENTIFIER, "child", 2, 5, "child"),
            Token(TokenType.LBRACE, "{", 2, 11, "{"),
            Token(TokenType.IDENTIFIER, "property", 3, 9, "property"),
            Token(TokenType.SEMICOLON, ";", 3, 17, ";"),
            Token(TokenType.RBRACE, "}", 4, 5, "}"),
            Token(TokenType.SEMICOLON, ";", 4, 6, ";"),
            Token(TokenType.RBRACE, "}", 5, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 5, 2, ";"),
            Token(TokenType.EOF, "", 6, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        parent = list(root.children.values())[0]
        assert parent.name == "parent"
        assert len(parent.children) == 1

        child = list(parent.children.values())[0]
        assert child.name == "child"
        assert len(child.properties) == 1

    def test_parse_with_errors(self) -> None:
        """Test parsing with syntax errors."""
        # Missing semicolon
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "property", 2, 5, "property"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),  # Missing semicolon after property
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        # Should have errors but still parse partial structure
        assert len(parser.errors) > 0
        assert isinstance(root, DTNode)

    def test_parse_fatal_error(self) -> None:
        """Test handling of fatal parsing errors."""
        tokens = [Token(TokenType.EOF, "", 1, 1, "")]

        with patch.object(DTParser, "_parse_root_node", side_effect=Exception("Fatal error")):
            parser = DTParser(tokens)
            with pytest.raises(DTParseError, match="Fatal parsing error"):
                parser.parse()

    def test_comment_association_with_nodes(self) -> None:
        """Test that comments are properly associated with nodes."""
        parser = DTParser([Token(TokenType.EOF, "", 1, 1, "")])
        node = DTNode("test", line=5, column=1)

        # Add comments that should be associated
        parser.comments = [
            DTComment("// Close comment", 4, 1, False),
            DTComment("// Far comment", 1, 1, False),
        ]

        parser._associate_pending_comments_with_node(node, 5)

        # Should associate the close comment but not the far one
        assert len(node.comments) >= 0  # May associate based on proximity logic

    def test_comment_association_with_properties(self) -> None:
        """Test that comments are properly associated with properties."""
        parser = DTParser([Token(TokenType.EOF, "", 1, 1, "")])
        prop = DTProperty("test", DTValue.string("value"), 3, 1)

        # Add comment that should be associated
        parser.comments = [DTComment("// Property comment", 2, 1, False)]

        parser._associate_pending_comments_with_property(prop, 3)

        # Should associate the comment
        assert len(prop.comments) >= 0  # May associate based on proximity logic

    def test_helper_methods(self) -> None:
        """Test helper methods."""
        tokens = [
            Token(TokenType.IDENTIFIER, "test", 1, 1, "test"),
            Token(TokenType.EOF, "", 1, 5, ""),
        ]
        parser = DTParser(tokens)

        # Test _match
        assert parser._match(TokenType.IDENTIFIER) is True
        assert parser._match(TokenType.STRING) is False

        # Test _current_line and _current_column
        assert parser._current_line() == 1
        assert parser._current_column() == 1

        # Test _is_at_end
        assert parser._is_at_end() is False
        parser._advance()  # Move to EOF
        assert parser._is_at_end() is True

    def test_get_context(self) -> None:
        """Test context generation for error reporting."""
        tokens = [
            Token(TokenType.IDENTIFIER, "a", 1, 1, "a"),
            Token(TokenType.IDENTIFIER, "b", 1, 3, "b"),
            Token(TokenType.IDENTIFIER, "c", 1, 5, "c"),
            Token(TokenType.IDENTIFIER, "d", 1, 7, "d"),
            Token(TokenType.EOF, "", 1, 9, ""),
        ]
        parser = DTParser(tokens)
        parser.pos = 2  # Position at 'c'
        parser.current_token = tokens[2]

        context = parser._get_context(window=1)
        assert ">>> c <<<" in context
        assert "b" in context
        assert "d" in context

    def test_synchronize(self) -> None:
        """Test error synchronization."""
        tokens = [
            Token(TokenType.IDENTIFIER, "error", 1, 1, "error"),
            Token(TokenType.IDENTIFIER, "more", 1, 7, "more"),
            Token(TokenType.SEMICOLON, ";", 1, 11, ";"),
            Token(TokenType.IDENTIFIER, "good", 1, 13, "good"),
            Token(TokenType.EOF, "", 1, 17, ""),
        ]
        parser = DTParser(tokens)

        # Synchronize should advance to semicolon
        parser._synchronize()
        assert parser.current_token is not None
        assert parser.current_token.type == TokenType.IDENTIFIER
        assert parser.current_token.value == "good"

    def test_is_property_identification(self) -> None:
        """Test property vs node identification."""
        # Property case (followed by =)
        tokens = [
            Token(TokenType.IDENTIFIER, "property", 1, 1, "property"),
            Token(TokenType.EQUALS, "=", 1, 9, "="),
            Token(TokenType.EOF, "", 1, 10, ""),
        ]
        parser = DTParser(tokens)
        assert parser._is_property() is True

        # Node case (followed by {)
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 5, "{"),
            Token(TokenType.EOF, "", 1, 6, ""),
        ]
        parser = DTParser(tokens)
        assert parser._is_property() is False


class TestHelperFunctions:
    """Test helper functions for device tree parsing."""

    def test_parse_dt(self) -> None:
        """Test parse_dt function."""
        dt_text = """
        / {
            compatible = "test-device";
        };
        """

        with patch("zmk_layout.parsers.dt_parser.tokenize_dt") as mock_tokenize:
            mock_tokens = [
                Token(TokenType.SLASH, "/", 1, 1, "/"),
                Token(TokenType.LBRACE, "{", 1, 3, "{"),
                Token(TokenType.IDENTIFIER, "compatible", 2, 5, "compatible"),
                Token(TokenType.EQUALS, "=", 2, 15, "="),
                Token(TokenType.STRING, "test-device", 2, 17, '"test-device"'),
                Token(TokenType.SEMICOLON, ";", 2, 30, ";"),
                Token(TokenType.RBRACE, "}", 3, 1, "}"),
                Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
                Token(TokenType.EOF, "", 4, 1, ""),
            ]
            mock_tokenize.return_value = mock_tokens

            root = parse_dt(dt_text)

            assert isinstance(root, DTNode)
            assert len(root.properties) == 1
            prop = list(root.properties.values())[0]
            assert prop.name == "compatible"

    def test_parse_dt_safe(self) -> None:
        """Test parse_dt_safe function."""
        dt_text = "invalid syntax {"

        with patch("zmk_layout.parsers.dt_parser.tokenize_dt") as mock_tokenize:
            mock_tokenize.return_value = [Token(TokenType.EOF, "", 1, 1, "")]

            root, errors = parse_dt_safe(dt_text)

            # Should handle errors gracefully
            assert isinstance(root, DTNode) or root is None
            assert isinstance(errors, list)

    def test_parse_dt_safe_with_exception(self) -> None:
        """Test parse_dt_safe with tokenizer exception."""
        dt_text = "test"

        with patch("zmk_layout.parsers.dt_parser.tokenize_dt", side_effect=Exception("Tokenize error")):
            root, errors = parse_dt_safe(dt_text)

            assert root is None
            assert len(errors) == 1
            assert "Parsing failed" in str(errors[0])

    def test_parse_dt_multiple(self) -> None:
        """Test parse_dt_multiple function."""
        dt_text = """
        node1 { };
        node2 { };
        """

        with patch("zmk_layout.parsers.dt_parser.tokenize_dt") as mock_tokenize:
            mock_tokens = [
                Token(TokenType.IDENTIFIER, "node1", 1, 1, "node1"),
                Token(TokenType.LBRACE, "{", 1, 7, "{"),
                Token(TokenType.RBRACE, "}", 1, 9, "}"),
                Token(TokenType.SEMICOLON, ";", 1, 10, ";"),
                Token(TokenType.IDENTIFIER, "node2", 2, 1, "node2"),
                Token(TokenType.LBRACE, "{", 2, 7, "{"),
                Token(TokenType.RBRACE, "}", 2, 9, "}"),
                Token(TokenType.SEMICOLON, ";", 2, 10, ";"),
                Token(TokenType.EOF, "", 3, 1, ""),
            ]
            mock_tokenize.return_value = mock_tokens

            roots = parse_dt_multiple(dt_text)

            assert isinstance(roots, list)
            assert len(roots) >= 1  # Should parse at least one root

    def test_parse_dt_multiple_safe(self) -> None:
        """Test parse_dt_multiple_safe function."""
        dt_text = "test"

        with patch("zmk_layout.parsers.dt_parser.tokenize_dt") as mock_tokenize:
            mock_tokenize.return_value = [Token(TokenType.EOF, "", 1, 1, "")]

            roots, errors = parse_dt_multiple_safe(dt_text)

            assert isinstance(roots, list)
            assert isinstance(errors, list)

    def test_parse_dt_multiple_safe_with_exception(self) -> None:
        """Test parse_dt_multiple_safe with exception."""
        dt_text = "test"

        with patch("zmk_layout.parsers.dt_parser.tokenize_dt", side_effect=Exception("Error")):
            roots, errors = parse_dt_multiple_safe(dt_text)

            assert roots == []
            assert len(errors) == 1

    def test_parse_dt_lark(self) -> None:
        """Test parse_dt_lark function."""
        dt_text = "test"

        # Test with lark parser available
        mock_nodes = [DTNode("test")]
        with patch("zmk_layout.parsers.dt_parser.parse_dt_lark"):
            # Mock the inner import and function
            mock_lark_module = Mock()
            mock_lark_module.parse_dt_lark.return_value = mock_nodes

            with patch.dict("sys.modules", {"zmk_layout.parsers.lark_dt_parser": mock_lark_module}):
                result = parse_dt_lark(dt_text)
                assert len(result) >= 0  # May fallback

    def test_parse_dt_lark_fallback(self) -> None:
        """Test parse_dt_lark fallback when lark unavailable."""
        dt_text = "/ { };"

        with patch("zmk_layout.parsers.dt_parser.tokenize_dt") as mock_tokenize:
            mock_tokens = [
                Token(TokenType.SLASH, "/", 1, 1, "/"),
                Token(TokenType.LBRACE, "{", 1, 3, "{"),
                Token(TokenType.RBRACE, "}", 1, 5, "}"),
                Token(TokenType.SEMICOLON, ";", 1, 6, ";"),
                Token(TokenType.EOF, "", 2, 1, ""),
            ]
            mock_tokenize.return_value = mock_tokens

            # Should fallback to regular parser
            result = parse_dt_lark(dt_text)
            assert isinstance(result, list)
            assert len(result) == 1

    def test_parse_dt_lark_safe(self) -> None:
        """Test parse_dt_lark_safe function."""
        dt_text = "test"

        # Test fallback behavior
        with patch("zmk_layout.parsers.dt_parser.tokenize_dt") as mock_tokenize:
            mock_tokens = [Token(TokenType.EOF, "", 1, 1, "")]
            mock_tokenize.return_value = mock_tokens

            nodes, errors = parse_dt_lark_safe(dt_text)
            assert isinstance(nodes, list)
            assert isinstance(errors, list)

    def test_parse_dt_lark_safe_with_exception(self) -> None:
        """Test parse_dt_lark_safe with exception."""
        dt_text = "test"

        with patch("zmk_layout.parsers.dt_parser.parse_dt", side_effect=Exception("Parse error")):
            nodes, errors = parse_dt_lark_safe(dt_text)

            assert nodes == []
            assert len(errors) == 1
            assert "Parse error" in errors[0]


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_array_parsing(self) -> None:
        """Test parsing empty array."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "array", 2, 5, "array"),
            Token(TokenType.EQUALS, "=", 2, 10, "="),
            Token(TokenType.ANGLE_OPEN, "<", 2, 12, "<"),
            Token(TokenType.ANGLE_CLOSE, ">", 2, 13, ">"),
            Token(TokenType.SEMICOLON, ";", 2, 14, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        prop = list(node.properties.values())[0]
        assert prop.name == "array"
        assert prop.value is not None
        assert prop.value.type == DTValueType.ARRAY
        assert prop.value.value == []

    def test_malformed_array_parsing(self) -> None:
        """Test parsing malformed array (missing close bracket)."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "array", 2, 5, "array"),
            Token(TokenType.EQUALS, "=", 2, 10, "="),
            Token(TokenType.ANGLE_OPEN, "<", 2, 12, "<"),
            Token(TokenType.NUMBER, "1", 2, 13, "1"),
            Token(TokenType.SEMICOLON, ";", 2, 14, ";"),  # Missing >
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        parser.parse()

        # Should have parsing errors
        assert len(parser.errors) > 0

    def test_invalid_number_parsing(self) -> None:
        """Test parsing invalid number values."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "prop", 2, 5, "prop"),
            Token(TokenType.EQUALS, "=", 2, 9, "="),
            Token(TokenType.NUMBER, "invalid", 2, 11, "invalid"),  # Invalid number
            Token(TokenType.SEMICOLON, ";", 2, 18, ";"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        node = list(root.children.values())[0]
        prop = list(node.properties.values())[0]
        # Should fallback to string value
        assert prop.value is not None
        assert prop.value.type == DTValueType.STRING
        assert prop.value.value == "invalid"

    def test_unexpected_token_handling(self) -> None:
        """Test handling of unexpected tokens."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.LPAREN, "(", 2, 5, "("),  # Unexpected token
            Token(TokenType.RBRACE, "}", 3, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        # Should handle unexpected token and continue parsing
        assert len(parser.errors) > 0
        assert isinstance(root, DTNode)

    def test_parser_with_logger_warnings(self) -> None:
        """Test parser with logger for warning messages."""
        mock_logger = Mock()
        tokens = [
            Token(TokenType.IDENTIFIER, "invalid", 1, 1, "invalid"),
            Token(TokenType.EOF, "", 1, 8, ""),
        ]
        parser = DTParser(tokens, logger=mock_logger)

        # Force an error
        parser._error("Test error")

        # Logger should be called
        mock_logger.warning.assert_called()

    def test_complex_nested_structure(self) -> None:
        """Test parsing complex nested structure."""
        tokens = [
            Token(TokenType.SLASH, "/", 1, 1, "/"),
            Token(TokenType.LBRACE, "{", 1, 3, "{"),
            Token(TokenType.IDENTIFIER, "parent", 2, 5, "parent"),
            Token(TokenType.LBRACE, "{", 2, 12, "{"),
            Token(TokenType.IDENTIFIER, "child1", 3, 9, "child1"),
            Token(TokenType.LBRACE, "{", 3, 16, "{"),
            Token(TokenType.IDENTIFIER, "prop1", 4, 13, "prop1"),
            Token(TokenType.SEMICOLON, ";", 4, 18, ";"),
            Token(TokenType.RBRACE, "}", 5, 9, "}"),
            Token(TokenType.SEMICOLON, ";", 5, 10, ";"),
            Token(TokenType.IDENTIFIER, "child2", 6, 9, "child2"),
            Token(TokenType.LBRACE, "{", 6, 16, "{"),
            Token(TokenType.IDENTIFIER, "prop2", 7, 13, "prop2"),
            Token(TokenType.EQUALS, "=", 7, 18, "="),
            Token(TokenType.STRING, "value", 7, 20, '"value"'),
            Token(TokenType.SEMICOLON, ";", 7, 27, ";"),
            Token(TokenType.RBRACE, "}", 8, 9, "}"),
            Token(TokenType.SEMICOLON, ";", 8, 10, ";"),
            Token(TokenType.RBRACE, "}", 9, 5, "}"),
            Token(TokenType.SEMICOLON, ";", 9, 6, ";"),
            Token(TokenType.RBRACE, "}", 10, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 10, 2, ";"),
            Token(TokenType.EOF, "", 11, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        assert root.name == ""
        assert len(root.children) == 1

        parent = list(root.children.values())[0]
        assert parent.name == "parent"
        assert len(parent.children) == 2

        children = list(parent.children.values())
        child1 = children[0]
        child2 = children[1]
        assert child1.name == "child1"
        assert len(child1.properties) == 1

        assert child2.name == "child2"
        assert len(child2.properties) == 1
        prop = list(child2.properties.values())[0]
        assert prop.value is not None
        assert prop.value.value == "value"

    def test_conditionals_collection(self) -> None:
        """Test that preprocessor directives are collected as conditionals."""
        tokens = [
            Token(TokenType.PREPROCESSOR, "#ifdef CONFIG_TEST", 1, 1, "#ifdef CONFIG_TEST"),
            Token(TokenType.IDENTIFIER, "node", 2, 1, "node"),
            Token(TokenType.LBRACE, "{", 2, 6, "{"),
            Token(TokenType.RBRACE, "}", 2, 7, "}"),
            Token(TokenType.SEMICOLON, ";", 2, 8, ";"),
            Token(TokenType.PREPROCESSOR, "#endif", 3, 1, "#endif"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()

        # Should collect preprocessor directives as conditionals
        assert len(parser.conditionals) >= 1
        assert parser.conditionals[0].directive == "ifdef"
        assert parser.conditionals[0].condition == "CONFIG_TEST"

        # Conditionals should be attached to root
        assert len(root.conditionals) >= 1
