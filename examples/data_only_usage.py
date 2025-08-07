#!/usr/bin/env python3
"""
Data-Only API Usage Examples for zmk-layout Library

This file demonstrates the new data-only API approach where Layout operates purely
on data without direct file I/O. External file operations are handled using
Python's pathlib.Path and the JSON utilities from zmk_layout.utils.json_operations.

Key concepts:
- Layout.from_dict(data) instead of Layout.from_file(path)
- Layout.to_dict() instead of Layout.save(path)
- Path.read_text()/write_text() for file operations
- JSON utilities for data serialization
- Parser works with string content, not files directly
- Generators produce string output, not files
"""

import json
from pathlib import Path

from zmk_layout import Layout
from zmk_layout.generators.zmk_generator import ZMKGenerator
from zmk_layout.parsers.zmk_keymap_parser import ParsingMode, ZMKKeymapParser
from zmk_layout.providers.factory import create_default_providers
from zmk_layout.utils.json_operations import (
    parse_json_data,
    parse_layout_data,
    serialize_json_data,
    serialize_layout_data,
)


def example_1_load_from_json_file():
    """Load layout data from a JSON file using Path and Layout.from_dict()."""
    print("=== Example 1: Load from JSON File ===")

    # Step 1: Create some sample data and save it to a file
    sample_data = {
        "version": "1.0",
        "keyboard": "corne",
        "title": "Sample Corne Layout",
        "layers": [
            [
                {"key": 0, "value": "&kp Q"},
                {"key": 1, "value": "&kp W"},
                {"key": 2, "value": "&kp E"},
                {"key": 3, "value": "&kp R"},
                {"key": 4, "value": "&kp T"},
                {"key": 5, "value": "&kp Y"},
                {"key": 6, "value": "&kp U"},
                {"key": 7, "value": "&kp I"},
                {"key": 8, "value": "&kp O"},
                {"key": 9, "value": "&kp P"},
            ]
        ],
        "layer_names": ["base"],
        "hold_taps": [],
        "combos": [],
        "macros": [],
    }

    # Step 2: Save sample data to file using Path.write_text()
    sample_file = Path("/tmp/sample_layout.json")
    sample_file.write_text(json.dumps(sample_data, indent=2))
    print(f"Created sample file: {sample_file}")

    # Step 3: Load data from file using Path.read_text()
    json_content = sample_file.read_text()
    print("✓ Read JSON content from file using Path.read_text()")

    # Step 4: Parse JSON to dictionary
    layout_dict = parse_json_data(json_content)
    print("✓ Parsed JSON string to dictionary")

    # Step 5: Create Layout from dictionary using from_dict()
    layout = Layout.from_dict(layout_dict)
    print("✓ Created Layout from dictionary using Layout.from_dict()")

    # Verify the layout
    stats = layout.get_statistics()
    print(
        f"Loaded layout: {stats['keyboard_name']}, {len(stats['layer_names'])} layers"
    )

    return layout, sample_file


def example_2_save_to_json_file():
    """Save layout data to a JSON file using Layout.to_dict() and Path.write_text()."""
    print("\n=== Example 2: Save to JSON File ===")

    # Step 1: Create a layout programmatically
    layout = Layout.create_empty(keyboard="lily58", title="Lily58 Demo Layout")

    # Add some content
    base_layer = layout.layers.add("base")
    base_layer.set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E")

    nav_layer = layout.layers.add("nav")
    nav_layer.set(0, "&kp HOME").set(1, "&kp END").set(2, "&kp PG_UP")

    layout.behaviors.add_hold_tap(
        name="mt_space", tap="&kp SPACE", hold="&mo 1", tapping_term_ms=200
    )

    print("✓ Created layout with layers and behaviors")

    # Step 2: Convert layout to dictionary using to_dict()
    layout_dict = layout.to_dict()
    print("✓ Converted Layout to dictionary using to_dict()")

    # Step 3: Serialize to JSON string
    json_content = serialize_json_data(layout_dict, indent=2)
    print("✓ Serialized dictionary to JSON string")

    # Step 4: Write to file using Path.write_text()
    output_file = Path("/tmp/lily58_layout.json")
    output_file.write_text(json_content)
    print(f"✓ Saved layout to file: {output_file}")

    return layout, output_file


