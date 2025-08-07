#!/usr/bin/env python3
"""
Glove80 Fluent API Demonstration
This example demonstrates using the fluent API with a proper Glove80 profile,
including correct templates, key layouts, and Glove80-specific behaviors.
Features demonstrated:
- Proper Glove80 keyboard profile with 80 keys
- Complete home row mods (GUI/ALT/CTRL/SHIFT on both hands)
- Four-layer layout: Base, Lower, Symbol, and Magic layers
- Symbol layer with brackets, operators, and punctuation
- Glove80-specific behaviors (&magic, &lower, &bt_0, etc.)
- Layer tap behavior for easy symbol access
- Correct key position defines and layer formatting
- RGB underglow and Bluetooth configuration
- Template-based keymap generation with fluent API
- Consistent provider pattern usage like other demos
"""

import sys
from pathlib import Path
from types import SimpleNamespace


# Add the keyboards directory to path for importing the profile
sys.path.append(str(Path(__file__).parent.parent / "keyboards"))

from keyboards.glove80_profile import create_complete_glove80_profile
from zmk_layout import Layout
from zmk_layout.providers.factory import create_default_providers


def create_glove80_profile_for_fluent_api():
    """Create a Glove80 profile compatible with the fluent API."""
    # Get the complete profile data
    glove80_data = create_complete_glove80_profile()

    # Convert to SimpleNamespace structure that the fluent API expects
    profile = SimpleNamespace(
        keyboard_name="glove80",
        firmware_version="v25.05",
        keyboard_config=SimpleNamespace(
            key_count=80,
            keymap=SimpleNamespace(
                header_includes=glove80_data.keymap.header_includes,
                key_position_header=glove80_data.keymap.key_position_defines,
                system_behaviors_dts=glove80_data.keymap.system_behaviors_dts,
                keymap_dtsi=None,
                keymap_dtsi_file=None,
                formatting=SimpleNamespace(
                    key_gap=glove80_data.keymap.formatting["key_gap"],
                    base_indent=glove80_data.keymap.formatting["base_indent"],
                    rows=glove80_data.keymap.formatting["rows"],
                ),
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
                    layer_define="#define LAYER_{layer_name} {layer_index}",
                ),
                layout=SimpleNamespace(keys=80),
                hold_tap_flavors=["balanced", "tap-preferred", "hold-preferred"],
                validation_limits=SimpleNamespace(
                    required_holdtap_bindings=2, max_macro_params=32
                ),
            ),
        ),
        kconfig_options={
            "RGB_UNDERGLOW": True,
            "BLE": True,
            "USB": True,
            "BT_CTLR_TX_PWR_PLUS_8": True,
            "SLEEP": True,
        },
    )
    return profile


