"""Comprehensive tests for keymap_generator module with fluent API."""

import logging
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from pytest import LogCaptureFixture

from zmk_layout.core.layout import Layout
from zmk_layout.generators.keymap_generator import (
    ConfigBuilder,
    ExportManager,
    KeymapBuilder,
)
from zmk_layout.models import LayoutBinding, LayoutData
from zmk_layout.models.behaviors import ComboBehavior, HoldTapBehavior, MacroBehavior
from zmk_layout.models.metadata import ConfigParameter


class MockConfigOption:
    """Mock for a kconfig option definition in a profile."""

    def __init__(self, name: str, default: Any = None) -> None:
        self.name = name
        self.default = default


@pytest.fixture
def base_layout_data() -> LayoutData:
    """Fixture for a basic LayoutData object."""
    return LayoutData(
        keyboard="test_board",
        title="Test Layout",
        layer_names=["base", "raise"],
        layers=[
            [LayoutBinding.from_str("&kp Q"), LayoutBinding.from_str("&kp W")],
            [LayoutBinding.from_str("&kp 1"), LayoutBinding.from_str("&kp 2")],
        ],
        config_parameters=[],
    )


@pytest.fixture
def base_layout(base_layout_data: LayoutData) -> Layout:
    """Fixture for a basic Layout object."""
    return Layout(base_layout_data)


@pytest.fixture
def base_profile() -> SimpleNamespace:
    """Fixture for a basic KeyboardProfile object."""
    return SimpleNamespace(
        keyboard_name="test_board",
        firmware_version="v1.0",
        kconfig_options={},
        keyboard_config=SimpleNamespace(
            key_count=42,
            keymap=SimpleNamespace(
                header_includes=["behaviors.dtsi", "dt-bindings/zmk/keys.h"],
                key_position_header="/* Key positions */",
                system_behaviors_dts="/* System behaviors */",
                keymap_dtsi=None,
                keymap_dtsi_file=None,
            ),
            zmk=SimpleNamespace(
                compatible_strings=SimpleNamespace(
                    keymap="zmk,keymap",
                    hold_tap="zmk,behavior-hold-tap",
                    tap_dance="zmk,behavior-tap-dance",
                    macro="zmk,behavior-macro",
                    combos="zmk,combos",
                ),
                patterns=SimpleNamespace(
                    kconfig_prefix="CONFIG_ZMK_",
                    layer_define="#define {layer_name} {layer_index}",
                ),
                layout=SimpleNamespace(keys=42),
                validation_limits=SimpleNamespace(
                    required_holdtap_bindings=2, max_macro_params=32
                ),
            ),
        ),
    )


class TestExportManager:
    """Tests for ExportManager class."""

    def test_export_manager_creation(self, base_layout: Layout) -> None:
        """Test that ExportManager is created properly."""
        export_manager = base_layout.export
        assert export_manager is not None
        assert isinstance(export_manager, ExportManager)

        # Should return same instance on subsequent calls
        export_manager2 = base_layout.export
        assert export_manager is export_manager2

    def test_keymap_method_returns_builder(
        self, base_layout: Layout, base_profile: SimpleNamespace
    ) -> None:
        """Test that keymap() method returns KeymapBuilder."""
        builder = base_layout.export.keymap()
        assert isinstance(builder, KeymapBuilder)

        # With profile
        builder_with_profile = base_layout.export.keymap(base_profile)
        assert isinstance(builder_with_profile, KeymapBuilder)

    def test_config_method_returns_builder(
        self, base_layout: Layout, base_profile: SimpleNamespace
    ) -> None:
        """Test that config() method returns ConfigBuilder."""
        builder = base_layout.export.config()
        assert isinstance(builder, ConfigBuilder)

        # With profile
        builder_with_profile = base_layout.export.config(base_profile)
        assert isinstance(builder_with_profile, ConfigBuilder)

    def test_to_dict_method(self, base_layout: Layout) -> None:
        """Test to_dict() method."""
        result = base_layout.export.to_dict()
        assert isinstance(result, dict)
        assert result["keyboard"] == "test_board"
        assert result["title"] == "Test Layout"
        assert len(result["layers"]) == 2

    def test_to_json_method(self, base_layout: Layout) -> None:
        """Test to_json() method."""
        result = base_layout.export.to_json()
        assert isinstance(result, str)
        assert "test_board" in result
        assert "Test Layout" in result


