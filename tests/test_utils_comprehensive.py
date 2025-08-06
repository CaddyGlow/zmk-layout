"""Comprehensive tests for zmk_layout utils modules."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from zmk_layout.models import LayoutBinding, LayoutData
from zmk_layout.utils.json_operations import (
    VariableResolutionContext,
    parse_layout_data,
    serialize_layout_data,
    should_skip_variable_resolution,
)
from zmk_layout.utils.layer_references import (
    LayoutError,
    OutputPaths,
    prepare_output_paths,
    process_json_file,
    resolve_template_file_path,
)
from zmk_layout.utils.validation import (
    validate_layer_exists,
    validate_layer_has_bindings,
    validate_layer_name_unique,
    validate_output_path,
    validate_position_index,
)


class TestVariableResolutionContext:
    """Test VariableResolutionContext functionality."""

    def test_context_manager_basic(self) -> None:
        """Test basic context manager functionality."""
        with VariableResolutionContext(skip=True):
            assert should_skip_variable_resolution() is True

    def test_context_manager_nested(self) -> None:
        """Test nested context managers."""
        original = should_skip_variable_resolution()

        with VariableResolutionContext(skip=True):
            assert should_skip_variable_resolution() is True

            with VariableResolutionContext(skip=False):
                assert should_skip_variable_resolution() is False

            assert should_skip_variable_resolution() is True

        assert should_skip_variable_resolution() == original

    def test_context_manager_exception_handling(self) -> None:
        """Test context manager restores state on exception."""
        original = should_skip_variable_resolution()

        try:
            with VariableResolutionContext(skip=True):
                assert should_skip_variable_resolution() is True
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert should_skip_variable_resolution() == original


class TestJSONOperations:
    """Test JSON operations functionality."""

    @pytest.fixture
    def mock_file_provider(self) -> Mock:
        """Create mock file provider."""
        provider = Mock()
        provider.exists.return_value = True
        provider.read_text.return_value = '{"keyboard": "test", "title": "Test Layout", "layers": [], "layer_names": []}'
        return provider

    @pytest.fixture
    def sample_layout_data(self) -> LayoutData:
        """Create sample layout data."""
        return LayoutData(
            keyboard="test_keyboard", title="Test Layout", layers=[], layer_names=[]
        )

    def test_parse_layout_data_success(self) -> None:
        """Test successful layout data parsing."""
        json_content = '{"keyboard": "test", "title": "Test Layout", "layers": [], "layer_names": []}'
        result = parse_layout_data(json_content)

        assert isinstance(result, LayoutData)
        assert result.keyboard == "test"
        assert result.title == "Test Layout"

    def test_parse_layout_data_invalid_json(self) -> None:
        """Test parsing invalid JSON."""
        invalid_json = "invalid json"

        with pytest.raises(json.JSONDecodeError):
            parse_layout_data(invalid_json)

    def test_parse_layout_data_invalid_data(self) -> None:
        """Test parsing invalid layout data."""
        invalid_data = '{"invalid": "data"}'

        with pytest.raises(ValueError, match="Invalid layout data"):
            parse_layout_data(invalid_data)

    def test_serialize_layout_data_success(
        self, sample_layout_data: LayoutData
    ) -> None:
        """Test successful layout data serialization."""
        result = serialize_layout_data(sample_layout_data)

        # Should be valid JSON
        parsed_back = json.loads(result)
        assert parsed_back["keyboard"] == "test_keyboard"

    def test_parse_layout_data_roundtrip(self, sample_layout_data: LayoutData) -> None:
        """Test roundtrip serialization and parsing."""
        # Serialize to JSON string
        serialized = serialize_layout_data(sample_layout_data)

        # Parse back from string
        parsed = parse_layout_data(serialized)

        # Should match original
        assert parsed.keyboard == sample_layout_data.keyboard
        assert parsed.title == sample_layout_data.title

    def test_parse_layout_data_with_skip_variable_resolution(
        self, sample_layout_data: LayoutData
    ) -> None:
        """Test parsing with skip variable resolution flag."""
        serialized = serialize_layout_data(sample_layout_data)

        # Parse with skip_variable_resolution=True
        parsed = parse_layout_data(serialized, skip_variable_resolution=True)

        assert parsed.keyboard == sample_layout_data.keyboard

    def test_parse_layout_data_with_dict_input(self) -> None:
        """Test parsing with dictionary input instead of JSON string."""
        test_data = {
            "keyboard": "test",
            "title": "Test",
            "layers": [],
            "layer_names": [],
        }

        result = parse_layout_data(test_data)
        assert isinstance(result, LayoutData)
        assert result.keyboard == "test"


class TestValidation:
    """Test validation utilities."""

    @pytest.fixture
    def sample_layout_data(self) -> LayoutData:
        """Create sample layout data."""
        return LayoutData(
            keyboard="test",
            title="Test",
            layer_names=["default", "lower", "raise"],
            layers=[
                [LayoutBinding(value="&kp A")],
                [LayoutBinding(value="&kp B")],
                [LayoutBinding(value="&kp C")],
            ],
        )

    def test_validate_layer_exists_success(
        self, sample_layout_data: LayoutData
    ) -> None:
        """Test successful layer validation."""
        result = validate_layer_exists(sample_layout_data, "lower")
        assert result == 1

    def test_validate_layer_exists_failure(
        self, sample_layout_data: LayoutData
    ) -> None:
        """Test layer validation failure."""
        with pytest.raises(ValueError, match="Layer 'missing' not found"):
            validate_layer_exists(sample_layout_data, "missing")

    def test_validate_layer_has_bindings_success(
        self, sample_layout_data: LayoutData
    ) -> None:
        """Test successful layer binding validation."""
        # Should not raise
        validate_layer_has_bindings(sample_layout_data, "default", 0)

    def test_validate_layer_has_bindings_failure(
        self, sample_layout_data: LayoutData
    ) -> None:
        """Test layer binding validation failure."""
        with pytest.raises(ValueError, match="has no binding data"):
            validate_layer_has_bindings(sample_layout_data, "missing", 10)

    def test_validate_output_path_success(self, tmp_path: Path) -> None:
        """Test successful output path validation."""
        output_file = tmp_path / "output.json"
        # Should not raise
        validate_output_path(output_file)

    def test_validate_output_path_exists_no_force(self, tmp_path: Path) -> None:
        """Test output path validation with existing file."""
        output_file = tmp_path / "existing.json"
        output_file.write_text("existing content")

        with pytest.raises(ValueError, match="already exists"):
            validate_output_path(output_file)

    def test_validate_output_path_exists_with_force(self, tmp_path: Path) -> None:
        """Test output path validation with force flag."""
        output_file = tmp_path / "existing.json"
        output_file.write_text("existing content")

        # Should not raise with force
        validate_output_path(output_file, force=True)

    def test_validate_position_index_none_allow_append(self) -> None:
        """Test position validation with None and append allowed."""
        result = validate_position_index(None, 5, allow_append=True)
        assert result == 5

    def test_validate_position_index_none_no_append(self) -> None:
        """Test position validation with None and append not allowed."""
        with pytest.raises(ValueError, match="must be specified"):
            validate_position_index(None, 5, allow_append=False)

    def test_validate_position_index_positive(self) -> None:
        """Test position validation with positive index."""
        result = validate_position_index(2, 5)
        assert result == 2

    def test_validate_position_index_negative(self) -> None:
        """Test position validation with negative index."""
        result = validate_position_index(-1, 5)
        assert result == 5  # Should be normalized

    def test_validate_position_index_out_of_bounds(self) -> None:
        """Test position validation with out of bounds index."""
        result = validate_position_index(10, 5)
        assert result == 5  # Should be clamped

    def test_validate_layer_name_unique_success(
        self, sample_layout_data: LayoutData
    ) -> None:
        """Test successful unique layer name validation."""
        # Should not raise
        validate_layer_name_unique(sample_layout_data, "new_layer")

    def test_validate_layer_name_unique_failure(
        self, sample_layout_data: LayoutData
    ) -> None:
        """Test unique layer name validation failure."""
        with pytest.raises(ValueError, match="already exists"):
            validate_layer_name_unique(sample_layout_data, "default")


class TestLayerReferences:
    """Test layer references and core operations."""

    def test_output_paths_creation(self) -> None:
        """Test OutputPaths creation."""
        paths = OutputPaths(
            keymap=Path("test.keymap"), conf=Path("test.conf"), json=Path("test.json")
        )

        assert paths.keymap == Path("test.keymap")
        assert paths.conf == Path("test.conf")
        assert paths.json == Path("test.json")

    def test_layout_error(self) -> None:
        """Test LayoutError exception."""
        error = LayoutError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_prepare_output_paths_basic(self) -> None:
        """Test basic output path preparation."""
        result = prepare_output_paths("/tmp/my_keymap")

        assert result.keymap == Path("/tmp/my_keymap.keymap")
        assert result.conf == Path("/tmp/my_keymap.conf")
        assert result.json == Path("/tmp/my_keymap.json")

    def test_prepare_output_paths_with_path_object(self) -> None:
        """Test output path preparation with Path object."""
        input_path = Path("/home/user/layouts/custom")
        result = prepare_output_paths(input_path)

        assert result.keymap.name == "custom.keymap"
        assert result.conf.name == "custom.conf"
        assert result.json.name == "custom.json"

    def test_process_json_file_success(self, tmp_path: Path) -> None:
        """Test successful JSON file processing."""
        # Create test file
        test_file = tmp_path / "test.json"
        layout_data = LayoutData(
            keyboard="test", title="Test", layers=[], layer_names=[]
        )
        test_file.write_text(layout_data.model_dump_json())

        # Mock logger
        logger = Mock()

        # Test operation function
        def test_operation(data: LayoutData) -> str:
            return f"Processed {data.keyboard}"

        result = process_json_file(
            test_file, "test operation", test_operation, logger
        )

        assert result == "Processed test"
        logger.info.assert_called_once()

    def test_process_json_file_failure(self, tmp_path: Path) -> None:
        """Test JSON file processing failure."""
        test_file = tmp_path / "nonexistent.json"  # File doesn't exist

        # Mock logger
        logger = Mock()

        def test_operation(data: LayoutData) -> str:
            return "success"

        with pytest.raises(LayoutError, match="test operation failed"):
            process_json_file(
                test_file, "test operation", test_operation, logger
            )

        logger.error.assert_called_once()

    def test_resolve_template_file_path_absolute(self, tmp_path: Path) -> None:
        """Test template path resolution with absolute path."""
        template_file = tmp_path / "template.txt"
        template_file.write_text("template content")

        result = resolve_template_file_path("keyboard", str(template_file))
        assert result == template_file.resolve()

    def test_resolve_template_file_path_absolute_not_found(self) -> None:
        """Test template path resolution with non-existent absolute path."""
        with pytest.raises(LayoutError, match="Template file not found"):
            resolve_template_file_path("keyboard", "/nonexistent/template.txt")

    def test_resolve_template_file_path_relative_with_provider(
        self, tmp_path: Path
    ) -> None:
        """Test template path resolution with relative path and provider."""
        # Setup directory structure
        keyboard_dir = tmp_path / "test_keyboard"
        keyboard_dir.mkdir()
        template_file = keyboard_dir / "template.txt"
        template_file.write_text("template content")

        # Mock configuration provider
        config_provider = Mock()
        config_provider.get_search_paths.return_value = [tmp_path]

        result = resolve_template_file_path(
            "test_keyboard", "template.txt", config_provider
        )
        assert result == template_file.resolve()

    def test_resolve_template_file_path_relative_search_root(
        self, tmp_path: Path
    ) -> None:
        """Test template path resolution in search root."""
        # Setup template in search root
        template_file = tmp_path / "template.txt"
        template_file.write_text("template content")

        # Mock configuration provider
        config_provider = Mock()
        config_provider.get_search_paths.return_value = [tmp_path]

        result = resolve_template_file_path("keyboard", "template.txt", config_provider)
        assert result == template_file.resolve()

    def test_resolve_template_file_path_not_found(self, tmp_path: Path) -> None:
        """Test template path resolution failure."""
        config_provider = Mock()
        config_provider.get_search_paths.return_value = [tmp_path]

        with pytest.raises(LayoutError, match="Template file not found"):
            resolve_template_file_path("keyboard", "missing.txt", config_provider)

    def test_resolve_template_file_path_no_provider(self, tmp_path: Path) -> None:
        """Test template path resolution without provider."""
        template_file = tmp_path / "template.txt"
        template_file.write_text("template content")

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            result = resolve_template_file_path("keyboard", "template.txt")
            assert result == template_file.resolve()
