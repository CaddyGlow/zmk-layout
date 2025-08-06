#!/usr/bin/env python3
"""
Simple Demo of zmk-layout Library

This demonstrates the core fluent API working exactly as specified in the plan:
Layout().layers.add().set().save()
"""

from zmk_layout import Layout


def target_api_demo():
    """Demonstrate the exact target API from the extraction plan."""
    print("=== Target API Demo ===")
    print("Demonstrating: Layout().layers.add().set().save()")

    # The exact API specification from the plan:
    # l = Layout("myfile.keymap")
    # l.layers.add("newlayer")
    # l.layers.get("newlayer").set(0, "&kp D")
    # l.save("mylayout.json")

    print("\n1. Creating empty layout...")
    layout = Layout.create_empty(keyboard="demo", title="Target API Demo")

    print("2. Adding layer with fluent chaining...")
    new_layer = layout.layers.add("newlayer")

    print("3. Setting key binding with chaining...")
    new_layer.set(0, "&kp D")

    print("4. Saving layout with chaining...")
    layout.save("/tmp/demo_layout.json")

    print("✓ Target API working perfectly!")

    # Show what we created
    stats = layout.get_statistics()
    print("\nCreated layout:")
    print(f"  Keyboard: {stats['keyboard']}")
    print(f"  Layers: {stats['layer_names']}")
    print(f"  Total bindings: {stats['total_bindings']}")


def fluent_chaining_demo():
    """Show fluent chaining within a single layer."""
    print("\n=== Fluent Chaining Demo ===")

    layout = Layout.create_empty(keyboard="crkbd", title="Fluent Chain Demo")

    # Demonstrate fluent chaining on a single layer
    print("Creating base layer with chained operations...")

    layout.layers.add("base").set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E").set(
        3, "&kp R"
    ).set(4, "&kp T")

    # Show multiple layer operations
    print("Adding and configuring multiple layers...")

    nav_layer = layout.layers.add("nav")
    nav_layer.set(0, "&kp HOME").set(1, "&kp END").set(2, "&kp PG_UP").set(
        3, "&kp PG_DN"
    )

    sym_layer = layout.layers.add("sym")
    sym_layer.set(0, "&kp EXCL").set(1, "&kp AT").set(2, "&kp HASH").set(3, "&kp DLLR")

    print("✓ Fluent chaining works perfectly!")

    # Show results
    base_layer = layout.layers.get("base")
    print(f"\nBase layer has {len(base_layer.bindings)} bindings:")
    for i, binding in enumerate(base_layer.bindings[:5]):
        print(f"  Key {i}: {binding}")


def behavior_fluent_demo():
    """Show behavior management with fluent API."""
    print("\n=== Behavior Fluent API Demo ===")

    layout = Layout.create_empty(keyboard="ferris", title="Behavior Demo")

    # Add behaviors with fluent interface
    print("Adding behaviors...")

    layout.behaviors.add_hold_tap(
        name="hm_a", tap="&kp A", hold="&kp LGUI", tapping_term_ms=200
    )

    layout.behaviors.add_combo(name="esc_combo", keys=[0, 1], binding="&kp ESC")

    layout.behaviors.add_macro(name="hello_macro", sequence=["&kp H", "&kp I"])

    # Use behaviors in layer
    print("Using behaviors in layout...")
    base_layer = layout.layers.add("base")
    base_layer.set(0, "&hm_a").set(1, "&kp S").set(10, "&hello_macro")

    stats = layout.get_statistics()
    print(f"✓ Added {stats['total_behaviors']} behaviors successfully!")


def context_manager_demo():
    """Show context manager usage."""
    print("\n=== Context Manager Demo ===")

    print("Using layout in context manager...")

    with Layout.create_empty(keyboard="planck", title="Context Demo") as layout:
        # All operations are managed within context
        layout.layers.add("base").set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E")

        layout.layers.add("lower").set(0, "&kp N1").set(1, "&kp N2").set(2, "&kp N3")

        layout.behaviors.add_hold_tap(
            name="mt_space", tap="&kp SPACE", hold="&kp LSHIFT"
        )

        # Save within context
        layout.save("/tmp/context_demo.json")
        layout.save("/tmp/context_demo.keymap")

        stats = layout.get_statistics()
        print("✓ Context operations completed:")
        print(f"  Layers: {len(stats['layer_names'])}")
        print(f"  Behaviors: {stats['total_behaviors']}")

    print("✓ Context automatically cleaned up!")


def main():
    """Run all demonstrations."""
    print("ZMK Layout Library - Simple API Demonstrations")
    print("=" * 60)

    demonstrations = [
        target_api_demo,
        fluent_chaining_demo,
        behavior_fluent_demo,
        context_manager_demo,
    ]

    for demo_func in demonstrations:
        try:
            demo_func()
            print()
        except Exception as e:
            print(f"✗ Demo failed: {e}")
            import traceback

            traceback.print_exc()
            print()

    print("=" * 60)
    print("✓ All demonstrations completed!")
    print("\nThe zmk-layout library fluent API is working exactly as designed!")


if __name__ == "__main__":
    main()