def example_3_parse_keymap_string():
    """Parse ZMK keymap content from string using the parser."""
    print("\n=== Example 3: Parse Keymap String ===")

    # Sample keymap content as a string
    keymap_content = """
/*
 * Sample Keymap for Demo
 */

#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

#define DEFAULT 0
#define LOWER   1

/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp Q  &kp W  &kp E  &kp R  &kp T
                &kp Y  &kp U  &kp I  &kp O  &kp P
                &kp A  &kp S  &kp D  &kp F  &kp G
                &kp H  &kp J  &kp K  &kp L  &kp SEMICOLON
            >;
        };

        lower_layer {
            bindings = <
                &kp N1  &kp N2  &kp N3  &kp N4  &kp N5
                &kp N6  &kp N7  &kp N8  &kp N9  &kp N0
                &trans  &trans  &trans  &trans  &trans
                &trans  &trans  &trans  &trans  &trans
            >;
        };
    };
};
"""

    print("✓ Prepared keymap content as string")

    # Step 1: Parse the keymap content directly from string
    providers = create_default_providers()
    parser = ZMKKeymapParser(
        configuration_provider=providers.configuration, logger=providers.logger
    )

    # Parse keymap content string directly (not file path)
    parse_result = parser.parse_keymap(
        keymap_content, title="Sample Keymap", mode=ParsingMode.FULL
    )
    print("✓ Parsed keymap content string using ZMKKeymapParser")

    # Step 2: Extract layout data
    if hasattr(parse_result, "layout_data") and parse_result.layout_data is not None:
        layout_data = parse_result.layout_data
    else:
        layout_data = parse_result

    print(f"✓ Extracted layout data with {len(layout_data.layer_names)} layers")

    # Step 3: Convert to dictionary
    layout_dict = layout_data.model_dump(by_alias=True)
    print("✓ Converted parsed data to dictionary")

    # Step 4: Create Layout from parsed data
    layout = Layout.from_dict(layout_dict)
    print("✓ Created Layout from parsed data")

    stats = layout.get_statistics()
    print(f"Final layout: {stats['keyboard_name']}, {len(stats['layer_names'])} layers")

    return layout


