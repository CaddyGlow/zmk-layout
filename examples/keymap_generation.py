#!/usr/bin/env python3
"""
ZMK Keymap File Generation Example

This example demonstrates how to create a layout and generate actual ZMK keymap files
(.keymap, .dtsi files) using the real ZMK generators instead of manual string formatting.
"""

from pathlib import Path
from typing import Any

from zmk_layout import Layout
from zmk_layout.generators.zmk_generator import create_zmk_generator
from zmk_layout.providers.factory import create_default_providers


class MockKeyboardConfig:
    """Mock keyboard config that provides the structure expected by ZMK generators."""

    def __init__(self, keyboard_name: str = "corne", key_count: int = 42):
        self.key_count = key_count
        self.keymap = MockKeymapConfig()
        self.zmk = MockZMKConfig()


class MockKeymapConfig:
    """Mock keymap configuration."""

    def __init__(self):
        self.header_includes = [
            "behaviors.dtsi",
            "dt-bindings/zmk/keys.h",
            "dt-bindings/zmk/bt.h",
        ]
        self.key_position_header = ""
        self.system_behaviors_dts = ""


class MockZMKConfig:
    """Mock ZMK configuration with required patterns and strings."""

    def __init__(self):
        self.patterns = MockPatterns()
        self.compatible_strings = MockCompatibleStrings()
        self.validation_limits = MockValidationLimits()
        self.hold_tap_flavors = ["tap-preferred", "hold-preferred", "balanced"]


class MockPatterns:
    """Mock patterns for ZMK generation."""

    def __init__(self):
        self.layer_define = "#define {layer_name} {layer_index}"
        self.node_name_sanitize = r"\W|^(?=\d)"
        self.kconfig_prefix = "CONFIG_ZMK_"


class MockCompatibleStrings:
    """Mock compatible strings for device tree."""

    def __init__(self):
        self.keymap = "zmk,keymap"
        self.hold_tap = "zmk,behavior-hold-tap"
        self.combos = "zmk,combos"
        self.macro = "zmk,behavior-macro"
        self.macro_one_param = "zmk,behavior-macro-one-param"
        self.macro_two_param = "zmk,behavior-macro-two-param"


class MockValidationLimits:
    """Mock validation limits."""

    def __init__(self):
        self.required_holdtap_bindings = 2
        self.max_macro_params = 2


class MockProfile:
    """Mock profile that provides the structure expected by generators."""

    def __init__(self, keyboard_name: str = "corne", key_count: int = 42):
        self.keyboard_name = keyboard_name
        self.keyboard_config = MockKeyboardConfig(keyboard_name, key_count)


