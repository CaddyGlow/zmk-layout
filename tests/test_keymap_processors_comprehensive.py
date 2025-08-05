"""Comprehensive tests for keymap processors functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List, Optional

from zmk_layout.parsers.keymap_processors import (
    BaseKeymapProcessor,
    FullKeymapProcessor,
    TemplateAwareProcessor,
    create_full_keymap_processor,
    create_template_aware_processor,
)
from zmk_layout.parsers.parsing_models import ParsingContext
from zmk_layout.models.metadata import LayoutData
from zmk_layout.models.core import LayoutBinding, LayoutParam
from zmk_layout.parsers.ast_nodes import DTNode, DTValue, DTConditional


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


class MockSectionExtractor:
    def __init__(self, sections=None):
        self.sections = sections or {}
        self.extract_calls = []

    def extract_sections(self, content):
        self.extract_calls.append(content)
        return self.sections


@pytest.fixture
def mock_logger():
    return MockLogger()


@pytest.fixture
def mock_section_extractor():
    return MockSectionExtractor()


@pytest.fixture
def sample_parsing_context():
    return ParsingContext(
        keymap_content="/ { keymap { layer_0 { bindings = <&kp Q>; }; }; };",
        title="Test Layout",
        keyboard_name="test_keyboard",
        extraction_config={"key_count": 10},
    )


@pytest.fixture
def base_processor(mock_logger, mock_section_extractor):
    return BaseKeymapProcessor(logger=mock_logger, section_extractor=mock_section_extractor)


class TestBaseKeymapProcessorDefineExtraction:
    """Tests for define extraction from AST."""

    def test_extract_defines_from_ast_with_values(self, base_processor, mock_logger):
        """Test extracting defines with values from AST."""
        # Create root node with conditional defines
        root_node = DTNode(name="root")
        root_node.conditionals = [
            DTConditional(directive="define", condition="CUSTOM_KEY Q"),
            DTConditional(directive="define", condition="MOD_KEY LCTRL"),
        ]
        
        defines = base_processor._extract_defines_from_ast([root_node])
        
        assert defines == {"CUSTOM_KEY": "Q", "MOD_KEY": "LCTRL"}
        assert len(mock_logger.debug_calls) >= 2  # Should log each define extraction

    def test_extract_defines_from_ast_without_values(self, base_processor, mock_logger):
        """Test extracting defines without values."""
        root_node = DTNode(name="root")
        root_node.conditionals = [
            DTConditional(directive="define", condition="FLAG_ONLY"),
        ]
        
        defines = base_processor._extract_defines_from_ast([root_node])
        
        assert defines == {"FLAG_ONLY": ""}

    def test_extract_defines_from_ast_empty(self, base_processor):
        """Test extracting defines from empty AST."""
        root_node = DTNode(name="root")
        # No conditionals added
        
        defines = base_processor._extract_defines_from_ast([root_node])
        
        assert defines == {}

    def test_extract_defines_from_ast_no_conditionals(self, base_processor):
        """Test AST without conditional nodes."""
        root_node = DTNode(name="root")
        root_node.conditionals = [
            DTConditional(directive="ifdef", condition="SOME_FLAG"),  # Not a define
        ]
        
        defines = base_processor._extract_defines_from_ast([root_node])
        
        assert defines == {}


class TestBaseKeymapProcessorDefineResolution:
    """Tests for define resolution logic."""

    def test_resolve_define_found(self, base_processor, mock_logger):
        """Test resolving a token that exists in defines."""
        defines = {"CUSTOM_KEY": "Q", "MOD_KEY": "LCTRL"}
        
        result = base_processor._resolve_define("CUSTOM_KEY", defines)
        
        assert result == "Q"
        assert any("Resolved define" in call[0] for call in mock_logger.debug_calls)

    def test_resolve_define_not_found(self, base_processor):
        """Test resolving a token that doesn't exist in defines."""
        defines = {"CUSTOM_KEY": "Q"}
        
        result = base_processor._resolve_define("UNKNOWN_KEY", defines)
        
        assert result == "UNKNOWN_KEY"

    def test_resolve_define_empty_defines(self, base_processor):
        """Test resolving with empty defines dictionary."""
        defines = {}
        
        result = base_processor._resolve_define("ANY_KEY", defines)
        
        assert result == "ANY_KEY"


