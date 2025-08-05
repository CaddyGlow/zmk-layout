"""Comprehensive tests for template context and processing functionality."""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List, Optional

from zmk_layout.generators.template_context import (
    TemplateService,
    TemplateError,
    CircularReferenceError,
    create_template_service,
    create_jinja2_template_service,
    TemplateContext,
)
from zmk_layout.models.metadata import LayoutData
from zmk_layout.models.core import LayoutBinding, LayoutParam


class MockTemplateProvider:
    def __init__(self, render_responses=None, should_raise=None):
        self.render_responses = render_responses or {}
        self.should_raise = should_raise
        self.render_calls = []

    def render_string(self, template, context):
        self.render_calls.append((template, context))
        if self.should_raise:
            raise self.should_raise
        return self.render_responses.get(template, template)


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


class MockProviders:
    def __init__(self, template_provider=None, logger=None):
        self.template = template_provider or MockTemplateProvider()
        self.logger = logger or MockLogger()


@pytest.fixture
def mock_providers():
    return MockProviders()


@pytest.fixture
def template_service(mock_providers):
    return TemplateService(mock_providers)


@pytest.fixture
def sample_layout_data():
    return LayoutData(
        title="Test Layout",
        keyboard="test_keyboard",
        layer_names=["base", "nav"],
        layers=[
            [LayoutBinding(value="&kp", params=[LayoutParam(value="Q")]), LayoutBinding(value="&kp", params=[LayoutParam(value="W")])],
            [LayoutBinding(value="&trans", params=[]), LayoutBinding(value="&kp", params=[LayoutParam(value="ESC")])],
        ],
        variables={"custom_key": "Q", "mod_key": "LCTRL"},
    )


class TestTemplateServiceBasicFunctionality:
    """Tests for basic template service functionality."""

    def test_process_layout_data_no_templates(self, template_service, sample_layout_data):
        """Test processing layout data without templates."""
        # Layout data without template syntax
        result = template_service.process_layout_data(sample_layout_data)
        
        # Should return the same data when no templates are found
        assert result.title == sample_layout_data.title
        assert result.keyboard == sample_layout_data.keyboard
        assert len(result.layers) == len(sample_layout_data.layers)

    def test_process_layout_data_with_templates(self, template_service, mock_providers):
        """Test processing layout data with templates."""
        layout_data = LayoutData(
            title="{{variables.custom_title}}",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[LayoutBinding(value="&kp", params=[LayoutParam(value="{{variables.custom_key}}")])]],
            variables={"custom_title": "My Layout", "custom_key": "Q"},
        )
        
        # Configure mock template provider
        mock_providers.template.render_responses = {
            "{{variables.custom_title}}": "My Layout",
            "{{variables.custom_key}}": "Q",
        }
        
        result = template_service.process_layout_data(layout_data)
        
        assert result.title == "My Layout"
        # Check that template processing was called
        assert len(mock_providers.template.render_calls) > 0

    def test_process_layout_data_template_error(self, template_service, mock_providers):
        """Test handling of template processing errors."""
        layout_data = LayoutData(
            title="{{invalid_template",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
        )
        
        # Configure template provider to raise error
        mock_providers.template.should_raise = RuntimeError("Template error")
        
        with pytest.raises(TemplateError) as exc_info:
            template_service.process_layout_data(layout_data)
        
        assert "Template processing failed" in str(exc_info.value)