def example_4_generate_keymap_string():
    """Generate ZMK keymap string output using generators."""
    print("\n=== Example 4: Generate Keymap String ===")

    # Step 1: Create a layout with comprehensive content
    layout = Layout.create_empty(keyboard="planck", title="Planck Demo Layout")

    # Add behaviors
    layout.behaviors.add_hold_tap(
        name="hm_gui",
        tap="&kp A",
        hold="&kp LGUI",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_combo(
        name="esc_combo", keys=[0, 1], binding="&kp ESC", timeout_ms=50
    )
    layout.behaviors.add_macro(
        name="hello_macro", sequence=["&kp H", "&kp E", "&kp L", "&kp L", "&kp O"]
    )

    # Add layers
    base_layer = layout.layers.add("base")
    base_layer.set_range(
        0,
        10,
        [
            "&hm_gui",
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

    lower_layer = layout.layers.add("lower")
    lower_layer.set_range(
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

    print("✓ Created layout with behaviors and layers")

    # Step 2: Set up generator with providers
    providers = create_default_providers()
    generator = ZMKGenerator(
        configuration_provider=providers.configuration,
        template_provider=providers.template,
        logger=providers.logger,
    )

    # Step 3: Create a mock profile (simplified for demo)
    from types import SimpleNamespace

    mock_profile = SimpleNamespace(
        keyboard_config=SimpleNamespace(
            zmk=SimpleNamespace(
                compatible_strings=SimpleNamespace(keymap="zmk,keymap"),
                patterns=SimpleNamespace(
                    layer_define="#define {layer_name} {layer_index}"
                ),
            )
        )
    )

    # Step 4: Generate keymap components as strings
    layout_data = layout.data
    layer_names = layout_data.layer_names
    layers_data = layout_data.layers

    # Generate behaviors DTSI
    behaviors_dtsi = ""
    if layout_data.hold_taps:
        behaviors_dtsi = generator.generate_behaviors_dtsi(
            mock_profile, layout_data.hold_taps
        )
        print("✓ Generated behaviors DTSI string")

    # Generate combos DTSI
    combos_dtsi = ""
    if layout_data.combos:
        combos_dtsi = generator.generate_combos_dtsi(
            mock_profile, layout_data.combos, layer_names
        )
        print("✓ Generated combos DTSI string")

    # Generate macros DTSI
    macros_dtsi = ""
    if layout_data.macros:
        macros_dtsi = generator.generate_macros_dtsi(mock_profile, layout_data.macros)
        print("✓ Generated macros DTSI string")

    # Generate keymap node
    keymap_node = generator.generate_keymap_node(mock_profile, layer_names, layers_data)
    print("✓ Generated keymap node string")

    # Generate layer defines
    layer_defines = generator.generate_layer_defines(mock_profile, layer_names)
    print("✓ Generated layer defines string")

    # Step 5: Assemble complete keymap content
    keymap_parts = []
    keymap_parts.append("/*")
    keymap_parts.append(f" * {layout_data.title}")
    keymap_parts.append(" * Generated using data-only API")
    keymap_parts.append(" */")
    keymap_parts.append("")
    keymap_parts.append("#include <behaviors.dtsi>")
    keymap_parts.append("#include <dt-bindings/zmk/keys.h>")
    keymap_parts.append("")

    if layer_defines:
        keymap_parts.append("/* Layer definitions */")
        keymap_parts.append(layer_defines)
        keymap_parts.append("")

    keymap_parts.append("/ {")

    if behaviors_dtsi or combos_dtsi or macros_dtsi:
        keymap_parts.append("    behaviors {")
        if behaviors_dtsi:
            keymap_parts.append(behaviors_dtsi)
        if macros_dtsi:
            if behaviors_dtsi:
                keymap_parts.append("")
            keymap_parts.append(macros_dtsi)
        keymap_parts.append("    };")
        keymap_parts.append("")

    if combos_dtsi:
        keymap_parts.append(f"    {combos_dtsi}")
        keymap_parts.append("")

    keymap_parts.append(f"    {keymap_node}")
    keymap_parts.append("};")

    complete_keymap = "\n".join(keymap_parts)
    print("✓ Assembled complete keymap string")

    # Step 6: Save generated keymap to file
    keymap_file = Path("/tmp/generated_planck.keymap")
    keymap_file.write_text(complete_keymap)
    print(f"✓ Saved generated keymap to: {keymap_file}")

    return layout, complete_keymap, keymap_file


def example_5_roundtrip_data_operations():
    """Demonstrate complete roundtrip: JSON → Layout → modification → JSON."""
    print("\n=== Example 5: Roundtrip Data Operations ===")

    # Step 1: Start with JSON data
    initial_data = {
        "version": "1.0",
        "keyboard": "ergodox",
        "title": "ErgoDox Roundtrip Demo",
        "layers": [
            [
                {"key": 0, "value": "&kp Q"},
                {"key": 1, "value": "&kp W"},
                {"key": 2, "value": "&kp E"},
            ]
        ],
        "layer_names": ["base"],
        "hold_taps": [],
        "combos": [],
        "macros": [],
    }

    print("✓ Created initial JSON data")

    # Step 2: Load into Layout
    layout = Layout.from_dict(initial_data)
    print("✓ Loaded data into Layout using from_dict()")

    # Step 3: Modify the layout
    # Add a new layer
    nav_layer = layout.layers.add("nav")
    nav_layer.set(0, "&kp HOME").set(1, "&kp END").set(2, "&kp PG_UP")

    # Add a behavior
    layout.behaviors.add_hold_tap(
        name="ctrl_a", tap="&kp A", hold="&kp LCTRL", tapping_term_ms=200
    )

    # Modify existing layer
    base_layer = layout.layers.get("base")
    base_layer.set(0, "&ctrl_a")  # Replace Q with our new behavior

    print("✓ Modified layout: added layer, behavior, modified bindings")

    # Step 4: Extract modified data
    modified_data = layout.to_dict()
    print("✓ Extracted modified data using to_dict()")

    # Step 5: Save to files
    # Save original
    original_file = Path("/tmp/roundtrip_original.json")
    original_file.write_text(serialize_json_data(initial_data, indent=2))

    # Save modified
    modified_file = Path("/tmp/roundtrip_modified.json")
    modified_file.write_text(serialize_json_data(modified_data, indent=2))

    print(f"✓ Saved original data to: {original_file}")
    print(f"✓ Saved modified data to: {modified_file}")

    # Step 6: Verify roundtrip by loading modified data back
    reloaded_data = parse_json_data(modified_file.read_text())
    reloaded_layout = Layout.from_dict(reloaded_data)

    # Verify the modifications persisted
    reloaded_stats = reloaded_layout.get_statistics()
    print("✓ Reloaded modified data and verified:")
    print(
        f"  - Layers: {len(reloaded_stats['layer_names'])} ({', '.join(reloaded_stats['layer_names'])})"
    )
    print(f"  - Behaviors: {reloaded_stats['behavior_count']}")
    print(f"  - First binding: {reloaded_layout.layers.get('base').bindings[0].value}")

    return layout, original_file, modified_file


def example_6_json_utilities_showcase():
    """Showcase the JSON utilities from zmk_layout.utils.json_operations."""
    print("\n=== Example 6: JSON Utilities Showcase ===")

    # Step 1: Create layout data
    layout = Layout.create_empty(keyboard="kyria", title="JSON Utils Demo")
    layout.layers.add("base").set(0, "&kp Q").set(1, "&kp W")
    layout.behaviors.add_combo(name="test_combo", keys=[0, 1], binding="&kp ESC")

    # Step 2: Use serialize_layout_data utility
    json_string = serialize_layout_data(layout.data, indent=4)
    print("✓ Used serialize_layout_data() with custom indentation")

    # Step 3: Save and load using utilities
    json_file = Path("/tmp/utils_demo.json")
    json_file.write_text(json_string)

    # Step 4: Load back using parse_layout_data
    loaded_json = json_file.read_text()
    layout_data = parse_layout_data(loaded_json)
    print("✓ Used parse_layout_data() to load and validate JSON")

    # Step 5: Create Layout from validated data
    new_layout = Layout.from_dict(layout_data.model_dump(by_alias=True))
    print("✓ Created Layout from validated LayoutData")

    # Step 6: Demonstrate error handling
    try:
        invalid_json = "{ invalid json }"
        parse_json_data(invalid_json)
    except json.JSONDecodeError as e:
        print(f"✓ JSON utilities properly handle invalid JSON: {type(e).__name__}")

    # Step 7: Demonstrate different serialization options
    compact_json = serialize_json_data(layout.to_dict(), indent=None)
    readable_json = serialize_json_data(layout.to_dict(), indent=2, ensure_ascii=False)

    compact_file = Path("/tmp/compact.json")
    readable_file = Path("/tmp/readable.json")

    compact_file.write_text(compact_json)
    readable_file.write_text(readable_json)

    print("✓ Demonstrated different serialization formats:")
    print(f"  - Compact: {len(compact_json)} chars")
    print(f"  - Readable: {len(readable_json)} chars")

    return layout, [json_file, compact_file, readable_file]


def summary_best_practices():
    """Summary of data-only API best practices."""
    print("\n=== Data-Only API Best Practices ===")
    print()
    print("1. FILE OPERATIONS:")
    print("   - Use Path.read_text() to load file content")
    print("   - Use Path.write_text() to save file content")
    print("   - Layout never directly touches the filesystem")
    print()
    print("2. JSON OPERATIONS:")
    print("   - Use Layout.from_dict(data) instead of Layout.from_file(path)")
    print("   - Use Layout.to_dict() instead of Layout.save(path)")
    print("   - Use json_operations utilities for robust parsing/serialization")
    print()
    print("3. PARSING:")
    print("   - Parser works with file paths (temporary files if needed)")
    print("   - Extract layout data, then use Layout.from_dict()")
    print("   - Parser returns LayoutData, convert to dict for Layout")
    print()
    print("4. GENERATION:")
    print("   - Generators produce strings, not files")
    print("   - Save generator output using Path.write_text()")
    print("   - Assemble components into complete files manually")
    print()
    print("5. SEPARATION OF CONCERNS:")
    print("   - Layout = pure data operations")
    print("   - File I/O = external using Path")
    print("   - Parsing/Generation = string-based processing")
    print("   - JSON = handled by utilities")
    print()
    print("This approach provides:")
    print("  ✓ Clear separation of concerns")
    print("  ✓ Better testability (mock data, not files)")
    print("  ✓ More flexible integration patterns")
    print("  ✓ Easier data pipeline composition")


def main():
    """Run all data-only API examples."""
    print("ZMK Layout Library - Data-Only API Examples")
    print("=" * 60)
    print()
    print("This demonstration shows the new data-only approach where:")
    print("- Layout operates on dictionaries, not files")
    print("- File I/O is handled externally with pathlib.Path")
    print("- JSON operations use dedicated utilities")
    print("- Parsers and generators work with strings")
    print()

    examples = [
        example_1_load_from_json_file,
        example_2_save_to_json_file,
        example_3_parse_keymap_string,
        example_4_generate_keymap_string,
        example_5_roundtrip_data_operations,
        example_6_json_utilities_showcase,
    ]

    results = {}

    for example_func in examples:
        try:
            print("-" * 60)
            result = example_func()
            results[example_func.__name__] = result
            print()
        except Exception as e:
            print(f"✗ Example failed: {e}")
            import traceback

            traceback.print_exc()
            print()

    # Clean up temp files
    temp_files = [
        "/tmp/sample_layout.json",
        "/tmp/lily58_layout.json",
        "/tmp/generated_planck.keymap",
        "/tmp/roundtrip_original.json",
        "/tmp/roundtrip_modified.json",
        "/tmp/utils_demo.json",
        "/tmp/compact.json",
        "/tmp/readable.json",
    ]

    print("-" * 60)
    summary_best_practices()

    print("\n" + "=" * 60)
    print(f"✓ Completed {len(results)}/{len(examples)} data-only API examples!")

    if results:
        print("\nGenerated files for inspection:")
        for temp_file in temp_files:
            file_path = Path(temp_file)
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  - {file_path.name} ({size} bytes)")

    print("\nThe data-only API provides clean separation between:")
    print("  • Data manipulation (Layout)")
    print("  • File operations (pathlib.Path)")
    print("  • JSON handling (json_operations utilities)")
    print("  • String processing (parsers & generators)")


if __name__ == "__main__":
    main()
