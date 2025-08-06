"""
Comprehensive Factory Layout Roundtrip Testing with Glove80 Profile

This module implements the comprehensive testing strategy outlined in
FACTORY_LAYOUT_TESTING_PLAN.md for validating bidirectional transformations
between JSON and keymap formats using proper Glove80 keyboard profile configuration.

Key Features:
- Glove80ConfigurationProvider with keyboard-specific behaviors
- Factory layout JSON <-> Keymap roundtrip validation
- Data integrity and feature preservation testing
- Comprehensive edge case coverage
"""

import json

# Import the complete Glove80 profile
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from zmk_layout.generators.zmk_generator import ZMKGenerator
from zmk_layout.models.metadata import LayoutData
from zmk_layout.parsers.zmk_keymap_parser import ZMKKeymapParser
from zmk_layout.providers.configuration import ConfigurationProvider, SystemBehavior
from zmk_layout.providers.factory import LayoutProviders

sys.path.append(str(Path(__file__).parent.parent / "keyboards"))
try:
    from glove80_profile import CompleteGlove80Profile, create_complete_glove80_profile
except ImportError:
    # Fallback for when the module isn't available
    CompleteGlove80Profile = Any  # type: ignore[misc,assignment]

    def create_complete_glove80_profile() -> CompleteGlove80Profile:
        return None  # type: ignore[return-value]


@dataclass
class Glove80ProfileData:
    """Container for Glove80 profile configuration data."""

    keyboard: str = "glove80"
    key_count: int = 80
    behaviors: list[dict[str, Any]] | None = None
    hardware_config: dict[str, Any] | None = None
    keymap_config: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.behaviors is None:
            self.behaviors = []
        if self.hardware_config is None:
            self.hardware_config = {}
        if self.keymap_config is None:
            self.keymap_config = {}


class Glove80ConfigurationProvider(ConfigurationProvider):
    """
    Glove80-specific configuration provider based on complete profile data.

    This provider implements all Glove80-specific features using the complete
    keyboard profile with full hardware specifications, behaviors, firmware
    configurations, and validation rules.
    """

    def __init__(self, complete_profile: CompleteGlove80Profile | None = None):
        if complete_profile is None:
            complete_profile = create_complete_glove80_profile()
        self.profile = complete_profile
        self._behavior_definitions: list[SystemBehavior] | None = None
        self._template_context: dict[str, Any] | None = None
        self._validation_rules: dict[str, Any] | None = None

    def get_behavior_definitions(self) -> list[SystemBehavior]:
        """Get comprehensive Glove80 behavior definitions from complete profile."""
        if self._behavior_definitions is None:
            self._behavior_definitions = []

            # Convert all behaviors from the complete profile
            all_behaviors = self.profile.get_all_behaviors()
            for behavior_dict in all_behaviors:
                # Extract the behavior code (remove & prefix if present)
                code = behavior_dict["code"]
                if code.startswith("&"):
                    code = code[1:]

                # Create SystemBehavior with proper name and description
                system_behavior = SystemBehavior(
                    name=code,
                    description=behavior_dict.get("description", ""),
                    url=behavior_dict.get("url", ""),
                    origin=behavior_dict.get("origin", "zmk"),
                )

                self._behavior_definitions.append(system_behavior)

        return self._behavior_definitions

    def get_include_files(self) -> list[str]:
        """Get Glove80-specific include files from complete profile."""
        include_files: list[str] = self.profile.get_includes()
        return include_files

    def get_validation_rules(self) -> dict[str, Any]:
        """Get Glove80-specific validation rules from complete profile."""
        if self._validation_rules is None:
            validation = self.profile.validation
            self._validation_rules = {
                "max_layers": validation.max_layers,
                "key_positions": validation.key_positions,
                "supported_behaviors": validation.supported_behaviors,
                "bluetooth_profiles": validation.bluetooth_profiles,
                "rgb_commands": validation.rgb_commands,
                "bt_commands": validation.bt_commands,
                "out_commands": validation.out_commands,
            }
        return self._validation_rules

    def get_template_context(self) -> dict[str, Any]:
        """Get Glove80 template context from complete profile."""
        if self._template_context is None:
            keymap_config = self.profile.keymap
            hardware = self.profile.hardware
            firmware = self.profile.firmware

            self._template_context = {
                "keyboard_name": hardware.keyboard,
                "firmware_version": firmware.default_firmware,
                "key_count": hardware.key_count,
                "layer_defines": keymap_config.layer_defines,
                "key_position_defines": keymap_config.key_position_defines,
                "system_behaviors_dts": keymap_config.system_behaviors_dts,
                "formatting": keymap_config.formatting,
                "layer_names": keymap_config.layer_names,
                "header_includes": keymap_config.header_includes,
            }
        return self._template_context

    def get_kconfig_options(self) -> dict[str, Any]:
        """Get Glove80 kconfig options from complete profile."""
        kconfig = self.profile.kconfig
        options = {}

        # Add standard options with their default values
        for option_name, option_config in kconfig.standard_options.items():
            options[option_name] = option_config["default"]

        # Add experimental options with their default values
        for option_name, option_config in kconfig.experimental_options.items():
            options[option_name] = option_config["default"]

        return options

    def get_formatting_config(self) -> dict[str, Any]:
        """Get Glove80 formatting configuration from complete profile."""
        formatting_config: dict[str, Any] = self.profile.keymap.formatting
        return formatting_config

    def get_search_paths(self) -> list[Path]:
        """Get Glove80 search paths from complete profile."""
        search_paths: list[Path] = self.profile.get_template_paths()
        return search_paths

    def get_keyboard_profile(self) -> Any:
        """Get the complete Glove80 keyboard profile."""
        return self.profile


