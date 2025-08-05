"""Comprehensive tests for ZMK keymap parser functionality."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Any, Dict, List, Optional

from zmk_layout.parsers.zmk_keymap_parser import (
    ZMKKeymapParser,
    create_zmk_keymap_parser,
    create_zmk_keymap_parser_from_profile,
    ParsingMode,
    ParsingMethod,
    KeymapParseResult,
)
from zmk_layout.models.metadata import LayoutData
from zmk_layout.models.core import LayoutBinding, LayoutParam
from zmk_layout.parsers.parsing_models import ParsingContext


class MockLogger:
    def __init__(self):
        self.debug_calls = []
        self.error_calls = []
        self.warning_calls = []

    def debug(self, message, **kwargs):
        self.debug_calls.append((message, kwargs))

    def error(self, message, **kwargs):
        self.error_calls.append((message, kwargs))

    def warning(self, message, **kwargs):
        self.warning_calls.append((message, kwargs))


class MockProcessor:
    def __init__(self, return_value=None, should_raise=None):
        self.return_value = return_value
        self.should_raise = should_raise
        self.process_calls = []

    def process(self, context):
        self.process_calls.append(context)
        if self.should_raise:
            raise self.should_raise
        return self.return_value


class MockConfigurationProvider:
    def __init__(self, extraction_config=None):
        self.extraction_config = extraction_config or {}

    def get_extraction_config(self, profile=None):
        return self.extraction_config


@pytest.fixture
def mock_logger():
    return MockLogger()


@pytest.fixture
def mock_configuration_provider():
    return MockConfigurationProvider()


@pytest.fixture
def sample_layout_data():
    return LayoutData(
        title="Test Layout",
        keyboard="test_keyboard",
        layer_names=["base", "nav"],
        layers=[
            [LayoutBinding(value="&kp", params=[LayoutParam(value="Q")]), LayoutBinding(value="&kp", params=[LayoutParam(value="W")])],
            [LayoutBinding(value="&trans", params=[]), LayoutBinding(value="&kp", params=[LayoutParam(value="ESC")])],
        ]
    )


@pytest.fixture
def zmk_parser(mock_logger, mock_configuration_provider):
    mock_processors = {
        ParsingMode.TEMPLATE_AWARE: MockProcessor(),
        ParsingMode.FULL: MockProcessor(),
    }
    
    parser = ZMKKeymapParser(
        configuration_provider=mock_configuration_provider,
        logger=mock_logger,
        processors=mock_processors,
    )
    return parser


class TestZMKKeymapParserFileHandling:
    """Tests for file I/O and error handling."""

    def test_parse_keymap_missing_file(self, zmk_parser):
        """Test parsing when keymap file doesn't exist."""
        non_existent_file = Path("/non/existent/file.keymap")
        
        result = zmk_parser.parse_keymap(non_existent_file)
        
        assert not result.success
        assert any("Keymap file not found" in error for error in result.errors)
        assert result.parsing_mode == ParsingMode.TEMPLATE_AWARE
        assert result.parsing_method == ParsingMethod.AST

    def test_parse_keymap_empty_file(self, zmk_parser, tmp_path, sample_layout_data):
        """Test parsing empty keymap file."""
        empty_file = tmp_path / "empty.keymap"
        empty_file.write_text("")
        
        zmk_parser.processors[ParsingMode.TEMPLATE_AWARE].return_value = sample_layout_data
        
        result = zmk_parser.parse_keymap(empty_file)
        
        assert result.success
        assert result.layout_data is not None

    @patch('pathlib.Path.read_text')
    def test_parse_keymap_encoding_error(self, mock_read_text, zmk_parser):
        """Test parsing file with encoding issues."""
        mock_read_text.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')
        
        keymap_file = Path("test.keymap")
        result = zmk_parser.parse_keymap(keymap_file)
        
        assert not result.success
        assert any("Parsing failed" in error for error in result.errors)

    def test_parse_keymap_with_different_modes(self, zmk_parser, tmp_path, sample_layout_data):
        """Test parsing with different parsing modes."""
        keymap_file = tmp_path / "test.keymap"
        keymap_file.write_text("/ { keymap { layer_0 { bindings = <&kp Q>; }; }; };")
        
        # Test TEMPLATE_AWARE mode
        zmk_parser.processors[ParsingMode.TEMPLATE_AWARE].return_value = sample_layout_data
        result_template = zmk_parser.parse_keymap(keymap_file, mode=ParsingMode.TEMPLATE_AWARE)
        assert result_template.parsing_mode == ParsingMode.TEMPLATE_AWARE
        
        # Test FULL mode  
        zmk_parser.processors[ParsingMode.FULL].return_value = sample_layout_data
        result_full = zmk_parser.parse_keymap(keymap_file, mode=ParsingMode.FULL)
        assert result_full.parsing_mode == ParsingMode.FULL


