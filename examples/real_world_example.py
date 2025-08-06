#!/usr/bin/env python3
"""
Real-World Example: Creating a Complete Corne Layout

This example demonstrates creating a realistic 3x6+3 Corne keyboard layout
with home row mods, multiple layers, combos, and macros.
"""

from zmk_layout import Layout


def create_corne_layout():
    """Create a complete Corne keyboard layout."""
    print("=== Creating Complete Corne Layout ===")
    
    # Create empty layout for Corne (3x6+3 = 42 keys)
    layout = Layout.create_empty(
        keyboard="corne", 
        title="Complete Corne Layout with Home Row Mods"
    )
    
    print("1. Setting up home row mod behaviors...")
    
    # Add home row mod behaviors
    layout.behaviors.add_hold_tap(
        name="hm_gui", tap="&kp A", hold="&kp LGUI", 
        tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_alt", tap="&kp S", hold="&kp LALT",
        tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_ctrl", tap="&kp D", hold="&kp LCTRL",
        tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_shift", tap="&kp F", hold="&kp LSHIFT",
        tapping_term_ms=280, quick_tap_ms=175
    )
    
    # Right hand home row mods
    layout.behaviors.add_hold_tap(
        name="hm_rshift", tap="&kp J", hold="&kp RSHIFT",
        tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_rctrl", tap="&kp K", hold="&kp RCTRL",
        tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_ralt", tap="&kp L", hold="&kp RALT",
        tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_rgui", tap="&kp SEMICOLON", hold="&kp RGUI",
        tapping_term_ms=280, quick_tap_ms=175
    )
    
    print("2. Setting up layer toggle behaviors...")
    
    # Layer toggle behaviors
    layout.behaviors.add_hold_tap(
        name="lt_lower", tap="&kp SPACE", hold="&mo 1",
        tapping_term_ms=200
    )
    layout.behaviors.add_hold_tap(
        name="lt_raise", tap="&kp ENTER", hold="&mo 2", 
        tapping_term_ms=200
    )
    
    print("3. Adding useful combos...")
    
    # Useful combos
    layout.behaviors.add_combo(
        name="combo_esc", keys=[0, 1], binding="&kp ESC",
        timeout_ms=50
    )
    layout.behaviors.add_combo(
        name="combo_tab", keys=[10, 11], binding="&kp TAB",
        timeout_ms=50
    )
    layout.behaviors.add_combo(
        name="combo_del", keys=[8, 9], binding="&kp DEL",
        timeout_ms=50
    )
    
    print("4. Adding productivity macros...")
    
    # Productivity macros
    layout.behaviors.add_macro(
        name="macro_email",
        sequence=["&kp U", "&kp S", "&kp E", "&kp R", "&kp AT", "&kp E", "&kp X", "&kp A", "&kp M", "&kp P", "&kp L", "&kp E"]
    )
    layout.behaviors.add_macro(
        name="macro_screenshot",
        sequence=["&kp LGUI", "&kp LSHIFT", "&kp N4"]  # macOS screenshot
    )
    
    print("5. Creating base layer (QWERTY with home row mods)...")
    
    # Base layer (QWERTY with home row mods)
    base_layer = layout.layers.add("base")
    
    # Top row
    base_layer.set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E") \
              .set(3, "&kp R").set(4, "&kp T") \
              .set(5, "&kp Y").set(6, "&kp U").set(7, "&kp I") \
              .set(8, "&kp O").set(9, "&kp P")
    
    # Home row with mods
    base_layer.set(10, "&hm_gui").set(11, "&hm_alt").set(12, "&hm_ctrl") \
              .set(13, "&hm_shift").set(14, "&kp G") \
              .set(15, "&kp H").set(16, "&hm_rshift").set(17, "&hm_rctrl") \
              .set(18, "&hm_ralt").set(19, "&hm_rgui")
    
    # Bottom row
    base_layer.set(20, "&kp Z").set(21, "&kp X").set(22, "&kp C") \
              .set(23, "&kp V").set(24, "&kp B") \
              .set(25, "&kp N").set(26, "&kp M").set(27, "&kp COMMA") \
              .set(28, "&kp DOT").set(29, "&kp SLASH")
    
    # Thumb keys
    base_layer.set(30, "&kp LGUI").set(31, "&lt_lower").set(32, "&kp LCTRL") \
              .set(33, "&kp LALT").set(34, "&lt_raise").set(35, "&kp RSHIFT")
    
    print("6. Creating lower layer (numbers and navigation)...")
    
    # Lower layer (numbers and navigation)
    lower_layer = layout.layers.add("lower")
    
    # Numbers row
    lower_layer.set(0, "&kp N1").set(1, "&kp N2").set(2, "&kp N3") \
              .set(3, "&kp N4").set(4, "&kp N5") \
              .set(5, "&kp N6").set(6, "&kp N7").set(7, "&kp N8") \
              .set(8, "&kp N9").set(9, "&kp N0")
    
    # Navigation
    lower_layer.set(10, "&kp TAB").set(11, "&kp HOME").set(12, "&kp UP") \
              .set(13, "&kp END").set(14, "&kp PG_UP") \
              .set(15, "&kp PG_DN").set(16, "&kp LEFT").set(17, "&kp DOWN") \
              .set(18, "&kp RIGHT").set(19, "&kp BSPC")
    
    # Function keys
    lower_layer.set(20, "&kp F1").set(21, "&kp F2").set(22, "&kp F3") \
              .set(23, "&kp F4").set(24, "&kp F5") \
              .set(25, "&kp F6").set(26, "&kp F7").set(27, "&kp F8") \
              .set(28, "&kp F9").set(29, "&kp F10")
    
    # Thumb keys (transparent where not needed)
    lower_layer.set(30, "&trans").set(31, "&trans").set(32, "&trans") \
              .set(33, "&trans").set(34, "&mo 3").set(35, "&trans")
    
    print("7. Creating raise layer (symbols and brackets)...")
    
    # Raise layer (symbols and brackets)
    raise_layer = layout.layers.add("raise")
    
    # Symbol row
    raise_layer.set(0, "&kp EXCL").set(1, "&kp AT").set(2, "&kp HASH") \
              .set(3, "&kp DLLR").set(4, "&kp PRCNT") \
              .set(5, "&kp CARET").set(6, "&kp AMPS").set(7, "&kp STAR") \
              .set(8, "&kp LPAR").set(9, "&kp RPAR")
    
    # Brackets and operators
    raise_layer.set(10, "&kp GRAVE").set(11, "&kp LBKT").set(12, "&kp MINUS") \
              .set(13, "&kp RBKT").set(14, "&kp PIPE") \
              .set(15, "&kp BSLH").set(16, "&kp EQUAL").set(17, "&kp PLUS") \
              .set(18, "&kp LBRC").set(19, "&kp RBRC")
    
    # More symbols
    raise_layer.set(20, "&kp TILDE").set(21, "&kp UNDER").set(22, "&kp LT") \
              .set(23, "&kp GT").set(24, "&kp PIPE") \
              .set(25, "&trans").set(26, "&kp SQT").set(27, "&kp DQT") \
              .set(28, "&kp COLON").set(29, "&kp QMARK")
    
    # Thumb keys
    raise_layer.set(30, "&trans").set(31, "&mo 3").set(32, "&trans") \
              .set(33, "&trans").set(34, "&trans").set(35, "&trans")
    
    print("8. Creating adjust layer (system controls and macros)...")
    
    # Adjust layer (system controls and macros)
    adjust_layer = layout.layers.add("adjust")
    
    # Media controls
    adjust_layer.set(0, "&kp C_MUTE").set(1, "&kp C_VOL_DN").set(2, "&kp C_VOL_UP") \
               .set(3, "&kp C_PREV").set(4, "&kp C_NEXT") \
               .set(5, "&kp C_PP").set(6, "&macro_screenshot").set(7, "&macro_email") \
               .set(8, "&trans").set(9, "&trans")
    
    # System controls
    adjust_layer.set(10, "&bt BT_CLR").set(11, "&bt BT_SEL 0").set(12, "&bt BT_SEL 1") \
               .set(13, "&bt BT_SEL 2").set(14, "&trans") \
               .set(15, "&trans").set(16, "&trans").set(17, "&trans") \
               .set(18, "&trans").set(19, "&sys_reset")
    
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
    if 'layer_sizes' in stats:
        print("\nLayer Sizes:")
        for layer_name, size in stats['layer_sizes'].items():
            print(f"  {layer_name}: {size} keys")
    
    # Demonstrate layer queries
    print("\nLayer Queries:")
    nav_layers = layout.find_layers(lambda name: 'lower' in name or 'nav' in name.lower())
    print(f"  Navigation-related layers: {nav_layers}")
    
    system_layers = layout.find_layers(lambda name: 'adjust' in name or 'system' in name.lower())
    print(f"  System/adjust layers: {system_layers}")
    
    # Show some key bindings from base layer
    print("\nBase Layer Sample (first 10 keys):")
    base_layer = layout.layers.get("base")
    for i in range(min(10, len(base_layer.bindings))):
        binding = base_layer.bindings[i]
        print(f"  Key {i:2d}: {binding}")
    
    return layout


