#!/usr/bin/env python3
"""Debug the to_dict conversion issue."""

from zmk_layout.core.layout import Layout


# Create a simple test layout
test_data = {
    "keyboard": "test",
    "title": "Test Layout",
    "layer_names": ["default"],
    "layers": [
        ["&kp Q", "&kp W"]
    ]
}

print("=== Creating Layout ===")
layout = Layout.from_dict(test_data)

print("\n=== Testing layout.data.layers ===")
for i, binding in enumerate(layout.data.layers[0]):
    print(f"Binding {i}: {repr(binding)}")
    print(f"  type: {type(binding)}")
    print(f"  to_str(): '{binding.to_str()}'")

print("\n=== Testing layout.to_dict() ===")
layout_dict = layout.to_dict()
print("Layer data in dict:")
for i, binding in enumerate(layout_dict["layers"][0]):
    print(f"Binding {i}: {repr(binding)}")
    print(f"  type: {type(binding)}")

    # Check if it's the problematic format
    if isinstance(binding, dict) and "value" in binding and "params" in binding:
        print("  ❌ Found problematic dict format!")
        print(f"    value: {binding['value']}")
        print(f"    params: {binding['params']}")
    elif isinstance(binding, str):
        print(f"  ✅ String format: '{binding}'")
    else:
        print(f"  ❓ Other format: {type(binding)}")