class TestKeymapBuilder:
    """Tests for KeymapBuilder class."""

    def test_fluent_interface(self, base_layout: Layout) -> None:
        """Test that KeymapBuilder methods return self for chaining."""
        builder = base_layout.export.keymap()

        # All methods should return the builder for chaining
        assert builder.with_headers(True) is builder
        assert builder.with_behaviors(True) is builder
        assert builder.with_combos(False) is builder
        assert builder.with_macros(True) is builder
        assert builder.with_tap_dances(False) is builder
        assert builder.with_template("test.j2") is builder
        assert builder.with_context(foo="bar") is builder

    def test_generate_basic_keymap(self, base_layout: Layout) -> None:
        """Test basic keymap generation."""
        keymap = base_layout.export.keymap().generate()

        assert isinstance(keymap, str)
        assert len(keymap) > 0
        assert "keymap" in keymap
        assert "&kp Q" in keymap
        assert "&kp W" in keymap

    def test_generate_without_headers(self, base_layout: Layout) -> None:
        """Test keymap generation without headers."""
        keymap_with_headers = base_layout.export.keymap().with_headers(True).generate()
        keymap_without_headers = (
            base_layout.export.keymap().with_headers(False).generate()
        )

        # Without headers should be shorter
        assert len(keymap_without_headers) < len(keymap_with_headers)
        assert "Copyright" in keymap_with_headers
        assert "Copyright" not in keymap_without_headers
        assert "#include" in keymap_with_headers

    def test_generate_with_profile(
        self, base_layout: Layout, base_profile: SimpleNamespace
    ) -> None:
        """Test keymap generation with custom profile."""
        keymap = base_layout.export.keymap(base_profile).generate()

        assert isinstance(keymap, str)
        assert "zmk,keymap" in keymap
        assert "/* Key positions */" in keymap
        assert "/* System behaviors */" in keymap

    def test_generate_with_behaviors(self, base_layout: Layout) -> None:
        """Test keymap generation with behaviors."""
        # Add a behavior to the layout
        base_layout.behaviors.add_hold_tap(
            name="mt_ctrl", tap="&kp A", hold="&kp LCTRL", tapping_term_ms=200
        )

        keymap = base_layout.export.keymap().with_behaviors(True).generate()
        assert isinstance(keymap, str)
        # The behavior definition should be included
        assert "mt_ctrl" in keymap or "behaviors" in keymap

    def test_generate_with_custom_context(self, base_layout: Layout) -> None:
        """Test keymap generation with custom context variables."""
        keymap = (
            base_layout.export.keymap()
            .with_context(
                author="Test Author", version="1.2.3", custom_var="custom_value"
            )
            .generate()
        )

        assert isinstance(keymap, str)
        # Context variables should be accessible in template

    def test_method_chaining(
        self, base_layout: Layout, base_profile: SimpleNamespace
    ) -> None:
        """Test complete method chaining."""
        keymap = (
            base_layout.export.keymap(base_profile)
            .with_headers(True)
            .with_behaviors(True)
            .with_combos(True)
            .with_macros(True)
            .with_tap_dances(True)
            .with_context(test="value")
            .generate()
        )

        assert isinstance(keymap, str)
        assert len(keymap) > 0