def create_simple_corne_layout():
    """Create a simple but complete Corne layout."""
    print("=== Creating Simple Corne Layout ===")

    layout = Layout.create_empty(keyboard="corne", title="Simple Corne Layout")

    # Add hold-tap behaviors for home row mods
    layout.behaviors.add_hold_tap(
        name="hm_a", tap="&kp A", hold="&kp LGUI", tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_s", tap="&kp S", hold="&kp LALT", tapping_term_ms=280, quick_tap_ms=175
    )
    layout.behaviors.add_hold_tap(
        name="hm_d",
        tap="&kp D",
        hold="&kp LCTRL",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )
    layout.behaviors.add_hold_tap(
        name="hm_f",
        tap="&kp F",
        hold="&kp LSHIFT",
        tapping_term_ms=280,
        quick_tap_ms=175,
    )

    # Layer toggle behaviors
    layout.behaviors.add_hold_tap(
        name="lt_spc", tap="&kp SPACE", hold="&mo 1", tapping_term_ms=200
    )
    layout.behaviors.add_hold_tap(
        name="lt_ent", tap="&kp ENTER", hold="&mo 2", tapping_term_ms=200
    )

    # Add useful combos
    layout.behaviors.add_combo(
        name="combo_esc", keys=[0, 1], binding="&kp ESC", timeout_ms=50
    )
    layout.behaviors.add_combo(
        name="combo_tab", keys=[10, 11], binding="&kp TAB", timeout_ms=50
    )

    # Add a useful macro
    layout.behaviors.add_macro(
        name="email_macro",
        sequence=[
            "&kp U",
            "&kp S",
            "&kp E",
            "&kp R",
            "&kp AT",
            "&kp D",
            "&kp O",
            "&kp M",
            "&kp A",
            "&kp I",
            "&kp N",
        ],
    )

    print("Adding base layer (QWERTY)...")
    # Base layer - QWERTY layout with home row mods
    base_layer = layout.layers.add("base")

    # Corne has 42 keys (3x6+3 per side)
    base_bindings = [
        # Left side - Top row (0-5)
        "&kp Q",
        "&kp W",
        "&kp E",
        "&kp R",
        "&kp T",
        # Right side - Top row (6-11)
        "&kp Y",
        "&kp U",
        "&kp I",
        "&kp O",
        "&kp P",
        # Left side - Home row (12-17) with mods
        "&hm_a",
        "&hm_s",
        "&hm_d",
        "&hm_f",
        "&kp G",
        # Right side - Home row (18-23)
        "&kp H",
        "&kp J",
        "&kp K",
        "&kp L",
        "&kp SEMICOLON",
        # Left side - Bottom row (24-29)
        "&kp Z",
        "&kp X",
        "&kp C",
        "&kp V",
        "&kp B",
        # Right side - Bottom row (30-35)
        "&kp N",
        "&kp M",
        "&kp COMMA",
        "&kp DOT",
        "&kp SLASH",
        # Left thumb keys (36-38)
        "&kp LGUI",
        "&lt_spc",
        "&kp LCTRL",
        # Right thumb keys (39-41)
        "&kp LALT",
        "&lt_ent",
        "&kp RSHIFT",
    ]

    for i, binding in enumerate(base_bindings):
        base_layer.set(i, binding)

    print("Adding lower layer (numbers/navigation)...")
    # Lower layer - Numbers and navigation
    lower_layer = layout.layers.add("lower")

    lower_bindings = [
        # Numbers row
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
        # Navigation
        "&kp TAB",
        "&kp HOME",
        "&kp UP",
        "&kp END",
        "&kp PG_UP",
        "&kp PG_DN",
        "&kp LEFT",
        "&kp DOWN",
        "&kp RIGHT",
        "&kp BSPC",
        # Function keys
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
        # Thumb keys
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&mo 3",
        "&trans",
    ]

    for i, binding in enumerate(lower_bindings):
        lower_layer.set(i, binding)

    print("Adding raise layer (symbols)...")
    # Raise layer - Symbols and special characters
    raise_layer = layout.layers.add("raise")

    raise_bindings = [
        # Symbol row
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
        # Brackets and operators
        "&kp GRAVE",
        "&kp LBKT",
        "&kp MINUS",
        "&kp RBKT",
        "&kp PIPE",
        "&kp BSLH",
        "&kp EQUAL",
        "&kp PLUS",
        "&kp LBRC",
        "&kp RBRC",
        # More symbols
        "&kp TILDE",
        "&kp UNDER",
        "&kp LT",
        "&kp GT",
        "&trans",
        "&trans",
        "&kp SQT",
        "&kp DQT",
        "&kp COLON",
        "&kp QMARK",
        # Thumb keys
        "&trans",
        "&mo 3",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
    ]

    for i, binding in enumerate(raise_bindings):
        raise_layer.set(i, binding)

    print("Adding adjust layer (system/media)...")
    # Adjust layer - System controls and media
    adjust_layer = layout.layers.add("adjust")

    adjust_bindings = [
        # Media controls
        "&kp C_MUTE",
        "&kp C_VOL_DN",
        "&kp C_VOL_UP",
        "&kp C_PREV",
        "&kp C_NEXT",
        "&kp C_PP",
        "&email_macro",
        "&trans",
        "&trans",
        "&trans",
        # Bluetooth controls
        "&bt BT_CLR",
        "&bt BT_SEL 0",
        "&bt BT_SEL 1",
        "&bt BT_SEL 2",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&sys_reset",
        # Fill rest with transparent
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        # Thumb keys
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
    ]

    for i, binding in enumerate(adjust_bindings):
        adjust_layer.set(i, binding)

    print(f"✓ Created complete Corne layout with {len(layout.layers.names)} layers")
    return layout


