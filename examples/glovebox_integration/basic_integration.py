#!/usr/bin/env python3
"""
Basic integration example for using zmk-layout in glovebox.

This example shows how to integrate the zmk-layout library into
glovebox with minimal changes to existing code.
"""

from pathlib import Path
from typing import Any

# Import from zmk-layout library
from zmk_layout import Layout
from zmk_layout.providers import LayoutProviders


def create_minimal_providers() -> LayoutProviders:
    """Create minimal provider configuration for glovebox."""

    # Import glovebox services (these would be your actual imports)
    # from glovebox.services import get_keyboard_profile_service
    # from glovebox.adapters import get_file_adapter

    # For this example, we'll create simple implementations
    class SimpleConfigProvider:
        def get_behavior_definitions(self):
            return [
                {"name": "kp", "type": "key-press"},
                {"name": "mt", "type": "mod-tap"},
                {"name": "lt", "type": "layer-tap"},
            ]

        def get_include_files(self):
            return ["behaviors.dtsi", "keys.h"]

        def get_validation_rules(self):
            return {"key_count": 42, "layer_limit": 10}

        def get_template_context(self):
            return {"keyboard": "crkbd"}

    class SimpleTemplateProvider:
        def render_string(self, template: str, context: dict[str, Any]) -> str:
            for key, value in context.items():
                template = template.replace(f"{{{{{key}}}}}", str(value))
            return template

        def has_template_syntax(self, content: str) -> bool:
            return "{{" in content

        def validate_template(self, template: str) -> list[str]:
            return []

    class SimpleLogger:
        def debug(self, msg: str, **kwargs):
            print(f"DEBUG: {msg}")

        def info(self, msg: str, **kwargs):
            print(f"INFO: {msg}")

        def warning(self, msg: str, **kwargs):
            print(f"WARNING: {msg}")

        def error(self, msg: str, **kwargs):
            print(f"ERROR: {msg}")

            # File operations now handled directly by the library using pathlib.Path

        def exists(self, path: Path) -> bool:
            return path.exists()

    # Create and return providers
    return LayoutProviders(
        configuration=SimpleConfigProvider(),
        template=SimpleTemplateProvider(),
        logger=SimpleLogger(),
    )