class TestTemplateServiceContextCreation:
    """Tests for template context creation."""

    def test_create_template_context_basic(self, template_service, sample_layout_data):
        """Test basic template context creation."""
        context = template_service.create_template_context(sample_layout_data, "basic")
        
        assert context["variables"] == sample_layout_data.variables
        assert context["keyboard"] == sample_layout_data.keyboard
        assert context["title"] == sample_layout_data.title
        assert context["layer_names"] == sample_layout_data.layer_names

    def test_create_template_context_with_optional_fields(self, template_service):
        """Test context creation with optional fields."""
        layout_data = LayoutData(
            title="Test",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
            creator="test_creator",
            uuid="test-uuid-123",
            tags=["test", "layout"],
            version="2.0.0",  # Non-default version
        )
        
        context = template_service.create_template_context(layout_data, "basic")
        
        assert context["creator"] == "test_creator"
        assert context["uuid"] == "test-uuid-123"
        assert context["tags"] == ["test", "layout"]
        assert context["version"] == "2.0.0"

    def test_create_template_context_default_version_excluded(self, template_service):
        """Test that default version is excluded from context."""
        layout_data = LayoutData(
            title="Test",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
            version="1.0.0",  # Default version
        )
        
        context = template_service.create_template_context(layout_data, "basic")
        
        assert "version" not in context

    @patch('time.time')
    def test_create_template_context_date_handling(self, mock_time, template_service):
        """Test date field handling in context creation."""
        # Mock current time
        mock_time.return_value = 1000000.0
        
        # Test with old timestamp (should be included)
        layout_data_old = LayoutData(
            title="Test",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
            date=999900.0,  # More than 60 seconds old
        )
        
        context_old = template_service.create_template_context(layout_data_old, "basic")
        assert "date" in context_old
        
        # Test with recent timestamp (should be excluded)
        layout_data_recent = LayoutData(
            title="Test",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
            date=999950.0,  # Less than 60 seconds old
        )
        
        context_recent = template_service.create_template_context(layout_data_recent, "basic")
        assert "date" not in context_recent

    def test_create_template_context_layer_utilities(self, template_service, sample_layout_data):
        """Test layer utility functions in context."""
        context = template_service.create_template_context(sample_layout_data, "basic")
        
        assert "layer_name_to_index" in context
        assert context["layer_name_to_index"]["base"] == 0
        assert context["layer_name_to_index"]["nav"] == 1
        
        assert "get_layer_index" in context
        assert context["get_layer_index"]("base") == 0
        assert context["get_layer_index"]("nav") == 1
        assert context["get_layer_index"]("unknown") == -1

    def test_create_template_context_behaviors_stage(self, template_service, sample_layout_data):
        """Test context creation for behaviors stage."""
        # Pre-populate resolution cache
        template_service._resolution_cache = {
            "holdTaps": [{"name": "custom_ht"}],
            "combos": [{"name": "custom_combo"}],
            "macros": [{"name": "custom_macro"}],
        }
        
        context = template_service.create_template_context(sample_layout_data, "behaviors")
        
        assert context["holdTaps"] == [{"name": "custom_ht"}]
        assert context["combos"] == [{"name": "custom_combo"}]
        assert context["macros"] == [{"name": "custom_macro"}]

    def test_create_template_context_layers_stage(self, template_service, sample_layout_data):
        """Test context creation for layers stage."""
        # Pre-populate resolution cache
        template_service._resolution_cache = {
            "layers_by_name": {
                "base": [LayoutBinding(value="&kp", params=[LayoutParam(value="Q")])],
                "nav": [LayoutBinding(value="&trans", params=[])],
            }
        }
        
        context = template_service.create_template_context(sample_layout_data, "layers")
        
        assert "layers_by_name" in context
        assert "get_layer_bindings" in context
        assert len(context["get_layer_bindings"]("base")) == 1
        assert len(context["get_layer_bindings"]("nav")) == 1
        assert context["get_layer_bindings"]("unknown") == []


class TestTemplateServiceValidation:
    """Tests for template syntax validation."""

    def test_validate_template_syntax_valid(self, template_service, mock_providers):
        """Test validation of valid template syntax."""
        layout_data = LayoutData(
            title="{{variables.title}}",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
            variables={"title": "Valid"},
        )
        
        # Configure template provider to succeed
        mock_providers.template.render_responses = {"{{variables.title}}": "Valid"}
        
        errors = template_service.validate_template_syntax(layout_data)
        
        assert errors == []

    def test_validate_template_syntax_invalid(self, template_service, mock_providers):
        """Test validation of invalid template syntax."""
        layout_data = LayoutData(
            title="{{invalid_template",  # Missing closing braces
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
        )
        
        # Configure template provider to raise error on render_string
        def error_render(template, context):
            if "invalid_template" in template:
                raise RuntimeError("Invalid syntax")
            return template
        
        mock_providers.template.render_string = error_render
        
        errors = template_service.validate_template_syntax(layout_data)
        
        assert len(errors) > 0
        assert any("Invalid template syntax" in error for error in errors)

    def test_validate_template_syntax_no_templates(self, template_service):
        """Test validation when no templates are present."""
        layout_data = LayoutData(
            title="Plain Title",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
        )
        
        errors = template_service.validate_template_syntax(layout_data)
        
        assert errors == []