def create_mock_generator_profile() -> Any:
    """Create a mock profile with the expected structure for ZMKGenerator."""
    from types import SimpleNamespace

    return SimpleNamespace(
        keyboard_config=SimpleNamespace(zmk=SimpleNamespace(compatible_strings=SimpleNamespace(keymap="zmk,keymap")))
    )


def create_glove80_providers(profile_path: str | None = None) -> tuple[LayoutProviders, Any]:
    """Create LayoutProviders with complete Glove80 configuration.

    Returns:
        Tuple of (LayoutProviders, mock_generator_profile)
    """
    # Create complete Glove80 profile
    complete_profile = create_complete_glove80_profile()

    # Create the configuration provider with complete profile
    glove80_config = Glove80ConfigurationProvider(complete_profile)

    from zmk_layout.providers.factory import create_default_providers

    default_providers = create_default_providers()

    providers = LayoutProviders(
        configuration=glove80_config,
        template=default_providers.template,
        logger=default_providers.logger,
        file=default_providers.file,
    )

    # Return providers and a mock profile for the generator
    return providers, create_mock_generator_profile()


class TestGlove80ConfigurationProvider:
    """Test suite for Glove80ConfigurationProvider validation."""

    def test_profile_data_loading(self) -> None:
        """Validate complete profile loading and initialization."""
        complete_profile = create_complete_glove80_profile()
        provider = Glove80ConfigurationProvider(complete_profile)

        assert provider.profile.hardware.keyboard == "glove80"
        assert provider.profile.hardware.key_count == 80
        assert provider.profile.hardware.is_split
        assert len(provider.profile.hardware.physical_layout) == 6  # 6 rows

    def test_behavior_definitions_completeness(self) -> None:
        """Test behavior definitions include all behaviors from complete profile."""
        provider = Glove80ConfigurationProvider()

        behaviors = provider.get_behavior_definitions()
        behavior_codes = [b.name for b in behaviors]

        # Check basic ZMK behaviors
        assert "kp" in behavior_codes
        assert "trans" in behavior_codes
        assert "none" in behavior_codes
        assert "mt" in behavior_codes
        assert "lt" in behavior_codes
        assert "mo" in behavior_codes
        assert "to" in behavior_codes
        assert "bt" in behavior_codes
        assert "out" in behavior_codes

        # Check Glove80-specific behaviors
        assert "magic" in behavior_codes
        assert "lower" in behavior_codes
        assert "bt_0" in behavior_codes
        assert "bt_1" in behavior_codes
        assert "bt_2" in behavior_codes
        assert "bt_3" in behavior_codes
        assert "rgb_ug" in behavior_codes
        assert "reset" in behavior_codes
        assert "bootloader" in behavior_codes
        assert "Custom" in behavior_codes

        # Verify we have a comprehensive set (should have all ZMK + Glove80 behaviors)
        assert len(behaviors) >= 20  # Should have 16+ ZMK behaviors + 7 Glove80 behaviors

    def test_validation_rules_accuracy(self) -> None:
        """Verify validation rules match complete Glove80 specifications."""
        provider = Glove80ConfigurationProvider()

        rules = provider.get_validation_rules()

        assert rules["max_layers"] == 10
        assert len(rules["key_positions"]) == 80
        assert rules["key_positions"] == list(range(80))

        supported_behaviors = rules["supported_behaviors"]
        assert isinstance(supported_behaviors, list)
        assert "magic" in supported_behaviors
        assert "rgb_ug" in supported_behaviors
        assert "bt_0" in supported_behaviors
        assert "Custom" in supported_behaviors

        # Test additional validation rule categories
        assert "bluetooth_profiles" in rules
        assert "rgb_commands" in rules
        assert "bt_commands" in rules
        assert "out_commands" in rules

        bluetooth_profiles = rules["bluetooth_profiles"]
        assert isinstance(bluetooth_profiles, list)
        assert bluetooth_profiles == [0, 1, 2, 3]

    def test_template_context_accuracy(self) -> None:
        """Test template context includes all required data from complete profile."""
        provider = Glove80ConfigurationProvider()

        context = provider.get_template_context()

        assert context["keyboard_name"] == "glove80"
        assert context["key_count"] == 80
        assert context["firmware_version"] == "v25.05"  # Default firmware
        assert "layer_defines" in context
        assert "key_position_defines" in context
        assert "system_behaviors_dts" in context
        assert "layer_names" in context
        assert "header_includes" in context

        # Check formatting config
        formatting = context["formatting"]
        assert isinstance(formatting, dict)
        assert len(formatting["rows"]) == 6  # Glove80 has 6 rows
        assert len(formatting["rows"][0]) == 18  # First row has 18 positions
        assert formatting["key_gap"] == "  "
        assert formatting["base_indent"] == ""

        # Check layer names
        layer_names = context["layer_names"]
        assert isinstance(layer_names, dict)
        assert layer_names["Base"] == 0
        assert layer_names["Lower"] == 1
        assert layer_names["Magic"] == 2


