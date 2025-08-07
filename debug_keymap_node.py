#!/usr/bin/env python3
"""Debug the keymap node generation directly."""

from types import SimpleNamespace

from zmk_layout.generators.zmk_generator import ZMKGenerator
from zmk_layout.models.core import LayoutBinding


# Create test bindings
bindings = [
    LayoutBinding.from_str("&kp Q"),
    LayoutBinding.from_str("&kp W"),
    LayoutBinding.from_str("&kp E")
]

print("=== Test Bindings ===")
for i, binding in enumerate(bindings):
    print(f"Binding {i}: {repr(binding)}")
    print(f"  to_str(): '{binding.to_str()}'")

# Create a minimal profile structure
profile = SimpleNamespace(
    keyboard_config=SimpleNamespace(
        zmk=SimpleNamespace(
            compatible_strings=SimpleNamespace(
                keymap="zmk,keymap"
            )
        )
    )
)

# Test ZMK generator directly
print("\n=== Testing ZMKGenerator.generate_keymap_node ===")
generator = ZMKGenerator()
layer_names = ["default"]
layers_data = [bindings]

try:
    keymap_node = generator.generate_keymap_node(profile, layer_names, layers_data)
    print("Generated keymap_node:")
    print(keymap_node)

    # Check for the problematic pattern
    if "value='&kp' params=[LayoutParam" in keymap_node:
        print("\n❌ Found problematic binding format!")
    else:
        print("\n✅ Binding format looks correct!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