class TestZMKKeymapParserBindingConversion:
    """Tests for AST binding conversion logic."""

    def test_resolve_binding_string_with_defines(self, zmk_parser):
        """Test binding string resolution with defines."""
        zmk_parser.defines = {"CUSTOM_KEY": "Q", "MOD_KEY": "LCTRL"}
        
        # Test define resolution
        result = zmk_parser._resolve_binding_string("&kp CUSTOM_KEY")
        assert result == "&kp Q"
        
        # Test behavior references are not resolved
        result = zmk_parser._resolve_binding_string("&custom_behavior")
        assert result == "&custom_behavior"

    def test_resolve_binding_string_no_defines(self, zmk_parser):
        """Test binding string when no defines match."""
        result = zmk_parser._resolve_binding_string("&kp UNKNOWN_KEY")
        assert result == "&kp UNKNOWN_KEY"

    def test_convert_ast_bindings_complex_parameters(self, zmk_parser):
        """Test conversion of AST bindings with complex parameters."""
        from zmk_layout.parsers.ast_nodes import DTValue
        
        # Mock complex binding structure
        mock_binding_value = DTValue(
            value=["&hm", "LCTRL", "A", "&kp", "Q", "&mt", "LSHIFT", "ESC"],
            type="array"
        )
        
        with patch.object(zmk_parser, '_preprocess_moergo_binding_edge_cases', side_effect=lambda x: x):
            with patch.object(zmk_parser, '_resolve_binding_string', side_effect=lambda x: x):
                bindings = zmk_parser._convert_ast_bindings(mock_binding_value)
        
        assert len(bindings) == 3  # Three separate bindings
        assert bindings[0].value == "&hm"
        assert len(bindings[0].params) == 2  # LCTRL, A
        assert bindings[1].value == "&kp"
        assert len(bindings[1].params) == 1  # Q

    def test_convert_ast_bindings_empty_value(self, zmk_parser):
        """Test conversion with empty or None binding value."""
        from zmk_layout.parsers.ast_nodes import DTValue
        
        # Test None value
        result = zmk_parser._convert_ast_bindings(None)
        assert result == []
        
        # Test empty DTValue
        empty_value = DTValue(value=None, type="empty")
        result = zmk_parser._convert_ast_bindings(empty_value)
        assert result == []

    def test_convert_ast_bindings_parsing_failure(self, zmk_parser, mock_logger):
        """Test handling of binding parsing failures."""
        from zmk_layout.parsers.ast_nodes import DTValue
        
        mock_binding_value = DTValue(value=["&invalid_binding"], type="array")
        
        with patch.object(zmk_parser, '_preprocess_moergo_binding_edge_cases', side_effect=lambda x: x):
            with patch.object(zmk_parser, '_resolve_binding_string', side_effect=lambda x: x):
                with patch('zmk_layout.models.core.LayoutBinding.from_str', side_effect=ValueError("Invalid binding")):
                    bindings = zmk_parser._convert_ast_bindings(mock_binding_value)
        
        # Should create fallback binding
        assert len(bindings) == 1
        assert bindings[0].value == "&invalid_binding"
        assert bindings[0].params == []
        
        # Should log error
        assert any("Failed to parse binding" in call[0] for call in mock_logger.error_calls)


class TestZMKKeymapParserMoErgoPreprocessing:
    """Tests for MoErgo-specific preprocessing."""

    def test_preprocess_moergo_binding_edge_cases(self, zmk_parser):
        """Test MoErgo binding preprocessing."""
        # Test various edge cases that might be specific to MoErgo boards
        test_cases = [
            ("&kp Q", "&kp Q"),  # Normal case - no change
            ("&custom_behavior PARAM", "&custom_behavior PARAM"),  # Normal case
        ]
        
        for input_binding, expected_output in test_cases:
            result = zmk_parser._preprocess_moergo_binding_edge_cases(input_binding)
            assert result == expected_output


class TestZMKKeymapParserIntegration:
    """Integration tests for complete parsing workflow."""

    @patch('zmk_layout.parsers.zmk_keymap_parser.datetime')
    def test_parse_keymap_success_workflow(self, mock_datetime, zmk_parser, tmp_path, sample_layout_data):
        """Test successful complete parsing workflow."""
        # Mock datetime.now() for deterministic testing
        fixed_datetime = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_datetime
        
        keymap_file = tmp_path / "test.keymap"
        keymap_file.write_text("/ { keymap { layer_0 { bindings = <&kp Q>; }; }; };")
        
        zmk_parser.processors[ParsingMode.TEMPLATE_AWARE].return_value = sample_layout_data
        
        result = zmk_parser.parse_keymap(keymap_file)
        
        assert result.success
        assert result.layout_data is not None
        assert result.layout_data.date == fixed_datetime
        assert result.layout_data.creator == "glovebox"
        assert "test.keymap" in result.layout_data.notes

    def test_parse_keymap_processor_error(self, zmk_parser, tmp_path):
        """Test handling of processor errors."""
        keymap_file = tmp_path / "test.keymap"
        keymap_file.write_text("invalid content")
        
        # Configure processor to raise an exception
        zmk_parser.processors[ParsingMode.TEMPLATE_AWARE].should_raise = RuntimeError("Processing failed")
        
        result = zmk_parser.parse_keymap(keymap_file)
        
        assert not result.success
        assert any("Parsing failed" in error for error in result.errors)

    def test_parse_keymap_with_profile(self, zmk_parser, tmp_path, sample_layout_data):
        """Test parsing with keyboard profile."""
        from zmk_layout.models.core import KeyboardProfile
        
        keymap_file = tmp_path / "test.keymap"
        keymap_file.write_text("/ { keymap { layer_0 { bindings = <&kp Q>; }; }; };")
        
        profile = Mock()
        profile.keyboard_name = "test_board"
        
        zmk_parser.processors[ParsingMode.TEMPLATE_AWARE].return_value = sample_layout_data
        
        result = zmk_parser.parse_keymap(keymap_file, profile=profile)
        
        # Verify profile was used in parsing context
        context = zmk_parser.processors[ParsingMode.TEMPLATE_AWARE].process_calls[0]
        assert context.keyboard_name == "test_board"


