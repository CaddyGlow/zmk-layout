#!/usr/bin/env python3
"""
Simple Layout Roundtrip Demonstration using Helper Methods

This script demonstrates a complete roundtrip transformation using the new Layout helper methods:
1. Load Factory.json → Convert to keymap → Save as generated.keymap
2. Load Factory.keymap → Convert to JSON → Save as generated.json
3. Perform full cycle validation and save intermediate files

All generated files are saved to the output directory for inspection.

The new approach uses:
- Layout.from_string() for auto-detection of JSON/keymap formats
- Layout.export.keymap().generate() for direct keymap generation with fluent API
- Much simpler code with less setup required

OLD WAY (complex):
    parser = ZMKKeymapParser(providers.configuration, providers.logger)
    result = parser.parse_keymap(file_path, mode=ParsingMode.FULL)
    layout_data = result.layout_data if hasattr(result, 'layout_data') else result
    layout = Layout.from_dict(layout_data.model_dump(by_alias=True))

NEW WAY (simple):
    content = Path(file_path).read_text()
    layout = Layout.from_string(content)  # Auto-detects format!
"""

import json
import sys
from pathlib import Path


# Add the keyboards directory to the path for profile imports
sys.path.append(str(Path(__file__).parent.parent / "keyboards"))

from zmk_layout import Layout
from zmk_layout.providers.factory import create_default_providers


# Note: Complex provider setup removed - now using simple helper methods


def main():
    """Main demonstration function."""
    print("🔄 Factory Layout Roundtrip Demonstration")
    print("=" * 50)

    # Set up paths
    examples_dir = Path(__file__).parent
    layouts_dir = examples_dir / "layouts"
    output_dir = examples_dir / "output"
    output_dir.mkdir(exist_ok=True)

    factory_json_path = layouts_dir / "Factory.json"
    factory_keymap_path = layouts_dir / "Factory.keymap"

    # Verify input files exist
    if not factory_json_path.exists():
        print(f"❌ Factory.json not found at {factory_json_path}")
        return 1

    if not factory_keymap_path.exists():
        print(f"❌ Factory.keymap not found at {factory_keymap_path}")
        return 1

    print("📁 Input files:")
    print(f"   JSON: {factory_json_path}")
    print(f"   Keymap: {factory_keymap_path}")
    print(f"📁 Output directory: {output_dir}")
    print()

    # Create providers (simplified - just use default providers)
    providers = create_default_providers()

    # Test 1: JSON → Keymap transformation (using helper methods)
    print("🔄 Test 1: JSON → Keymap transformation")
    try:
        # Load and parse JSON using from_string()
        json_content = factory_json_path.read_text()
        layout = Layout.from_string(json_content, providers=providers)
        print(f"✅ Loaded Factory.json with {layout.layers.count} layers")

        # Generate keymap using new fluent API
        keymap_content = layout.export.keymap().with_headers(True).generate()

        # Save generated keymap
        generated_keymap_path = output_dir / "generated_from_json.keymap"
        generated_keymap_path.write_text(keymap_content)
        print(f"✅ Generated keymap saved to: {generated_keymap_path}")

    except Exception as e:
        print(f"❌ JSON → Keymap failed: {e}")
        return 1

    print()

    # Test 2: Keymap → JSON transformation (using helper methods)
    print("🔄 Test 2: Keymap → JSON transformation")
    try:
        # Load and parse keymap using from_string()
        keymap_content = factory_keymap_path.read_text()
        layout = Layout.from_string(
            keymap_content, title="Factory Keymap", providers=providers
        )
        print(f"✅ Parsed Factory.keymap with {layout.layers.count} layers")

        # Convert to JSON using to_dict()
        generated_json = layout.to_dict()

        # Save generated JSON
        generated_json_path = output_dir / "generated_from_keymap.json"
        generated_json_path.write_text(json.dumps(generated_json, indent=2))
        print(f"✅ Generated JSON saved to: {generated_json_path}")

    except Exception as e:
        print(f"❌ Keymap → JSON failed: {e}")
        return 1

    print()

    # Test 3: Full roundtrip validation (using helper methods)
    print("🔄 Test 3: Full roundtrip cycle (JSON → Keymap → JSON)")
    try:
        # Step 1: Load original JSON
        json_content = factory_json_path.read_text()
        original_json = json.loads(json_content)
        layout1 = Layout.from_string(json_content, providers=providers)
        print("✅ Step 1: Loaded original JSON")

        # Step 2: Convert to keymap using new fluent API
        intermediate_keymap = layout1.export.keymap().with_headers(True).generate()
        roundtrip_keymap_path = output_dir / "roundtrip_intermediate.keymap"
        roundtrip_keymap_path.write_text(intermediate_keymap)
        print("✅ Step 2: Generated intermediate keymap")

        # Step 3: Parse keymap back to Layout
        layout2 = Layout.from_string(
            intermediate_keymap, title="Roundtrip", providers=providers
        )
        print("✅ Step 3: Parsed keymap back to Layout")

        # Step 4: Convert back to JSON
        final_json = layout2.to_dict()
        roundtrip_json_path = output_dir / "roundtrip_final.json"
        roundtrip_json_path.write_text(json.dumps(final_json, indent=2))
        print("✅ Step 4: Generated final JSON")

        print("✅ Roundtrip completed!")
        print(f"   Intermediate keymap: {roundtrip_keymap_path}")
        print(f"   Final JSON: {roundtrip_json_path}")

        # Validate roundtrip integrity
        print("\n🔍 Roundtrip validation:")

        # Compare layer counts
        original_layer_count = len(original_json.get("layers", []))
        final_layer_count = len(final_json.get("layers", []))
        if original_layer_count == final_layer_count:
            print(f"✅ Layer count preserved: {original_layer_count}")
        else:
            print(
                f"⚠️  Layer count changed: {original_layer_count} → {final_layer_count}"
            )

        # Compare layer names
        original_layer_names = original_json.get("layer_names", [])
        final_layer_names = final_json.get("layer_names", [])
        if original_layer_names == final_layer_names:
            print(f"✅ Layer names preserved: {original_layer_names}")
        else:
            print(
                f"⚠️  Layer names changed: {original_layer_names} → {final_layer_names}"
            )

        # Show layout statistics
        stats1 = layout1.get_statistics()
        stats2 = layout2.get_statistics()
        print(
            f"✅ Original layout stats: {stats1['layer_count']} layers, {stats1['total_bindings']} bindings"
        )
        print(
            f"✅ Final layout stats: {stats2['layer_count']} layers, {stats2['total_bindings']} bindings"
        )

        # Validate data integrity
        if stats1["layer_count"] == stats2["layer_count"]:
            print("✅ Layer count integrity maintained")
        else:
            print(
                f"⚠️  Layer count integrity lost: {stats1['layer_count']} → {stats2['layer_count']}"
            )

    except Exception as e:
        print(f"❌ Roundtrip cycle failed: {e}")
        return 1

    print()

    # Summary
    print("📊 Generated Files Summary:")
    print("-" * 30)
    for file_path in sorted(output_dir.glob("*")):
        size = file_path.stat().st_size
        print(f"   {file_path.name:<25} ({size:,} bytes)")

    print("\n🎉 Roundtrip demonstration completed successfully!")
    print(f"All generated files are available in: {output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
