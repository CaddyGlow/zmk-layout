#!/usr/bin/env python3
"""Demo script showing the new fluent API for keymap and config generation."""

from types import SimpleNamespace

from zmk_layout.core.layout import Layout
from zmk_layout.models.core import LayoutBinding


def demo_fluent_api():
    """Demonstrate the new fluent API for export operations."""
    print("=== ZMK Layout Generator Fluent API Demo ===\n")

    # Create sample layout data with proper LayoutBinding objects
    sample_data = {
        "keyboard": "corne",
        "title": "Test Layout",
        "layer_names": ["default", "lower", "raise"],
        "layers": [
            [
                LayoutBinding.from_str("&kp Q"),
                LayoutBinding.from_str("&kp W"),
                LayoutBinding.from_str("&kp E"),
            ],
            [
                LayoutBinding.from_str("&kp 1"),
                LayoutBinding.from_str("&kp 2"),
                LayoutBinding.from_str("&kp 3"),
            ],
            [
                LayoutBinding.from_str("&kp F1"),
                LayoutBinding.from_str("&kp F2"),
                LayoutBinding.from_str("&kp F3"),
            ],
        ],
        "config_parameters": [
            {"param_name": "ZMK_COMBO_MAX_PRESSED_COMBOS", "value": 10}
        ],
    }

    # Create Layout using fluent API
    layout = Layout.from_dict(sample_data)

    print("1. Basic Keymap Generation (with default profile):")
    print("-" * 50)
    keymap = layout.export.keymap().generate()
    print(f"   Generated keymap: {len(keymap)} characters")
    print("   First 200 characters:")
    print("   " + "\n   ".join(keymap[:200].split("\n")))
    print()

    print("2. Keymap Without Headers:")
    print("-" * 50)
    keymap_no_headers = layout.export.keymap().with_headers(False).generate()
    print(f"   Generated keymap: {len(keymap_no_headers)} characters")
    print("   First 150 characters:")
    print("   " + "\n   ".join(keymap_no_headers[:150].split("\n")))
    print()

    # Create a custom profile for more advanced examples
    profile = SimpleNamespace(
        keyboard_name="corne",
        firmware_version="3.6",
        keyboard_config=SimpleNamespace(
            key_count=42,
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
            keymap=SimpleNamespace(
                header_includes=["behaviors.dtsi", "dt-bindings/zmk/keys.h"],
                key_position_header="/* Key positions for Corne */",
                system_behaviors_dts="",
                keymap_dtsi=None,
                keymap_dtsi_file=None,
            ),
        ),
        kconfig_options={
            "ZMK_COMBO_MAX_PRESSED_COMBOS": SimpleNamespace(
                name="CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS", default=8
            )
        },
    )

    print("3. Keymap with Custom Profile:")
    print("-" * 50)
    keymap_with_profile = layout.export.keymap(profile).generate()
    print(f"   Generated keymap with profile: {len(keymap_with_profile)} characters")
    print()

    print("4. Keymap with Chained Configuration:")
    print("-" * 50)
    keymap_custom = (
        layout.export.keymap(profile)
        .with_headers(True)
        .with_behaviors(True)
        .with_combos(True)
        .with_macros(True)
        .with_context(author="Demo User", description="Example keymap generation")
        .generate()
    )
    print(f"   Generated custom keymap: {len(keymap_custom)} characters")
    print()

    print("5. Config File Generation:")
    print("-" * 50)
    config_content, settings = layout.export.config(profile).generate()
    print(f"   Config content: {len(config_content)} characters")
    print("   Settings extracted: {settings}")
    print("   Config preview:")
    print("   " + "\n   ".join(config_content.split("\n")[:5]))
    print()

    print("6. Config with Additional Options:")
    print("-" * 50)
    config_with_options, settings = (
        layout.export.config(profile)
        .with_options(IDLE_TIMEOUT=30000, SLEEP_ENABLE=True)
        .generate()
    )
    print(f"   Config with options: {len(config_with_options)} characters")
    print(f"   Settings: {settings}")
    print()

    print("7. JSON Export:")
    print("-" * 50)
    json_export = layout.export.to_json(indent=2)
    print(f"   JSON export: {len(json_export)} characters")
    print("   First 200 characters:")
    print("   " + json_export[:200] + "...")
    print()

    print("8. Advanced Usage - Adding Behaviors and Then Exporting:")
    print("-" * 50)
    # Add some behaviors using the behavior manager
    layout.behaviors.add_hold_tap(
        name="mt_ctrl", tap="&kp A", hold="&kp LCTRL", tapping_term_ms=200
    )

    # Now export with the new behaviors
    keymap_with_behaviors = (
        layout.export.keymap(profile).with_behaviors(True).generate()
    )
    print(f"   Keymap with custom behaviors: {len(keymap_with_behaviors)} characters")
    print()

    print("Summary:")
    print("-" * 50)
    print("✓ All generation now uses fluent API through Layout.export")
    print("✓ Method chaining allows intuitive configuration")
    print("✓ Profile support for keyboard-specific settings")
    print("✓ Clean separation between Layout manipulation and export")
    print("✓ No direct file writing - all functions return strings")
    print()
    print("The old config_generator functions are replaced by:")
    print("  - layout.export.keymap() for keymap generation")
    print("  - layout.export.config() for config generation")
    print("  - layout.export.to_json() for JSON export")


if __name__ == "__main__":
    demo_fluent_api()
