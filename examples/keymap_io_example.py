#!/usr/bin/env python3
"""
Simple examples of loading from and saving to ZMK keymap format.

This demonstrates the data-only API where:
- Parser accepts keymap content as strings (not file paths)
- Generators return keymap content as strings (not writing files)
- File I/O is handled externally using Path.read_text() and Path.write_text()
"""

from pathlib import Path
from types import SimpleNamespace

from zmk_layout import Layout
from zmk_layout.generators.zmk_generator import ZMKGenerator
from zmk_layout.parsers.zmk_keymap_parser import ParsingMode, ZMKKeymapParser
from zmk_layout.providers.factory import create_default_providers


def load_keymap_to_layout(keymap_path: str) -> Layout:
    """
    Load a .keymap file and convert it to a Layout object.

    Args:
        keymap_path: Path to the .keymap file

    Returns:
        Layout object with the parsed keymap data
    """
    # Step 1: Read the keymap file content
    keymap_content = Path(keymap_path).read_text()

    # Step 2: Set up parser with providers
    providers = create_default_providers()
    parser = ZMKKeymapParser(
        configuration_provider=providers.configuration, logger=providers.logger
    )

    # Step 3: Parse the keymap content (string, not file path!)
    parse_result = parser.parse_keymap(
        keymap_content,  # Pass content string, not file path
        title=Path(keymap_path).stem,  # Use filename as title
        mode=ParsingMode.FULL,
    )

    # Step 4: Extract layout data from parse result
    if hasattr(parse_result, "layout_data"):
        layout_data = parse_result.layout_data
    else:
        layout_data = parse_result

    # Step 5: Convert to Layout object
    layout_dict = layout_data.model_dump(by_alias=True)
    layout = Layout.from_dict(layout_dict)

    return layout


def save_layout_to_keymap(
    layout: Layout, output_path: str, keyboard_name: str = "corne"
):
    """
    Save a Layout object to a .keymap file.

    Args:
        layout: Layout object to save
        output_path: Path where to save the .keymap file
        keyboard_name: Name of the keyboard for the profile
    """
    # Step 1: Get layout data as dictionary
    layout_dict = layout.to_dict()

    # Step 2: Set up generator with providers
    providers = create_default_providers()
    generator = ZMKGenerator(
        configuration_provider=providers.configuration,
        template_provider=providers.template,
        logger=providers.logger,
    )

    # Step 3: Create a minimal keyboard profile
    # In real usage, this would come from your keyboard configuration
    profile = SimpleNamespace(
        keyboard_config=SimpleNamespace(
            zmk=SimpleNamespace(
                compatible_strings=SimpleNamespace(keymap="zmk,keymap"),
                layout=SimpleNamespace(
                    keys=42  # Example: Corne has 42 keys
                ),
            )
        )
    )

    # Step 4: Process layers to extract binding strings
    layers_data = []
    for layer in layout_dict.get("layers", []):
        if isinstance(layer, list):
            # Extract binding strings from layer
            layer_bindings = []
            for binding in layer:
                if isinstance(binding, dict):
                    # Convert binding dict to string format
                    if "value" in binding:
                        value = binding["value"]
                        params = binding.get("params", [])
                        if (
                            params
                            and isinstance(params[0], dict)
                            and "value" in params[0]
                        ):
                            layer_bindings.append(f"{value} {params[0]['value']}")
                        else:
                            layer_bindings.append(value)
                    else:
                        layer_bindings.append(str(binding))
                else:
                    layer_bindings.append(str(binding))
            layers_data.append(layer_bindings)
        else:
            layers_data.append(layer)

    # Step 5: Generate the keymap content (returns string, not writes file!)
    keymap_content = generator.generate_keymap_node(
        profile=profile,
        layer_names=layout_dict.get("layer_names", ["default"]),
        layers_data=layers_data,
    )

    # Step 6: Add the standard keymap file wrapper
    full_keymap = f"""/*
 * Copyright (c) 2024 The ZMK Contributors
 * SPDX-License-Identifier: MIT
 */

#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>
#include <dt-bindings/zmk/bt.h>

/ {{
{keymap_content}
}};
"""

    # Step 7: Write the content to file
    Path(output_path).write_text(full_keymap)


def roundtrip_example():
    """
    Example of loading a keymap, modifying it, and saving it back.
    """
    # Create a sample keymap content
    sample_keymap = """
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";

        default_layer {
            bindings = <
                &kp Q    &kp W    &kp E    &kp R    &kp T    &kp Y
                &kp A    &kp S    &kp D    &kp F    &kp G    &kp H
                &kp Z    &kp X    &kp C    &kp V    &kp B    &kp N
            >;
        };
    };
};
"""

    # Save sample to temp file
    temp_input = Path("/tmp/input.keymap")
    temp_input.write_text(sample_keymap)

    # Load the keymap
    print("Loading keymap...")
    layout = load_keymap_to_layout("/tmp/input.keymap")

    # Modify the layout
    print("Modifying layout...")
    if layout.layers.count > 0:  # count is a property, not a method
        # Change first key to ESC
        layout.layers.get(0).set(0, "&kp ESC")
        print("Changed first key to ESC")

    # Add a new layer
    new_layer = layout.layers.add("numbers")
    new_layer.set_range(
        0, 6, ["&kp N1", "&kp N2", "&kp N3", "&kp N4", "&kp N5", "&kp N6"]
    )
    print("Added numbers layer")

    # Save back to keymap
    print("Saving modified keymap...")
    save_layout_to_keymap(layout, "/tmp/output.keymap")

    # Show the result
    output_content = Path("/tmp/output.keymap").read_text()
    print("\nGenerated keymap preview:")
    print("=" * 50)
    print(output_content[:500] + "..." if len(output_content) > 500 else output_content)
    print("=" * 50)

    # Clean up
    temp_input.unlink()
    Path("/tmp/output.keymap").unlink()

    print("\nRoundtrip complete!")


if __name__ == "__main__":
    print("ZMK Keymap I/O Examples\n")
    print("=" * 60)

    roundtrip_example()

    print("\nKey API patterns demonstrated:")
    print("- Parser accepts keymap CONTENT (string), not file paths")
    print("- Generator returns keymap CONTENT (string), not writes files")
    print("- File I/O handled externally with Path.read_text()/write_text()")
    print("- Layout uses from_dict() and to_dict() for data operations")