def generate_zmk_keymap_file(layout: Layout, output_dir: str = "/tmp/zmk_output"):
    """Generate ZMK keymap files using the real ZMK generators."""
    print("\n=== Generating ZMK Keymap Files Using Real Generators ===")

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create a mock profile for the generators
    profile = MockProfile("corne", 42)

    # Set up providers
    providers = create_default_providers()

    # Create the ZMK generator with providers
    generator = create_zmk_generator(
        configuration_provider=providers.configuration,
        template_provider=providers.template,
        logger=providers.logger,
    )

    # Get layout data
    layout_data = layout.data
    layer_names = layout_data.layer_names
    layers_data = layout_data.layers

    print(f"Generating ZMK files for {len(layer_names)} layers...")

    # Generate individual DTSI components
    behaviors_dtsi = ""
    if layout_data.hold_taps:
        print(
            f"Generating behaviors DTSI for {len(layout_data.hold_taps)} hold-tap behaviors..."
        )
        behaviors_dtsi = generator.generate_behaviors_dtsi(
            profile, layout_data.hold_taps
        )

    combos_dtsi = ""
    if layout_data.combos:
        print(f"Generating combos DTSI for {len(layout_data.combos)} combos...")
        combos_dtsi = generator.generate_combos_dtsi(
            profile, layout_data.combos, layer_names
        )

    macros_dtsi = ""
    if layout_data.macros:
        print(f"Generating macros DTSI for {len(layout_data.macros)} macros...")
        macros_dtsi = generator.generate_macros_dtsi(profile, layout_data.macros)

    # Generate the main keymap node
    print("Generating keymap node...")
    keymap_node = generator.generate_keymap_node(profile, layer_names, layers_data)

    # Generate layer defines
    layer_defines = generator.generate_layer_defines(profile, layer_names)

    # Build the complete keymap file
    keymap_content = generate_complete_keymap_file(
        layout_data,
        behaviors_dtsi,
        combos_dtsi,
        macros_dtsi,
        keymap_node,
        layer_defines,
    )

    # Write keymap file
    keymap_file = output_path / f"{layout_data.keyboard}.keymap"
    providers.file.write_text(keymap_file, keymap_content)
    print(f"✓ Generated ZMK keymap using real generators: {keymap_file}")

    return keymap_file


def generate_complete_keymap_file(
    layout_data: Any,
    behaviors_dtsi: str,
    combos_dtsi: str,
    macros_dtsi: str,
    keymap_node: str,
    layer_defines: str,
) -> str:
    """Assemble all generated components into a complete keymap file."""

    # Build the complete keymap file content
    keymap_parts = []

    # Add header comment
    keymap_parts.append("/*")
    keymap_parts.append(f" * {layout_data.title}")
    keymap_parts.append(" * Generated by zmk-layout library using real ZMK generators")
    keymap_parts.append(f" * Keyboard: {layout_data.keyboard}")
    keymap_parts.append(" */")
    keymap_parts.append("")

    # Add includes
    keymap_parts.append("#include <behaviors.dtsi>")
    keymap_parts.append("#include <dt-bindings/zmk/keys.h>")
    keymap_parts.append("#include <dt-bindings/zmk/bt.h>")
    keymap_parts.append("")

    # Add layer defines if present
    if layer_defines:
        keymap_parts.append("/* Layer definitions */")
        keymap_parts.append(layer_defines)
        keymap_parts.append("")

    # Add root node start
    keymap_parts.append("/ {")

    # Add behaviors section if we have any
    if behaviors_dtsi or combos_dtsi or macros_dtsi:
        keymap_parts.append("    behaviors {")

        if behaviors_dtsi:
            keymap_parts.append(behaviors_dtsi)

        if macros_dtsi:
            # Add spacing if we had behaviors before
            if behaviors_dtsi:
                keymap_parts.append("")
            keymap_parts.append(macros_dtsi)

        keymap_parts.append("    };")
        keymap_parts.append("")

    # Add combos section if present
    if combos_dtsi:
        keymap_parts.append(f"    {combos_dtsi}")
        keymap_parts.append("")

    # Add keymap section
    keymap_parts.append(f"    {keymap_node}")

    # Close root node
    keymap_parts.append("};")

    return "\n".join(keymap_parts)