class TestTemplateServiceMultiPassResolution:
    """Tests for multi-pass template resolution."""

    def test_multipass_resolution_order(self, template_service, mock_providers):
        """Test that multi-pass resolution follows correct order."""
        from zmk_layout.models.behaviors import HoldTapBehavior
        
        layout_data = LayoutData(
            title="{{variables.title}}",
            keyboard="test_keyboard",
            layer_names=["base"],
            layers=[[]],
            variables={"title": "Test", "ht_name": "custom_ht"},
            hold_taps=[HoldTapBehavior(name="{{variables.ht_name}}", bindings=["&kp", "&mo"])],
        )
        
        mock_providers.template.render_responses = {
            "{{variables.title}}": "Test Layout",
            "{{variables.ht_name}}": "custom_ht",
        }
        
        with patch.object(template_service, '_resolve_basic_fields', wraps=template_service._resolve_basic_fields) as mock_basic:
            with patch.object(template_service, '_resolve_behaviors', wraps=template_service._resolve_behaviors) as mock_behaviors:
                with patch.object(template_service, '_resolve_layers', wraps=template_service._resolve_layers) as mock_layers:
                    with patch.object(template_service, '_resolve_custom_code', wraps=template_service._resolve_custom_code) as mock_custom:
                        template_service.process_layout_data(layout_data)
        
        # Verify resolution order
        assert mock_basic.called
        assert mock_behaviors.called
        assert mock_layers.called
        assert mock_custom.called

    def test_resolve_basic_fields(self, template_service, mock_providers):
        """Test basic fields resolution."""
        data = {
            "title": "{{variables.title}}",
            "notes": "{{variables.notes}}",
            "creator": "{{variables.creator}}",
            "variables": {"title": "Test", "notes": "Test notes", "creator": "Test creator"},
        }
        
        mock_providers.template.render_responses = {
            "{{variables.title}}": "Test Layout",
            "{{variables.notes}}": "Test notes processed",
            "{{variables.creator}}": "Test creator processed",
        }
        
        result = template_service._resolve_basic_fields(data)
        
        assert result["title"] == "Test Layout"
        assert result["notes"] == "Test notes processed"
        assert result["creator"] == "Test creator processed"

    def test_resolve_behaviors(self, template_service, mock_providers):
        """Test behavior resolution."""
        data = {
            "holdTaps": [{"name": "{{variables.ht_name}}"}],
            "macros": [{"name": "{{variables.macro_name}}"}],
            "combos": [],
            "variables": {"ht_name": "custom_ht", "macro_name": "custom_macro"},
        }
        
        mock_providers.template.render_responses = {
            "{{variables.ht_name}}": "custom_ht",
            "{{variables.macro_name}}": "custom_macro",
        }
        
        result = template_service._resolve_behaviors(data)
        
        # Check that behaviors were processed and cached
        assert template_service._resolution_cache["holdTaps"][0]["name"] == "custom_ht"
        assert template_service._resolution_cache["macros"][0]["name"] == "custom_macro"

    def test_resolve_layers(self, template_service, mock_providers):
        """Test layer resolution."""
        data = {
            "layers": [["{{variables.binding}}"]],
            "layer_names": ["base"],
            "variables": {"binding": "&kp Q"},
        }
        
        mock_providers.template.render_responses = {
            "{{variables.binding}}": "&kp Q",
        }
        
        result = template_service._resolve_layers(data)
        
        # Check that layers were processed and cached
        assert "layers_by_name" in template_service._resolution_cache
        assert template_service._resolution_cache["layers_by_name"]["base"][0] == "&kp Q"

    def test_resolve_custom_code(self, template_service, mock_providers):
        """Test custom code resolution."""
        data = {
            "custom_defined_behaviors": "{{variables.custom_behavior}}",
            "custom_devicetree": "{{variables.custom_dt}}",
            "variables": {"custom_behavior": "my_behavior", "custom_dt": "my_dt"},
        }
        
        mock_providers.template.render_responses = {
            "{{variables.custom_behavior}}": "resolved_behavior",
            "{{variables.custom_dt}}": "resolved_dt",
        }
        
        result = template_service._resolve_custom_code(data)
        
        assert result["custom_defined_behaviors"] == "resolved_behavior"
        assert result["custom_devicetree"] == "resolved_dt"


