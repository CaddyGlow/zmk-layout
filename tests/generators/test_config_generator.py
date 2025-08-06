"""Comprehensive tests for config_generator module."""

import logging
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pytest import LogCaptureFixture

from zmk_layout.generators.config_generator import (
    build_template_context,
    convert_keymap_section_from_dict,
    generate_config_file,
    generate_config_file_with_result,
    generate_kconfig_conf,
    generate_keymap_file,
    generate_keymap_file_with_result,
    get_required_includes_for_layout,
)
from zmk_layout.models import LayoutData
from zmk_layout.models.metadata import ConfigParameter


class MockConfigOption:
    """Mock for a kconfig option definition in a profile."""

    def __init__(self, name: str, default: Any = None) -> None:
        self.name = name
        self.default = default


# ConfigParameter removed - using ConfigParameter directly


@pytest.fixture
def mock_file_provider() -> MagicMock:
    """A mock FileProvider that uses an in-memory dict as a filesystem."""
    fs = {}

    def write_text(path: Any, content: str) -> None:
        fs[str(path)] = content

    def exists(path: Any) -> bool:
        return str(path) in fs

    provider = MagicMock()
    provider.write_text.side_effect = write_text
    provider.exists.side_effect = exists
    provider.fs = fs  # Expose for assertions
    return provider


@pytest.fixture
def mock_template_adapter() -> MagicMock:
    """A mock template adapter."""
    adapter = MagicMock()
    adapter.render_string.side_effect = lambda t, c: t.format(
        **{k: v for k, v in c.items() if isinstance(v, str | int)}
    )
    adapter.render_template.side_effect = lambda t, c: f"TPL:{t}"
    return adapter


@pytest.fixture
def base_keymap_data() -> LayoutData:
    """Fixture for a basic LayoutData object."""
    return LayoutData(
        keyboard="test_board",
        title="Test Layout",  # Required field
        layer_names=["base", "raise"],
        layers=[[], []],
        config_parameters=[],
    )


@pytest.fixture
def base_profile() -> SimpleNamespace:
    """Fixture for a basic KeyboardProfile object."""
    return SimpleNamespace(
        keyboard_name="test_board",
        firmware_version="v1.0",
        kconfig_options={},
        keyboard_config=SimpleNamespace(
            keymap=SimpleNamespace(
                header_includes=["behaviors.dtsi", "dt-bindings/zmk/keys.h"],
                key_position_header="/* Key positions */",
                system_behaviors_dts="/* System behaviors */",
                keymap_dtsi=None,
                keymap_dtsi_file=None,
            ),
            zmk=SimpleNamespace(patterns=SimpleNamespace(kconfig_prefix="CONFIG_ZMK_")),
        ),
    )


class TestGetRequiredIncludesForLayout:
    """Tests for get_required_includes_for_layout function."""

    def test_returns_empty_list(
        self, base_profile: SimpleNamespace, base_keymap_data: LayoutData
    ) -> None:
        """Verify stub implementation returns empty list."""
        result = get_required_includes_for_layout(base_profile, base_keymap_data)
        assert result == []
        assert isinstance(result, list)


class TestGenerateConfigFile:
    """Tests for generate_config_file function."""

    def test_successful_generation(
        self,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test successful config file generation."""
        # Arrange
        output_path = Path("/test/zmk.conf")
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="IDLE_TIMEOUT", value=60000)
        ]
        base_profile.kconfig_options = {
            "IDLE_TIMEOUT": MockConfigOption("CONFIG_ZMK_IDLE_TIMEOUT", 30000)
        }

        # Act
        settings = generate_config_file(
            mock_file_provider, base_profile, base_keymap_data, output_path
        )

        # Assert
        assert str(output_path) in mock_file_provider.fs
        assert settings == {"CONFIG_ZMK_IDLE_TIMEOUT": 60000}
        content = mock_file_provider.fs[str(output_path)]
        assert "CONFIG_ZMK_IDLE_TIMEOUT=60000" in content

    def test_empty_config_parameters(
        self,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test generation with no config parameters."""
        # Arrange
        output_path = Path("/test/zmk.conf")

        # Act
        settings = generate_config_file(
            mock_file_provider, base_profile, base_keymap_data, output_path
        )

        # Assert
        assert str(output_path) in mock_file_provider.fs
        assert settings == {}
        content = mock_file_provider.fs[str(output_path)]
        assert "# Generated ZMK configuration" in content

    def test_file_write_error(
        self,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test handling of file write errors."""
        # Arrange
        output_path = Path("/test/zmk.conf")
        mock_file_provider.write_text.side_effect = OSError("Permission denied")

        # Act & Assert
        with pytest.raises(IOError, match="Permission denied"):
            generate_config_file(
                mock_file_provider, base_profile, base_keymap_data, output_path
            )

    def test_logging_of_settings(
        self,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test that kconfig settings are logged."""
        # Arrange
        output_path = Path("/test/zmk.conf")
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="IDLE_TIMEOUT", value=60000),
            ConfigParameter(paramName="SLEEP", value="y"),
        ]
        base_profile.kconfig_options = {
            "IDLE_TIMEOUT": MockConfigOption("CONFIG_ZMK_IDLE_TIMEOUT"),
            "SLEEP": MockConfigOption("CONFIG_ZMK_SLEEP"),
        }

        # Act
        with caplog.at_level(logging.DEBUG):
            settings = generate_config_file(
                mock_file_provider, base_profile, base_keymap_data, output_path
            )

        # Assert
        assert len(settings) == 2
        assert "Generated Kconfig with 2 options" in caplog.text


