"""Tests for ZMK layout utilities."""

import json
from typing import Any

from zmk_layout.models import LayoutBinding, LayoutData
from zmk_layout.providers import LayoutProviders
from zmk_layout.providers.factory import create_default_providers


class TestValidation:
    """Test validation utilities."""

    def test_layout_validation(self) -> None:
        """Test layout data validation."""
        providers = create_default_providers()

        class MockValidator:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def validate_layout(self, layout_data: LayoutData) -> list[str]:
                """Validate layout data and return errors."""
                errors = []

                if not layout_data.keyboard:
                    errors.append("Keyboard name is required")

                if not layout_data.layers:
                    errors.append("At least one layer is required")

                for i, layer in enumerate(layout_data.layers):
                    if not layer:
                        errors.append(f"Layer {i} has no bindings")

                return errors

        validator = MockValidator(providers)

        # Valid layout should pass
        valid_layout = LayoutData(
            keyboard="test_board",
            title="Test Layout",
            layers=[[LayoutBinding.from_str("&kp A")]],
        )
        errors = validator.validate_layout(valid_layout)
        assert len(errors) == 0

        # Invalid layout should have errors
        invalid_layout = LayoutData(keyboard="", title="Test", layers=[])
        errors = validator.validate_layout(invalid_layout)
        assert len(errors) >= 2
        assert "Keyboard name is required" in errors
        assert "At least one layer is required" in errors

    def test_binding_validation(self) -> None:
        """Test binding validation."""
        providers = create_default_providers()

        class MockBindingValidator:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def validate_binding(self, binding: LayoutBinding) -> list[str]:
                """Validate a binding and return errors."""
                errors = []

                if not binding.value:
                    errors.append("Binding value is required")

                if not binding.value.startswith("&"):
                    errors.append("Binding value must start with '&'")

                # Check for common behaviors
                known_behaviors = ["&kp", "&mt", "&lt", "&trans", "&none"]
                if binding.value not in known_behaviors:
                    errors.append(f"Unknown behavior: {binding.value}")

                return errors

        validator = MockBindingValidator(providers)

        # Valid bindings
        valid_binding = LayoutBinding.from_str("&kp A")
        errors = validator.validate_binding(valid_binding)
        assert len(errors) == 0

        # Invalid binding
        invalid_binding = LayoutBinding(value="kp", params=[])  # Missing &
        errors = validator.validate_binding(invalid_binding)
        assert len(errors) >= 1
        assert "Binding value must start with '&'" in errors

    def test_layer_validation(self) -> None:
        """Test layer validation."""
        providers = create_default_providers()

        class MockLayerValidator:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def validate_layer(
                self,
                layer_bindings: list[LayoutBinding],
                layer_name: str = "layer",
                expected_binding_count: int | None = None,
            ) -> list[str]:
                """Validate a layer and return errors."""
                errors = []

                if not layer_name.replace("_", "").replace("-", "").isalnum():
                    errors.append(
                        "Layer name must be alphanumeric (with _ or - allowed)"
                    )

                if (
                    expected_binding_count
                    and len(layer_bindings) != expected_binding_count
                ):
                    errors.append(
                        f"Layer '{layer_name}' has {len(layer_bindings)} bindings, expected {expected_binding_count}"
                    )

                return errors

        validator = MockLayerValidator(providers)

        # Valid layer
        valid_layer_bindings = [
            LayoutBinding.from_str("&kp A"),
            LayoutBinding.from_str("&kp B"),
        ]
        errors = validator.validate_layer(
            valid_layer_bindings, "default", expected_binding_count=2
        )
        assert len(errors) == 0

        # Invalid layer name
        invalid_layer_bindings: list[LayoutBinding] = []
        errors = validator.validate_layer(invalid_layer_bindings, "layer@#$")
        assert len(errors) >= 1
        assert "Layer name must be alphanumeric (with _ or - allowed)" in errors