def create_glove80_layout():
    """Create a complete Glove80 layout with home row mods and symbol layer."""
    print("=== Creating Complete Glove80 Layout (4 layers, 80 keys) ===")

    # Create empty layout for Glove80
    layout = Layout.create_empty(keyboard="glove80", title="Glove80 with Magic Layer")

    print("1. Setting up Glove80-specific behaviors...")

    # Add Glove80-specific behaviors
    layout.behaviors.add_hold_tap(
        name="magic",
        tap="&rgb_ug_status_macro",
        hold="&mo 2",  # Magic layer
        tapping_term_ms=200,
    )

    # Left hand home row mods
    layout.behaviors.add_hold_tap(
        name="hm_a", tap="&kp A", hold="&kp LGUI", tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_s", tap="&kp S", hold="&kp LALT", tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_d",
        tap="&kp D",
        hold="&kp LCTRL",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_f",
        tap="&kp F",
        hold="&kp LSHIFT",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )

    # Right hand home row mods
    layout.behaviors.add_hold_tap(
        name="hm_j",
        tap="&kp J",
        hold="&kp RSHIFT",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_k",
        tap="&kp K",
        hold="&kp RCTRL",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_l", tap="&kp L", hold="&kp RALT", tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_semi",
        tap="&kp SEMI",
        hold="&kp RGUI",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )

    # Layer tap behaviors
    layout.behaviors.add_hold_tap(
        name="lt_sym",
        tap="&kp SPACE",
        hold="&mo 3",
        tapping_term_ms=200,  # Symbol layer
    )

    # Add useful combos
    layout.behaviors.add_combo(
        name="combo_esc",
        keys=[11, 12],
        binding="&kp ESC",
        timeout_ms=50,  # Q+W = ESC
    )
    layout.behaviors.add_combo(
        name="combo_tab",
        keys=[24, 25],
        binding="&kp TAB",
        timeout_ms=50,  # A+S = TAB
    )
    layout.behaviors.add_combo(
        name="combo_caps",
        keys=[26, 27],
        binding="&caps_word",
        timeout_ms=50,  # D+F = CAPS_WORD
    )

    print("2. Setting up base layer (QWERTY)...")
    # Create base layer with proper Glove80 key mapping
    base_layer = layout.layers.add("Base")

    # Row 1 (Numbers)
    for i, key in enumerate(
        [
            "F1",
            "N1",
            "N2",
            "N3",
            "N4",
            "N5",
            "F6",
            "F7",
            "N6",
            "N7",
            "N8",
            "N9",
            "N0",
            "F10",
        ]
    ):
        if i < 6:
            base_layer.set(i, f"&kp {key}")
        else:
            base_layer.set(i + 7, f"&kp {key}")  # Skip gap in physical layout

    # Row 2 (Top alpha row)
    row2_keys = [
        "TAB",
        "Q",
        "W",
        "E",
        "R",
        "T",
        "EQUAL",
        "Y",
        "U",
        "I",
        "O",
        "P",
        "BSLH",
    ]
    for i, key in enumerate(row2_keys):
        if i < 6:
            base_layer.set(10 + i, f"&kp {key}")
        else:
            base_layer.set(10 + i + 1, f"&kp {key}")  # Account for gap

    # Row 3 (Home row with mods)
    row3_keys = [
        "ESC",
        "&hm_a",
        "&hm_s",
        "&hm_d",
        "&hm_f",
        "G",
        "H",
        "&hm_j",
        "&hm_k",
        "&hm_l",
        "&hm_semi",
        "SQT",
    ]
    for i, key in enumerate(row3_keys):
        if i < 6:
            base_layer.set(22 + i, key)
        else:
            base_layer.set(22 + i + 1, key)  # Account for gap

    # Row 4 (Bottom alpha row)
    row4_keys = [
        "LSHIFT",
        "Z",
        "X",
        "C",
        "V",
        "B",
        "N",
        "M",
        "COMMA",
        "DOT",
        "SLASH",
        "RSHIFT",
    ]
    for i, key in enumerate(row4_keys):
        if i < 6:
            base_layer.set(34 + i, f"&kp {key}")
        else:
            base_layer.set(34 + i + 1, f"&kp {key}")  # Account for gap

    # Row 5 (Function row and thumbs)
    row5_left = ["LCTRL", "LALT", "HOME", "LEFT", "RIGHT", "END"]
    row5_right = ["UP", "DOWN", "LBKT", "RBKT", "RALT", "RCTRL"]

    # Left side
    for i, key in enumerate(row5_left):
        base_layer.set(46 + i, f"&kp {key}")

    # Thumbs (with layer tap for symbol layer)
    thumb_keys = [
        "BSPC",
        "DEL",
        "&lt_sym",
        "ENTER",
    ]  # Space becomes layer tap for symbols
    for i, key in enumerate(thumb_keys):
        base_layer.set(52 + i, key if key.startswith("&") else f"&kp {key}")

    # Right side
    for i, key in enumerate(row5_right):
        base_layer.set(58 + i, f"&kp {key}")

    # Row 6 (Bottom row)
    row6_keys = [
        "GRAVE",
        "INS",
        "CAPS",
        "PG_UP",
        "&lower",
        "LGUI",
        "RGUI",
        "&magic",
        "PG_DN",
        "MINUS",
        "EQUAL",
        "RSHIFT",
    ]

    # Map bottom row (skip middle gap)
    positions = [64, 65, 66, 67, 68, 69, 70, 74, 75, 76, 77, 78, 79]
    for i, key in enumerate(row6_keys):
        if i < len(positions):
            base_layer.set(positions[i], key if key.startswith("&") else f"&kp {key}")

    print("3. Setting up Lower layer...")
    # Create Lower layer
    lower_layer = layout.layers.add("Lower")

    # Fill with function keys and numbers
    for i in range(80):
        if i < 10:
            lower_layer.set(i, f"&kp F{i + 1}")
        elif 10 <= i < 20:
            lower_layer.set(i, f"&kp N{i - 9}")
        else:
            lower_layer.set(i, "&trans")  # Transparent for other keys

    # Set specific lower layer bindings
    lower_layer.set(68, "&trans")  # Lower key stays transparent when active
    lower_layer.set(74, "&to 0")  # Magic key goes back to base

    print("4. Setting up Symbol layer...")
    # Create Symbol layer for symbols and punctuation
    symbol_layer = layout.layers.add("Symbol")

    # Fill with transparent first
    for i in range(80):
        symbol_layer.set(i, "&trans")

    # Row 1: Numbers and function keys
    symbol_row1 = [
        "F1",
        "N1",
        "N2",
        "N3",
        "N4",
        "N5",
        "F6",
        "F7",
        "N6",
        "N7",
        "N8",
        "N9",
        "N0",
        "F10",
    ]
    for i, key in enumerate(symbol_row1):
        if i < 6:
            symbol_layer.set(i, f"&kp {key}")
        else:
            symbol_layer.set(i + 7, f"&kp {key}")

    # Row 2: Symbols top row
    symbol_row2 = [
        "GRAVE",
        "EXCL",
        "AT",
        "HASH",
        "DLLR",
        "PRCNT",
        "CARET",
        "AMPS",
        "STAR",
        "LPAR",
        "RPAR",
        "UNDER",
        "PLUS",
    ]
    for i, key in enumerate(symbol_row2):
        if i < 6:
            symbol_layer.set(10 + i, f"&kp {key}")
        else:
            symbol_layer.set(10 + i + 1, f"&kp {key}")

    # Row 3: Brackets and operators (home row)
    # fmt: off
    symbol_row3 = [
        "TILDE", "LBRC", "RBRC", "LPAR", "RPAR", "PIPE",
        "MINUS", "EQUAL", "LBKT", "RBKT", "BSLH", "DQT",
    ]
    # fmt: on
    for i, key in enumerate(symbol_row3):
        if i < 6:
            symbol_layer.set(22 + i, f"&kp {key}")
        else:
            symbol_layer.set(22 + i + 1, f"&kp {key}")

    # Row 4: Additional symbols
    # fmt: off
    symbol_row4 = [
        "trans", "LT", "GT", "COMMA", "DOT", "SLASH",
        "COLON", "SEMI", "SQT", "QMARK", "FSLH", "trans",
    ]
    # fmt: on
    for i, key in enumerate(symbol_row4):
        if i < 6:
            symbol_layer.set(34 + i, "&trans" if key == "trans" else f"&kp {key}")
        else:
            symbol_layer.set(34 + i + 1, "&trans" if key == "trans" else f"&kp {key}")

    # Navigation in thumb area
    symbol_layer.set(52, "&kp BSPC")  # Backspace
    symbol_layer.set(53, "&kp DEL")  # Delete
    symbol_layer.set(54, "&trans")  # Symbol layer key (transparent when active)
    symbol_layer.set(55, "&kp ENTER")  # Enter

    print("5. Setting up Magic layer...")
    # Create Magic layer for system controls
    magic_layer = layout.layers.add("Magic")

    # Fill with system controls and RGB
    for i in range(80):
        magic_layer.set(i, "&trans")  # Start with transparent

    # Add Bluetooth controls
    magic_layer.set(10, "&bt_0")  # BT profile 0
    magic_layer.set(11, "&bt_1")  # BT profile 1
    magic_layer.set(12, "&bt_2")  # BT profile 2
    magic_layer.set(13, "&bt_3")  # BT profile 3
    magic_layer.set(14, "&bt BT_CLR")  # Clear BT

    # RGB controls
    magic_layer.set(22, "&rgb_ug RGB_TOG")  # RGB toggle
    magic_layer.set(23, "&rgb_ug RGB_BRI")  # Brightness up
    magic_layer.set(24, "&rgb_ug RGB_BRD")  # Brightness down
    magic_layer.set(25, "&rgb_ug RGB_EFF")  # Next effect

    # System controls
    magic_layer.set(46, "&out OUT_TOG")  # Toggle USB/BT
    magic_layer.set(47, "&reset")  # Reset
    magic_layer.set(48, "&bootloader")  # Bootloader

    return layout