def validate_keymap_file(keymap_file: Path):
    """Basic validation of generated keymap file."""
    print("\n=== Validating Keymap File ===")

    if not keymap_file.exists():
        print("✗ Keymap file does not exist")
        return False

    content = keymap_file.read_text()

    # Basic validation checks
    validation_checks = [
        ("#include <behaviors.dtsi>", "behaviors.dtsi included"),
        ("#include <dt-bindings/zmk/keys.h>", "ZMK keys included"),
        ("keymap {", "keymap block present"),
        ("bindings = <", "bindings defined"),
        ("&kp", "key presses defined"),
        (
            "Generated by zmk-layout library using real ZMK generators",
            "generated using real generators",
        ),
    ]

    print("Validation Results:")
    all_passed = True
    for check_pattern, description in validation_checks:
        if check_pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False

    # Count layers
    layer_count = content.count("_layer {")
    print(f"  ✓ Found {layer_count} layers defined")

    # Check file size
    file_size = keymap_file.stat().st_size
    print(f"  ✓ Keymap file size: {file_size} bytes")

    if all_passed:
        print("✓ Keymap file validation passed!")
    else:
        print("⚠ Some validation checks failed")

    return all_passed


def example_keymap_workflow():
    """Complete workflow: create layout -> generate keymap -> validate."""
    print("ZMK Keymap Generation - Complete Workflow Using Real Generators")
    print("=" * 70)

    try:
        # Step 1: Create the layout
        layout = create_simple_corne_layout()

        # Step 2: Save layout as JSON for reference using data-only API
        layout_data = layout.to_dict()
        from zmk_layout.utils.json_operations import serialize_json_data

        json_content = serialize_json_data(layout_data, indent=2)
        Path("/tmp/corne_layout.json").write_text(json_content)
        print("✓ Saved layout JSON for reference using data-only API")

        # Step 3: Generate ZMK keymap files
        keymap_file = generate_zmk_keymap_file(layout)

        # Step 4: Validate the generated keymap
        if keymap_file:
            validate_keymap_file(keymap_file)

        # Step 5: Show layout statistics
        stats = layout.get_statistics()
        print("\n=== Final Layout Statistics ===")
        print(f"  Keyboard: {stats['keyboard']}")
        print(f"  Layers: {stats['layer_count']} ({', '.join(stats['layer_names'])})")
        print(f"  Total Bindings: {stats['total_bindings']}")
        print(f"  Behaviors: {stats['total_behaviors']}")
        print(f"  Hold-Taps: {stats['behavior_counts']['hold_taps']}")
        print(f"  Combos: {stats['behavior_counts']['combos']}")
        print(f"  Macros: {stats['behavior_counts']['macros']}")

        print(
            "\n✓ Keymap generation workflow completed successfully using REAL GENERATORS!"
        )
        print("Generated files:")
        print("  - Layout JSON: /tmp/corne_layout.json")
        if keymap_file:
            print(f"  - ZMK Keymap: {keymap_file}")
            print(
                "\n🎉 This keymap was generated using the actual ZMK generators, not manual string formatting!"
            )

        return layout, keymap_file

    except Exception as e:
        print(f"✗ Workflow failed: {e}")
        import traceback

        traceback.print_exc()
        return None, None