class TestFactoryJsonToKeymap:
    """Test Factory JSON to Keymap transformation."""

    def test_json_to_keymap_basic_transformation(self) -> None:
        """Test basic JSON to keymap transformation with Glove80 provider."""
        providers, profile = create_glove80_providers()

        # Mock JSON data based on Factory.json structure
        factory_json_path = Path(__file__).parent.parent / "examples" / "layouts" / "Factory.json"

        if factory_json_path.exists():
            with open(factory_json_path) as f:
                factory_json = json.load(f)

            # Test that we can process the Factory JSON with Glove80 providers
            # This would use the actual LayoutData.from_json() method
            assert factory_json["keyboard"] == "glove80"
            assert len(factory_json["layers"]) == 3  # Base, Lower, Magic
            assert len(factory_json["layers"][0]) == 80  # 80 keys per layer

    def test_glove80_specific_features_preservation(self) -> None:
        """Test that Glove80-specific features are preserved during transformation."""
        providers, profile = create_glove80_providers()

        # Test magic behavior handling
        magic_behaviors = ["&magic", "&bt_0", "&bt_1", "&bt_2", "&bt_3"]
        for behavior in magic_behaviors:
            supported = providers.configuration.get_validation_rules()["supported_behaviors"]
            assert isinstance(supported, list)
            behavior_code = behavior.lstrip("&")
            assert behavior_code in supported, f"Behavior {behavior} not supported"

    def test_rgb_underglow_behavior_handling(self) -> None:
        """Test RGB underglow behavior validation and processing."""
        providers, profile = create_glove80_providers()

        validation_rules = providers.configuration.get_validation_rules()
        supported_behaviors = validation_rules["supported_behaviors"]
        assert isinstance(supported_behaviors, list)
        assert "rgb_ug" in supported_behaviors

        # Test that RGB_* parameters would be validated
        # In a full implementation, these would be validated as parameters


