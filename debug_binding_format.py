#!/usr/bin/env python3
"""Debug binding formatting."""

from zmk_layout.core.layout import Layout
from zmk_layout.models.core import LayoutBinding, LayoutParam


# Create a simple test layout with some basic bindings
test_data = {
    "keyboard": "corne",
    "title": "Test Layout",
    "layer_names": ["default"],
    "layers": [
        [
            "&kp Q", "&kp W", "&kp E", "&kp R",
            "&bt BT_CLR", "&to 1", "&none"
        ]
    ]
}

print("=== Testing Layout Creation ===")
layout = Layout.from_dict(test_data)
print(f"Layout created with {len(layout.data.layers[0])} bindings")

print("\n=== Testing Individual Binding Formatting ===")
for i, binding in enumerate(layout.data.layers[0]):
    print(f"Binding {i}: {repr(binding)} -> '{binding}'")
    if hasattr(binding, 'value'):
        print(f"  Value: {binding.value}")
        print(f"  Params: {binding.params}")

print("\n=== Testing Keymap Generation ===")
try:
    keymap = layout.to_keymap()
    print("Generated keymap (first 1000 chars):")
    print(keymap[:1000])
    print("...")

    # Look for the bindings section
    if "bindings = <" in keymap:
        bindings_start = keymap.find("bindings = <")
        bindings_end = keymap.find(">;", bindings_start)
        if bindings_end != -1:
            bindings_section = keymap[bindings_start:bindings_end + 2]
            print("\n=== Bindings Section ===")
            print(bindings_section)

except Exception as e:
    print(f"Error generating keymap: {e}")
    import traceback
    traceback.print_exc()