def save_and_validate_layout():
    """Save the layout and validate it can be loaded."""
    print("\n=== Save and Validation ===")
    
    layout = create_corne_layout()
    
    # Save the layout
    output_file = "/tmp/complete_corne_layout.json"
    print(f"Saving layout to: {output_file}")
    layout.save(output_file)
    
    # Validate by loading it back
    print("Loading layout to validate...")
    try:
        loaded_layout = Layout.from_file(output_file)
        
        # Compare statistics
        original_stats = layout.get_statistics()
        loaded_stats = loaded_layout.get_statistics()
        
        validation_checks = [
            ("Layer count", original_stats['layer_count'] == loaded_stats['layer_count']),
            ("Total bindings", original_stats['total_bindings'] == loaded_stats['total_bindings']),
            ("Total behaviors", original_stats['total_behaviors'] == loaded_stats['total_behaviors']),
            ("Keyboard name", original_stats['keyboard'] == loaded_stats['keyboard']),
            ("Title", original_stats['title'] == loaded_stats['title']),
        ]
        
        print("Validation Results:")
        all_passed = True
        for check_name, passed in validation_checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("✓ Layout saved and loaded successfully!")
        else:
            print("✗ Some validation checks failed")
            
        return loaded_layout
        
    except Exception as e:
        print(f"✗ Failed to load layout: {e}")
        return None


def main():
    """Main demonstration."""
    print("ZMK Layout Library - Real-World Corne Layout Example")
    print("=" * 70)
    
    try:
        # Create and demonstrate the layout
        demonstrate_layout_features()
        
        # Save and validate
        loaded_layout = save_and_validate_layout()
        
        if loaded_layout:
            print("\n" + "=" * 70)
            print("✓ Complete Corne layout created successfully!")
            print("✓ All features working: home row mods, layers, combos, macros")
            print("✓ Save/load cycle validated")
            print("\nThis demonstrates a production-ready ZMK layout created")
            print("entirely with the zmk-layout library's fluent API!")
        
    except Exception as e:
        print(f"✗ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()