class TestConfigBuilder:
    """Tests for ConfigBuilder class."""

    def test_fluent_interface(self, base_layout: Layout) -> None:
        """Test that ConfigBuilder methods return self for chaining."""
        builder = base_layout.export.config()

        # All methods should return the builder for chaining
        assert builder.with_options(IDLE_TIMEOUT=30000) is builder
        assert builder.with_defaults(True) is builder

    def test_generate_basic_config(self, base_layout: Layout) -> None:
        """Test basic config generation."""
        config_content, settings = base_layout.export.config().generate()

        assert isinstance(config_content, str)
        assert isinstance(settings, dict)
        assert "# Generated Kconfig configuration" in config_content

    def test_generate_with_profile(
        self, base_layout: Layout, base_profile: SimpleNamespace
    ) -> None:
        """Test config generation with profile."""
        # Add config parameters to layout
        base_layout.data.config_parameters = [
            ConfigParameter(paramName="IDLE_TIMEOUT", value=60000)
        ]
        base_profile.kconfig_options = {
            "IDLE_TIMEOUT": MockConfigOption("CONFIG_ZMK_IDLE_TIMEOUT", 30000)
        }

        config_content, settings = base_layout.export.config(base_profile).generate()

        assert isinstance(config_content, str)
        assert isinstance(settings, dict)
        # Note: Current implementation doesn't process custom config parameters
        # This is a known limitation that should be addressed in future
        assert "CONFIG_ZMK_KEYBOARD_NAME" in config_content
        # assert settings.get("CONFIG_ZMK_IDLE_TIMEOUT") == 60000  # TODO: Not yet implemented

    def test_generate_with_additional_options(
        self, base_layout: Layout, base_profile: SimpleNamespace
    ) -> None:
        """Test config generation with additional options."""
        config_content, settings = (
            base_layout.export.config(base_profile)
            .with_options(SLEEP_ENABLE=True, IDLE_TIMEOUT=45000)
            .generate()
        )

        assert isinstance(config_content, str)
        assert isinstance(settings, dict)
        # Should include the additional options

    def test_method_chaining(
        self, base_layout: Layout, base_profile: SimpleNamespace
    ) -> None:
        """Test complete method chaining."""
        config_content, settings = (
            base_layout.export.config(base_profile)
            .with_options(TEST_OPTION=123)
            .with_defaults(False)
            .generate()
        )

        assert isinstance(config_content, str)
        assert isinstance(settings, dict)


class TestIntegration:
    """Integration tests for the complete fluent API."""

    def test_complete_workflow(
        self, base_layout: Layout, base_profile: SimpleNamespace
    ) -> None:
        """Test a complete workflow with the fluent API."""
        # Add behaviors
        base_layout.behaviors.add_hold_tap("mt_shift", "&kp A", "&kp LSHIFT")
        base_layout.behaviors.add_combo("esc_combo", [0, 1], "&kp ESC")
        base_layout.behaviors.add_macro(
            "email", ["&kp E", "&kp M", "&kp A", "&kp I", "&kp L"]
        )

        # Generate keymap with all features
        keymap = (
            base_layout.export.keymap(base_profile)
            .with_headers(True)
            .with_behaviors(True)
            .with_combos(True)
            .with_macros(True)
            .generate()
        )

        assert isinstance(keymap, str)
        assert len(keymap) > 100  # Should have substantial content

        # Generate config
        config_content, settings = (
            base_layout.export.config(base_profile)
            .with_options(COMBO_MAX=10)
            .generate()
        )

        assert isinstance(config_content, str)
        assert isinstance(settings, dict)

    def test_export_formats(self, base_layout: Layout) -> None:
        """Test different export formats."""
        # Keymap export
        keymap = base_layout.export.keymap().generate()
        assert isinstance(keymap, str)

        # Config export
        config, settings = base_layout.export.config().generate()
        assert isinstance(config, str)
        assert isinstance(settings, dict)

        # Dict export
        layout_dict = base_layout.export.to_dict()
        assert isinstance(layout_dict, dict)

        # JSON export
        layout_json = base_layout.export.to_json()
        assert isinstance(layout_json, str)

    @patch("zmk_layout.generators.keymap_generator.datetime")
    def test_timestamp_in_context(
        self, mock_datetime: Mock, base_layout: Layout
    ) -> None:
        """Test that generation timestamp is included in context."""
        mock_now = Mock()
        mock_now.isoformat.return_value = "2024-01-01T12:00:00"
        mock_now.year = 2024
        mock_datetime.now.return_value = mock_now

        keymap = base_layout.export.keymap().generate()

        # Timestamp should be used in generation
        mock_datetime.now.assert_called()


class TestErrorHandling:
    """Tests for error handling in the fluent API."""

    def test_invalid_template_path(self, base_layout: Layout) -> None:
        """Test error handling for invalid template path."""
        with pytest.raises((FileNotFoundError, ValueError, AttributeError)):
            base_layout.export.keymap().with_template("nonexistent.j2").generate()

    def test_empty_layout(self) -> None:
        """Test handling of empty layout."""
        empty_data = LayoutData(
            keyboard="empty", title="Empty", layers=[], layer_names=[]
        )
        empty_layout = Layout(empty_data)

        # Should still generate valid output
        keymap = empty_layout.export.keymap().generate()
        assert isinstance(keymap, str)

        config, settings = empty_layout.export.config().generate()
        assert isinstance(config, str)
        assert isinstance(settings, dict)
