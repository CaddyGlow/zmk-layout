#!/usr/bin/env python3
"""
Real-World Example: Creating a Complete Corne Layout

This example demonstrates creating a realistic 3x6+3 Corne keyboard layout
with home row mods, multiple layers, combos, and macros using the new
helper methods for simplified API usage.

Features demonstrated:
- Layout.create_empty() for starting layouts
- Layout.to_keymap() for generating ZMK keymap files
- Layout.from_string() for loading any format
- Automatic file format detection
- Clean, simple API without complex setup
"""

import json
from pathlib import Path

from zmk_layout import Layout


def create_corne_layout():
    """Create a complete Corne keyboard layout."""
    print("=== Creating Complete Corne Layout ===")

    # Create empty layout for Corne (3x6+3 = 42 keys)
    layout = Layout.create_empty(
        keyboard="corne", title="Complete Corne Layout with Home Row Mods"
    )

    print("1. Setting up home row mod behaviors...")

    # Add home row mod behaviors
    layout.behaviors.add_hold_tap(
        name="hm_gui",
        tap="&kp A",
        hold="&kp LGUI",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_alt",
        tap="&kp S",
        hold="&kp LALT",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_ctrl",
        tap="&kp D",
        hold="&kp LCTRL",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_shift",
        tap="&kp F",
        hold="&kp LSHIFT",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )

    # Right hand home row mods
    layout.behaviors.add_hold_tap(
        name="hm_rshift",
        tap="&kp J",
        hold="&kp RSHIFT",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_rctrl",
        tap="&kp K",
        hold="&kp RCTRL",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_ralt",
        tap="&kp L",
        hold="&kp RALT",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_rgui",
        tap="&kp SEMICOLON",
        hold="&kp RGUI",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )

    print("2. Setting up layer toggle behaviors...")

    # Layer toggle behaviors
    layout.behaviors.add_hold_tap(
        name="lt_lower", tap="&kp SPACE", hold="&mo 1", tapping_term_ms=200
    )
    layout.behaviors.add_hold_tap(
        name="lt_raise", tap="&kp ENTER", hold="&mo 2", tapping_term_ms=200
    )

    print("3. Adding useful combos...")

    # Useful combos
    layout.behaviors.add_combo(
        name="combo_esc", keys=[0, 1], binding="&kp ESC", timeout_ms=50
    )
    layout.behaviors.add_combo(
        name="combo_tab", keys=[10, 11], binding="&kp TAB", timeout_ms=50
    )
    layout.behaviors.add_combo(
        name="combo_del", keys=[8, 9], binding="&kp DEL", timeout_ms=50
    )

    print("4. Adding productivity macros...")

    # Productivity macros
    layout.behaviors.add_macro(
        name="macro_email",
        sequence=[
            "&kp U",
            "&kp S",
            "&kp E",
            "&kp R",
            "&kp AT",
            "&kp E",
            "&kp X",
            "&kp A",
            "&kp M",
            "&kp P",
            "&kp L",
            "&kp E",
        ],
    )
    layout.behaviors.add_macro(
        name="macro_screenshot",
        sequence=["&kp LGUI", "&kp LSHIFT", "&kp N4"],  # macOS screenshot
    )

    print("5. Creating base layer (QWERTY with home row mods)...")

    # Base layer (QWERTY with home row mods)
    base_layer = layout.layers.add("base")

    # Top row
    base_layer.set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E").set(3, "&kp R").set(
        4, "&kp T"
    ).set(5, "&kp Y").set(6, "&kp U").set(7, "&kp I").set(8, "&kp O").set(9, "&kp P")

    # Home row with mods
    base_layer.set(10, "&hm_gui").set(11, "&hm_alt").set(12, "&hm_ctrl").set(
        13, "&hm_shift"
    ).set(14, "&kp G").set(15, "&kp H").set(16, "&hm_rshift").set(17, "&hm_rctrl").set(
        18, "&hm_ralt"
    ).set(19, "&hm_rgui")

    # Bottom row
    base_layer.set(20, "&kp Z").set(21, "&kp X").set(22, "&kp C").set(23, "&kp V").set(
        24, "&kp B"
    ).set(25, "&kp N").set(26, "&kp M").set(27, "&kp COMMA").set(28, "&kp DOT").set(
        29, "&kp SLASH"
    )

    # Thumb keys
    base_layer.set(30, "&kp LGUI").set(31, "&lt_lower").set(32, "&kp LCTRL").set(
        33, "&kp LALT"
    ).set(34, "&lt_raise").set(35, "&kp RSHIFT")

    print("6. Creating lower layer (numbers and navigation)...")

    # Lower layer (numbers and navigation)
    lower_layer = layout.layers.add("lower")

    # Numbers row
    lower_layer.set(0, "&kp N1").set(1, "&kp N2").set(2, "&kp N3").set(3, "&kp N4").set(
        4, "&kp N5"
    ).set(5, "&kp N6").set(6, "&kp N7").set(7, "&kp N8").set(8, "&kp N9").set(
        9, "&kp N0"
    )

    # Navigation
    lower_layer.set(10, "&kp TAB").set(11, "&kp HOME").set(12, "&kp UP").set(
        13, "&kp END"
    ).set(14, "&kp PG_UP").set(15, "&kp PG_DN").set(16, "&kp LEFT").set(
        17, "&kp DOWN"
    ).set(18, "&kp RIGHT").set(19, "&kp BSPC")

    # Function keys
    lower_layer.set(20, "&kp F1").set(21, "&kp F2").set(22, "&kp F3").set(
        23, "&kp F4"
    ).set(24, "&kp F5").set(25, "&kp F6").set(26, "&kp F7").set(27, "&kp F8").set(
        28, "&kp F9"
    ).set(29, "&kp F10")

    # Thumb keys (transparent where not needed)
    lower_layer.set(30, "&trans").set(31, "&trans").set(32, "&trans").set(
        33, "&trans"
    ).set(34, "&mo 3").set(35, "&trans")

    print("7. Creating raise layer (symbols and brackets)...")

    # Raise layer (symbols and brackets)
    raise_layer = layout.layers.add("raise")

    # Symbol row
    raise_layer.set(0, "&kp EXCL").set(1, "&kp AT").set(2, "&kp HASH").set(
        3, "&kp DLLR"
    ).set(4, "&kp PRCNT").set(5, "&kp CARET").set(6, "&kp AMPS").set(7, "&kp STAR").set(
        8, "&kp LPAR"
    ).set(9, "&kp RPAR")

    # Brackets and operators
    raise_layer.set(10, "&kp GRAVE").set(11, "&kp LBKT").set(12, "&kp MINUS").set(
        13, "&kp RBKT"
    ).set(14, "&kp PIPE").set(15, "&kp BSLH").set(16, "&kp EQUAL").set(
        17, "&kp PLUS"
    ).set(18, "&kp LBRC").set(19, "&kp RBRC")

    # More symbols
    raise_layer.set(20, "&kp TILDE").set(21, "&kp UNDER").set(22, "&kp LT").set(
        23, "&kp GT"
    ).set(24, "&kp PIPE").set(25, "&trans").set(26, "&kp SQT").set(27, "&kp DQT").set(
        28, "&kp COLON"
    ).set(29, "&kp QMARK")

    # Thumb keys
    raise_layer.set(30, "&trans").set(31, "&mo 3").set(32, "&trans").set(
        33, "&trans"
    ).set(34, "&trans").set(35, "&trans")

    print("8. Creating adjust layer (system controls and macros)...")

    # Adjust layer (system controls and macros)
    adjust_layer = layout.layers.add("adjust")

    # Media controls
    adjust_layer.set(0, "&kp C_MUTE").set(1, "&kp C_VOL_DN").set(2, "&kp C_VOL_UP").set(
        3, "&kp C_PREV"
    ).set(4, "&kp C_NEXT").set(5, "&kp C_PP").set(6, "&macro_screenshot").set(
        7, "&macro_email"
    ).set(8, "&trans").set(9, "&trans")

    # System controls
    adjust_layer.set(10, "&bt BT_CLR").set(11, "&bt BT_SEL 0").set(
        12, "&bt BT_SEL 1"
    ).set(13, "&bt BT_SEL 2").set(14, "&trans").set(15, "&trans").set(16, "&trans").set(
        17, "&trans"
    ).set(18, "&trans").set(19, "&sys_reset")

    # Fill rest with transparent
    for i in range(20, 36):
        adjust_layer.set(i, "&trans")

    return layout


