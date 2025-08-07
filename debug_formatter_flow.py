#!/usr/bin/env python3
"""Debug the exact formatter flow."""

from zmk_layout.generators.zmk_generator import BehaviorFormatter
from zmk_layout.models.core import LayoutBinding


# Test the exact flow that happens in keymap generation
binding = LayoutBinding.from_str("&kp Q")

print("=== Testing LayoutBinding object ===")
print(f"Binding: {repr(binding)}")
print(f"binding.to_str(): '{binding.to_str()}'")
print(f"str(binding): '{str(binding)}'")
print(f"hasattr(binding, 'to_str'): {hasattr(binding, 'to_str')}")

# Test BehaviorFormatter directly
print("\n=== Testing BehaviorFormatter ===")
formatter = BehaviorFormatter()
formatted = formatter.format_binding(binding)
print(f"formatter.format_binding(binding): '{formatted}'")

# Test what happens in LayoutFormatter.generate_layer_layout
print("\n=== Testing LayoutFormatter behavior ===")
from zmk_layout.generators.zmk_generator import LayoutFormatter


layout_formatter = LayoutFormatter()
# Simulate the generate_layer_layout call
bindings = [binding]

# Test the flow in generate_layer_layout
print("Testing generate_layer_layout with single binding:")
result = layout_formatter.generate_layer_layout(bindings, base_indent="")
print("Result:")
print(repr(result))
print("\nActual output:")
print(result)
