#!/usr/bin/env python3
"""
Corrected Basic Usage Examples for zmk-layout Library

This file demonstrates the correct usage of the zmk-layout library's fluent API.
"""

from zmk_layout import Layout


def example_1_create_empty_layout():
    """Create a new empty layout and add layers."""
    print("=== Example 1: Create Empty Layout ===")

    # Create a new empty layout - correct API
    layout = Layout.create_empty(keyboard="corne", title="My Corne Layout")

    # Add layers - each add() returns a LayerProxy, not LayerManager
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

    layout = Layout.create_empty(keyboard="planck", title="My Planck Layout")

    # Add a base layer and set some key bindings using chaining
    base_layer = layout.layers.add("base")
    base_layer.set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E").set(3, "&kp R")

    # Add gaming layer with different bindings
    gaming_layer = layout.layers.add("gaming")
    gaming_layer.set(0, "&kp T").set(1, "&kp A").set(2, "&kp B").set(3, "&trans")

    # Get specific layer and modify it
    base_layer = layout.layers.get("base")
    base_layer.set(10, "&kp SPACE").set(11, "&mo 1")

    print("Base layer bindings (first 5 keys):")
    base_layer = layout.layers.get("base")
    for i in range(min(5, len(base_layer.bindings))):
        binding = base_layer.bindings[i]
        print(f"  Key {i}: {binding}")

    return layout


def example_3_batch_operations():
    """Use batch operations for multiple changes."""
    print("\n=== Example 3: Batch Operations ===")

    layout = Layout.create_empty(keyboard="kyria", title="Kyria Layout")

    # Define batch operations
    def setup_base_layer(layout):
        layout.layers.add("base")
        return layout

    def setup_nav_layer(layout):
        layer = layout.layers.add("nav")
        layer.set(0, "&kp HOME").set(1, "&kp END").set(2, "&kp PG_UP").set(3, "&kp PG_DN")
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
    print(f"  Behaviors: {stats['total_behaviors']}")

    return layout


def example_4_behavior_management():
    """Add custom behaviors to the layout."""
    print("\n=== Example 4: Behavior Management ===")

    layout = Layout.create_empty(keyboard="iris", title="Iris with Behaviors")

    # Add different types of behaviors using fluent API
    layout.behaviors.add_hold_tap(name="mt_ctrl_a", tap="&kp A", hold="&kp LCTRL", tapping_term_ms=200)

    layout.behaviors.add_combo(name="combo_esc", keys=[0, 1], binding="&kp ESC", timeout_ms=50)

    layout.behaviors.add_macro(name="email_macro", sequence=["&kp H", "&kp E", "&kp L", "&kp L", "&kp O"])

    # Add layer and use the custom behaviors
    base_layer = layout.layers.add("base")
    base_layer.set(0, "&mt_ctrl_a").set(1, "&kp S").set(10, "&email_macro")

    stats = layout.get_statistics()
    print(f"Added {stats['total_behaviors']} custom behaviors")

    return layout


def example_5_context_manager():
    """Use context manager for automatic resource handling."""
    print("\n=== Example 5: Context Manager Usage ===")

    # Create layout using context manager
    with Layout.create_empty(keyboard="moonlander", title="Moonlander Layout") as layout:
        # All operations within context are automatically managed
        base_layer = layout.layers.add("base")
        base_layer.set_range(0, 4, ["&kp Q", "&kp W", "&kp E", "&kp R"])

        fn_layer = layout.layers.add("fn")
        fn_layer.set(0, "&kp F1").set(1, "&kp F2").set(2, "&kp F3")

        # Add some behaviors
        layout.behaviors.add_hold_tap(name="sft_spc", tap="&kp SPACE", hold="&kp LSHIFT")

        print("Context manager operations completed successfully")
        print(f"Final layer count: {len(layout.layers.get_names())}")

    # Layout is automatically cleaned up after context


def example_6_query_and_search():
    """Query and search functionality."""
    print("\n=== Example 6: Query and Search ===")

    layout = Layout.create_empty(keyboard="ergodox", title="ErgoDox Layout")

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
    print(f"  Keyboard: {stats['keyboard']}")
    print(f"  Title: {stats['title']}")
    print(f"  Total layers: {stats['layer_count']}")

    return layout


def example_7_save_and_load():
    """Save and load layouts."""
    print("\n=== Example 7: Save and Load ===")

    # Create and configure a layout
    layout = Layout.create_empty(keyboard="lily58", title="Lily58 Pro Layout")

    base_layer = layout.layers.add("base")
    base_layer.set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E")

    lower_layer = layout.layers.add("lower")
    lower_layer.set(0, "&kp N1").set(1, "&kp N2").set(2, "&kp N3")

    layout.behaviors.add_hold_tap(name="home_a", tap="&kp A", hold="&kp LGUI")

    # Save layout to JSON file
    output_file = "/tmp/lily58_layout.json"
    layout.save(output_file)
    print(f"Layout saved to: {output_file}")

    # Load layout from file
    try:
        loaded_layout = Layout.from_file(output_file)
        print(f"Successfully loaded layout with {len(loaded_layout.layers.get_names())} layers")

        # Verify data integrity
        original_stats = layout.get_statistics()
        loaded_stats = loaded_layout.get_statistics()

        if original_stats["layer_count"] == loaded_stats["layer_count"]:
            print("✓ Save/load integrity verified")
        else:
            print("✗ Save/load integrity check failed")

    except Exception as e:
        print(f"Error loading layout: {e}")


def example_8_layer_manipulation():
    """Advanced layer manipulation."""
    print("\n=== Example 8: Layer Manipulation ===")

    layout = Layout.create_empty(keyboard="corne", title="Corne Advanced")

    # Add several layers
    layout.layers.add("base")
    layout.layers.add("nav")
    layout.layers.add("sym")
    layout.layers.add("gaming")

    # Demonstrate layer operations
    print(f"Initial layers: {layout.layers.get_names()}")

    # Move a layer
    layout.layers.move("gaming", 1)  # Move gaming to position 1
    print(f"After moving gaming: {layout.layers.get_names()}")

    # Copy a layer
    layout.layers.copy("base", "base_backup")
    print(f"After copying base: {layout.layers.get_names()}")

    # Rename a layer
    layout.layers.rename("base_backup", "backup")
    print(f"After renaming: {layout.layers.get_names()}")

    # Remove a layer
    layout.layers.remove("backup")
    print(f"After removing backup: {layout.layers.get_names()}")

    return layout


def main():
    """Run all examples."""
    print("ZMK Layout Library - Corrected Usage Examples")
    print("=" * 60)

    examples = [
        example_1_create_empty_layout,
        example_2_modify_layer_bindings,
        example_3_batch_operations,
        example_4_behavior_management,
        example_5_context_manager,
        example_6_query_and_search,
        example_7_save_and_load,
        example_8_layer_manipulation,
    ]

    results = {}

    for example_func in examples:
        try:
            result = example_func()
            results[example_func.__name__] = result
            print("✓ Success\n")
        except Exception as e:
            print(f"✗ Failed: {e}")
            import traceback

            traceback.print_exc()
            print()

    print("=" * 60)
    print(f"Completed {len(results)}/{len(examples)} examples successfully!")


if __name__ == "__main__":
    main()