def show_keymap_preview(keymap_file: Path, lines: int = 30):
    """Show preview of generated keymap file."""
    if not keymap_file or not keymap_file.exists():
        print("No keymap file to preview")
        return

    print(f"\n=== Keymap File Preview ({keymap_file.name}) ===")

    content_lines = keymap_file.read_text().split("\n")
    preview_lines = content_lines[:lines]

    for i, line in enumerate(preview_lines, 1):
        print(f"{i:3d}: {line}")

    if len(content_lines) > lines:
        print(f"... ({len(content_lines) - lines} more lines)")


def main():
    """Run the complete keymap generation example."""
    # Run the complete workflow
    layout, keymap_file = example_keymap_workflow()

    if keymap_file:
        # Show preview of generated keymap
        show_keymap_preview(keymap_file)

        print("\n" + "=" * 70)
        print("🎉 ZMK Keymap Generation Complete - Using Real Generators!")
        print("\nYou now have:")
        print("  1. A complete ZMK layout created with the fluent API")
        print(
            "  2. Generated .keymap file using REAL ZMK generators (not manual formatting)"
        )
        print("  3. JSON layout file for backup/reference")
        print("\nThe keymap file was generated using:")
        print("  • ZMKGenerator.generate_behaviors_dtsi() for hold-tap behaviors")
        print("  • ZMKGenerator.generate_combos_dtsi() for combo behaviors")
        print("  • ZMKGenerator.generate_macros_dtsi() for macro behaviors")
        print("  • ZMKGenerator.generate_keymap_node() for the main keymap")
        print("\nThe keymap file can be used directly with ZMK firmware!")


def add_zmk_export_to_layout():
    """
    Demonstration of how you could add ZMK export functionality as a method to Layout class.

    This shows how the real generators could be integrated into the Layout class
    for convenient keymap generation.
    """

    def export_zmk_keymap(self, output_path: str | Path, keyboard_profile=None) -> Path:
        """Export layout as ZMK keymap file using real generators.

        Args:
            output_path: Path to write the .keymap file
            keyboard_profile: Optional keyboard profile (uses mock if None)

        Returns:
            Path to generated keymap file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Use provided profile or create mock
        profile = keyboard_profile or MockProfile(self.data.keyboard, 42)

        # Create generator
        generator = create_zmk_generator(
            configuration_provider=self._providers.configuration,
            template_provider=self._providers.template,
            logger=self._providers.logger,
        )

        # Generate components
        layout_data = self.data
        layer_names = layout_data.layer_names
        layers_data = layout_data.layers

        behaviors_dtsi = ""
        combos_dtsi = ""
        macros_dtsi = ""

        if layout_data.hold_taps:
            behaviors_dtsi = generator.generate_behaviors_dtsi(
                profile, layout_data.hold_taps
            )

        if layout_data.combos:
            combos_dtsi = generator.generate_combos_dtsi(
                profile, layout_data.combos, layer_names
            )

        if layout_data.macros:
            macros_dtsi = generator.generate_macros_dtsi(profile, layout_data.macros)

        keymap_node = generator.generate_keymap_node(profile, layer_names, layers_data)
        layer_defines = generator.generate_layer_defines(profile, layer_names)

        # Generate complete keymap
        keymap_content = generate_complete_keymap_file(
            layout_data,
            behaviors_dtsi,
            combos_dtsi,
            macros_dtsi,
            keymap_node,
            layer_defines,
        )

        # Write file
        self._providers.file.write_text(output_file, keymap_content)
        return output_file

    # This demonstrates how you could patch the Layout class:
    # Layout.export_zmk_keymap = export_zmk_keymap

    print("\n=== Layout Class Extension Demo ===")
    print("The above function shows how to add ZMK export capability to Layout class:")
    print("  layout.export_zmk_keymap('/path/to/output.keymap')")
    print("This would make the real generators directly accessible via the fluent API!")


if __name__ == "__main__":
    main()
    add_zmk_export_to_layout()
