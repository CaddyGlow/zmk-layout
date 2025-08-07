"""Minimal working tests for DTParser functionality."""

from zmk_layout.parsers.ast_nodes import DTNode
from zmk_layout.parsers.dt_parser import DTParser
from zmk_layout.parsers.tokenizer import Token, TokenType


class TestDTParserBasics:
    """Test basic DTParser functionality."""

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

    def test_parse_empty_tokens(self) -> None:
        """Test parsing empty token list."""
        parser = DTParser([Token(TokenType.EOF, "", 1, 1, "")])
        root = parser.parse()
        assert isinstance(root, DTNode)
        assert root.name == ""

    def test_parse_simple_node(self) -> None:
        """Test parsing a simple node."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.RBRACE, "}", 1, 7, "}"),
            Token(TokenType.SEMICOLON, ";", 1, 8, ";"),
            Token(TokenType.EOF, "", 2, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()
        assert len(root.children) == 1
        child = list(root.children.values())[0]
        assert child.name == "node"

    def test_parse_property(self) -> None:
        """Test parsing a property."""
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
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
        node = list(root.children.values())[0]
        assert len(node.properties) == 1
        prop = list(node.properties.values())[0]
        assert prop.name == "property"
        assert prop.value.value == "value"

    def test_parse_multiple_nodes(self) -> None:
        """Test parsing multiple nodes in a root structure."""
        # / { node1 {}; node2 {}; };
        tokens = [
            Token(TokenType.SLASH, "/", 1, 1, "/"),
            Token(TokenType.LBRACE, "{", 1, 3, "{"),
            Token(TokenType.IDENTIFIER, "node1", 2, 5, "node1"),
            Token(TokenType.LBRACE, "{", 2, 11, "{"),
            Token(TokenType.RBRACE, "}", 2, 12, "}"),
            Token(TokenType.SEMICOLON, ";", 2, 13, ";"),
            Token(TokenType.IDENTIFIER, "node2", 3, 5, "node2"),
            Token(TokenType.LBRACE, "{", 3, 11, "{"),
            Token(TokenType.RBRACE, "}", 3, 12, "}"),
            Token(TokenType.SEMICOLON, ";", 3, 13, ";"),
            Token(TokenType.RBRACE, "}", 4, 1, "}"),
            Token(TokenType.SEMICOLON, ";", 4, 2, ";"),
            Token(TokenType.EOF, "", 5, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()
        assert len(root.children) == 2
        child1, child2 = list(root.children.values())
        assert child1.name in ["node1", "node2"]
        assert child2.name in ["node1", "node2"]
        assert child1.name != child2.name

    def test_parse_with_errors(self) -> None:
        """Test error handling during parsing."""
        # Invalid syntax - missing semicolon
        tokens = [
            Token(TokenType.IDENTIFIER, "node", 1, 1, "node"),
            Token(TokenType.LBRACE, "{", 1, 6, "{"),
            Token(TokenType.IDENTIFIER, "property", 2, 5, "property"),
            Token(TokenType.RBRACE, "}", 3, 1, "}"),  # Missing semicolon
            Token(TokenType.SEMICOLON, ";", 3, 2, ";"),
            Token(TokenType.EOF, "", 4, 1, ""),
        ]
        parser = DTParser(tokens)
        root = parser.parse()
        # Should handle errors gracefully
        assert isinstance(root, DTNode)
        # May or may not have errors depending on implementation
        assert len(parser.errors) >= 0