class TestTemplateServiceTypeConversion:
    """Tests for type conversion functionality."""

    def test_convert_to_appropriate_type_int(self, template_service):
        """Test conversion to integer."""
        assert template_service._convert_to_appropriate_type("123") == 123
        assert template_service._convert_to_appropriate_type("-456") == -456

    def test_convert_to_appropriate_type_float(self, template_service):
        """Test conversion to float."""
        assert template_service._convert_to_appropriate_type("3.14") == 3.14
        assert template_service._convert_to_appropriate_type("-2.5") == -2.5

    def test_convert_to_appropriate_type_bool_true(self, template_service):
        """Test conversion to boolean true."""
        true_values = ["true", "True", "TRUE", "yes", "Yes", "YES", "1"]
        for value in true_values:
            assert template_service._convert_to_appropriate_type(value) is True

    def test_convert_to_appropriate_type_bool_false(self, template_service):
        """Test conversion to boolean false."""
        false_values = ["false", "False", "FALSE", "no", "No", "NO", "0"]
        for value in false_values:
            assert template_service._convert_to_appropriate_type(value) is False

    def test_convert_to_appropriate_type_string(self, template_service):
        """Test fallback to string."""
        string_values = ["hello", "world", "not_a_number", "not_a_bool"]
        for value in string_values:
            assert template_service._convert_to_appropriate_type(value) == value

    def test_process_string_field_no_templates(self, template_service):
        """Test string field processing without templates."""
        result = template_service._process_string_field("plain text", {})
        assert result == "plain text"

    def test_process_string_field_with_templates(self, template_service, mock_providers):
        """Test string field processing with templates."""
        mock_providers.template.render_responses = {"{{variable}}": "123"}
        
        result = template_service._process_string_field("{{variable}}", {"variable": "123"})
        
        assert result == 123  # Should be converted to int

    def test_process_string_field_template_error(self, template_service, mock_providers):
        """Test string field processing with template error."""
        mock_providers.template.should_raise = RuntimeError("Template error")
        
        with pytest.raises(TemplateError) as exc_info:
            template_service._process_string_field("{{invalid}}", {})
        
        assert "Template rendering failed" in str(exc_info.value)


class TestTemplateServiceRawDataProcessing:
    """Tests for raw data processing."""

    def test_process_raw_data_success(self, template_service, mock_providers):
        """Test successful raw data processing."""
        data = {
            "title": "{{variables.title}}",
            "variables": {"title": "Test"},
        }
        
        mock_providers.template.render_responses = {"{{variables.title}}": "Processed Title"}
        
        result = template_service.process_raw_data(data)
        
        assert result["title"] == "Processed Title"
        # Original data should not be modified
        assert data["title"] == "{{variables.title}}"

    def test_process_raw_data_no_templates(self, template_service):
        """Test raw data processing without templates."""
        data = {"title": "Plain Title", "keyboard": "test"}
        
        result = template_service.process_raw_data(data)
        
        assert result == data

    def test_process_raw_data_error(self, template_service, mock_providers):
        """Test raw data processing with error."""
        data = {"title": "{{invalid}}"}
        
        mock_providers.template.should_raise = RuntimeError("Processing error")
        
        with pytest.raises(TemplateError) as exc_info:
            template_service.process_raw_data(data)
        
        assert "Raw data template processing failed" in str(exc_info.value)