class TestBaseKeymapProcessorBehaviorTransformation:
    """Tests for behavior reference transformation."""

    def test_transform_behavior_references_simple(self, base_processor):
        """Test simple behavior reference transformation."""
        content = """
        / {
            behaviors {
                custom_ht: custom_ht {
                    compatible = "zmk,behavior-hold-tap";
                    bindings = <&kp>, <&mo>;
                };
            };
        };
        """
        
        result = base_processor._transform_behavior_references_to_definitions(content)
        
        # Should remain mostly unchanged for simple case
        assert "custom_ht:" in result
        assert "compatible" in result

    def test_transform_behavior_references_with_input_listener(self, base_processor):
        """Test transformation with input listener references."""
        content = """
        / {
            keymap {
                compatible = "zmk,keymap";
                
                layer_0 {
                    bindings = <&encoder_input_listener>;
                };
            };
            
            &encoder_input_listener {
                status = "okay";
            };
        };
        """
        
        result = base_processor._transform_behavior_references_to_definitions(content)
        
        # Should insert compatible string for input listener reference
        assert 'compatible = "zmk,input-listener";' in result

    def test_transform_behavior_references_multiple_listeners(self, base_processor):
        """Test transformation with multiple input listener references."""
        content = """
        / {
            &encoder_1 {
                status = "okay";
            };
            
            &encoder_2 {
                status = "okay";
            };
        };
        """
        
        result = base_processor._transform_behavior_references_to_definitions(content)
        
        # Should handle multiple input listeners
        compatible_count = result.count('compatible = "zmk,input-listener";')
        assert compatible_count == 2