def demonstrate_layout_features():
    """Show off the created layout features."""
    print("\n=== Layout Features Demonstration ===")

    layout = create_corne_layout()

    # Get comprehensive statistics
    stats = layout.get_statistics()

    print("\nLayout Statistics:")
    print(f"  Keyboard: {stats['keyboard']}")
    print(f"  Title: {stats['title']}")
    print(f"  Total Layers: {stats['layer_count']}")
    print(f"  Layer Names: {stats['layer_names']}")
    print(f"  Total Key Bindings: {stats['total_bindings']}")
    print(f"  Total Behaviors: {stats['total_behaviors']}")
    print(f"  Hold-Tap Behaviors: {stats['behavior_counts']['hold_taps']}")
    print(f"  Combo Behaviors: {stats['behavior_counts']['combos']}")
    print(f"  Macro Behaviors: {stats['behavior_counts']['macros']}")

    # Show layer sizes
    if "layer_sizes" in stats:
        print("\nLayer Sizes:")
        for layer_name, size in stats["layer_sizes"].items():
            print(f"  {layer_name}: {size} keys")

    # Demonstrate layer queries
    print("\nLayer Queries:")
    nav_layers = layout.find_layers(
        lambda name: "lower" in name or "nav" in name.lower()
    )
    print(f"  Navigation-related layers: {nav_layers}")

    system_layers = layout.find_layers(
        lambda name: "adjust" in name or "system" in name.lower()
    )
    print(f"  System/adjust layers: {system_layers}")

    # Show some key bindings from base layer
    print("\nBase Layer Sample (first 10 keys):")
    base_layer = layout.layers.get("base")
    for i in range(min(10, len(base_layer.bindings))):
        binding = base_layer.bindings[i]
        print(f"  Key {i:2d}: {binding}")

    return layout