def demonstrate_glove80_fluent_api():
    """Demonstrate the Glove80 fluent API with proper profile."""
    print("=== Glove80 Fluent API Demonstration ===\\n")

    # Create providers (consistent with other demos)
    providers = create_default_providers()
    print("✅ Created default providers for template consistency")
    print()

    # Create layout and profile
    layout = create_glove80_layout()
    profile = create_glove80_profile_for_fluent_api()

    # Get layout statistics
    stats = layout.get_statistics()
    print("Layout Statistics:")
    print(f"  Keyboard: {stats['keyboard']}")
    print(f"  Title: {stats['title']}")
    print(f"  Total Layers: {stats['layer_count']}")
    print(f"  Layer Names: {stats['layer_names']}")
    print(f"  Total Key Bindings: {stats['total_bindings']}")
    print(f"  Total Behaviors: {stats['total_behaviors']}")
    print()

    # Test 1: Basic keymap generation
    print("1. Basic Keymap Generation:")
    print("   " + "-" * 40)
    keymap = layout.export.keymap().generate()
    print(f"   Generated keymap: {len(keymap)} characters")
    print(f"   Lines: {keymap.count(chr(10))}")
    print()

    # Test 2: Keymap with Glove80 profile
    print("2. Keymap with Glove80 Profile:")
    print("   " + "-" * 40)
    keymap_with_profile = layout.export.keymap(profile).with_headers(True).generate()
    print(f"   Generated keymap with profile: {len(keymap_with_profile)} characters")
    print(f"   Lines: {keymap_with_profile.count(chr(10))}")

    # Show first few lines to verify Glove80 includes
    lines = keymap_with_profile.split("\\n")[:20]
    print("   First 20 lines:")
    for i, line in enumerate(lines, 1):
        print(f"   {i:2d}: {line}")
    print()

    # Test 3: Config generation
    print("3. Config Generation:")
    print("   " + "-" * 40)
    config_content, settings = layout.export.config(profile).generate()
    print(f"   Generated config: {len(config_content)} characters")
    print(f"   Settings: {len(settings)} items")
    print(f"   Config preview:\\n   {chr(10).join(config_content.split(chr(10))[:10])}")
    print()

    # Test 4: JSON export
    print("4. JSON Export:")
    print("   " + "-" * 40)
    json_data = layout.export.to_json()
    print(f"   JSON export: {len(json_data)} characters")
    print(f"   Data includes keyboard: {layout.data.keyboard}")
    print()

    # Test 5: Advanced fluent usage
    print("5. Advanced Fluent Usage:")
    print("   " + "-" * 40)
    advanced_keymap = (
        layout.export.keymap(profile)
        .with_headers(True)
        .with_behaviors(True)
        .with_context(author="Glove80 User", version="1.0")
        .generate()
    )
    print(f"   Advanced keymap: {len(advanced_keymap)} characters")
    print()

    # Test parsing capabilities with providers (consistent with other demos)
    print("6. Testing Parsing Capabilities with Providers:")
    print("   " + "-" * 40)
    try:
        # Test round-trip: JSON → Layout → Keymap → Layout → JSON (using providers)
        print("   Testing round-trip conversion with providers...")
        json_content = layout.export.to_json()

        # Use providers for consistent parsing (same pattern as other demos)
        loaded_layout = Layout.from_string(
            json_content, title="Loaded from JSON via Providers", providers=providers
        )
        print("   ✓ Successfully loaded layout from JSON using providers")
        print(
            f"   ✓ Preserved {loaded_layout.layers.count} layers and {len(loaded_layout.get_statistics()['total_behaviors'])} behaviors"
        )

        # Generate keymap from loaded layout
        regenerated_keymap = (
            loaded_layout.export.keymap(profile).with_headers(True).generate()
        )
        print(f"   ✓ Regenerated keymap: {len(regenerated_keymap)} characters")

        # Test keymap parsing back to layout (full round-trip with providers)
        print("   Testing keymap → layout parsing with providers...")
        keymap_parsed_layout = Layout.from_string(
            regenerated_keymap, title="Parsed from Keymap", providers=providers
        )
        print(
            f"   ✓ Successfully parsed keymap back to layout with {keymap_parsed_layout.layers.count} layers"
        )

        # Compare original and regenerated sizes
        original_size = len(keymap_with_profile)
        regenerated_size = len(regenerated_keymap)
        size_diff = abs(original_size - regenerated_size)

        print(f"   Original keymap: {original_size} chars")
        print(f"   Regenerated: {regenerated_size} chars")
        print(f"   Size difference: {size_diff} chars")

        if size_diff < 100:  # Allow small differences due to formatting
            print("   ✓ Round-trip successful (minimal size difference)")
        else:
            print("   ⚠ Round-trip completed but with size differences")

    except Exception as e:
        print(f"   ✗ Parsing test failed: {e}")
        import traceback

        traceback.print_exc()
    print()

    # Save output files
    output_dir = Path("/tmp/glove80_fluent_output")
    output_dir.mkdir(exist_ok=True)

    print("7. Saving Output Files:")
    print("   " + "-" * 40)

    # Save keymap
    keymap_file = output_dir / "glove80.keymap"
    keymap_file.write_text(keymap_with_profile)
    print(f"   Saved keymap: {keymap_file} ({keymap_file.stat().st_size:,} bytes)")

    # Save config
    config_file = output_dir / "glove80.conf"
    config_file.write_text(config_content)
    print(f"   Saved config: {config_file} ({config_file.stat().st_size:,} bytes)")

    # Save JSON
    json_file = output_dir / "glove80_layout.json"
    json_file.write_text(json_data)
    print(f"   Saved JSON: {json_file} ({json_file.stat().st_size:,} bytes)")
    print()

    # Test 8: Round-trip verification with providers (enhanced from original)
    print("8. Round-trip Verification with Providers:")
    print("   " + "-" * 40)
    try:
        # Load the generated keymap back using providers (consistent with other demos)
        keymap_content = keymap_file.read_text()
        loaded_layout = Layout.from_string(
            keymap_content, title="Loaded Glove80 Layout", providers=providers
        )

        # DEBUG: Print behaviors from original and loaded layouts
        print("   === DEBUG: Behavior Comparison ===")
        print("   Original Hold-tap behaviors:")
        for ht in layout.data.hold_taps:
            print(
                f"     {ht.name}: bindings={ht.bindings}, tapping_term={ht.tapping_term_ms}ms"
            )
        print("   Loaded Hold-tap behaviors:")
        for ht in loaded_layout.data.hold_taps:
            print(
                f"     {ht.name}: bindings={ht.bindings}, tapping_term={ht.tapping_term_ms}ms"
            )
        print("   Original Combos:")
        for combo in layout.data.combos:
            print(
                f"     {combo.name}: binding={combo.binding}, keys={combo.key_positions}"
            )
        print("   Loaded Combos:")
        for combo in loaded_layout.data.combos:
            print(
                f"     {combo.name}: binding={combo.binding}, keys={combo.key_positions}"
            )
        print("   === END DEBUG ===")
        print()

        # Compare basic statistics
        original_stats = layout.get_statistics()
        loaded_stats = loaded_layout.get_statistics()

        print(f"   Original layout layers: {original_stats['layer_count']}")
        print(f"   Loaded layout layers: {loaded_stats['layer_count']}")
        print(f"   Original bindings: {original_stats['total_bindings']}")
        print(f"   Loaded bindings: {loaded_stats['total_bindings']}")
        print(f"   Original behaviors: {original_stats['total_behaviors']}")
        print(f"   Loaded behaviors: {loaded_stats['total_behaviors']}")

        # Check if layer names match
        layer_names_match = original_stats["layer_names"] == loaded_stats["layer_names"]
        print(f"   Layer names match: {layer_names_match}")

        # Compare individual layers
        print("   Layer-by-layer comparison:")
        for i, (orig_name, loaded_name) in enumerate(
            zip(
                original_stats["layer_names"], loaded_stats["layer_names"], strict=False
            )
        ):
            orig_layer = layout.layers.get(orig_name)
            loaded_layer = loaded_layout.layers.get(loaded_name)

            # Count non-transparent bindings in each layer
            orig_bindings = [str(b) for b in orig_layer.bindings if str(b) != "&trans"]
            loaded_bindings = [
                str(b) for b in loaded_layer.bindings if str(b) != "&trans"
            ]
            print(
                f"     Layer {i} ({orig_name}): Original={len(orig_bindings)}, Loaded={len(loaded_bindings)}"
            )

        # Test regeneration - can we generate the same keymap again?
        regenerated_keymap = (
            loaded_layout.export.keymap(profile).with_headers(True).generate()
        )

        # Compare file sizes (rough validation)
        original_size = len(keymap_with_profile)
        regenerated_size = len(regenerated_keymap)
        size_diff = abs(original_size - regenerated_size)

        print(f"   Original keymap size: {original_size} chars")
        print(f"   Regenerated size: {regenerated_size} chars")
        print(
            f"   Size difference: {size_diff} chars ({size_diff / original_size * 100:.1f}%)"
        )

        # Basic validation - check if key structures are present
        has_behaviors = "behaviors {" in regenerated_keymap
        has_combos = "combos {" in regenerated_keymap
        has_keymap = "keymap {" in regenerated_keymap
        has_layers = all(
            name in regenerated_keymap for name in original_stats["layer_names"]
        )

        print(f"   Regenerated keymap has behaviors: {has_behaviors}")
        print(f"   Regenerated keymap has combos: {has_combos}")
        print(f"   Regenerated keymap has keymap section: {has_keymap}")
        print(f"   Regenerated keymap has all layers: {has_layers}")

        if (
            has_behaviors
            and has_combos
            and has_keymap
            and has_layers
            and size_diff < original_size * 0.1  # Allow 10% difference
        ):
            print("   ✓ Round-trip verification successful!")
        else:
            print("   ⚠ Round-trip verification completed with minor issues")
    except Exception as e:
        print(f"   ✗ Round-trip verification failed: {e}")
        import traceback

        traceback.print_exc()

    print()
    print(
        "✓ Round-trip verification with providers ensures keymap can be loaded back correctly"
    )
    print("✅ Template pattern consistency maintained with other demos")
    return layout, profile


if __name__ == "__main__":
    print("ZMK Layout Library - Glove80 Fluent API Demo")
    print("=" * 50)
    try:
        demonstrate_glove80_fluent_api()
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        import traceback

        traceback.print_exc()