class TestBaseKeymapProcessorLayerExtraction:
    """Tests for layer extraction from roots."""

    def test_extract_layers_from_roots_success(self, base_processor):
        """Test successful layer extraction."""
        # Mock root nodes with layer content
        layer_bindings = [
            LayoutBinding(value="&kp", params=[LayoutParam(value="Q")]),
            LayoutBinding(value="&kp", params=[LayoutParam(value="W")]),
        ]
        
        expected_layers_data = {
            "layer_names": ["base", "nav"],
            "layers": [
                layer_bindings,
                [LayoutBinding(value="&trans", params=[])],
            ]
        }
        
        mock_root = Mock()
        # Mock the temporary parser's method
        with patch('zmk_layout.parsers.keymap_processors.ZMKKeymapParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser._extract_layers_from_ast.return_value = expected_layers_data
            mock_parser_class.return_value = mock_parser
            
            result = base_processor._extract_layers_from_roots([mock_root], {})
        
        assert result == expected_layers_data

    def test_extract_layers_from_roots_empty(self, base_processor):
        """Test layer extraction with empty roots."""
        result = base_processor._extract_layers_from_roots([], {})
        
        assert result is None

    def test_extract_layers_from_roots_no_layers(self, base_processor):
        """Test layer extraction when no layers found in roots."""
        mock_root = Mock()
        # Mock the temporary parser's method to return None
        with patch('zmk_layout.parsers.keymap_processors.ZMKKeymapParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser._extract_layers_from_ast.return_value = None
            mock_parser_class.return_value = mock_parser
            
            result = base_processor._extract_layers_from_roots([mock_root], {})
        
        assert result is None


class TestBaseKeymapProcessorBehaviorPopulation:
    """Tests for behavior population in layout."""

    def test_populate_behaviors_in_layout_success(self, base_processor):
        """Test successful behavior population."""
        layout_data = LayoutData(
            title="Test",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[LayoutBinding(value="&kp", params=[LayoutParam(value="Q")])]],
        )
        
        roots = {
            "hold_taps": [{"name": "custom_ht", "description": "Custom hold-tap"}],
            "macros": [{"name": "custom_macro", "description": "Custom macro"}],
            "combos": [],
        }
        
        base_processor._populate_behaviors_in_layout(layout_data, roots)
        
        # Should populate behavior lists
        assert len(layout_data.hold_taps) == 1
        assert layout_data.hold_taps[0]["name"] == "custom_ht"
        assert len(layout_data.macros) == 1
        assert layout_data.macros[0]["name"] == "custom_macro"
        assert len(layout_data.combos) == 0

    def test_populate_behaviors_in_layout_missing_roots(self, base_processor):
        """Test behavior population with missing behavior types in roots."""
        layout_data = LayoutData(
            title="Test",
            keyboard="test_keyboard", 
            layer_names=["base"],
            layers=[[LayoutBinding(value="&kp", params=[LayoutParam(value="Q")])]],
        )
        
        roots = {}  # No behavior data
        
        # Should not crash with missing behavior data
        base_processor._populate_behaviors_in_layout(layout_data, roots)
        
        assert layout_data.hold_taps == []
        assert layout_data.macros == []
        assert layout_data.combos == []


class TestFullKeymapProcessor:
    """Tests for FullKeymapProcessor."""

    @pytest.fixture
    def full_processor(self, mock_logger, mock_section_extractor):
        return FullKeymapProcessor(logger=mock_logger, section_extractor=mock_section_extractor)

    def test_process_success(self, full_processor, sample_parsing_context):
        """Test successful processing."""
        with patch.object(full_processor, '_extract_defines_from_ast', return_value={}):
            with patch.object(full_processor, '_create_base_layout_data') as mock_create:
                with patch.object(full_processor, '_extract_layers_from_roots', return_value=None):
                    mock_create.return_value = LayoutData(
                        title="Test",
                        keyboard="test_keyboard",
                        layer_names=[],
                        layers=[],
                    )
                    
                    result = full_processor.process(sample_parsing_context)
                    
                    assert result is not None
                    assert isinstance(result, LayoutData)

    def test_process_parsing_failure(self, full_processor, sample_parsing_context, mock_logger):
        """Test processing with parsing failure."""
        # Simulate parsing error by adding error to context
        sample_parsing_context.errors.append("Parsing failed")
        
        result = full_processor.process(sample_parsing_context)
        
        assert result is None
        assert any("AST parsing failed" in call[0] for call in mock_logger.error_calls)

    def test_process_exception_handling(self, full_processor, sample_parsing_context, mock_logger):
        """Test exception handling during processing."""
        with patch.object(full_processor, '_extract_defines_from_ast', side_effect=RuntimeError("Extraction failed")):
            result = full_processor.process(sample_parsing_context)
            
            assert result is None
            assert any("Processing failed" in call[0] for call in mock_logger.error_calls)


class TestTemplateAwareProcessor:
    """Tests for TemplateAwareProcessor."""

    @pytest.fixture
    def template_processor(self, mock_logger, mock_section_extractor):
        mock_section_extractor.sections = {
            "layer_names": ["base", "nav"],
            "layers": {
                "base": [LayoutBinding(value="&kp", params=[LayoutParam(value="Q")])],
                "nav": [LayoutBinding(value="&trans", params=[])],
            },
            "holdTaps": [],
            "macros": [],
            "combos": [],
        }
        return TemplateAwareProcessor(logger=mock_logger, section_extractor=mock_section_extractor)

    def test_process_success(self, template_processor, sample_parsing_context):
        """Test successful template-aware processing."""
        result = template_processor.process(sample_parsing_context)
        
        assert result is not None
        assert isinstance(result, LayoutData)
        assert result.layer_names == ["base", "nav"]
        assert len(result.layers) == 2

    def test_process_no_layer_names(self, template_processor, sample_parsing_context, mock_logger):
        """Test processing when no layer names are found."""
        template_processor.section_extractor.sections = {}
        
        result = template_processor.process(sample_parsing_context)
        
        assert result is None
        assert any("No layer_names found" in call[0] for call in mock_logger.error_calls)

    def test_process_layer_count_mismatch(self, template_processor, sample_parsing_context, mock_logger):
        """Test processing with layer count mismatch."""
        template_processor.section_extractor.sections = {
            "layer_names": ["base", "nav", "extra"],  # 3 names
            "layers": {
                "base": [LayoutBinding(value="&kp", params=[LayoutParam(value="Q")])],
                "nav": [LayoutBinding(value="&trans", params=[])],
                # Missing "extra" layer - only 2 layers
            },
            "holdTaps": [],
            "macros": [],
            "combos": [],
        }
        
        result = template_processor.process(sample_parsing_context)
        
        assert result is None
        assert any("Layer count mismatch" in call[0] for call in mock_logger.error_calls)

    def test_process_extraction_failure(self, template_processor, sample_parsing_context, mock_logger):
        """Test processing with extraction failure."""
        template_processor.section_extractor.extract_sections = Mock(side_effect=RuntimeError("Extraction failed"))
        
        result = template_processor.process(sample_parsing_context)
        
        assert result is None
        assert any("Processing failed" in call[0] for call in mock_logger.error_calls)


class TestKeymapProcessorFactories:
    """Tests for processor factory functions."""

    def test_create_full_keymap_processor(self):
        """Test full processor factory."""
        processor = create_full_keymap_processor()
        
        assert isinstance(processor, FullKeymapProcessor)

    def test_create_template_aware_processor(self):
        """Test template-aware processor factory."""
        processor = create_template_aware_processor()
        
        assert isinstance(processor, TemplateAwareProcessor)


class TestKeymapProcessorEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_base_processor_with_none_logger(self, mock_section_extractor):
        """Test processor behavior with None logger."""
        processor = BaseKeymapProcessor(logger=None, section_extractor=mock_section_extractor)
        
        # Should not crash when logger is None
        defines = processor._resolve_define("KEY", {"KEY": "Q"})
        assert defines == "Q"

    def test_processor_with_malformed_content(self, base_processor):
        """Test processor with malformed input content."""
        malformed_content = "this is not valid device tree syntax"
        
        # Should handle gracefully
        result = base_processor._transform_behavior_references_to_definitions(malformed_content)
        assert result == malformed_content  # Should return original if no matches

    def test_create_base_layout_data(self, base_processor, sample_parsing_context):
        """Test base layout data creation."""
        layout_data = base_processor._create_base_layout_data(sample_parsing_context)
        
        assert layout_data.title == "Test Layout"
        assert layout_data.keyboard == "test_keyboard"
        assert layout_data.layer_names == []
        assert layout_data.layers == []

    def test_extract_behaviors_and_metadata(self, base_processor):
        """Test behavior and metadata extraction."""
        expected_behaviors = {
            "hold_taps": [{"name": "ht1"}],
            "macros": [{"name": "macro1"}],
            "combos": [{"name": "combo1"}],
        }
        
        mock_root = Mock()
        # Mock the section extractor's behavior extractor
        mock_section_extractor = Mock()
        mock_behavior_extractor = Mock()
        mock_behavior_extractor.extract_behaviors_as_models.return_value = expected_behaviors
        mock_section_extractor.behavior_extractor = mock_behavior_extractor
        base_processor.section_extractor = mock_section_extractor
        
        result = base_processor._extract_behaviors_and_metadata([mock_root], "content", {})
        
        assert result == expected_behaviors

    def test_populate_layout_from_processed_data(self):
        """Test layout population from processed data."""
        template_processor = TemplateAwareProcessor(logger=MockLogger(), section_extractor=MockSectionExtractor())
        
        layout_data = LayoutData(
            title="Test",
            keyboard="test_keyboard",
            layer_names=[],
            layers=[],
        )
        
        processed_data = {
            "holdTaps": [{"name": "ht1"}],
            "macros": [],
            "combos": [],
        }
        
        template_processor._populate_layout_from_processed_data(layout_data, processed_data)
        
        assert len(layout_data.hold_taps) == 1
        assert layout_data.hold_taps[0]["name"] == "ht1"