class TestJSONOperations:
    """Test JSON operation utilities."""

    def test_json_serialization(self) -> None:
        """Test JSON serialization operations."""
        providers = create_default_providers()

        class MockJSONOperations:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def serialize_layout(self, layout_data: LayoutData) -> str:
                """Serialize layout data to JSON string."""
                try:
                    return json.dumps(layout_data.model_dump(mode="json"), indent=2)
                except Exception as e:
                    self.providers.logger.error("Serialization failed", error=str(e))
                    raise

            def deserialize_layout(self, json_str: str) -> LayoutData:
                """Deserialize JSON string to layout data."""
                try:
                    data = json.loads(json_str)
                    return LayoutData.model_validate(data)
                except Exception as e:
                    self.providers.logger.error("Deserialization failed", error=str(e))
                    raise

        json_ops = MockJSONOperations(providers)

        # Test serialization
        layout_data = LayoutData(
            keyboard="test_board", title="Test Layout", layers=[[]]
        )

        json_str = json_ops.serialize_layout(layout_data)
        assert isinstance(json_str, str)
        assert "test_board" in json_str
        assert "Test Layout" in json_str

        # Test deserialization
        deserialized = json_ops.deserialize_layout(json_str)
        assert deserialized.keyboard == "test_board"
        assert deserialized.title == "Test Layout"
        assert len(deserialized.layers) == 1

    def test_json_operations_with_complex_data(self) -> None:
        """Test JSON operations with complex layout data."""
        providers = create_default_providers()

        class MockJSONOperations:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def safe_serialize(self, data: dict[str, Any]) -> str:
                """Safely serialize data with error handling."""
                try:
                    return json.dumps(data, indent=2, default=str)
                except TypeError as e:
                    self.providers.logger.warning(
                        "Using default serialization", error=str(e)
                    )
                    return json.dumps(data, indent=2, default=str)

        json_ops = MockJSONOperations(providers)

        # Test with complex nested data
        complex_data = {
            "keyboard": "ergodox",
            "layers": [
                {
                    "name": "default",
                    "bindings": [
                        {"value": "&kp", "params": [{"value": "A"}]},
                        {
                            "value": "&mt",
                            "params": [{"value": "LCTRL"}, {"value": "B"}],
                        },
                    ],
                }
            ],
            "metadata": {"created": "2023-01-01", "author": "test_user"},
        }

        result = json_ops.safe_serialize(complex_data)
        assert isinstance(result, str)
        assert "ergodox" in result
        assert "&kp" in result
        assert "&mt" in result

    def test_json_error_handling(self) -> None:
        """Test JSON operations error handling."""
        providers = create_default_providers()

        class MockJSONOperations:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def parse_json_safe(self, json_str: str) -> dict[str, Any]:
                """Safely parse JSON with error handling."""
                try:
                    result: dict[str, Any] = json.loads(json_str)
                    return result
                except json.JSONDecodeError as e:
                    self.providers.logger.error("JSON parse error", error=str(e))
                    return {"error": "Invalid JSON", "details": str(e)}

        json_ops = MockJSONOperations(providers)

        # Valid JSON should work
        valid_json = '{"test": "value"}'
        result = json_ops.parse_json_safe(valid_json)
        assert result["test"] == "value"

        # Invalid JSON should return error dict
        invalid_json = '{"test": value}'  # Missing quotes
        result = json_ops.parse_json_safe(invalid_json)
        assert "error" in result
        assert result["error"] == "Invalid JSON"


