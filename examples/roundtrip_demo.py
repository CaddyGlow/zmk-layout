#!/usr/bin/env python3
"""
Factory Layout Roundtrip Demonstration

This script demonstrates a complete roundtrip transformation using the Factory layout files:
1. Load Factory.json → Convert to keymap → Save as generated.keymap
2. Load Factory.keymap → Convert to JSON → Save as generated.json
3. Perform full cycle validation and save intermediate files

All generated files are saved to the output directory for inspection.
"""

import json
import sys
from pathlib import Path
from typing import Any


# Add the keyboards directory to the path for profile imports
sys.path.append(str(Path(__file__).parent.parent / "keyboards"))

from zmk_layout.generators.zmk_generator import ZMKGenerator
from zmk_layout.models.metadata import LayoutData
from zmk_layout.parsers.zmk_keymap_parser import ParsingMode, ZMKKeymapParser
from zmk_layout.providers.configuration import ConfigurationProvider, SystemBehavior
from zmk_layout.providers.factory import LayoutProviders, create_default_providers


try:
    from glove80_profile import CompleteGlove80Profile, create_complete_glove80_profile
except ImportError:
    print("Warning: glove80_profile not available. Using mock configuration.")
    CompleteGlove80Profile = Any

    def create_complete_glove80_profile() -> Any:
        return None


class Glove80ConfigurationProvider(ConfigurationProvider):
    """Glove80-specific configuration provider for demonstration."""

    def __init__(self, complete_profile: Any = None):
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

            if self.profile:
                # Convert all behaviors from the complete profile
                all_behaviors = self.profile.get_all_behaviors()
                for behavior_dict in all_behaviors:
                    code = behavior_dict["code"]
                    if code.startswith("&"):
                        code = code[1:]

                    system_behavior = SystemBehavior(
                        name=code,
                        description=behavior_dict.get("description", ""),
                        url=behavior_dict.get("url", ""),
                        origin=behavior_dict.get("origin", "zmk"),
                    )
                    self._behavior_definitions.append(system_behavior)
            else:
                # Fallback basic behaviors for when profile is not available
                basic_behaviors = [
                    "kp",
                    "trans",
                    "none",
                    "mt",
                    "lt",
                    "mo",
                    "to",
                    "bt",
                    "out",
                    "magic",
                    "lower",
                    "bt_0",
                    "bt_1",
                    "bt_2",
                    "bt_3",
                    "rgb_ug",
                    "reset",
                    "bootloader",
                ]
                for behavior in basic_behaviors:
                    self._behavior_definitions.append(
                        SystemBehavior(
                            name=behavior, description="", url="", origin="zmk"
                        )
                    )

        return self._behavior_definitions

    def get_include_files(self) -> list[str]:
        """Get Glove80-specific include files."""
        if self.profile:
            return self.profile.get_includes()
        return [
            "dt-bindings/zmk/keys.h",
            "dt-bindings/zmk/bt.h",
            "dt-bindings/zmk/rgb.h",
            "dt-bindings/zmk/outputs.h",
        ]

    def get_validation_rules(self) -> dict[str, Any]:
        """Get Glove80-specific validation rules."""
        if self._validation_rules is None:
            if self.profile:
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
            else:
                # Fallback validation rules
                self._validation_rules = {
                    "max_layers": 10,
                    "key_positions": list(range(80)),
                    "supported_behaviors": [
                        "kp",
                        "trans",
                        "none",
                        "mt",
                        "lt",
                        "mo",
                        "to",
                        "bt",
                        "out",
                        "magic",
                        "lower",
                        "bt_0",
                        "bt_1",
                        "bt_2",
                        "bt_3",
                        "rgb_ug",
                        "reset",
                        "bootloader",
                    ],
                    "bluetooth_profiles": [0, 1, 2, 3],
                    "rgb_commands": ["RGB_TOG", "RGB_BRI", "RGB_BRD"],
                    "bt_commands": ["BT_CLR", "BT_NXT", "BT_PRV"],
                    "out_commands": ["OUT_TOG", "OUT_USB", "OUT_BLE"],
                }
        return self._validation_rules

    def get_template_context(self) -> dict[str, Any]:
        """Get Glove80 template context."""
        if self._template_context is None:
            if self.profile:
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
            else:
                # Fallback template context
                self._template_context = {
                    "keyboard_name": "glove80",
                    "firmware_version": "v25.05",
                    "key_count": 80,
                    "layer_defines": "Base Lower Magic",
                    "key_position_defines": "// Key position defines would go here",
                    "system_behaviors_dts": "// System behaviors would go here",
                    "formatting": {"rows": [], "key_gap": "  ", "base_indent": ""},
                    "layer_names": {"Base": 0, "Lower": 1, "Magic": 2},
                    "header_includes": ["behaviors.dtsi"],
                }
        return self._template_context

    def get_kconfig_options(self) -> dict[str, Any]:
        """Get Glove80 kconfig options."""
        return {}

    def get_formatting_config(self) -> dict[str, Any]:
        """Get Glove80 formatting configuration."""
        if self.profile:
            return self.profile.keymap.formatting
        return {"rows": [], "key_gap": "  ", "base_indent": ""}

    def get_search_paths(self) -> list[Path]:
        """Get Glove80 search paths."""
        if self.profile:
            return self.profile.get_template_paths()
        return []

    def get_keyboard_profile(self) -> Any:
        """Get the complete Glove80 keyboard profile."""
        return self.profile


