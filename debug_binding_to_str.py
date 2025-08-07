#!/usr/bin/env python3
"""Debug binding to_str method."""

from zmk_layout.models.core import LayoutBinding


# Test to_str method directly
bindings = [
    "&kp Q",
    "&kp W",
    "&bt BT_CLR",
    "&to 1",
    "&none"
]

print("=== Testing to_str() method directly ===")
for binding_str in bindings:
    binding = LayoutBinding.from_str(binding_str)
    print(f"Input: '{binding_str}'")
    print(f"  Parsed: {repr(binding)}")
    print(f"  to_str(): '{binding.to_str()}'")
    print(f"  str(): '{str(binding)}'")
    print()

# Test formatter directly
print("=== Testing BehaviorFormatter directly ===")
from zmk_layout.generators.zmk_generator import BehaviorFormatter


formatter = BehaviorFormatter()
for binding_str in bindings:
    binding = LayoutBinding.from_str(binding_str)
    formatted = formatter.format_binding(binding)
    print(f"Input: '{binding_str}' -> Formatted: '{formatted}'")