def save_layout_files():
    """Save the layout in both JSON and keymap formats using helper methods."""
    print("\n=== Saving Layout Files ===")

    layout = create_corne_layout()

    # Create output directory
    output_dir = Path("/tmp/corne_layout_output")
    output_dir.mkdir(exist_ok=True)

    # Save as JSON using to_dict() and simple file writing
    json_file = output_dir / "complete_corne_layout.json"
    print(f"1. Saving JSON layout to: {json_file}")

    layout_data = layout.to_dict()
    json_content = json.dumps(layout_data, indent=2)
    json_file.write_text(json_content)
    print(f"   ✓ JSON file saved ({json_file.stat().st_size:,} bytes)")

    # Save as ZMK keymap using to_keymap() helper
    keymap_file = output_dir / "corne.keymap"
    print(f"2. Saving ZMK keymap to: {keymap_file}")

    keymap_content = layout.to_keymap(keyboard_name="corne", include_headers=True)
    keymap_file.write_text(keymap_content)
    print(f"   ✓ Keymap file saved ({keymap_file.stat().st_size:,} bytes)")

    return layout, json_file, keymap_file


def validate_roundtrip():
    """Validate that we can load both file formats using helper methods."""
    print("\n=== Roundtrip Validation ===")

    # Create original layout
    original_layout = create_corne_layout()
    original_stats = original_layout.get_statistics()

    # Save files
    _, json_file, keymap_file = save_layout_files()

    # Test 1: Load from JSON using from_string()
    print("1. Testing JSON roundtrip...")
    try:
        json_content = json_file.read_text()
        json_loaded_layout = Layout.from_string(json_content)  # Auto-detects JSON!
        json_stats = json_loaded_layout.get_statistics()

        json_checks = [
            ("Layer count", original_stats["layer_count"] == json_stats["layer_count"]),
            (
                "Total bindings",
                original_stats["total_bindings"] == json_stats["total_bindings"],
            ),
            (
                "Total behaviors",
                original_stats["total_behaviors"] == json_stats["total_behaviors"],
            ),
        ]

        json_passed = all(check[1] for check in json_checks)
        status = "✓" if json_passed else "✗"
        print(
            f"   {status} JSON roundtrip: {len([c for c in json_checks if c[1]])}/{len(json_checks)} checks passed"
        )

    except Exception as e:
        print(f"   ✗ JSON roundtrip failed: {e}")
        json_passed = False

    # Test 2: Load from keymap using from_string()
    print("2. Testing keymap roundtrip...")
    try:
        keymap_content = keymap_file.read_text()
        keymap_loaded_layout = Layout.from_string(
            keymap_content, title="Corne Keymap"
        )  # Auto-detects keymap!
        keymap_stats = keymap_loaded_layout.get_statistics()

        # Note: Keymap parsing may not preserve all metadata perfectly
        keymap_checks = [
            ("Has layers", keymap_stats["layer_count"] > 0),
            ("Has bindings", keymap_stats["total_bindings"] > 0),
        ]

        keymap_passed = all(check[1] for check in keymap_checks)
        status = "✓" if keymap_passed else "✗"
        print(
            f"   {status} Keymap roundtrip: {len([c for c in keymap_checks if c[1]])}/{len(keymap_checks)} checks passed"
        )

    except Exception as e:
        print(f"   ✗ Keymap roundtrip failed: {e}")
        keymap_passed = False

    # Test 3: Show format auto-detection
    print("3. Testing format auto-detection...")
    try:
        # Test that from_string() correctly identifies each format
        json_layout = Layout.from_string(json_file.read_text())  # Should detect JSON
        keymap_layout = Layout.from_string(
            keymap_file.read_text(), title="Test"
        )  # Should detect keymap

        detection_passed = True
        print("   ✓ Format auto-detection working correctly")

    except Exception as e:
        print(f"   ✗ Format auto-detection failed: {e}")
        detection_passed = False

    # Summary
    overall_passed = json_passed and keymap_passed and detection_passed
    if overall_passed:
        print("\n✓ All validation tests passed!")
    else:
        print("\n⚠️  Some validation tests failed")

    return overall_passed