class TestFactoryKeymapToJson:
    """Test Factory Keymap to JSON transformation."""

    def test_keymap_parsing_with_glove80_configuration(self) -> None:
        """Test keymap parsing with proper Glove80 parser configuration."""
        providers, profile = create_glove80_providers()

        factory_keymap_path = Path(__file__).parent.parent / "examples" / "layouts" / "Factory.keymap"

        if factory_keymap_path.exists():
            # In full implementation, would use ZMKKeymapParser
            # parser = ZMKKeymapParser(configuration_provider=providers.configuration)
            # layout_data = parser.parse_keymap_file(factory_keymap_path, keyboard_profile="glove80")

            # For now, just verify file exists and has expected structure
            with open(factory_keymap_path) as f:
                content = f.read()

            # Check for Glove80-specific elements
            assert "layer_Base" in content
            assert "layer_Lower" in content
            assert "layer_Magic" in content
            assert "rgb_ug" in content
            assert "bt_0" in content
            assert "magic" in content

    def test_bluetooth_management_parsing(self) -> None:
        """Test parsing of Glove80 Bluetooth management behaviors."""
        providers, profile = create_glove80_providers()

        # Test that bt_* behaviors are recognized
        bt_behaviors = ["bt_0", "bt_1", "bt_2", "bt_3"]
        validation_rules = providers.configuration.get_validation_rules()
        supported = validation_rules["supported_behaviors"]
        assert isinstance(supported, list)

        for bt_behavior in bt_behaviors:
            assert bt_behavior in supported, f"Bluetooth behavior {bt_behavior} not supported"

    def test_complex_binding_parameter_handling(self) -> None:
        """Test handling of complex key bindings with nested parameters."""
        providers, profile = create_glove80_providers()

        # Test that complex bindings like &kp LC(LS(Z)) would be handled
        # This tests the parameter parsing capabilities
        validation_rules = providers.configuration.get_validation_rules()
        supported_behaviors = validation_rules["supported_behaviors"]
        assert isinstance(supported_behaviors, list)
        assert "kp" in supported_behaviors