class TestZMKKeymapParserFactories:
    """Tests for parser factory functions."""

    def test_create_zmk_keymap_parser(self):
        """Test basic parser creation."""
        parser = create_zmk_keymap_parser()
        
        assert isinstance(parser, ZMKKeymapParser)
        assert parser.logger is None  # Default is None
        assert parser.configuration_provider is None  # Default is None

    def test_create_zmk_keymap_parser_from_profile(self):
        """Test parser creation from profile."""
        mock_profile = Mock()
        
        parser = create_zmk_keymap_parser_from_profile(mock_profile)
        
        assert isinstance(parser, ZMKKeymapParser)


class TestZMKKeymapParserErrorHandling:
    """Tests for comprehensive error handling."""

    def test_extraction_config_error_handling(self, zmk_parser):
        """Test error handling in extraction config retrieval."""
        # Configure provider to return None or invalid config
        zmk_parser.configuration_provider.extraction_config = None
        
        config = zmk_parser._get_extraction_config(None)
        
        # Should handle gracefully and return some default
        assert isinstance(config, dict)

    def test_template_path_error_handling(self, zmk_parser):
        """Test error handling in template path retrieval."""
        mock_profile = Mock()
        mock_profile.template_path = None
        
        # Should handle missing template path gracefully
        path = zmk_parser._get_template_path(mock_profile)
        # Should return fallback path or None
        assert path is None or isinstance(path, Path)

    def test_logging_with_none_logger(self):
        """Test parser behavior with None logger."""
        mock_processors = {
            ParsingMode.TEMPLATE_AWARE: MockProcessor(),
            ParsingMode.FULL: MockProcessor(),
        }
        
        parser = ZMKKeymapParser(
            configuration_provider=MockConfigurationProvider(),
            logger=None,  # None logger
            processors=mock_processors,
        )
        
        # Should not crash when logger is None
        result = parser._resolve_binding_string("&kp Q")
        assert result == "&kp Q"


class TestZMKKeymapParserEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_parse_keymap_with_warnings(self, zmk_parser, tmp_path, sample_layout_data):
        """Test parsing that generates warnings."""
        keymap_file = tmp_path / "test.keymap"
        keymap_file.write_text("/ { keymap { layer_0 { bindings = <&kp Q>; }; }; };")
        
        # Configure processor to add warnings to context
        def mock_process(context):
            context.warnings.append("Test warning")
            return sample_layout_data
        
        zmk_parser.processors[ParsingMode.TEMPLATE_AWARE].process = mock_process
        
        result = zmk_parser.parse_keymap(keymap_file)
        
        assert result.success
        assert "Test warning" in result.warnings

    def test_standalone_parameter_handling(self, zmk_parser, mock_logger):
        """Test handling of standalone parameters without behavior references."""
        from zmk_layout.parsers.ast_nodes import DTValue
        
        # Mock binding with standalone parameter (edge case)
        mock_binding_value = DTValue(value=["STANDALONE_PARAM"], type="array")
        
        bindings = zmk_parser._convert_ast_bindings(mock_binding_value)
        
        # Should handle gracefully and log warning
        assert len(bindings) == 0  # No valid bindings created
        assert any("Found standalone parameter" in call[0] for call in mock_logger.warning_calls)

    def test_single_binding_conversion(self, zmk_parser):
        """Test conversion of single binding (non-array)."""
        from zmk_layout.parsers.ast_nodes import DTValue
        
        mock_binding_value = DTValue(value="&kp Q", type="string")
        
        with patch.object(zmk_parser, '_preprocess_moergo_binding_edge_cases', side_effect=lambda x: x):
            with patch.object(zmk_parser, '_resolve_binding_string', side_effect=lambda x: x):
                bindings = zmk_parser._convert_ast_bindings(mock_binding_value)
        
        assert len(bindings) == 1
        assert bindings[0].value == "&kp"
        assert len(bindings[0].params) == 1
        assert bindings[0].params[0].value == "Q"