def create_mock_generator_profile() -> Any:
    """Create a mock profile for the generator."""
    from types import SimpleNamespace

    return SimpleNamespace(
        keyboard_config=SimpleNamespace(
            zmk=SimpleNamespace(compatible_strings=SimpleNamespace(keymap="zmk,keymap"))
        )
    )


def create_glove80_providers() -> tuple[LayoutProviders, Any]:
    """Create LayoutProviders with Glove80 configuration."""
    complete_profile = create_complete_glove80_profile()
    glove80_config = Glove80ConfigurationProvider(complete_profile)

    default_providers = create_default_providers()

    providers = LayoutProviders(
        configuration=glove80_config,
        template=default_providers.template,
        logger=default_providers.logger,
        file=default_providers.file,
    )

    return providers, create_mock_generator_profile()


def main():
    """Main demonstration function."""
    print("🔄 Factory Layout Roundtrip Demonstration")
    print("=" * 50)

    # Set up paths
    examples_dir = Path(__file__).parent
    layouts_dir = examples_dir / "layouts"
    output_dir = examples_dir / "output"
    output_dir.mkdir(exist_ok=True)

    factory_json_path = layouts_dir / "Factory.json"
    factory_keymap_path = layouts_dir / "Factory.keymap"

    # Verify input files exist
    if not factory_json_path.exists():
        print(f"❌ Factory.json not found at {factory_json_path}")
        return 1

    if not factory_keymap_path.exists():
        print(f"❌ Factory.keymap not found at {factory_keymap_path}")
        return 1

    print("📁 Input files:")
    print(f"   JSON: {factory_json_path}")
    print(f"   Keymap: {factory_keymap_path}")
    print(f"📁 Output directory: {output_dir}")
    print()

    # Create providers
    providers, generator_profile = create_glove80_providers()

    # Test 1: JSON → Keymap transformation
    print("🔄 Test 1: JSON → Keymap transformation")
    try:
        # Load original JSON
        with open(factory_json_path) as f:
            original_json = json.load(f)
        print(
            f"✅ Loaded Factory.json ({len(original_json['layers'])} layers, {len(original_json['layers'][0])} keys)"
        )

        # Convert to LayoutData
        layout_data = LayoutData.model_validate(original_json)
        print("✅ Converted JSON to LayoutData")

        # Generate keymap
        generator = ZMKGenerator(
            configuration_provider=providers.configuration,
            template_provider=providers.template,
            logger=providers.logger,
        )

        keymap_content = generator.generate_keymap_node(
            generator_profile, layout_data.layer_names, layout_data.layers
        )

        # Save generated keymap
        generated_keymap_path = output_dir / "generated_from_json.keymap"
        generated_keymap_path.write_text(keymap_content)
        print(f"✅ Generated keymap saved to: {generated_keymap_path}")

    except Exception as e:
        print(f"❌ JSON → Keymap failed: {e}")
        return 1

    print()

    # Test 2: Keymap → JSON transformation
    print("🔄 Test 2: Keymap → JSON transformation")
    try:
        # Parse original keymap
        parser = ZMKKeymapParser(
            configuration_provider=providers.configuration, logger=providers.logger
        )

        # Use FULL parsing mode to avoid timeout issues
        parse_result = parser.parse_keymap(factory_keymap_path, mode=ParsingMode.FULL)

        # Extract LayoutData
        if (
            hasattr(parse_result, "layout_data")
            and parse_result.layout_data is not None
        ):
            parsed_layout_data = parse_result.layout_data
        else:
            parsed_layout_data = parse_result

        print("✅ Parsed Factory.keymap to LayoutData")

        # Convert to JSON
        generated_json = parsed_layout_data.model_dump(by_alias=True)

        # Save generated JSON
        generated_json_path = output_dir / "generated_from_keymap.json"
        with open(generated_json_path, "w") as f:
            json.dump(generated_json, f, indent=2)
        print(f"✅ Generated JSON saved to: {generated_json_path}")

    except Exception as e:
        print(f"❌ Keymap → JSON failed: {e}")
        return 1

    print()

    # Test 3: Full roundtrip validation
    print("🔄 Test 3: Full roundtrip cycle (JSON → Keymap → JSON)")
    try:
        # Step 1: JSON → LayoutData
        with open(factory_json_path) as f:
            original_json = json.load(f)
        layout_data_1 = LayoutData.model_validate(original_json)

        # Step 2: LayoutData → Keymap
        keymap_content = generator.generate_keymap_node(
            generator_profile, layout_data_1.layer_names, layout_data_1.layers
        )

        # Save intermediate keymap
        roundtrip_keymap_path = output_dir / "roundtrip_intermediate.keymap"
        roundtrip_keymap_path.write_text(keymap_content)

        # Step 3: Keymap → LayoutData
        parse_result = parser.parse_keymap(roundtrip_keymap_path, mode=ParsingMode.FULL)
        if (
            hasattr(parse_result, "layout_data")
            and parse_result.layout_data is not None
        ):
            layout_data_2 = parse_result.layout_data
        else:
            layout_data_2 = parse_result

        # Step 4: LayoutData → JSON
        roundtrip_json = layout_data_2.model_dump(by_alias=True)

        # Save final JSON
        roundtrip_json_path = output_dir / "roundtrip_final.json"
        with open(roundtrip_json_path, "w") as f:
            json.dump(roundtrip_json, f, indent=2)

        print("✅ Roundtrip completed!")
        print(f"   Intermediate keymap: {roundtrip_keymap_path}")
        print(f"   Final JSON: {roundtrip_json_path}")

        # Validate roundtrip integrity
        print("\n🔍 Roundtrip validation:")

        # Compare layer counts
        original_layer_count = len(original_json["layers"])
        roundtrip_layer_count = len(roundtrip_json["layers"])
        if original_layer_count == roundtrip_layer_count:
            print(f"✅ Layer count preserved: {original_layer_count}")
        else:
            print(
                f"⚠️  Layer count changed: {original_layer_count} → {roundtrip_layer_count}"
            )

        # Compare layer names
        original_layer_names = original_json["layer_names"]
        roundtrip_layer_names = roundtrip_json["layer_names"]
        if original_layer_names == roundtrip_layer_names:
            print(f"✅ Layer names preserved: {original_layer_names}")
        else:
            print(
                f"⚠️  Layer names changed: {original_layer_names} → {roundtrip_layer_names}"
            )

        # Check key counts per layer
        for i, (orig_layer, rt_layer) in enumerate(
            zip(original_json["layers"], roundtrip_json["layers"], strict=False)
        ):
            if len(orig_layer) == len(rt_layer):
                print(f"✅ Layer {i} key count preserved: {len(orig_layer)}")
            else:
                print(
                    f"⚠️  Layer {i} key count changed: {len(orig_layer)} → {len(rt_layer)}"
                )

        # Check for Glove80-specific behaviors
        behaviors_found = set()
        for layer in roundtrip_json["layers"]:
            for key in layer:
                if key and "value" in key:
                    behaviors_found.add(key["value"])

        glove80_behaviors = ["&magic", "&bt_0", "&bt_1", "&bt_2", "&bt_3", "&rgb_ug"]
        preserved_behaviors = [
            b
            for b in glove80_behaviors
            if b in behaviors_found or b.lstrip("&") in str(behaviors_found)
        ]
        print(
            f"✅ Glove80 behaviors preserved: {len(preserved_behaviors)}/{len(glove80_behaviors)}"
        )

    except Exception as e:
        print(f"❌ Roundtrip cycle failed: {e}")
        return 1

    print()

    # Summary
    print("📊 Generated Files Summary:")
    print("-" * 30)
    for file_path in sorted(output_dir.glob("*")):
        size = file_path.stat().st_size
        print(f"   {file_path.name:<25} ({size:,} bytes)")

    print("\n🎉 Roundtrip demonstration completed successfully!")
    print(f"All generated files are available in: {output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