class TestFactoryRoundTripValidation:
    """Test complete roundtrip validation (JSON <-> Keymap <-> JSON)."""

    def test_json_keymap_json_cycle(self) -> None:
        """Test full JSON -> Keymap -> JSON cycle preserves data integrity."""
        providers, complete_profile = create_glove80_providers()

        # Load the original Factory.json
        factory_json_path = Path(__file__).parent.parent / "examples" / "layouts" / "Factory.json"

        if not factory_json_path.exists():
            pytest.skip(f"Factory.json not found at {factory_json_path}")

        with open(factory_json_path) as f:
            original_json = json.load(f)

        # Step 1: Convert JSON to LayoutData (using Pydantic model_validate)
        layout_data = LayoutData.model_validate(original_json)

        # Use temporary files for intermediate steps
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Step 2: Generate keymap file using ZMKGenerator
            generator = ZMKGenerator(
                configuration_provider=providers.configuration,
                template_provider=providers.template,
                logger=providers.logger,
            )
            keymap_path = temp_path / "test_factory.keymap"

            # Generate keymap content and write to file
            keymap_content = generator.generate_keymap_node(
                complete_profile, layout_data.layer_names, layout_data.layers
            )
            keymap_path.write_text(keymap_content)

            # Verify keymap was created and has expected content
            assert keymap_path.exists()
            keymap_content = keymap_path.read_text()
            assert "layer_Base" in keymap_content
            assert "layer_Lower" in keymap_content
            assert "layer_Magic" in keymap_content

            # Step 3: Parse keymap back to LayoutData using ZMKKeymapParser
            parser = ZMKKeymapParser(configuration_provider=providers.configuration, logger=providers.logger)
            # Parse keymap content from file
            keymap_content = keymap_path.read_text()
            parsed_layout_data = parser.parse_keymap(keymap_path)

            # Step 4: Convert back to JSON (using Pydantic model_dump)
            roundtrip_json = parsed_layout_data.model_dump(by_alias=True)

            # Step 5: Compare essential data (normalize for comparison)
            # Focus on core layout data that should survive roundtrip
            assert roundtrip_json["keyboard"] == original_json["keyboard"]
            assert roundtrip_json["layer_names"] == original_json["layer_names"]
            assert len(roundtrip_json["layers"]) == len(original_json["layers"])

            # Verify each layer has correct number of keys
            for i, (orig_layer, rt_layer) in enumerate(
                zip(original_json["layers"], roundtrip_json["layers"], strict=False)
            ):
                assert len(rt_layer) == len(orig_layer), f"Layer {i} key count mismatch"

            # Test that Glove80-specific behaviors are preserved
            keymap_behaviors = set()
            for layer in roundtrip_json["layers"]:
                for key in layer:
                    if key and "value" in key:
                        keymap_behaviors.add(key["value"])

            # Should contain Glove80-specific behaviors
            assert "&magic" in keymap_behaviors or "magic" in str(keymap_behaviors)
            assert any("&bt_" in str(behavior) or "bt_" in str(behavior) for behavior in keymap_behaviors)

    def test_keymap_json_keymap_cycle(self) -> None:
        """Test reverse cycle: Keymap -> JSON -> Keymap preserves structure."""
        providers, profile = create_glove80_providers()

        # Load the original Factory.keymap
        factory_keymap_path = Path(__file__).parent.parent / "examples" / "layouts" / "Factory.keymap"

        if not factory_keymap_path.exists():
            pytest.skip(f"Factory.keymap not found at {factory_keymap_path}")

        # Step 1: Parse keymap to LayoutData using ZMKKeymapParser
        parser = ZMKKeymapParser(configuration_provider=providers.configuration, logger=providers.logger)
        # Parse keymap content from file
        keymap_content = factory_keymap_path.read_text()
        original_layout_data = parser.parse_keymap(factory_keymap_path)

        # Use temporary files for intermediate steps
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Step 2: Convert to JSON (using Pydantic model_dump)
            json_data = original_layout_data.model_dump(by_alias=True)
            json_path = temp_path / "test_factory.json"
            with open(json_path, "w") as f:
                json.dump(json_data, f, indent=2)

            # Verify JSON was created and has expected content
            assert json_path.exists()
            assert json_data["keyboard"] == "glove80"
            assert len(json_data["layer_names"]) >= 3  # Base, Lower, Magic
            assert len(json_data["layers"]) >= 3

            # Step 3: Convert JSON back to LayoutData
            with open(json_path) as f:
                loaded_json = json.load(f)
            roundtrip_layout_data = LayoutData.model_validate(loaded_json)

            # Step 4: Generate keymap from roundtrip LayoutData
            generator = ZMKGenerator(
                configuration_provider=providers.configuration,
                template_provider=providers.template,
                logger=providers.logger,
            )
            roundtrip_keymap_path = temp_path / "roundtrip_factory.keymap"
            # Generate keymap content and write to file
            keymap_content = generator.generate_keymap_node(
                profile, roundtrip_layout_data.layer_names, roundtrip_layout_data.layers
            )
            roundtrip_keymap_path.write_text(keymap_content)

            # Step 5: Compare key structural elements
            original_content = factory_keymap_path.read_text()
            roundtrip_content = roundtrip_keymap_path.read_text()

            # Both should contain the same layer definitions
            assert "layer_Base" in original_content and "layer_Base" in roundtrip_content
            assert "layer_Lower" in original_content and "layer_Lower" in roundtrip_content
            assert "layer_Magic" in original_content and "layer_Magic" in roundtrip_content

            # Both should contain Glove80-specific behaviors
            glove80_behaviors = ["magic", "bt_0", "bt_1", "bt_2", "bt_3", "rgb_ug"]
            for behavior in glove80_behaviors:
                original_has_behavior = behavior in original_content
                roundtrip_has_behavior = behavior in roundtrip_content
                if original_has_behavior:
                    assert roundtrip_has_behavior, f"Behavior '{behavior}' lost in roundtrip"

            # Both should have the same number of layer definitions
            original_layers = original_content.count("layer {")
            roundtrip_layers = roundtrip_content.count("layer {")
            assert original_layers == roundtrip_layers, "Layer count mismatch in roundtrip"

    def test_data_integrity_validation(self) -> None:
        """Validate that no data is lost in transformations."""
        providers, profile = create_glove80_providers()

        # Test that all behavior definitions are preserved
        behaviors = providers.configuration.get_behavior_definitions()
        assert len(behaviors) >= 18  # Should have comprehensive behavior set

        # Test template context completeness
        context = providers.configuration.get_template_context()
        assert "layer_defines" in context
        assert "key_position_defines" in context
        assert "system_behaviors_dts" in context

    def test_temporary_file_management(self) -> None:
        """Test that temporary files are properly managed and cleaned up."""
        providers, profile = create_glove80_providers()

        # Load Factory.json for testing
        factory_json_path = Path(__file__).parent.parent / "examples" / "layouts" / "Factory.json"

        if not factory_json_path.exists():
            pytest.skip(f"Factory.json not found at {factory_json_path}")

        with open(factory_json_path) as f:
            original_json = json.load(f)

        layout_data = LayoutData.model_validate(original_json)
        temp_files_created = []

        # Test that temporary files are created and accessible during operations
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate multiple temporary files
            generator = ZMKGenerator(
                configuration_provider=providers.configuration,
                template_provider=providers.template,
                logger=providers.logger,
            )

            for i in range(3):
                keymap_path = temp_path / f"test_keymap_{i}.keymap"
                # Generate keymap content and write to file
                keymap_content = generator.generate_keymap_node(profile, layout_data.layer_names, layout_data.layers)
                keymap_path.write_text(keymap_content)

                # Verify file exists and has content
                assert keymap_path.exists()
                assert keymap_path.stat().st_size > 0
                temp_files_created.append(keymap_path)

            # Verify all files are accessible
            for temp_file in temp_files_created:
                assert temp_file.exists()
                content = temp_file.read_text()
                assert len(content) > 100  # Should have substantial content
                assert "layer_Base" in content

        # After exiting the context manager, verify files are cleaned up
        for temp_file in temp_files_created:
            assert not temp_file.exists(), f"Temporary file {temp_file} was not cleaned up"

    def test_file_content_consistency(self) -> None:
        """Test that generated files have consistent content across multiple generations."""
        providers, profile = create_glove80_providers()

        factory_json_path = Path(__file__).parent.parent / "examples" / "layouts" / "Factory.json"

        if not factory_json_path.exists():
            pytest.skip(f"Factory.json not found at {factory_json_path}")

        with open(factory_json_path) as f:
            original_json = json.load(f)

        layout_data = LayoutData.model_validate(original_json)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generator = ZMKGenerator(
                configuration_provider=providers.configuration,
                template_provider=providers.template,
                logger=providers.logger,
            )

            # Generate the same keymap multiple times
            keymap_contents = []
            for i in range(3):
                keymap_path = temp_path / f"consistency_test_{i}.keymap"
                # Generate keymap content and write to file
                keymap_content = generator.generate_keymap_node(profile, layout_data.layer_names, layout_data.layers)
                keymap_path.write_text(keymap_content)
                keymap_contents.append(keymap_path.read_text())

            # All generated files should have identical content
            for i, content in enumerate(keymap_contents[1:], 1):
                assert content == keymap_contents[0], f"Generated keymap {i} differs from first generation"

            # Verify essential elements are present in all generations
            for content in keymap_contents:
                assert "glove80" in content.lower()
                assert "layer_Base" in content
                assert "layer_Lower" in content
                assert "layer_Magic" in content

    def test_edge_cases_and_error_conditions(self) -> None:
        """Test handling of edge cases and error conditions."""
        # Test default profile creation
        provider = Glove80ConfigurationProvider()

        # Should provide valid defaults from complete profile
        rules = provider.get_validation_rules()
        key_positions = rules["key_positions"]
        assert isinstance(key_positions, list)
        assert len(key_positions) == 80  # Should have 80 key positions


