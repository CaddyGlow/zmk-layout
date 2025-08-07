#!/usr/bin/env python3
"""
Advanced Operations Examples for zmk-layout Library

This file demonstrates advanced features like complex behaviors, layer manipulation,
and integration with external providers using the new data-only API approach.
File operations are handled externally, while Layout operates on dictionary data.
"""

from pathlib import Path

from zmk_layout import Layout
from zmk_layout.core.exceptions import InvalidBindingError, LayerNotFoundError
from zmk_layout.providers import create_default_providers
from zmk_layout.utils.json_operations import parse_json_data, serialize_json_data


def example_1_complex_behaviors():
    """Create complex behaviors with detailed configurations."""
    print("=== Advanced Example 1: Complex Behaviors ===")

    layout = Layout.create_empty("ferris", "Ferris Sweep Advanced")

    # Add sophisticated hold-tap behaviors
    layout.behaviors.add_hold_tap(
        name="hm_a",  # Home row mod
        tap="&kp A",
        hold="&kp LGUI",
        tapping_term_ms=280,
        quick_tap_ms=175,
        flavor="balanced",
    )

    layout.behaviors.add_hold_tap(
        name="hm_s",
        tap="&kp S",
        hold="&kp LALT",
        tapping_term_ms=280,
        quick_tap_ms=175,
        flavor="balanced",
    )

    # Add tap-dance behavior
    layout.behaviors.add_tap_dance(
        name="td_caps", bindings=["&kp LSHIFT", "&caps_word"], tapping_term_ms=200
    )

    # Add complex combo behaviors
    layout.behaviors.add_combo(
        name="combo_qu",
        keys=[0, 1],  # Q + W
        binding="&macro_qu",
        timeout_ms=40,
        require_prior_idle_ms=125,
        layers=["base"],
    )

    layout.behaviors.add_combo(
        name="combo_esc",
        keys=[14, 15],  # J + K
        binding="&kp ESC",
        timeout_ms=50,
        slow_release=True,
    )

    # Create macro sequence
    layout.behaviors.add_macro(
        name="macro_qu",
        sequence=["&macro_press &kp Q", "&macro_tap &kp U", "&macro_release &kp Q"],
    )

    # Build base layer with home row mods
    base_layer = layout.layers.add("base")

    # Top row: Q W E R T Y U I O P
    qwerty_top = [
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
    ]
    base_layer.set_range(0, len(qwerty_top), qwerty_top)

    # Home row with mods: A S D F G H J K L ;
    home_row = [
        "&hm_a",
        "&hm_s",
        "&mt LCTRL D",
        "&mt LSHIFT F",
        "&kp G",
        "&kp H",
        "&mt RSHIFT J",
        "&mt RCTRL K",
        "&mt RALT L",
        "&kp SEMICOLON",
    ]
    base_layer.set_range(10, len(home_row), home_row)

    # Bottom row with tap-dance
    bottom_row = [
        "&td_caps",
        "&kp X",
        "&kp C",
        "&kp V",
        "&kp B",
        "&kp N",
        "&kp M",
        "&kp COMMA",
        "&kp DOT",
        "&kp SLASH",
    ]
    base_layer.set_range(20, len(bottom_row), bottom_row)

    # Thumb keys
    thumb_keys = ["&lt 1 TAB", "&kp SPACE", "&kp BSPC", "&lt 2 ENTER"]
    base_layer.set_range(30, len(thumb_keys), thumb_keys)

    stats = layout.get_statistics()
    print(f"Created layout with {stats['behavior_count']} custom behaviors")
    print(f"Behaviors: {', '.join(stats['behaviors_used'])}")

    return layout


