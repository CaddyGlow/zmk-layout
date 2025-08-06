#!/usr/bin/env python3
"""
Simple examples of the new Layout helper methods: from_string() and to_keymap()

These helpers make it much easier to work with layouts:
- from_string() auto-detects JSON or keymap format
- to_keymap() generates ZMK keymap format directly
"""

from pathlib import Path

from zmk_layout import Layout


def example_load_json_string():
    """Load layout from JSON string using from_string()."""
    print("=== Example 1: Load from JSON string ===")

    json_content = """{
        "version": "1.0",
        "keyboard": "corne",
        "title": "My Corne Layout",
        "layers": [
            [
                {"key": 0, "value": "&kp Q"},
                {"key": 1, "value": "&kp W"},
                {"key": 2, "value": "&kp E"}
            ]
        ],
        "layer_names": ["base"]
    }"""

    # Simply use from_string() - it auto-detects JSON
    layout = Layout.from_string(json_content)
    print(f"✓ Loaded layout: {layout.data.title}")
    print(f"  Keyboard: {layout.data.keyboard}")
    print(f"  Layers: {', '.join(layout.data.layer_names)}")

    return layout


def example_load_keymap_string():
    """Load layout from keymap string using from_string()."""
    print("\n=== Example 2: Load from keymap string ===")

    keymap_content = """
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp Q    &kp W    &kp E    &kp R    &kp T
                &kp A    &kp S    &kp D    &kp F    &kp G
            >;
        };

        nav_layer {
            bindings = <
                &kp HOME  &kp UP    &kp END   &kp PG_UP  &trans
                &kp LEFT  &kp DOWN  &kp RIGHT &kp PG_DN  &trans
            >;
        };
    };
};
"""

    # Simply use from_string() - it auto-detects keymap format
    layout = Layout.from_string(keymap_content, title="My Keymap")
    print(f"✓ Loaded layout: {layout.data.title}")
    print(f"  Layers: {', '.join(layout.data.layer_names)}")

    return layout


def example_generate_keymap():
    """Generate keymap string using to_keymap()."""
    print("\n=== Example 3: Generate keymap with to_keymap() ===")

    # Create a simple layout
    layout = Layout.create_empty(keyboard="planck", title="Planck Layout")

    # Add a base layer
    base = layout.layers.add("base")
    base.set_range(
        0,
        10,
        [
            "&kp Q",
            "&kp W",
            "&kp E",
            "&kp R",
            "&kp T",
            "&kp Y",
            "&kp U",
            "&kp I",
            "&kp O",
            "&kp P",
        ],
    )

    # Add a numbers layer
    numbers = layout.layers.add("numbers")
    numbers.set_range(
        0,
        10,
        [
            "&kp N1",
            "&kp N2",
            "&kp N3",
            "&kp N4",
            "&kp N5",
            "&kp N6",
            "&kp N7",
            "&kp N8",
            "&kp N9",
            "&kp N0",
        ],
    )

    # Generate keymap with headers
    keymap_with_headers = layout.to_keymap()
    print("✓ Generated keymap with headers:")
    print("  " + keymap_with_headers[:100].replace("\n", "\n  ") + "...")

    # Generate just the keymap node (no headers)
    keymap_node_only = layout.to_keymap(include_headers=False)
    print("\n✓ Generated keymap node only:")
    print("  " + keymap_node_only[:100].replace("\n", "\n  ") + "...")

    return layout, keymap_with_headers


def example_file_operations():
    """Show how to combine with file operations."""
    print("\n=== Example 4: File operations with helpers ===")

    # Read any file and auto-detect format
    test_file = Path("/tmp/test_layout.json")
    test_file.write_text("""{
        "keyboard": "lily58",
        "title": "Test Layout",
        "layers": [[]],
        "layer_names": ["default"]
    }""")

    # Load from file using from_string()
    content = test_file.read_text()
    layout = Layout.from_string(content)
    print(f"✓ Loaded from file: {layout.data.title}")

    # Save as keymap
    keymap_file = Path("/tmp/test_layout.keymap")
    keymap_content = layout.to_keymap()
    keymap_file.write_text(keymap_content)
    print(f"✓ Saved as keymap: {keymap_file}")

    # Clean up
    test_file.unlink()
    keymap_file.unlink()

    return layout


def example_roundtrip():
    """Complete roundtrip: keymap -> Layout -> modified -> keymap."""
    print("\n=== Example 5: Complete roundtrip ===")

    # Start with a working JSON format instead of keymap for better parsing
    original_json = """{
        "version": "1.0",
        "keyboard": "test_board",
        "title": "Roundtrip Test",
        "layers": [
            [
                {"key": 0, "value": "&kp A"},
                {"key": 1, "value": "&kp B"},
                {"key": 2, "value": "&kp C"},
                {"key": 3, "value": "&kp D"},
                {"key": 4, "value": "&kp E"},
                {"key": 5, "value": "&kp F"}
            ]
        ],
        "layer_names": ["alpha_layer"],
        "hold_taps": [],
        "combos": [],
        "macros": []
    }"""

    # Load from JSON
    layout = Layout.from_string(original_json)
    print(f"✓ Loaded layout with {layout.layers.count} layer(s)")
    print(
        f"  Original first key: {layout.data.layers[0][0] if layout.data.layers and layout.data.layers[0] else 'N/A'}"
    )

    # Modify it
    if layout.layers.count > 0:
        # Get the first layer by name
        first_layer_name = layout.data.layer_names[0]
        layout.layers.get(first_layer_name).set(0, "&kp ESC")
        print("✓ Modified first key to ESC")

    # Add another layer
    numbers_layer = layout.layers.add("numbers")
    numbers_layer.set_range(
        0, 6, ["&kp N1", "&kp N2", "&kp N3", "&kp N4", "&kp N5", "&kp N6"]
    )
    print("✓ Added numbers layer")

    # Generate new keymap
    new_keymap = layout.to_keymap(include_headers=False)
    print("✓ Generated modified keymap")

    # Show what we created
    print(f"\nFinal layout has {layout.layers.count} layers:")
    for i, name in enumerate(layout.data.layer_names):
        print(f"  {i + 1}. {name}")

    # Show keymap preview
    lines = new_keymap.strip().split("\n")
    preview_lines = [line for line in lines[:15] if line.strip()]
    print("\nGenerated keymap preview:")
    for line in preview_lines:
        print(f"  {line}")
    if len(lines) > 15:
        print("  ...")

    return layout


if __name__ == "__main__":
    print("Layout Helper Methods Demo")
    print("=" * 60)

    # Run all examples
    example_load_json_string()
    example_load_keymap_string()
    example_generate_keymap()
    example_file_operations()
    example_roundtrip()

    print("\n" + "=" * 60)
    print("Summary of new helper methods:")
    print("\n1. Layout.from_string(content, title='optional')")
    print("   - Auto-detects JSON or keymap format")
    print("   - No need to know format in advance")
    print("\n2. Layout.to_keymap(keyboard_name=None, include_headers=True)")
    print("   - Generates ZMK keymap string directly")
    print("   - Option to include/exclude headers")
    print("\nThese replace the need for:")
    print("   - Manual parser setup")
    print("   - Manual generator setup")
    print("   - Format detection logic")
    print("   - Binding processing logic")