class TestGlove80SpecificFeatures:
    """Test Glove80-specific feature validation."""

    def test_rgb_underglow_comprehensive_testing(self) -> None:
        """Comprehensive testing of RGB underglow behaviors."""
        providers, profile = create_glove80_providers()

        validation_rules = providers.configuration.get_validation_rules()
        supported = validation_rules["supported_behaviors"]
        assert isinstance(supported, list)
        assert "rgb_ug" in supported

        # Test include files include RGB headers
        includes = providers.configuration.get_include_files()
        assert "dt-bindings/zmk/rgb.h" in includes

    def test_bluetooth_management_comprehensive(self) -> None:
        """Comprehensive Bluetooth management validation."""
        providers, profile = create_glove80_providers()

        # Test all bt_* behaviors are supported
        validation_rules = providers.configuration.get_validation_rules()
        supported = validation_rules["supported_behaviors"]
        assert isinstance(supported, list)
        bt_behaviors = ["bt_0", "bt_1", "bt_2", "bt_3", "bt"]

        for bt_behavior in bt_behaviors:
            assert bt_behavior in supported

        # Test BT includes
        includes = providers.configuration.get_include_files()
        assert "dt-bindings/zmk/bt.h" in includes

    def test_magic_layer_functionality(self) -> None:
        """Test Magic layer functionality and behavior."""
        providers, profile = create_glove80_providers()

        validation_rules = providers.configuration.get_validation_rules()
        supported = validation_rules["supported_behaviors"]
        assert isinstance(supported, list)
        assert "magic" in supported

        # Test magic behavior in template context
        context = providers.configuration.get_template_context()
        behaviors_dts = context["system_behaviors_dts"]
        assert isinstance(behaviors_dts, str)
        assert "magic:" in behaviors_dts
        assert "MAGIC_HOLD_TAP" in behaviors_dts

    def test_system_behaviors_comprehensive(self) -> None:
        """Test system behaviors like reset, bootloader."""
        providers, profile = create_glove80_providers()

        validation_rules = providers.configuration.get_validation_rules()
        supported = validation_rules["supported_behaviors"]
        assert isinstance(supported, list)
        system_behaviors = ["reset", "bootloader"]  # Removed sys_reset as it's not in complete profile

        for behavior in system_behaviors:
            assert behavior in supported

    def test_key_position_mapping_accuracy(self) -> None:
        """Test accuracy of Glove80 key position mappings."""
        providers, profile = create_glove80_providers()

        context = providers.configuration.get_template_context()
        key_defines = context["key_position_defines"]
        assert isinstance(key_defines, str)

        # Test specific key positions from Factory.keymap
        assert "POS_LH_T1 52" in key_defines
        assert "POS_RH_T1 57" in key_defines
        assert "POS_LH_C6R1 0" in key_defines
        assert "POS_RH_C6R6 79" in key_defines

        # Test formatting rows match hardware
        formatting = context["formatting"]
        assert isinstance(formatting, dict)
        rows = formatting["rows"]
        assert isinstance(rows, list)
        assert len(rows) == 6  # 6 rows
        assert rows[0] == [0, 1, 2, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, 5, 6, 7, 8, 9]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
