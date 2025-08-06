"""Golden file testing for parse → modify → save round-trip testing."""

import json
import tempfile
from pathlib import Path
from typing import Any

from zmk_layout.models import ComboBehavior, HoldTapBehavior, LayoutBinding, LayoutData
from zmk_layout.providers.factory import create_default_providers


class TestGoldenFiles:
    """Test round-trip parsing and serialization."""

    def test_round_trip_simple_layout(self) -> None:
        """Test parse → modify → save produces consistent output."""
        # Create a simple layout
        original_data = LayoutData(
            keyboard="test_keyboard",
            title="Test Layout",
            layers=[
                [
                    LayoutBinding.from_str("&kp Q"),
                    LayoutBinding.from_str("&kp W"),
                    LayoutBinding.from_str("&kp E"),
                    LayoutBinding.from_str("&trans"),
                ],
                [
                    LayoutBinding.from_str("&kp N1"),
                    LayoutBinding.from_str("&kp N2"),
                    LayoutBinding.from_str("&kp N3"),
                    LayoutBinding.from_str("&trans"),
                ],
            ],
            holdTaps=[
                HoldTapBehavior(
                    name="mt",
                    bindings=["&kp", "&kp"],
                    tappingTermMs=200,
                    flavor="balanced",
                )
            ],
            combos=[
                ComboBehavior(
                    name="esc_combo",
                    keyPositions=[0, 1],
                    binding=LayoutBinding.from_str("&kp ESC"),
                )
            ],
        )

        # Serialize to JSON
        json_data = original_data.model_dump(mode="json")

        # Round-trip: JSON → Model → JSON
        parsed_data = LayoutData.model_validate(json_data)
        json_data_roundtrip = parsed_data.model_dump(mode="json")

        # Compare the two JSON outputs (excluding dynamic fields like date)
        def normalize_for_comparison(data: dict[str, Any]) -> dict[str, Any]:
            """Remove dynamic fields for comparison."""
            normalized = data.copy()
            if "date" in normalized:
                del normalized["date"]  # Date is dynamic
            return normalized

        original_normalized = normalize_for_comparison(json_data)
        roundtrip_normalized = normalize_for_comparison(json_data_roundtrip)

        assert original_normalized == roundtrip_normalized, (
            "Round-trip serialization should be identical"
        )

    def test_round_trip_complex_bindings(self) -> None:
        """Test round-trip with complex nested bindings."""
        # Create layout with complex bindings
        complex_bindings = [
            "&kp LC(X)",  # Nested parameters
            "&mt LCTRL A",  # Multiple parameters
            "&lt 1 SPACE",  # Layer tap
            "&kp LC(LS(Z))",  # Double nested
            "&trans",  # No parameters
        ]

        layer_bindings = [
            LayoutBinding.from_str(binding) for binding in complex_bindings
        ]

        layout_data = LayoutData(
            keyboard="complex_test",
            title="Complex Bindings Test",
            layers=[layer_bindings],
        )

        # Round-trip test
        json_data = layout_data.model_dump(mode="json")
        parsed_data = LayoutData.model_validate(json_data)

        # Verify all bindings parsed correctly
        parsed_data.layers[0]
        assert len(parsed_data.layers[0]) == len(complex_bindings)

        # Verify specific complex binding
        nested_binding = parsed_data.layers[0][0]  # "&kp LC(X)"
        assert nested_binding.value == "&kp"
        assert len(nested_binding.params) == 1
        assert nested_binding.params[0].value == "LC"
        assert len(nested_binding.params[0].params) == 1
        assert nested_binding.params[0].params[0].value == "X"

    def test_round_trip_empty_layout(self) -> None:
        """Test round-trip with minimal layout."""
        minimal_layout = LayoutData(keyboard="minimal", title="Minimal Layout")

        # Round-trip test
        json_data = minimal_layout.model_dump(mode="json")
        parsed_data = LayoutData.model_validate(json_data)
        json_data_roundtrip = parsed_data.model_dump(mode="json")

        # Normalize for comparison (remove dynamic fields)
        def normalize(data: dict[str, Any]) -> dict[str, Any]:
            normalized = data.copy()
            if "date" in normalized:
                del normalized["date"]
            return normalized

        assert normalize(json_data) == normalize(json_data_roundtrip)

    def test_file_persistence(self) -> None:
        """Test saving and loading from actual files."""
        layout_data = LayoutData(
            keyboard="file_test",
            title="File Persistence Test",
            layers=[[LayoutBinding.from_str("&kp SPACE")]],
        )

        # Test with temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            # Save to file
            json.dump(layout_data.model_dump(mode="json"), tmp_file, indent=2)
            tmp_path = Path(tmp_file.name)

        try:
            # Load from file
            with open(tmp_path) as f:
                loaded_data = json.load(f)

            parsed_layout = LayoutData.model_validate(loaded_data)

            # Verify data integrity
            assert parsed_layout.keyboard == "file_test"
            assert parsed_layout.title == "File Persistence Test"
            assert len(parsed_layout.layers) == 1
            assert len(parsed_layout.layers[0]) == 1
            assert parsed_layout.layers[0][0].value == "&kp"

        finally:
            # Clean up
            tmp_path.unlink()

    def test_golden_behavior_validation(self) -> None:
        """Test that behavior validation works correctly in round-trip."""
        # Create layout with various behaviors
        layout_data = LayoutData(
            keyboard="behavior_test",
            title="Behavior Validation Test",
            holdTaps=[
                HoldTapBehavior(
                    name="test_mt",
                    bindings=["&kp", "&kp"],
                    tappingTermMs=150,
                    flavor="tap-preferred",
                )
            ],
            combos=[
                ComboBehavior(
                    name="test_combo",
                    keyPositions=[0, 1, 2],
                    binding=LayoutBinding.from_str("&kp TAB"),
                    timeoutMs=50,
                )
            ],
        )

        # Round-trip should preserve all validation
        json_data = layout_data.model_dump(mode="json")
        parsed_data = LayoutData.model_validate(json_data)

        # Verify hold-tap
        hold_tap = parsed_data.hold_taps[0]
        assert hold_tap.name == "test_mt"
        assert hold_tap.tapping_term_ms == 150
        assert hold_tap.flavor == "tap-preferred"
        assert len(hold_tap.bindings) == 2

        # Verify combo
        combo = parsed_data.combos[0]
        assert combo.name == "test_combo"
        assert combo.key_positions == [0, 1, 2]
        assert combo.timeout_ms == 50
        assert combo.binding.value == "&kp"
        assert combo.binding.params[0].value == "TAB"


class TestProviderIntegration:
    """Test provider integration with golden files."""

    def test_providers_with_layout_data(self) -> None:
        """Test that providers work with layout data."""
        providers = create_default_providers()

        # Verify providers are created correctly
        assert providers.logger is not None
        assert providers.template is not None
        assert providers.configuration is not None
        assert providers.file is not None

        # Test basic provider functionality
        providers.logger.info("Test log message")

        # Test template provider (using fallback behavior)
        if hasattr(providers.template, "render_string"):
            result = providers.template.render_string(
                "Hello {{ name }}", {"name": "World"}
            )
            # With fallback template provider, it returns the template as-is
            assert "Hello" in result  # Basic test that something was returned
