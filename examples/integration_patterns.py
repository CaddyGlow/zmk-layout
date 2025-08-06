#!/usr/bin/env python3
"""
Integration Patterns for zmk-layout Library

This example shows how to integrate the zmk-layout library into larger applications,
work with custom providers, and handle advanced use cases.
"""

from pathlib import Path

from zmk_layout import Layout
from zmk_layout.providers import create_default_providers


class CustomFileProvider:
    """Example custom file provider for special file handling."""

    def __init__(self, base_path: str = "/tmp"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    def read_text(self, file_path: str) -> str:
        """Read text file with custom logging."""
        path = self.base_path / file_path
        print(f"[CustomFileProvider] Reading: {path}")
        return path.read_text(encoding="utf-8")

    def write_text(self, file_path: str, content: str) -> None:
        """Write text file with custom logging."""
        path = self.base_path / file_path
        print(f"[CustomFileProvider] Writing: {path}")
        path.write_text(content, encoding="utf-8")

    def exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return (self.base_path / file_path).exists()

    def is_file(self, file_path: str) -> bool:
        """Check if path is a file."""
        return (self.base_path / file_path).is_file()

    def mkdir(self, dir_path: str) -> None:
        """Create directory."""
        (self.base_path / dir_path).mkdir(parents=True, exist_ok=True)


class CustomLogger:
    """Example custom logger with structured output."""

    def __init__(self, prefix: str = "ZMK-Layout"):
        self.prefix = prefix

    def info(self, message: str, **kwargs) -> None:
        extra = f" {kwargs}" if kwargs else ""
        print(f"[{self.prefix}] INFO: {message}{extra}")

    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        extra = f" {kwargs}" if kwargs else ""
        print(f"[{self.prefix}] ERROR: {message}{extra}")

    def warning(self, message: str, **kwargs) -> None:
        extra = f" {kwargs}" if kwargs else ""
        print(f"[{self.prefix}] WARNING: {message}{extra}")

    def debug(self, message: str, **kwargs) -> None:
        extra = f" {kwargs}" if kwargs else ""
        print(f"[{self.prefix}] DEBUG: {message}{extra}")

    def exception(self, message: str, **kwargs) -> None:
        extra = f" {kwargs}" if kwargs else ""
        print(f"[{self.prefix}] EXCEPTION: {message}{extra}")


def example_1_custom_providers():
    """Demonstrate using custom providers."""
    print("=== Example 1: Custom Providers ===")

    # Create custom providers
    custom_providers = create_default_providers()
    custom_providers.file = CustomFileProvider("/tmp/zmk_custom")
    custom_providers.logger = CustomLogger("CustomZMK")

    # Use layout with custom providers
    layout = Layout.create_empty(
        keyboard="custom_board", title="Layout with Custom Providers", providers=custom_providers
    )

    # Operations will use custom providers
    custom_providers.logger.info("Creating layout with custom providers")

    layout.layers.add("base")
    layout.layers.get("base").set(0, "&kp Q").set(1, "&kp W")

    # Save using custom file provider
    layout.save("custom_layout.json")

    print("✓ Custom providers working correctly!")
    return layout


def example_2_batch_layout_processing():
    """Process multiple layouts in batch."""
    print("\n=== Example 2: Batch Layout Processing ===")

    # Create multiple layouts
    keyboards = ["corne", "lily58", "sofle", "kyria"]
    layouts = {}

    for keyboard in keyboards:
        print(f"Creating layout for {keyboard}...")

        layout = Layout.create_empty(keyboard=keyboard, title=f"{keyboard.title()} Layout")

        # Add common layers
        base_layer = layout.layers.add("base")
        base_layer.set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E")

        nav_layer = layout.layers.add("nav")
        nav_layer.set(0, "&kp HOME").set(1, "&kp END").set(2, "&kp UP")

        # Add common behaviors
        layout.behaviors.add_hold_tap(name="mt_space", tap="&kp SPACE", hold="&kp LCTRL")

        layouts[keyboard] = layout

    # Batch save all layouts
    print("\nSaving all layouts...")
    for keyboard, layout in layouts.items():
        layout.save(f"/tmp/{keyboard}_batch_layout.json")

    # Batch statistics
    print("\nBatch Statistics:")
    for keyboard, layout in layouts.items():
        stats = layout.get_statistics()
        print(f"  {keyboard}: {stats['layer_count']} layers, {stats['total_behaviors']} behaviors")

    print("✓ Batch processing completed!")
    return layouts


def example_3_layout_validation_and_analysis():
    """Demonstrate layout validation and analysis."""
    print("\n=== Example 3: Layout Validation and Analysis ===")

    # Create a complex layout
    layout = Layout.create_empty(keyboard="ergodox", title="Complex Validation Test")

    # Add layers with various configurations
    layers_config = {
        "base": ["&kp Q", "&kp W", "&kp E", "&kp R"],
        "symbols": ["&kp EXCL", "&kp AT", "&kp HASH", "&kp DLLR"],
        "numbers": ["&kp N1", "&kp N2", "&kp N3", "&kp N4"],
        "function": ["&kp F1", "&kp F2", "&kp F3", "&kp F4"],
        "gaming": ["&kp T", "&kp A", "&kp B", "&kp SPACE"],
    }

    for layer_name, bindings in layers_config.items():
        layer = layout.layers.add(layer_name)
        for i, binding in enumerate(bindings):
            layer.set(i, binding)

    # Add various behaviors
    layout.behaviors.add_hold_tap(name="hm_a", tap="&kp A", hold="&kp LGUI")
    layout.behaviors.add_combo(name="esc_combo", keys=[0, 1], binding="&kp ESC")
    layout.behaviors.add_macro(name="test_macro", sequence=["&kp T", "&kp E", "&kp S", "&kp T"])

    # Validate the layout
    print("Validating layout...")
    try:
        layout.validate()
        print("✓ Layout validation passed!")
    except Exception as e:
        print(f"✗ Layout validation failed: {e}")

    # Analyze the layout
    print("\nAnalyzing layout:")
    stats = layout.get_statistics()

    analysis = {
        "complexity_score": stats["total_behaviors"] * 2 + stats["layer_count"],
        "binding_density": stats["total_bindings"] / stats["layer_count"] if stats["layer_count"] > 0 else 0,
        "behavior_ratio": stats["total_behaviors"] / stats["layer_count"] if stats["layer_count"] > 0 else 0,
        "avg_layer_utilization": stats.get("avg_layer_size", 0),
    }

    print(f"  Complexity Score: {analysis['complexity_score']}")
    print(f"  Binding Density: {analysis['binding_density']:.1f} bindings/layer")
    print(f"  Behavior Ratio: {analysis['behavior_ratio']:.1f} behaviors/layer")
    print(f"  Average Layer Size: {analysis['avg_layer_utilization']:.1f} keys")

    # Layer utilization analysis
    print("\nLayer Utilization:")
    if "layer_sizes" in stats:
        for layer_name, size in stats["layer_sizes"].items():
            utilization = (size / 50) * 100  # Assuming 50 key max for demo
            print(f"  {layer_name}: {size} keys ({utilization:.1f}% utilization)")

    print("✓ Layout analysis completed!")
    return layout, analysis


def example_4_layout_templating():
    """Create layouts from templates."""
    print("\n=== Example 4: Layout Templating ===")

    # Define a layout template
    template_config = {
        "base_bindings": {
            "qwerty_row1": ["&kp Q", "&kp W", "&kp E", "&kp R", "&kp T", "&kp Y", "&kp U", "&kp I", "&kp O", "&kp P"],
            "qwerty_row2": [
                "&kp A",
                "&kp S",
                "&kp D",
                "&kp F",
                "&kp G",
                "&kp H",
                "&kp J",
                "&kp K",
                "&kp L",
                "&kp SEMICOLON",
            ],
            "qwerty_row3": [
                "&kp Z",
                "&kp X",
                "&kp C",
                "&kp V",
                "&kp B",
                "&kp N",
                "&kp M",
                "&kp COMMA",
                "&kp DOT",
                "&kp SLASH",
            ],
        },
        "nav_bindings": {
            "arrows": ["&kp LEFT", "&kp DOWN", "&kp UP", "&kp RIGHT"],
            "page": ["&kp HOME", "&kp PG_DN", "&kp PG_UP", "&kp END"],
        },
        "common_behaviors": [
            {"type": "hold_tap", "name": "mt_space", "tap": "&kp SPACE", "hold": "&kp LCTRL"},
            {"type": "combo", "name": "esc_combo", "keys": [0, 1], "binding": "&kp ESC"},
        ],
    }

    def create_layout_from_template(keyboard: str, template: dict) -> Layout:
        """Create a layout from a template configuration."""
        layout = Layout.create_empty(keyboard=keyboard, title=f"Templated {keyboard.title()} Layout")

        # Add base layer
        base_layer = layout.layers.add("base")
        offset = 0
        for _row_name, bindings in template["base_bindings"].items():
            for i, binding in enumerate(bindings):
                base_layer.set(offset + i, binding)
            offset += len(bindings)

        # Add navigation layer
        nav_layer = layout.layers.add("nav")
        offset = 0
        for _section_name, bindings in template["nav_bindings"].items():
            for i, binding in enumerate(bindings):
                nav_layer.set(offset + i, binding)
            offset += len(bindings)

        # Add common behaviors
        for behavior_config in template["common_behaviors"]:
            if behavior_config["type"] == "hold_tap":
                layout.behaviors.add_hold_tap(
                    name=behavior_config["name"], tap=behavior_config["tap"], hold=behavior_config["hold"]
                )
            elif behavior_config["type"] == "combo":
                layout.behaviors.add_combo(
                    name=behavior_config["name"], keys=behavior_config["keys"], binding=behavior_config["binding"]
                )

        return layout

    # Create layouts for different keyboards using the same template
    keyboards = ["planck", "preonic", "niu_mini"]
    templated_layouts = {}

    for keyboard in keyboards:
        print(f"Creating templated layout for {keyboard}...")
        layout = create_layout_from_template(keyboard, template_config)
        templated_layouts[keyboard] = layout

        # Save the templated layout
        layout.save(f"/tmp/{keyboard}_templated.json")

    # Show template results
    print("\nTemplate Results:")
    for keyboard, layout in templated_layouts.items():
        stats = layout.get_statistics()
        print(f"  {keyboard}: {stats['layer_count']} layers, {stats['total_bindings']} bindings")

    print("✓ Layout templating completed!")
    return templated_layouts


def example_5_layout_comparison():
    """Compare different layouts."""
    print("\n=== Example 5: Layout Comparison ===")

    # Create two different layouts
    layout_a = Layout.create_empty(keyboard="test_a", title="Layout A")
    layout_a.layers.add("base").set(0, "&kp Q").set(1, "&kp W")
    layout_a.layers.add("nav").set(0, "&kp HOME").set(1, "&kp END")
    layout_a.behaviors.add_hold_tap(name="mt_a", tap="&kp A", hold="&kp LCTRL")

    layout_b = Layout.create_empty(keyboard="test_b", title="Layout B")
    layout_b.layers.add("base").set(0, "&kp Q").set(1, "&kp W").set(2, "&kp E")
    layout_b.layers.add("symbols").set(0, "&kp EXCL").set(1, "&kp AT")
    layout_b.behaviors.add_hold_tap(name="mt_b", tap="&kp B", hold="&kp LALT")
    layout_b.behaviors.add_combo(name="combo_b", keys=[0, 1], binding="&kp ESC")

    # Compare statistics
    stats_a = layout_a.get_statistics()
    stats_b = layout_b.get_statistics()

    print("Layout Comparison:")
    comparison_metrics = [
        ("Layers", stats_a["layer_count"], stats_b["layer_count"]),
        ("Total Bindings", stats_a["total_bindings"], stats_b["total_bindings"]),
        ("Total Behaviors", stats_a["total_behaviors"], stats_b["total_behaviors"]),
        ("Hold-Taps", stats_a["behavior_counts"]["hold_taps"], stats_b["behavior_counts"]["hold_taps"]),
        ("Combos", stats_a["behavior_counts"]["combos"], stats_b["behavior_counts"]["combos"]),
    ]

    print(f"{'Metric':<15} {'Layout A':<10} {'Layout B':<10} {'Difference':<10}")
    print("-" * 50)

    for metric, value_a, value_b in comparison_metrics:
        diff = value_b - value_a
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        print(f"{metric:<15} {value_a:<10} {value_b:<10} {diff_str:<10}")

    # Find common and unique layer names
    layers_a = set(stats_a["layer_names"])
    layers_b = set(stats_b["layer_names"])

    common_layers = layers_a & layers_b
    unique_a = layers_a - layers_b
    unique_b = layers_b - layers_a

    print("\nLayer Analysis:")
    print(f"  Common layers: {list(common_layers)}")
    print(f"  Unique to A: {list(unique_a)}")
    print(f"  Unique to B: {list(unique_b)}")

    print("✓ Layout comparison completed!")
    return stats_a, stats_b


def main():
    """Run all integration pattern examples."""
    print("ZMK Layout Library - Integration Patterns")
    print("=" * 60)

    examples = [
        example_1_custom_providers,
        example_2_batch_layout_processing,
        example_3_layout_validation_and_analysis,
        example_4_layout_templating,
        example_5_layout_comparison,
    ]

    results = {}

    for example_func in examples:
        try:
            result = example_func()
            results[example_func.__name__] = result
            print("✓ Success\n")
        except Exception as e:
            print(f"✗ Failed: {e}")
            import traceback

            traceback.print_exc()
            print()

    print("=" * 60)
    print(f"Integration Patterns: {len(results)}/{len(examples)} examples completed!")
    print("\nThese patterns demonstrate how to:")
    print("  • Use custom providers for specialized requirements")
    print("  • Process multiple layouts in batch operations")
    print("  • Validate and analyze layout complexity")
    print("  • Create layouts from reusable templates")
    print("  • Compare different layout configurations")
    print("\nThe zmk-layout library provides a flexible foundation")
    print("for building sophisticated keyboard layout tools!")


if __name__ == "__main__":
    main()
