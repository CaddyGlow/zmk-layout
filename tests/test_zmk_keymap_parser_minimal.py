"""Minimal working tests for ZMK keymap parser functionality."""

from __future__ import annotations

from typing import Any

import pytest

from zmk_layout.models.metadata import LayoutData
from zmk_layout.parsers.ast_nodes import DTNode
from zmk_layout.parsers.zmk_keymap_parser import (
    KeymapParseResult,
    ParsingMethod,
    ParsingMode,
    ZMKKeymapParser,
    create_zmk_keymap_parser,
    create_zmk_keymap_parser_from_profile,
)


# Mock Classes for testing
class MockLogger:
    def __init__(self) -> None:
        self.debug_calls = []
        self.error_calls = []
        self.warning_calls = []

    def debug(self, message: str, **kwargs) -> None:
        self.debug_calls.append((message, dict(kwargs)))

    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        self.error_calls.append((message, dict(kwargs)))

    def warning(self, message: str, **kwargs) -> None:
        self.warning_calls.append((message, dict(kwargs)))

    def info(self, message: str, **kwargs) -> None:
        pass

    def exception(self, message: str, **kwargs) -> None:
        self.error_calls.append((message, dict(kwargs)))


class MockConfigurationProvider:
    def __init__(self, extraction_config: dict[str, Any] | None = None) -> None:
        self.extraction_config = extraction_config or {}

    def get_extraction_config(self, profile: Any = None) -> dict[str, Any]:
        return self.extraction_config


# Fixtures
@pytest.fixture
def mock_logger() -> MockLogger:
    return MockLogger()


@pytest.fixture
def mock_configuration_provider() -> MockConfigurationProvider:
    return MockConfigurationProvider()


@pytest.fixture
def sample_layout_data() -> LayoutData:
    return LayoutData(keyboard="test_keyboard", title="Test Layout", layers=[])


@pytest.fixture
def zmk_parser(
    mock_logger: MockLogger, mock_configuration_provider: MockConfigurationProvider
) -> ZMKKeymapParser:
    return ZMKKeymapParser(
        logger=mock_logger, configuration_provider=mock_configuration_provider
    )


class TestZMKKeymapParserBasics:
    """Test basic ZMKKeymapParser functionality."""

    def test_parser_initialization(self) -> None:
        """Test that parser initializes correctly."""
        parser = ZMKKeymapParser()
        assert isinstance(parser, ZMKKeymapParser)
        assert hasattr(parser, "defines")
        assert isinstance(parser.defines, dict)
        assert len(parser.defines) == 0

    def test_parser_defines_property(self) -> None:
        """Test that defines property works."""
        parser = ZMKKeymapParser()
        assert parser.defines == {}
        parser.defines["test"] = "value"
        assert parser.defines["test"] == "value"

    def test_parse_keymap_method_exists(self) -> None:
        """Test that parse_keymap method exists."""
        parser = ZMKKeymapParser()
        assert hasattr(parser, "parse_keymap")
        assert callable(parser.parse_keymap)

    def test_extract_layers_from_ast(self) -> None:
        """Test _extract_layers_from_ast method."""
        parser = ZMKKeymapParser()
        result = parser._extract_layers_from_ast(DTNode(name="test"))
        # Current implementation returns None
        assert result is None

    def test_parse_keymap_basic(self, zmk_parser: ZMKKeymapParser) -> None:
        """Test basic parse_keymap functionality."""
        content = 'keymap { compatible = "zmk,keymap"; };'
        result = zmk_parser.parse_keymap(content)
        assert isinstance(result, KeymapParseResult)
        # Should return a result regardless of success
        assert hasattr(result, "success")
        assert hasattr(result, "parsing_mode")


class TestZMKKeymapParserEnums:
    """Test enum values."""

    def test_parsing_mode_values(self) -> None:
        """Test ParsingMode enum values."""
        assert ParsingMode.FULL == "full"
        assert ParsingMode.TEMPLATE_AWARE == "template"

    def test_parsing_method_values(self) -> None:
        """Test ParsingMethod enum values."""
        assert ParsingMethod.AST == "ast"
        assert ParsingMethod.REGEX == "regex"


class TestZMKKeymapParserFactories:
    """Test factory functions."""

    def test_create_zmk_keymap_parser(self) -> None:
        """Test factory function."""
        parser = create_zmk_keymap_parser()
        assert isinstance(parser, ZMKKeymapParser)

    def test_create_zmk_keymap_parser_from_profile(self) -> None:
        """Test profile-based factory function."""

        class MockProfile:
            name = "test"

            @property
            def keyboard_name(self) -> str:
                return self.name

        profile = MockProfile()
        parser = create_zmk_keymap_parser_from_profile(profile)
        assert isinstance(parser, ZMKKeymapParser)


class TestKeymapParseResult:
    """Test KeymapParseResult model."""

    def test_keymap_parse_result_creation(self) -> None:
        """Test creating KeymapParseResult."""
        result = KeymapParseResult(
            success=True,
            parsing_mode=ParsingMode.FULL,
            parsing_method=ParsingMethod.AST,
        )
        assert result.success is True
        assert result.parsing_mode == ParsingMode.FULL
        assert result.parsing_method == ParsingMethod.AST