class TestBuildTemplateContext:
    """Tests for build_template_context function."""

    def test_full_profile_with_all_attributes(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test with complete profile containing all attributes."""
        # Arrange
        dtsi_generator = MagicMock()
        dtsi_generator._behavior_registry = {}

        # Act
        context = build_template_context(base_keymap_data, base_profile, dtsi_generator)

        # Assert
        assert context["keyboard"] == "test_board"
        assert context["layer_names"] == ["base", "raise"]
        assert len(context["layers"]) == 2
        assert context["profile_name"] == "test_board/v1.0"
        assert context["firmware_version"] == "v1.0"
        assert "#include <behaviors.dtsi>" in context["resolved_includes"]
        assert "#include <dt-bindings/zmk/keys.h>" in context["resolved_includes"]
        assert "generation_timestamp" in context
        assert context["key_position_header"] == "/* Key positions */"
        assert context["system_behaviors_dts"] == "/* System behaviors */"

    def test_missing_profile_attributes(self, base_keymap_data: LayoutData) -> None:
        """Test safe access with missing profile attributes."""
        # Arrange
        profile = SimpleNamespace()  # Minimal profile
        dtsi_generator = MagicMock()

        # Act
        context = build_template_context(base_keymap_data, profile, dtsi_generator)

        # Assert
        assert context["keyboard"] == "test_board"
        assert context["resolved_includes"] == ""
        assert context["key_position_header"] == ""
        assert context["system_behaviors_dts"] == ""
        assert context["profile_name"] == "unknown"
        assert context["firmware_version"] == "unknown"

    def test_empty_and_none_includes(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test handling of empty or None includes."""
        # Arrange
        base_profile.keyboard_config.keymap.header_includes = None
        dtsi_generator = MagicMock()

        # Act
        context = build_template_context(base_keymap_data, base_profile, dtsi_generator)

        # Assert
        assert context["resolved_includes"] == ""

    def test_custom_behaviors_and_devicetree(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test custom defined behaviors and devicetree."""
        # Arrange
        base_keymap_data.custom_defined_behaviors = "/* Custom behaviors */"
        base_keymap_data.custom_devicetree = "/* Custom devicetree */"
        dtsi_generator = MagicMock()

        # Act
        context = build_template_context(base_keymap_data, base_profile, dtsi_generator)

        # Assert
        assert context["custom_defined_behaviors"] == "/* Custom behaviors */"
        assert context["custom_devicetree"] == "/* Custom devicetree */"

    def test_behavior_manager_integration(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test integration with behavior manager."""
        # Arrange
        dtsi_generator = MagicMock()
        dtsi_generator._behavior_registry = {}
        behavior_manager = MagicMock()
        behavior_manager.get_behavior_registry.return_value = {"test": "behavior"}

        # Act
        build_template_context(
            base_keymap_data, base_profile, dtsi_generator, behavior_manager
        )

        # Assert
        behavior_manager.prepare_behaviors.assert_called_once_with(
            base_profile, base_keymap_data
        )
        assert dtsi_generator._behavior_registry == {"test": "behavior"}

    @patch("zmk_layout.generators.config_generator.datetime")
    def test_timestamp_generation(
        self,
        mock_datetime: MagicMock,
        base_keymap_data: LayoutData,
        base_profile: SimpleNamespace,
    ) -> None:
        """Test that timestamp is generated correctly."""
        # Arrange
        mock_now = datetime(2024, 1, 15, 10, 30, 45)
        mock_datetime.now.return_value = mock_now
        dtsi_generator = MagicMock()

        # Act
        context = build_template_context(base_keymap_data, base_profile, dtsi_generator)

        # Assert
        assert context["generation_timestamp"] == "2024-01-15T10:30:45"


class TestGenerateKconfigConf:
    """Tests for generate_kconfig_conf function."""

    def test_supported_option_non_default(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test supported option with non-default value."""
        # Arrange
        base_profile.kconfig_options = {
            "IDLE_TIMEOUT": MockConfigOption("CONFIG_ZMK_IDLE_TIMEOUT", 30000)
        }
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="IDLE_TIMEOUT", value=60000)
        ]

        # Act
        content, settings = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert "CONFIG_ZMK_IDLE_TIMEOUT=60000" in content
        assert "# CONFIG_ZMK_IDLE_TIMEOUT" not in content
        assert settings == {"CONFIG_ZMK_IDLE_TIMEOUT": 60000}

    def test_supported_option_with_default_value(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test option set to default value is commented out."""
        # Arrange
        base_profile.kconfig_options = {
            "IDLE_TIMEOUT": MockConfigOption("CONFIG_ZMK_IDLE_TIMEOUT", 30000)
        }
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="IDLE_TIMEOUT", value=30000)
        ]

        # Act
        content, settings = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert "# CONFIG_ZMK_IDLE_TIMEOUT=30000" in content
        assert settings == {}

    def test_unsupported_option(
        self,
        base_keymap_data: LayoutData,
        base_profile: SimpleNamespace,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test unsupported option is commented with warning."""
        # Arrange
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="UNKNOWN_OPTION", value="value")
        ]

        # Act
        with caplog.at_level(logging.WARNING):
            content, settings = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert "Unsupported kconfig option 'UNKNOWN_OPTION'" in caplog.text
        assert (
            "# Warning: 'UNKNOWN_OPTION' is not a supported kconfig option" in content
        )
        assert "# CONFIG_ZMK_UNKNOWN_OPTION=value" in content
        assert settings == {}

    def test_empty_config_parameters(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test with no config parameters."""
        # Act
        content, settings = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert content == "# Generated ZMK configuration"
        assert settings == {}

    def test_custom_kconfig_prefix(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test custom kconfig prefix for unsupported options."""
        # Arrange
        base_profile.keyboard_config.zmk.patterns.kconfig_prefix = "CONFIG_CUSTOM_"
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="TEST", value=123)
        ]

        # Act
        content, _ = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert "# CONFIG_CUSTOM_TEST=123" in content

    def test_option_already_has_prefix(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test that options with prefix aren't double-prefixed."""
        # Arrange
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="CONFIG_ZMK_ALREADY_PREFIXED", value="yes")
        ]

        # Act
        content, _ = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert "# CONFIG_ZMK_CONFIG_ZMK_ALREADY_PREFIXED=yes" not in content
        # The option name itself already starts with the prefix, so logic may vary

    def test_special_characters_in_values(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test handling of special characters in config values."""
        # Arrange
        base_profile.kconfig_options = {
            "STRING_OPT": MockConfigOption("CONFIG_ZMK_STRING")
        }
        base_keymap_data.config_parameters = [
            ConfigParameter(
                paramName="STRING_OPT", value="value with spaces and 'quotes'"
            )
        ]

        # Act
        content, settings = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert "CONFIG_ZMK_STRING=value with spaces and 'quotes'" in content
        assert settings["CONFIG_ZMK_STRING"] == "value with spaces and 'quotes'"


class TestGenerateKeymapFile:
    """Tests for generate_keymap_file function."""

    def test_inline_template_rendering(
        self,
        mock_file_provider: MagicMock,
        mock_template_adapter: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test rendering with inline template."""
        # Arrange
        output_path = Path("/test/keymap.dtsi")
        base_profile.keyboard_config.keymap.keymap_dtsi = "Keyboard: {keyboard}"
        dtsi_generator = MagicMock()
        dtsi_generator._behavior_registry = {}

        # Act
        generate_keymap_file(
            mock_file_provider,
            mock_template_adapter,
            dtsi_generator,
            base_keymap_data,
            base_profile,
            output_path,
        )

        # Assert
        mock_template_adapter.render_string.assert_called_once()
        assert str(output_path) in mock_file_provider.fs

    @patch("zmk_layout.utils.resolve_template_file_path")
    def test_file_template_rendering(
        self,
        mock_resolve: MagicMock,
        mock_file_provider: MagicMock,
        mock_template_adapter: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test rendering with file-based template."""
        # Arrange
        output_path = Path("/test/keymap.dtsi")
        base_profile.keyboard_config.keymap.keymap_dtsi_file = "keymap.template"
        template_path = Path("/templates/keymap.template")
        mock_resolve.return_value = template_path
        dtsi_generator = MagicMock()

        # Act
        generate_keymap_file(
            mock_file_provider,
            mock_template_adapter,
            dtsi_generator,
            base_keymap_data,
            base_profile,
            output_path,
        )

        # Assert
        mock_resolve.assert_called_once_with("test_board", "keymap.template")
        mock_template_adapter.render_template.assert_called_once()
        assert str(output_path) in mock_file_provider.fs

    def test_no_template_fallback(
        self,
        mock_file_provider: MagicMock,
        mock_template_adapter: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test fallback when no template is specified."""
        # Arrange
        output_path = Path("/test/keymap.dtsi")
        base_profile.keyboard_config.keymap.keymap_dtsi = None
        base_profile.keyboard_config.keymap.keymap_dtsi_file = None
        dtsi_generator = MagicMock()

        # Act
        generate_keymap_file(
            mock_file_provider,
            mock_template_adapter,
            dtsi_generator,
            base_keymap_data,
            base_profile,
            output_path,
        )

        # Assert
        assert str(output_path) in mock_file_provider.fs
        content = mock_file_provider.fs[str(output_path)]
        assert "/* Generated ZMK keymap */" in content

    def test_template_rendering_error(
        self,
        mock_file_provider: MagicMock,
        mock_template_adapter: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test handling of template rendering errors."""
        # Arrange
        output_path = Path("/test/keymap.dtsi")
        base_profile.keyboard_config.keymap.keymap_dtsi = "Bad template"
        mock_template_adapter.render_string.side_effect = ValueError("Template error")
        dtsi_generator = MagicMock()

        # Act & Assert
        with pytest.raises(ValueError, match="Template error"):
            generate_keymap_file(
                mock_file_provider,
                mock_template_adapter,
                dtsi_generator,
                base_keymap_data,
                base_profile,
                output_path,
            )


class TestConvertKeymapSectionFromDict:
    """Tests for convert_keymap_section_from_dict function."""

    def test_all_fields_present(self) -> None:
        """Test conversion with all fields present."""
        # Arrange
        keymap_dict = {
            "header_includes": ["test.h"],
            "system_behaviors": ["&bt"],
            "kconfig_options": {"OPT": "val"},
            "keymap_dtsi": "inline template",
            "keymap_dtsi_file": "template.dtsi",
            "system_behaviors_dts": "/* behaviors */",
            "key_position_header": "/* positions */",
        }

        # Act
        result = convert_keymap_section_from_dict(keymap_dict)

        # Assert
        assert result["header_includes"] == ["test.h"]
        assert result["system_behaviors"] == ["&bt"]
        assert result["kconfig_options"] == {"OPT": "val"}
        assert result["keymap_dtsi"] == "inline template"
        assert result["keymap_dtsi_file"] == "template.dtsi"
        assert result["system_behaviors_dts"] == "/* behaviors */"
        assert result["key_position_header"] == "/* positions */"

    def test_missing_fields_with_defaults(self) -> None:
        """Test conversion with missing fields uses defaults."""
        # Arrange
        keymap_dict: dict[str, Any] = {}

        # Act
        result = convert_keymap_section_from_dict(keymap_dict)

        # Assert
        assert result["header_includes"] == []
        assert result["system_behaviors"] == []
        assert result["kconfig_options"] == {}
        assert result["keymap_dtsi"] is None
        assert result["keymap_dtsi_file"] is None
        assert result["system_behaviors_dts"] is None
        assert result["key_position_header"] is None

    def test_legacy_field_names(self) -> None:
        """Test handling of legacy field names."""
        # Arrange
        keymap_dict = {
            "includes": ["legacy.h"],  # Legacy name for header_includes
        }

        # Act
        result = convert_keymap_section_from_dict(keymap_dict)

        # Assert
        assert result["header_includes"] == ["legacy.h"]


class TestGenerateKeymapFileWithResult:
    """Tests for generate_keymap_file_with_result wrapper."""

    def test_successful_generation(
        self,
        mock_file_provider: MagicMock,
        mock_template_adapter: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test successful keymap generation."""
        # Arrange
        output_path = Path("/test/keymap.dtsi")
        behavior_formatter = MagicMock()

        # Act
        result = generate_keymap_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            behavior_formatter,
            mock_template_adapter,
            mock_file_provider,
            force=False,
        )

        # Assert
        assert result.success is True
        assert result.keymap_path == str(output_path)
        assert "Generated keymap file" in result.messages[0]
        assert str(output_path) in mock_file_provider.fs

    def test_file_exists_without_force(
        self,
        mock_file_provider: MagicMock,
        mock_template_adapter: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test generation fails when file exists and force is False."""
        # Arrange
        output_path = Path("/test/keymap.dtsi")
        mock_file_provider.fs[str(output_path)] = "existing"
        behavior_formatter = MagicMock()

        # Act
        result = generate_keymap_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            behavior_formatter,
            mock_template_adapter,
            mock_file_provider,
            force=False,
        )

        # Assert
        assert result.success is False
        assert "Keymap file already exists" in result.errors[0]
        assert mock_file_provider.fs[str(output_path)] == "existing"

    def test_file_exists_with_force(
        self,
        mock_file_provider: MagicMock,
        mock_template_adapter: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test generation succeeds when file exists and force is True."""
        # Arrange
        output_path = Path("/test/keymap.dtsi")
        mock_file_provider.fs[str(output_path)] = "existing"
        behavior_formatter = MagicMock()

        # Act
        result = generate_keymap_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            behavior_formatter,
            mock_template_adapter,
            mock_file_provider,
            force=True,
        )

        # Assert
        assert result.success is True
        assert "Generated keymap file" in result.messages[0]
        assert mock_file_provider.fs[str(output_path)] != "existing"

    @patch("zmk_layout.generators.config_generator.generate_keymap_file")
    def test_exception_handling(
        self,
        mock_generate: MagicMock,
        mock_file_provider: MagicMock,
        mock_template_adapter: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test exception handling during generation."""
        # Arrange
        output_path = Path("/test/keymap.dtsi")
        mock_generate.side_effect = RuntimeError("Generation failed")
        behavior_formatter = MagicMock()

        # Act
        result = generate_keymap_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            behavior_formatter,
            mock_template_adapter,
            mock_file_provider,
            force=True,
        )

        # Assert
        assert result.success is False
        assert "Keymap generation failed: Generation failed" in result.errors[0]


class TestGenerateConfigFileWithResult:
    """Tests for generate_config_file_with_result wrapper."""

    def test_successful_generation(
        self,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test successful config generation."""
        # Arrange
        output_path = Path("/test/zmk.conf")
        dtsi_generator = MagicMock()

        # Act
        result = generate_config_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            dtsi_generator,
            mock_file_provider,
            force=False,
        )

        # Assert
        assert result.success is True
        assert result.conf_path == str(output_path)
        assert "Generated config file" in result.messages[0]
        assert str(output_path) in mock_file_provider.fs

    def test_file_exists_without_force(
        self,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test generation fails when file exists and force is False."""
        # Arrange
        output_path = Path("/test/zmk.conf")
        mock_file_provider.fs[str(output_path)] = "existing"
        dtsi_generator = MagicMock()

        # Act
        result = generate_config_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            dtsi_generator,
            mock_file_provider,
            force=False,
        )

        # Assert
        assert result.success is False
        assert "Config file already exists" in result.errors[0]
        assert mock_file_provider.fs[str(output_path)] == "existing"

    def test_file_exists_with_force(
        self,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test generation succeeds when file exists and force is True."""
        # Arrange
        output_path = Path("/test/zmk.conf")
        mock_file_provider.fs[str(output_path)] = "existing"
        dtsi_generator = MagicMock()

        # Act
        result = generate_config_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            dtsi_generator,
            mock_file_provider,
            force=True,
        )

        # Assert
        assert result.success is True
        assert "Generated config file" in result.messages[0]
        assert mock_file_provider.fs[str(output_path)] != "existing"

    @patch("zmk_layout.generators.config_generator.generate_config_file")
    def test_exception_handling(
        self,
        mock_generate: MagicMock,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test exception handling during generation."""
        # Arrange
        output_path = Path("/test/zmk.conf")
        mock_generate.side_effect = OSError("Disk full")
        dtsi_generator = MagicMock()

        # Act
        result = generate_config_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            dtsi_generator,
            mock_file_provider,
            force=True,
        )

        # Assert
        assert result.success is False
        assert "Config generation failed: Disk full" in result.errors[0]

    def test_with_kconfig_settings(
        self,
        mock_file_provider: MagicMock,
        base_profile: SimpleNamespace,
        base_keymap_data: LayoutData,
    ) -> None:
        """Test message includes kconfig settings count."""
        # Arrange
        output_path = Path("/test/zmk.conf")
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="OPT1", value="val1"),
            ConfigParameter(paramName="OPT2", value="val2"),
        ]
        base_profile.kconfig_options = {
            "OPT1": MockConfigOption("CONFIG_OPT1"),
            "OPT2": MockConfigOption("CONFIG_OPT2"),
        }
        dtsi_generator = MagicMock()

        # Act
        result = generate_config_file_with_result(
            base_profile,
            base_keymap_data,
            {},
            output_path,
            dtsi_generator,
            mock_file_provider,
            force=False,
        )

        # Assert
        assert result.success is True
        assert "Applied 2 configuration options" in result.messages[1]


class TestEdgeCasesAndBoundaryConditions:
    """Tests for edge cases and boundary conditions."""

    def test_unicode_in_config_values(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test handling of Unicode characters in config values."""
        # Arrange
        base_profile.kconfig_options = {"NAME": MockConfigOption("CONFIG_NAME")}
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="NAME", value="Unicode: 你好 😊")
        ]

        # Act
        content, settings = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert "CONFIG_NAME=Unicode: 你好 😊" in content
        assert settings["CONFIG_NAME"] == "Unicode: 你好 😊"

    def test_very_long_config_value(
        self, base_keymap_data: LayoutData, base_profile: SimpleNamespace
    ) -> None:
        """Test handling of very long config values."""
        # Arrange
        long_value = "A" * 10000
        base_profile.kconfig_options = {"LONG": MockConfigOption("CONFIG_LONG")}
        base_keymap_data.config_parameters = [
            ConfigParameter(paramName="LONG", value=long_value)
        ]

        # Act
        content, settings = generate_kconfig_conf(base_keymap_data, base_profile)

        # Assert
        assert f"CONFIG_LONG={long_value}" in content
        assert settings["CONFIG_LONG"] == long_value

    def test_none_values_in_optional_fields(self, base_keymap_data: LayoutData) -> None:
        """Test handling of None values in optional fields."""
        # Arrange
        base_keymap_data.custom_defined_behaviors = ""
        base_keymap_data.custom_devicetree = ""
        profile = SimpleNamespace()
        dtsi_generator = MagicMock()

        # Act
        context = build_template_context(base_keymap_data, profile, dtsi_generator)

        # Assert
        assert context["custom_defined_behaviors"] == ""
        assert context["custom_devicetree"] == ""

    def test_empty_layers_and_behaviors(self) -> None:
        """Test with completely empty layout data."""
        # Arrange
        keymap_data = LayoutData(
            keyboard="empty",
            title="Empty Layout",  # Required field
            layer_names=[],
            layers=[],
        )
        profile = SimpleNamespace()
        dtsi_generator = MagicMock()

        # Act
        context = build_template_context(keymap_data, profile, dtsi_generator)

        # Assert
        assert context["keyboard"] == "empty"
        assert context["layer_names"] == []
        assert context["layers"] == []

    def test_missing_keyboard_config_in_profile(
        self, base_keymap_data: LayoutData
    ) -> None:
        """Test when profile has no keyboard_config attribute."""
        # Arrange
        profile = SimpleNamespace(
            keyboard_name="test", firmware_version="v1", kconfig_options={}
        )
        dtsi_generator = MagicMock()

        # Act
        context = build_template_context(base_keymap_data, profile, dtsi_generator)

        # Assert
        assert context["resolved_includes"] == ""
        assert context["key_position_header"] == ""
        assert context["system_behaviors_dts"] == ""

    def test_profile_with_partial_nested_structure(
        self, base_keymap_data: LayoutData
    ) -> None:
        """Test profile with partially missing nested attributes."""
        # Arrange
        profile = SimpleNamespace(
            keyboard_name="partial",
            firmware_version="v2",
            keyboard_config=SimpleNamespace(),  # Has keyboard_config but no keymap
        )
        dtsi_generator = MagicMock()

        # Act
        context = build_template_context(base_keymap_data, profile, dtsi_generator)

        # Assert
        assert context["profile_name"] == "partial/v2"
        assert context["resolved_includes"] == ""
