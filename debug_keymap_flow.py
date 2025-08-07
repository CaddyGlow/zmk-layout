#!/usr/bin/env python3
"""Debug the keymap generation flow step by step."""

from zmk_layout.core.layout import Layout


# Create a simple test layout
test_data = {
    "keyboard": "test",
    "title": "Test Layout",
    "layer_names": ["default"],
    "layers": [
        ["&kp Q", "&kp W"]
    ]
}

print("=== Creating Layout ===")
layout = Layout.from_dict(test_data)
print(f"Layout created with {len(layout.data.layers[0])} bindings")

print("\n=== Testing Layer Bindings ===")
for i, binding in enumerate(layout.data.layers[0]):
    print(f"Binding {i}: {repr(binding)}")
    print(f"  to_str(): '{binding.to_str()}'")

print("\n=== Testing ZMK Generator Flow with New Fluent API ===")

# Test the new fluent API
try:
    # Generate keymap using new fluent API
    print("\nGenerating keymap with new API:")
    keymap_content = layout.export.keymap().generate()

    print("Keymap generated successfully!")
    print(f"  Length: {len(keymap_content)} characters")
    print(f"  Lines: {len(keymap_content.splitlines())}")

    # Check for our specific problematic pattern
    if "value='&kp' params=[LayoutParam" in keymap_content:
        print("    ❌ Found problematic binding format in keymap!")
        print("    First 500 characters:")
        print(f"    {keymap_content[:500]}...")
    else:
        print("    ✅ Keymap looks good")
        print("\nFirst 500 characters of generated keymap:")
        print(keymap_content[:500])

    # Test with custom profile
    print("\n=== Testing with Custom Profile ===")
    from types import SimpleNamespace
    profile = SimpleNamespace(
        keyboard_config=SimpleNamespace(
            keymap=SimpleNamespace(
                keymap_dtsi_file="config/templates/keymap.dtsi.j2",
                header_includes=["behaviors.dtsi", "dt-bindings/zmk/keys.h", "dt-bindings/zmk/bt.h"]
            ),
            zmk=SimpleNamespace(
                compatible_strings=SimpleNamespace(
                    keymap="zmk,keymap",
                    hold_tap="zmk,behavior-hold-tap",
                    tap_dance="zmk,behavior-tap-dance",
                    macro="zmk,behavior-macro",
                    combos="zmk,combos"
                ),
                patterns=SimpleNamespace(
                    kconfig_prefix="CONFIG_ZMK_",
                    layer_define="#define {layer_name} {layer_index}"
                ),
                validation_limits=SimpleNamespace(
                    required_holdtap_bindings=2,
                    max_macro_params=32
                )
            ),
            key_count=42
        ),
        keyboard_name="test",
        firmware_version="1.0.0",
        kconfig_options={}
    )

    # Generate with profile
    keymap_with_profile = layout.export.keymap(profile).generate()
    print(f"Generated keymap with profile: {len(keymap_with_profile)} characters")

    # Test without headers
    keymap_no_headers = layout.export.keymap().with_headers(False).generate()
    print(f"Generated keymap without headers: {len(keymap_no_headers)} characters")

    # Test config generation
    print("\n=== Testing Config Generation ===")
    config_content, settings = layout.export.config(profile).generate()
    print(f"Generated config: {len(config_content)} characters")
    print(f"Settings: {settings}")

except Exception as e:
    print(f"Error in new API testing: {e}")
    import traceback
    traceback.print_exc()