def example_basic_usage():
    """Basic usage example."""
    print("=== Basic ZMK-Layout Integration ===\n")

    # Create providers
    providers = create_minimal_providers()

    # Create a new layout using fluent API
    print("Creating new layout...")
    layout = (
        Layout.create_empty("crkbd", "My Corne Layout", size=42, providers=providers)
        .with_author("Integration Example")
        .with_description("Example layout for glovebox integration")
    )

    # Add layers
    print("Adding layers...")
    layout = (
        layout.layers.add("base")
        .set_range(
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
        .parent()
    )

    layout = (
        layout.layers.add("lower")
        .set_range(
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
        .parent()
    )

    # Add behaviors
    print("Adding behaviors...")
    layout = (
        layout.behaviors.add_hold_tap("hm", hold="&kp", tap="&kp", tapping_term_ms=200)
        .add_combo("copy", keys=[10, 11], binding="&kp LC(C)")
        .add_macro("hello", bindings=["&kp H", "&kp E", "&kp L", "&kp L", "&kp O"])
        .parent()
    )

    # Get statistics
    stats = layout.get_statistics()
    print("\nLayout Statistics:")
    print(f"  Layers: {stats['layer_count']}")
    print(f"  Total behaviors: {stats['total_behaviors']}")
    print(f"  Total bindings: {stats['total_bindings']}")

    # Export and save to file (file I/O handled by application)
    output_path = Path("output/example_layout.json")
    print(f"\nSaving to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    import json

    layout_data = layout.to_dict()
    output_path.write_text(json.dumps(layout_data, indent=2))

    print("✓ Layout created successfully!")

    return layout


def example_migration_wrapper():
    """Example showing backward compatibility wrapper."""
    print("\n=== Backward Compatibility Example ===\n")

    class LegacyLayoutWrapper:
        """Wrapper to support old glovebox API."""

        def __init__(self):
            self.providers = create_minimal_providers()
            self._layout = Layout.create_empty(
                "crkbd", "Legacy", providers=self.providers
            )

        # Old API methods (deprecated)
        def add_layer(self, name: str) -> None:
            """Old imperative API."""
            print(f"[DEPRECATED] add_layer('{name}') - use fluent API instead")
            self._layout = self._layout.layers.add(name).parent()

        def set_binding(self, layer: str, pos: int, binding: str) -> None:
            """Old imperative API."""
            print("[DEPRECATED] set_binding() - use fluent API instead")
            self._layout = self._layout.layers.get(layer).set(pos, binding).parent()

        # Bridge to new API
        def to_fluent(self) -> Layout:
            """Get fluent layout instance."""
            return self._layout

        def to_dict(self) -> dict[str, Any]:
            """Export to dictionary."""
            return self._layout.to_dict()

    # Use legacy wrapper
    print("Using legacy wrapper...")
    wrapper = LegacyLayoutWrapper()

    # Old API still works (with deprecation warnings)
    wrapper.add_layer("test")
    wrapper.set_binding("test", 0, "&kp A")

    # Can switch to fluent API
    layout = wrapper.to_fluent()
    print(f"Layers: {layout.layers.list()}")

    print("✓ Legacy API wrapper working!")

    return wrapper


def example_service_integration():
    """Example of integrating with glovebox services."""
    print("\n=== Service Integration Example ===\n")

    class LayoutService:
        """Glovebox layout service using zmk-layout internally."""

        def __init__(self):
            self.providers = create_minimal_providers()

        def compile(self, layout_data: dict[str, Any]) -> dict[str, Any]:
            """Compile layout using zmk-layout."""
            try:
                # Create layout from data
                layout = Layout.from_dict(layout_data, providers=self.providers)

                # Validate
                layout = layout.validate()

                # Generate outputs as strings
                keymap = layout.to_keymap()
                # Note: behaviors are included in keymap output

                return {
                    "success": True,
                    "keymap": keymap,
                    "layout_data": layout.to_dict(),
                }

            except Exception as e:
                return {"success": False, "error": str(e)}

        def parse_keymap(self, content: str) -> dict[str, Any]:
            """Parse keymap content."""
            # Use the new string-based parsing
            layout = Layout.from_string(content, providers=self.providers)
            return layout.to_dict()

    # Use the service
    service = LayoutService()

    # Create test data
    test_data = {
        "keyboard": "crkbd",
        "keymap": "test",
        "layout": "LAYOUT_split_3x6_3",
        "layer_names": ["base"],
        "layers": [{"name": "base", "bindings": ["&kp Q"] * 42}],
    }

    print("Compiling layout with service...")
    result = service.compile(test_data)

    if result["success"]:
        print("✓ Compilation successful!")
        print(f"  Generated keymap: {len(result['keymap'])} bytes")
    else:
        print(f"✗ Compilation failed: {result['error']}")

    return service


def example_advanced_features():
    """Example of advanced zmk-layout features."""
    print("\n=== Advanced Features Example ===\n")

    providers = create_minimal_providers()

    # Method chaining for complex operations
    print("Building complex layout with method chaining...")
    layout = (
        Layout.create_empty("crkbd", "Advanced", providers=providers)
        # Add multiple layers in one chain
        .layers.add("base")
        .parent()
        .layers.add("lower")
        .parent()
        .layers.add("raise")
        .parent()
        .layers.add("adjust")
        .parent()
        # Configure base layer
        .layers.get("base")
        .set_range(0, 5, ["&kp Q", "&kp W", "&kp E", "&kp R", "&kp T"])
        .set_range(5, 10, ["&kp Y", "&kp U", "&kp I", "&kp O", "&kp P"])
        .parent()
        # Add home row mods
        .behaviors.add_hold_tap("hm_l", hold="&kp LCTRL", tap="&kp A")
        .add_hold_tap("hm_r", hold="&kp RCTRL", tap="&kp SEMI")
        .parent()
        # Validate
        .validate()
    )

    # Query capabilities
    print("\nQuerying layout...")
    print(f"  Layers: {layout.layers.list()}")
    print(f"  Has base layer: {'base' in layout.layers.list()}")

    # Clone and modify
    print("\nCloning and modifying...")
    variant = (
        layout.clone().with_name("Advanced Variant").layers.remove("adjust").parent()
    )

    print(f"  Original layers: {layout.layers.list()}")
    print(f"  Variant layers: {variant.layers.list()}")

    print("\n✓ Advanced features demonstrated!")

    return layout, variant


def main():
    """Run all examples."""
    print("ZMK-Layout Glovebox Integration Examples")
    print("=" * 50)

    # Run examples
    layout = example_basic_usage()
    wrapper = example_migration_wrapper()
    service = example_service_integration()
    advanced, variant = example_advanced_features()

    print("\n" + "=" * 50)
    print("All examples completed successfully!")
    print("\nNext steps:")
    print("1. Review the generated files in 'output/' directory")
    print("2. Check the Provider Implementation Guide")
    print("3. Read the Glovebox Integration Guide")
    print("4. Start migrating your glovebox services")


if __name__ == "__main__":
    main()
