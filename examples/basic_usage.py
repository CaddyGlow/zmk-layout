#!/usr/bin/env python3
"""
Basic Usage Examples for zmk-layout Library

This file demonstrates the core fluent API functionality of the zmk-layout library.
"""

from zmk_layout import Layout


def example_1_create_empty_layout():
    """Create a new empty layout and add layers."""
    print("=== Example 1: Create Empty Layout ===")

    # Create a new empty layout
    layout = Layout.create_empty(keyboard="corne", title="My Corne Layout")

    # Add layers using fluent API
    layout.layers.add("base")
    layout.layers.add("lower")
    layout.layers.add("raise")

    print(f"Created layout with {len(layout.layers.get_names())} layers:")
    for layer_name in layout.layers.get_names():
        print(f"  - {layer_name}")

    return layout


def example_2_modify_layer_bindings():
    """Modify individual key bindings in layers."""
    print("\n=== Example 2: Modify Layer Bindings ===")

    layout = Layout.create_empty("planck", "My Planck Layout")

    # Add a base layer and set some key bindings
    layout.layers.add("base").set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E").set(
        3, "&kp R"
    )

    # Add gaming layer with different bindings
    layout.layers.add("gaming").set(0, "&kp T").set(1, "&kp A").set(2, "&kp B").set(
        3, "&trans"
    )

    # Get specific layer and modify it
    base_layer = layout.layers.get("base")
    base_layer.set(10, "&kp SPACE").set(11, "&mo 1")

    print("Base layer bindings (first 5 keys):")
    base_layer = layout.layers.get("base")
    for i in range(min(5, len(base_layer.bindings))):
        try:
            binding = base_layer.bindings[i]
            print(f"  Key {i}: {binding}")
        except Exception:
            print(f"  Key {i}: No binding")

    return layout


def example_3_batch_operations():
    """Use batch operations for multiple changes."""
    print("\n=== Example 3: Batch Operations ===")

    layout = Layout.create_empty("kyria", "Kyria Layout")

    # Define batch operations
    def setup_base_layer(layout):
        layout.layers.add("base")
        return layout

    def setup_nav_layer(layout):
        layer = layout.layers.add("nav")
        layer.set(0, "&kp HOME").set(1, "&kp END").set(2, "&kp PG_UP").set(
            3, "&kp PG_DN"
        )
        return layout

    def setup_sym_layer(layout):
        layer = layout.layers.add("sym")
        layer.set(0, "&kp EXCL").set(1, "&kp AT").set(2, "&kp HASH").set(3, "&kp DLLR")
        return layout

    # Execute batch operations
    layout.batch_operation([setup_base_layer, setup_nav_layer, setup_sym_layer])

    stats = layout.get_statistics()
    print("Layout statistics after batch operations:")
    print(f"  Layers: {stats['layer_count']}")
    print(f"  Total bindings: {stats['total_bindings']}")
    print(f"  Behaviors used: {len(stats['behaviors_used'])}")

    return layout


def example_4_behavior_management():
    """Add custom behaviors to the layout."""
    print("\n=== Example 4: Behavior Management ===")

    layout = Layout.create_empty("iris", "Iris with Behaviors")

    # Add different types of behaviors using fluent API
    layout.behaviors.add_hold_tap(
        name="mt_ctrl_a", tap="&kp A", hold="&kp LCTRL", tapping_term_ms=200
    ).add_combo(
        name="combo_esc", keys=[0, 1], binding="&kp ESC", timeout_ms=50
    ).add_macro(
        name="email_macro", sequence=["&kp H", "&kp E", "&kp L", "&kp L", "&kp O"]
    )

    # Add layer and use the custom behaviors
    layout.layers.add("base").set(0, "&mt_ctrl_a").set(1, "&kp S").set(
        10, "&email_macro"
    )

    stats = layout.get_statistics()
    print(f"Added {len(stats['behaviors_used'])} custom behaviors:")
    for behavior in stats["behaviors_used"]:
        print(f"  - {behavior}")

    return layout


def example_5_context_manager():
    """Use context manager for automatic resource handling."""
    print("\n=== Example 5: Context Manager Usage ===")

    # Create layout using context manager
    with Layout.create_empty("moonlander", "Moonlander Layout") as layout:
        # All operations within context are automatically managed
        layout.layers.add("base").set_range(0, 4, ["&kp Q", "&kp W", "&kp E", "&kp R"])

        layout.layers.add("fn").set(0, "&kp F1").set(1, "&kp F2").set(2, "&kp F3")

        # Add some behaviors
        layout.behaviors.add_hold_tap(
            name="sft_spc", tap="&kp SPACE", hold="&kp LSHIFT"
        )

        print("Context manager operations completed successfully")
        print(f"Final layer count: {len(layout.get_layer_names())}")

    # Layout is automatically cleaned up after context


def example_6_query_and_search():
    """Query and search functionality."""
    print("\n=== Example 6: Query and Search ===")

    layout = Layout.create_empty("ergodox", "ErgoDox Layout")

    # Add multiple layers
    layer_names = ["base", "gaming", "gaming_fn", "nav", "sym", "adjust"]
    for name in layer_names:
        layout.layers.add(name)

    # Find layers matching criteria
    gaming_layers = layout.find_layers(lambda name: "gaming" in name)
    print(f"Gaming-related layers: {gaming_layers}")

    # Find layers by pattern
    fn_layers = layout.find_layers(lambda name: name.endswith("_fn"))
    print(f"Function layers: {fn_layers}")

    # Get comprehensive statistics
    stats = layout.get_statistics()
    print("\nLayout overview:")
    print(f"  Keyboard: {stats['keyboard_name']}")
    print(f"  Total layers: {stats['layer_count']}")
    print(f"  Empty layers: {stats['empty_layer_count']}")

    return layout


def example_7_save_and_load():
    """Save and load layouts."""
    print("\n=== Example 7: Save and Load ===")

    # Create and configure a layout
    layout = Layout.create_empty("lily58", "Lily58 Pro Layout")

    layout.layers.add("base").set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E")

    layout.layers.add("lower").set(0, "&kp N1").set(1, "&kp N2").set(2, "&kp N3")

    layout.behaviors.add_hold_tap(name="home_a", tap="&kp A", hold="&kp LGUI")

    # Save layout to JSON file
    output_file = "/tmp/lily58_layout.json"
    layout.save(output_file)
    print(f"Layout saved to: {output_file}")

    # Load layout from file
    try:
        loaded_layout = Layout.from_file(output_file)
        print(
            f"Successfully loaded layout with {len(loaded_layout.get_layer_names())} layers"
        )

        # Verify data integrity
        original_stats = layout.get_statistics()
        loaded_stats = loaded_layout.get_statistics()

        if original_stats["layer_count"] == loaded_stats["layer_count"]:
            print("✓ Save/load integrity verified")
        else:
            print("✗ Save/load integrity check failed")

    except Exception as e:
        print(f"Error loading layout: {e}")


def main():
    """Run all examples."""
    print("ZMK Layout Library - Usage Examples")
    print("=" * 50)

    try:
        example_1_create_empty_layout()
        example_2_modify_layer_bindings()
        example_3_batch_operations()
        example_4_behavior_management()
        example_5_context_manager()
        example_6_query_and_search()
        example_7_save_and_load()

        print("\n" + "=" * 50)
        print("✓ All examples completed successfully!")

    except Exception as e:
        print(f"\n✗ Example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
