#!/usr/bin/env python3
"""Factory Layout Verification Demo

This example loads the Factory layout from both keymap and JSON formats
and generates separate keymaps to verify parsing works correctly.
"""

import sys
from pathlib import Path

# Add the project root to path
sys.path.append(str(Path(__file__).parent.parent))

from zmk_layout import Layout
from keyboards.glove80_profile import create_complete_glove80_profile
from types import SimpleNamespace


def factory_verification_demo():
    """Demo loading Factory layouts from different formats."""

    print("Factory Layout Verification Demo")
    print("=" * 50)

    # File paths
    factory_keymap = Path("/home/rick/Downloads/Factory With bindings.keymap")
    factory_json = Path("/home/rick/Downloads/Factory With bindings.json")
    output_dir = Path("/tmp/factory_verification")

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Load Glove80 profile and create compatible profile object
    glove80_data = create_complete_glove80_profile()

    # Create a compatible profile for the generator
    glove80_profile = SimpleNamespace(
        keyboard_name=glove80_data.hardware.keyboard,
        firmware_version=glove80_data.firmware.default_firmware,
        keyboard_config=glove80_data.keyboard_config,
    )

    print("1. Loading Factory layout from keymap file...")
    print("-" * 30)

    if factory_keymap.exists():
        # Load from keymap file
        keymap_content = factory_keymap.read_text()
        layout_from_keymap = Layout.from_string(
            keymap_content, title="Factory from Keymap"
        )

        print(f"   ✓ Loaded from keymap: {len(layout_from_keymap.layers)} layers")
        total_bindings = sum(
            len(layout_from_keymap.data.layers[i])
            for i in range(len(layout_from_keymap.layers))
        )
        print(f"   ✓ Total bindings: {total_bindings}")
        print(f"   ✓ Hold-taps: {len(layout_from_keymap.data.hold_taps)}")
        print(f"   ✓ Combos: {len(layout_from_keymap.data.combos)}")
        print(f"   ✓ Macros: {len(layout_from_keymap.data.macros)}")

        # Generate keymap from this layout
        generated_from_keymap = layout_from_keymap.export.keymap(
            glove80_profile
        ).generate()

        # Save outputs
        output_keymap = output_dir / "factory_from_keymap.keymap"
        output_keymap.write_text(generated_from_keymap)

        output_json_from_keymap = output_dir / "factory_from_keymap.json"
        output_json_from_keymap.write_text(layout_from_keymap.export.to_json())

        print(f"   ✓ Generated keymap: {len(generated_from_keymap)} characters")
        print(f"   ✓ Saved keymap to: {output_keymap}")
        print(f"   ✓ Saved JSON to: {output_json_from_keymap}")
    else:
        print(f"   ❌ Factory keymap not found: {factory_keymap}")

    print()
    print("2. Loading Factory layout from JSON file...")
    print("-" * 30)

    if factory_json.exists():
        # Load from JSON file
        import json

        json_content = json.loads(factory_json.read_text())
        layout_from_json = Layout.from_dict(json_content)

        print(f"   ✓ Loaded from JSON: {len(layout_from_json.layers)} layers")
        total_bindings_json = sum(
            len(layout_from_json.data.layers[i])
            for i in range(len(layout_from_json.layers))
        )
        print(f"   ✓ Total bindings: {total_bindings_json}")
        print(f"   ✓ Hold-taps: {len(layout_from_json.data.hold_taps)}")
        print(f"   ✓ Combos: {len(layout_from_json.data.combos)}")
        print(f"   ✓ Macros: {len(layout_from_json.data.macros)}")

        # Generate keymap from this layout
        generated_from_json = layout_from_json.export.keymap(glove80_profile).generate()

        # Save outputs
        output_json_keymap = output_dir / "factory_from_json.keymap"
        output_json_keymap.write_text(generated_from_json)

        output_json_from_json = output_dir / "factory_from_json.json"
        output_json_from_json.write_text(layout_from_json.export.to_json())

        print(f"   ✓ Generated keymap: {len(generated_from_json)} characters")
        print(f"   ✓ Saved keymap to: {output_json_keymap}")
        print(f"   ✓ Saved JSON to: {output_json_from_json}")
    else:
        print(f"   ❌ Factory JSON not found: {factory_json}")

    print()
    print("3. Comparison and Analysis...")
    print("-" * 30)

    if factory_keymap.exists() and factory_json.exists():
        # Compare the two layouts
        keymap_layers = layout_from_keymap.layers
        json_layers = layout_from_json.layers

        print(
            f"   Layer count - Keymap: {len(keymap_layers)}, JSON: {len(json_layers)}"
        )

        # Compare layer by layer
        for i in range(min(len(keymap_layers), len(json_layers))):
            k_bindings = len(layout_from_keymap.data.layers[i])
            j_bindings = len(layout_from_json.data.layers[i])
            match_status = "✓" if k_bindings == j_bindings else "✗"
            print(
                f"   Layer {i} bindings - Keymap: {k_bindings}, JSON: {j_bindings} {match_status}"
            )

        # Compare behaviors
        print(
            f"   Hold-taps - Keymap: {len(layout_from_keymap.data.hold_taps)}, JSON: {len(layout_from_json.data.hold_taps)}"
        )
        print(
            f"   Combos - Keymap: {len(layout_from_keymap.data.combos)}, JSON: {len(layout_from_json.data.combos)}"
        )
        print(
            f"   Macros - Keymap: {len(layout_from_keymap.data.macros)}, JSON: {len(layout_from_json.data.macros)}"
        )

        # Size comparison
        keymap_size = len(generated_from_keymap)
        json_size = len(generated_from_json)
        size_diff = abs(keymap_size - json_size)
        size_diff_pct = (size_diff / max(keymap_size, json_size)) * 100

        print(f"   Generated size - Keymap: {keymap_size}, JSON: {json_size}")
        print(f"   Size difference: {size_diff} characters ({size_diff_pct:.1f}%)")

    print()
    print("4. Testing Round-trip Verification...")
    print("-" * 30)

    if factory_keymap.exists():
        # Test round-trip with keymap source
        original_content = factory_keymap.read_text()
        parsed_layout = Layout.from_string(original_content, title="Round-trip Test")
        regenerated_content = parsed_layout.export.keymap(glove80_profile).generate()

        # Parse the regenerated content
        reparsed_layout = Layout.from_string(regenerated_content, title="Reparsed Test")

        print(f"   Original behaviors: {len(parsed_layout.data.hold_taps)}")
        print(f"   Regenerated behaviors: {len(reparsed_layout.data.hold_taps)}")

        # Check for binding parameter preservation
        if parsed_layout.data.hold_taps and reparsed_layout.data.hold_taps:
            orig_bindings = parsed_layout.data.hold_taps[0].bindings
            regen_bindings = reparsed_layout.data.hold_taps[0].bindings
            print(f"   Original hold-tap bindings: {orig_bindings}")
            print(f"   Regenerated hold-tap bindings: {regen_bindings}")

            bindings_match = orig_bindings == regen_bindings
            print(f"   Bindings preserved: {'✓' if bindings_match else '✗'}")

        round_trip_output = output_dir / "factory_round_trip.keymap"
        round_trip_output.write_text(regenerated_content)
        
        round_trip_json_output = output_dir / "factory_round_trip.json"
        round_trip_json_output.write_text(parsed_layout.export.to_json())
        
        print(f"   ✓ Round-trip keymap saved to: {round_trip_output}")
        print(f"   ✓ Round-trip JSON saved to: {round_trip_json_output}")

    print()
    print("✓ Factory verification completed!")
    print(f"✓ All outputs saved to: {output_dir}")
    print()
    print("Files generated:")
    for file in output_dir.glob("*"):
        if file.is_file():
            size = file.stat().st_size
            print(f"  - {file.name}: {size:,} bytes")


if __name__ == "__main__":
    factory_verification_demo()