def example_2_layer_manipulation():
    """Advanced layer operations - copying, moving, reordering."""
    print("\n=== Advanced Example 2: Layer Manipulation ===")

    layout = Layout.create_empty("crkbd", "Corne Advanced Layout")

    # Create base layer with full layout
    base = layout.layers.add("base")
    alpha_keys = [
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
        "&kp LGUI",
        "&mo 1",
        "&kp SPACE",
        "&kp ENTER",
        "&mo 2",
        "&kp RALT",
    ]
    base.set_range(0, len(alpha_keys), alpha_keys)

    # Create navigation layer
    nav = layout.layers.add("nav")
    nav_keys = [
        "&kp ESC",
        "&kp HOME",
        "&kp UP",
        "&kp END",
        "&kp PG_UP",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&kp TAB",
        "&kp LEFT",
        "&kp DOWN",
        "&kp RIGHT",
        "&kp PG_DN",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&kp LCTRL",
        "&kp LALT",
        "&kp LGUI",
        "&kp LSHIFT",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&kp SPACE",
        "&kp ENTER",
        "&trans",
        "&trans",
    ]
    nav.set_range(0, len(nav_keys), nav_keys)

    # Create symbol layer
    sym = layout.layers.add("sym")
    sym_keys = [
        "&kp EXCL",
        "&kp AT",
        "&kp HASH",
        "&kp DLLR",
        "&kp PRCNT",
        "&kp CARET",
        "&kp AMPS",
        "&kp STAR",
        "&kp LPAR",
        "&kp RPAR",
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
        "&kp GRAVE",
        "&kp MINUS",
        "&kp EQUAL",
        "&kp LBKT",
        "&kp RBKT",
        "&kp BSLH",
        "&kp SQT",
        "&kp COMMA",
        "&kp DOT",
        "&kp SLASH",
        "&trans",
        "&trans",
        "&kp SPACE",
        "&kp ENTER",
        "&trans",
        "&trans",
    ]
    sym.set_range(0, len(sym_keys), sym_keys)

    # Copy base layer to create gaming variant
    layout.layers.add("gaming")
    gaming_layer = layout.layers.get("gaming")
    gaming_layer.copy_from("base")

    # Modify gaming layer - remove layer toggles for dedicated keys
    gaming_layer.set(30, "&kp LCTRL")  # Replace LGUI with LCTRL
    gaming_layer.set(31, "&kp LSHIFT")  # Replace layer toggle with LSHIFT
    gaming_layer.set(34, "&kp SPACE")  # Replace layer toggle with SPACE

    # Add gaming function layer
    gaming_fn = layout.layers.add("gaming_fn")
    gaming_fn.copy_from("nav")  # Start with nav layout
    # Customize for gaming (F-keys, etc.)
    f_keys = [
        "&kp F1",
        "&kp F2",
        "&kp F3",
        "&kp F4",
        "&kp F5",
        "&kp F6",
        "&kp F7",
        "&kp F8",
        "&kp F9",
        "&kp F10",
    ]
    gaming_fn.set_range(0, len(f_keys), f_keys)

    # Reorder layers - put gaming layers together
    layer_names_before = layout.get_layer_names()
    print(f"Layer order before reorder: {layer_names_before}")

    # Move gaming_fn to be right after gaming
    layout.layers.move("gaming_fn", 4)  # Move to position after gaming

    layer_names_after = layout.get_layer_names()
    print(f"Layer order after reorder: {layer_names_after}")

    # Batch remove multiple layers if needed
    # layout.layers.remove_multiple(["unused1", "unused2"])  # Would remove if they existed

    return layout


def example_3_error_handling():
    """Demonstrate error handling and recovery."""
    print("\n=== Advanced Example 3: Error Handling ===")

    layout = Layout.create_empty("planck", "Error Handling Demo")

    # Add a base layer
    layout.layers.add("base")

    print("Demonstrating graceful error handling:")

    # Try to access non-existent layer
    try:
        layout.layers.get("nonexistent")
    except LayerNotFoundError as e:
        print(f"✓ Caught expected error: {e}")
        print(f"  Available layers: {layout.get_layer_names()}")

    # Try to set invalid binding
    try:
        layout.layers.get("base").set(0, "invalid_binding_format")
    except InvalidBindingError as e:
        print(f"✓ Caught binding error: {e}")

    # Try to set binding at invalid position
    try:
        layout.layers.get("base").set(-1, "&kp A")  # Negative index
    except ValueError as e:
        print(f"✓ Caught position error: {e}")

    # Try to copy from non-existent layer
    try:
        layout.layers.get("base").copy_from("nonexistent_source")
    except LayerNotFoundError as e:
        print(f"✓ Caught copy error: {e}")

    # Demonstrate successful operations after errors
    print("\nSuccessful operations after error recovery:")
    layout.layers.get("base").set(0, "&kp Q").set(1, "&kp W")
    layout.layers.add("symbols").set(0, "&kp EXCL")

    print(f"✓ Layout now has {len(layout.get_layer_names())} layers with bindings")

    return layout