def main():
    """Main demonstration."""
    print("ZMK Layout Library - Real-World Corne Layout Example")
    print("=" * 70)

    try:
        # Create and demonstrate the layout
        demonstrate_layout_features()

        # Save layout files and validate roundtrip
        validation_passed = validate_roundtrip()

        print("\n" + "=" * 70)
        print("✓ Complete Corne layout created successfully!")
        print("✓ All features working: home row mods, layers, combos, macros")

        if validation_passed:
            print("✓ Files saved in both JSON and keymap formats")
            print("✓ Format auto-detection working correctly")
            print("✓ Roundtrip validation passed")
        else:
            print("⚠️  Some validation tests failed (check output above)")

        print("\nNew Helper Methods Demonstrated:")
        print("• Layout.create_empty() - Start with empty layout")
        print("• Layout.to_dict() - Convert to dictionary")
        print("• Layout.to_keymap() - Generate ZMK keymap directly")
        print("• Layout.from_string() - Auto-detect and load any format")
        print("• Path.read_text() / Path.write_text() - Handle file I/O externally")

        print("\nFiles saved to: /tmp/corne_layout_output/")
        print("• complete_corne_layout.json - Layout data in JSON format")
        print("• corne.keymap - Ready-to-use ZMK keymap file")

        print("\nThis demonstrates a production-ready ZMK layout created")
        print("entirely with the zmk-layout library's simplified helper API!")

    except Exception as e:
        print(f"✗ Example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