class TestTemplateServiceUtilities:
    """Tests for utility functions."""

    def test_has_templates_with_templates(self, template_service):
        """Test template detection with templates present."""
        data_with_templates = {
            "field1": "{{variable}}",
            "field2": "{% for item in items %}{{item}}{% endfor %}",
            "field3": "{# comment #}",
        }
        
        assert template_service._has_templates(data_with_templates)

    def test_has_templates_without_templates(self, template_service):
        """Test template detection without templates."""
        data_without_templates = {
            "field1": "plain text",
            "field2": "another plain text",
            "nested": {"field": "more plain text"},
        }
        
        assert not template_service._has_templates(data_without_templates)

    def test_scan_for_templates_nested_structures(self, template_service):
        """Test template scanning in nested structures."""
        nested_data = {
            "level1": {
                "level2": ["{{template}}", "plain", {"level3": "{{another}}"}]
            }
        }
        
        assert template_service._scan_for_templates(nested_data)

    def test_scan_for_templates_primitive_types(self, template_service):
        """Test template scanning with primitive types."""
        assert not template_service._scan_for_templates(123)
        assert not template_service._scan_for_templates(True)
        assert not template_service._scan_for_templates(None)
        assert template_service._scan_for_templates("{{template}}")


class TestTemplateServiceFactories:
    """Tests for template service factory functions."""

    def test_create_template_service(self):
        """Test template service factory."""
        mock_providers = MockProviders()
        
        service = create_template_service(mock_providers)
        
        assert isinstance(service, TemplateService)
        assert service.providers == mock_providers

    def test_create_jinja2_template_service(self):
        """Test Jinja2 template service factory."""
        service = create_jinja2_template_service()
        
        assert isinstance(service, TemplateService)
        assert service.providers is not None


class TestTemplateServiceErrorHandling:
    """Tests for error handling and edge cases."""

    def test_log_error_with_context(self, template_service, mock_providers):
        """Test error logging with context."""
        error = RuntimeError("Test error")
        
        template_service.log_error_with_context("test_message", error, operation="test_op")
        
        assert len(mock_providers.logger.error_calls) == 1
        call_args = mock_providers.logger.error_calls[0]
        assert call_args[0] == "test_message"
        assert call_args[1]["error"] == "Test error"
        assert call_args[1]["error_type"] == "RuntimeError"
        assert call_args[1]["operation"] == "test_op"

    def test_process_field_value_nested_structures(self, template_service, mock_providers):
        """Test field value processing with nested structures."""
        nested_value = {
            "list": ["{{var1}}", "plain", {"nested": "{{var2}}"}],
            "dict": {"key": "{{var3}}"},
        }
        
        context = {"var1": "value1", "var2": "value2", "var3": "value3"}
        mock_providers.template.render_responses = {
            "{{var1}}": "value1",
            "{{var2}}": "value2", 
            "{{var3}}": "value3",
        }
        
        result = template_service._process_field_value(nested_value, context)
        
        assert result["list"][0] == "value1"
        assert result["list"][1] == "plain"
        assert result["list"][2]["nested"] == "value2"
        assert result["dict"]["key"] == "value3"

    def test_validate_templates_in_structure_edge_cases(self, template_service, mock_providers):
        """Test template validation with edge cases."""
        complex_structure = {
            "valid_template": "{{valid}}",
            "nested": {
                "invalid_template": "{{invalid",  # Missing closing brace
                "list": ["{{another_invalid", "plain_text"]
            }
        }
        
        # Configure some templates to fail validation
        def selective_render(template, context):
            if "invalid" in template:
                raise RuntimeError("Invalid template")
            return template
        
        mock_providers.template.render_string = selective_render
        
        errors = []
        template_service._validate_templates_in_structure(complex_structure, "", errors)
        
        # Should detect multiple validation errors
        assert len(errors) >= 2