def example_4_custom_providers():
    """Work with custom provider implementations."""
    print("\n=== Advanced Example 4: Custom Providers ===")

    # Create layout with custom providers
    custom_providers = create_default_providers()

    # You could create custom providers here:
    # custom_providers.configuration = MyCustomConfigurationProvider()
    # custom_providers.template = MyCustomTemplateProvider()

    layout = Layout.create_empty(
        "dactyl", "Custom Provider Demo", providers=custom_providers
    )

    # Add behaviors that might use template processing
    layout.behaviors.add_macro(
        name="signature",
        sequence=["&kp J", "&kp O", "&kp H", "&kp N"],  # "JOHN"
    )

    # Template-based layer creation (if templates are available)
    layout.layers.add("base")
    base_layer = layout.layers.get("base")

    # Set up common key patterns
    numbers = [f"&kp N{i}" for i in range(1, 11)]  # N1 through N0 (N10 = N0)
    numbers[-1] = "&kp N0"  # Fix the last one

    base_layer.set_range(0, len(numbers), numbers)

    # Add function keys
    f_keys = [f"&kp F{i}" for i in range(1, 13)]  # F1 through F12
    layout.layers.add("function")
    layout.layers.get("function").set_range(0, len(f_keys), f_keys)

    print("Created layout with custom providers")
    print(
        f"Provider types: {type(custom_providers.configuration).__name__}, {type(custom_providers.template).__name__}"
    )

    return layout


def example_5_performance_testing():
    """Test performance with large layouts."""
    print("\n=== Advanced Example 5: Performance Testing ===")

    import time

    # Create a large layout to test performance
    start_time = time.time()

    layout = Layout.create_empty("big_board", "Performance Test Layout")

    # Add many layers
    layer_names = [f"layer_{i}" for i in range(50)]
    for name in layer_names:
        layout.layers.add(name)

    layer_creation_time = time.time()
    print(
        f"Created {len(layer_names)} layers in {layer_creation_time - start_time:.3f}s"
    )

    # Add many bindings to each layer
    binding_start = time.time()
    for _i, name in enumerate(layer_names[:10]):  # Just first 10 for demo
        layer = layout.layers.get(name)
        for j in range(100):  # 100 bindings per layer
            layer.set(j, f"&kp KEY_{j}")

    binding_time = time.time()
    print(f"Added 1000 bindings in {binding_time - binding_start:.3f}s")

    # Test batch operations performance
    batch_start = time.time()

    def add_test_layer(layout):
        return layout.layers.add(f"batch_layer_{int(time.time() * 1000000) % 1000}")

    batch_ops = [add_test_layer for _ in range(20)]
    layout.batch_operation(batch_ops)

    batch_time = time.time()
    print(f"Batch operation (20 layers) in {batch_time - batch_start:.3f}s")

    # Memory usage check
    stats = layout.get_statistics()
    print(
        f"Final layout: {stats['layer_count']} layers, {stats['total_bindings']} bindings"
    )

    total_time = time.time() - start_time
    print(f"Total operation time: {total_time:.3f}s")

    return layout


