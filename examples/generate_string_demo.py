#!/usr/bin/env python3
"""Demo script showing the updated generator functions that return strings instead of writing files."""

from typing import Any

from zmk_layout.generators.config_generator import (
    generate_config_file,
    generate_kconfig_conf,
    generate_keymap_file,
)
from zmk_layout.generators.zmk_generator import ZMKGenerator
from zmk_layout.models import LayoutData
from zmk_layout.models.core import LayoutBinding


def demo_string_generators():
    """Demonstrate the updated string-returning generator functions."""
    print("=== ZMK Layout Generator String Demo ===\n")

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

    layout_data = LayoutData.model_validate(sample_data)

    # Create mock profile
    class MockProfile:
        keyboard_name = "corne"
        firmware_version = "3.6"

    profile = MockProfile()

    print("1. Testing generate_kconfig_conf() - returns (content, settings):")
    kconfig_content, kconfig_settings = generate_kconfig_conf(layout_data, profile)
    print("   Kconfig Content Preview:")
    print("   " + "\n   ".join(kconfig_content.split("\n")[:5]))
    print(f"   Settings: {kconfig_settings}")
    print()

    print("2. Testing generate_config_file() - returns (content, settings):")
    config_content, config_settings = generate_config_file(profile, layout_data)
    print("   Config Content Preview:")
    print("   " + "\n   ".join(config_content.split("\n")[:5]))
    print(f"   Settings: {config_settings}")
    print()

    print("3. Testing ZMKGenerator string methods:")
    generator = ZMKGenerator()

    try:
        # Test kconfig generation (this works with simple profile)
        zmk_kconfig, zmk_settings = generator.generate_kconfig_conf(
            layout_data, profile
        )
        print("   ZMK Kconfig Content Preview:")
        print("   " + "\n   ".join(zmk_kconfig.split("\n")[:3]))
        print(f"   ZMK Settings: {zmk_settings}")
    except Exception as e:
        print(f"   ZMK Kconfig generation failed: {e}")

    print("   Note: Other ZMKGenerator methods require full profile configuration")

    print("4. All generator functions now return strings instead of writing files!")
    print("   - generate_config_file() returns (content, settings)")
    print("   - generate_keymap_file() returns content")
    print("   - generate_kconfig_conf() returns (content, settings)")
    print("   - All ZMKGenerator methods return strings")
    print()
    print("   File writing is now handled by calling code when needed.")


if __name__ == "__main__":
    demo_string_generators()