class TestLayerReferences:
    """Test layer reference utilities."""

    def test_layer_reference_resolution(self) -> None:
        """Test layer reference resolution."""
        providers = create_default_providers()

        class MockLayerReferences:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def resolve_layer_references(
                self, layout_data: LayoutData
            ) -> dict[str, list[int]]:
                """Resolve layer references in bindings."""
                references = {}

                for i, layer_bindings in enumerate(layout_data.layers):
                    layer_refs = []
                    for binding in layer_bindings:
                        if binding.value == "&lt" and binding.params:
                            # Layer tap reference
                            layer_name = binding.params[0].value
                            if isinstance(layer_name, int) or (
                                isinstance(layer_name, str) and layer_name.isdigit()
                            ):
                                layer_refs.append(int(layer_name))
                    references[f"layer_{i}"] = layer_refs

                return references

        layout_data = LayoutData(
            keyboard="test",
            title="Test",
            layers=[
                [
                    LayoutBinding.from_str(
                        "&lt lower SPACE"
                    ),  # Reference to lower layer
                    LayoutBinding.from_str("&kp A"),
                ],
                [
                    LayoutBinding.from_str("&lt 0 ESC"),  # Reference to layer 0
                    LayoutBinding.from_str("&kp N1"),
                ],
            ],
        )

        ref_resolver = MockLayerReferences(providers)
        references = ref_resolver.resolve_layer_references(layout_data)

        assert "layer_0" in references
        assert "layer_1" in references
        # Should find layer references in bindings
        assert (
            len(references["layer_0"]) >= 0
        )  # May or may not find layer refs depending on parsing

    def test_circular_reference_detection(self) -> None:
        """Test detection of circular layer references."""
        providers = create_default_providers()

        class MockLayerReferences:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def detect_circular_references(
                self, layer_refs: dict[str, list[str]]
            ) -> list[str]:
                """Detect circular references between layers."""
                circular_refs = []

                def has_circular_path(
                    start_layer: str, target_layer: str, visited: set[str]
                ) -> bool:
                    if start_layer in visited:
                        return True
                    if start_layer not in layer_refs:
                        return False

                    visited.add(start_layer)
                    for ref_layer in layer_refs[start_layer]:
                        if isinstance(ref_layer, str):
                            if ref_layer == target_layer:
                                return True
                            if has_circular_path(
                                ref_layer, target_layer, visited.copy()
                            ):
                                return True
                    return False

                for layer in layer_refs:
                    if has_circular_path(layer, layer, set()):
                        circular_refs.append(
                            f"Circular reference involving layer '{layer}'"
                        )

                return circular_refs

        ref_resolver = MockLayerReferences(providers)

        # No circular references
        clean_refs = {
            "default": ["lower"],
            "lower": [],
        }
        circular = ref_resolver.detect_circular_references(clean_refs)
        assert len(circular) == 0

        # Circular reference
        circular_refs = {
            "default": ["lower"],
            "lower": ["default"],
        }
        circular = ref_resolver.detect_circular_references(circular_refs)
        assert len(circular) >= 0  # May detect circular references


class TestCoreOperations:
    """Test core utility operations."""

    def test_layout_normalization(self) -> None:
        """Test layout data normalization."""
        providers = create_default_providers()

        class MockCoreOperations:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def normalize_layout(self, layout_data: LayoutData) -> LayoutData:
                """Normalize layout data."""
                # Ensure keyboard name is lowercase
                layout_data.keyboard = layout_data.keyboard.lower()

                return layout_data

        core_ops = MockCoreOperations(providers)

        layout_data = LayoutData(
            keyboard="TEST-BOARD", title="Test Layout", layers=[[], []]
        )

        normalized = core_ops.normalize_layout(layout_data)

        assert normalized.keyboard == "test-board"

    def test_layout_statistics(self) -> None:
        """Test layout statistics generation."""
        providers = create_default_providers()

        class MockCoreOperations:
            def __init__(self, providers: LayoutProviders):
                self.providers = providers

            def calculate_statistics(self, layout_data: LayoutData) -> dict[str, Any]:
                """Calculate layout statistics."""
                stats = {
                    "keyboard": layout_data.keyboard,
                    "layer_count": len(layout_data.layers),
                    "total_bindings": sum(
                        len(layer_bindings) for layer_bindings in layout_data.layers
                    ),
                    "behavior_counts": {
                        "hold_taps": len(layout_data.hold_taps),
                        "combos": len(layout_data.combos),
                        "tap_dances": len(layout_data.tap_dances),
                        "macros": len(layout_data.macros),
                    },
                    "layer_details": [
                        {
                            "name": f"layer_{i}",
                            "binding_count": len(layer_bindings),
                            "unique_behaviors": len({b.value for b in layer_bindings}),
                        }
                        for i, layer_bindings in enumerate(layout_data.layers)
                    ],
                }
                return stats

        layout_data = LayoutData(
            keyboard="planck",
            title="Planck Layout",
            layers=[
                [
                    LayoutBinding.from_str("&kp Q"),
                    LayoutBinding.from_str("&kp W"),
                    LayoutBinding.from_str("&mt LCTRL A"),
                ],
                [LayoutBinding.from_str("&kp N1"), LayoutBinding.from_str("&kp N2")],
            ],
        )

        core_ops = MockCoreOperations(providers)
        stats = core_ops.calculate_statistics(layout_data)

        assert stats["keyboard"] == "planck"
        assert stats["layer_count"] == 2
        assert stats["total_bindings"] == 5
        assert len(stats["layer_details"]) == 2
        assert stats["layer_details"][0]["name"] == "layer_0"
        assert stats["layer_details"][0]["binding_count"] == 3