def example_6_file_operations():
    """Advanced file operations and format handling using data-only API."""
    print("\n=== Advanced Example 6: File Operations (Data-Only API) ===")

    # Create a comprehensive layout
    layout = Layout.create_empty("sofle", "Sofle RGB Layout")

    # Add multiple layers with full configurations
    layers_config = {
        "base": {
            "description": "Base QWERTY layer",
            "bindings": ["&kp Q", "&kp W", "&kp E", "&kp R", "&kp T"] + ["&trans"] * 55,
        },
        "lower": {
            "description": "Numbers and symbols",
            "bindings": ["&kp N1", "&kp N2", "&kp N3", "&kp N4", "&kp N5"]
            + ["&trans"] * 55,
        },
        "raise": {
            "description": "Function keys and navigation",
            "bindings": ["&kp F1", "&kp F2", "&kp F3", "&kp F4", "&kp F5"]
            + ["&trans"] * 55,
        },
    }

    for layer_name, config in layers_config.items():
        layer = layout.layers.add(layer_name)
        layer.set_range(0, len(config["bindings"]), config["bindings"])

    # Add comprehensive behaviors
    behaviors_config = [
        ("mt_gui_a", "hold_tap", {"tap": "&kp A", "hold": "&kp LGUI"}),
        ("td_shift", "tap_dance", {"bindings": ["&kp LSHIFT", "&caps_word"]}),
        ("combo_esc", "combo", {"keys": [0, 1], "binding": "&kp ESC"}),
        ("email_macro", "macro", {"sequence": ["&kp HELLO", "&kp AT", "&kp EXAMPLE"]}),
    ]

    for name, behavior_type, params in behaviors_config:
        if behavior_type == "hold_tap":
            layout.behaviors.add_hold_tap(name, **params)
        elif behavior_type == "tap_dance":
            layout.behaviors.add_tap_dance(name, **params)
        elif behavior_type == "combo":
            layout.behaviors.add_combo(name, **params)
        elif behavior_type == "macro":
            layout.behaviors.add_macro(name, **params)

    # Save to multiple formats/locations using data-only API
    base_path = Path("/tmp/sofle_layout")
    base_path.mkdir(exist_ok=True)

    # Get layout data
    layout_data = layout.to_dict()
    json_content = serialize_json_data(layout_data, indent=2)

    # Save main layout file
    main_file = base_path / "sofle_layout.json"
    main_file.write_text(json_content)
    print(f"✓ Saved main layout to: {main_file}")

    # Save backup with timestamp
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = base_path / f"sofle_layout_backup_{timestamp}.json"
    backup_file.write_text(json_content)
    print(f"✓ Saved backup to: {backup_file}")

    # Test file integrity using data-only API
    try:
        # Load using data-only API
        file_content = main_file.read_text()
        layout_dict = parse_json_data(file_content)
        loaded_layout = Layout.from_dict(layout_dict)

        original_stats = layout.get_statistics()
        loaded_stats = loaded_layout.get_statistics()

        integrity_checks = [
            (
                "Layer count",
                original_stats["layer_count"] == loaded_stats["layer_count"],
            ),
            (
                "Behavior count",
                original_stats["behavior_count"] == loaded_stats["behavior_count"],
            ),
            (
                "Keyboard name",
                original_stats["keyboard_name"] == loaded_stats["keyboard_name"],
            ),
        ]

        print("File integrity checks using data-only API:")
        for check_name, passed in integrity_checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")

    except Exception as e:
        print(f"✗ File integrity check failed: {e}")

    return layout, main_file


def main():
    """Run all advanced examples."""
    print("ZMK Layout Library - Advanced Usage Examples")
    print("=" * 60)

    examples = [
        example_1_complex_behaviors,
        example_2_layer_manipulation,
        example_3_error_handling,
        example_4_custom_providers,
        example_5_performance_testing,
        example_6_file_operations,
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
    print(f"Completed {len(results)}/{len(examples)} advanced examples")

    # Summary statistics
    if results:
        print("\nSummary Statistics:")
        for name, result in results.items():
            if hasattr(result, "get_statistics"):
                stats = result.get_statistics()
                print(
                    f"  {name}: {stats['layer_count']} layers, {stats['total_bindings']} bindings"
                )


if __name__ == "__main__":
    main()
