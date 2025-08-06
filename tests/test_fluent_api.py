"""Integration tests for the fluent API specification."""

import tempfile
from pathlib import Path

import pytest

from zmk_layout import Layout
from zmk_layout.core.exceptions import LayerExistsError, LayerNotFoundError


class TestFluentAPISpecification:
    """Test the target API specification exactly as planned."""

    def test_target_api_specification(self) -> None:
        """Test the exact API from the plan: Layout().layers.add().set().save()"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_layout.json"

            # Target API: Layout().layers.add().set().save()
            layout = Layout.create_empty("test_keyboard", "Test Layout")
            result = (
                layout.layers.add("newlayer")
                .set(0, "&kp D")
                .pad_to(5, "&trans")  # Add some padding for a more complete test
            )

            # Verify the result is a LayerProxy that can be chained
            assert hasattr(result, "set")
            assert hasattr(result, "name")
            assert result.name == "newlayer"

            # Complete the chain and save
            saved_layout = layout.save(output_path)

            # Verify chainable - save returns Layout
            assert isinstance(saved_layout, Layout)
            assert saved_layout is layout  # Same instance

            # Verify the file was created and contains expected data
            assert output_path.exists()

            # Load and verify content
            loaded_layout = Layout.from_file(output_path)
            assert loaded_layout.data.keyboard == "test_keyboard"
            assert "newlayer" in loaded_layout.layers.names
            assert len(loaded_layout.layers.get("newlayer")) == 5
            assert loaded_layout.layers.get("newlayer").get(0).to_str() == "&kp D"

    def test_complete_fluent_workflow(self) -> None:
        """Test a complete fluent workflow with multiple operations."""
        layout = Layout.create_empty("crkbd", "Complete Test Layout")

        # Create a complete workflow
        layout.layers.add("base").set_range(0, 3, ["&kp Q", "&kp W", "&kp E"]).pad_to(
            42, "&trans"
        )
        layout.layers.add("gaming")

        # Add behaviors
        layout.behaviors.add_hold_tap("hm", "&kp A", "&mo 1", tapping_term_ms=200)
        layout.behaviors.add_combo("esc_combo", [0, 1], "&kp ESC", timeout_ms=50)
        layout.behaviors.add_macro(
            "hello", ["&kp H", "&kp E", "&kp L", "&kp L", "&kp O"]
        )

        # Verify the complete layout
        assert len(layout.layers.names) == 2
        assert "base" in layout.layers
        assert "gaming" in layout.layers
        assert layout.layers.get("base").size == 42
        assert layout.behaviors.hold_tap_count == 1
        assert layout.behaviors.combo_count == 1
        assert layout.behaviors.macro_count == 1

    def test_context_manager_support(self) -> None:
        """Test context manager functionality."""
        with Layout.create_empty("test", "Context Test") as layout:
            layout.layers.add("test_layer").set(0, "&kp A")
            assert "test_layer" in layout.layers

        # Layout should still be accessible after context
        assert "test_layer" in layout.layers

    def test_batch_operations(self) -> None:
        """Test batch operation functionality."""
        layout = Layout.create_empty("test", "Batch Test")

        # Define batch operations
        operations = [
            lambda layout: layout.layers.add("layer1"),
            lambda layout: layout.layers.add("layer2"),
            lambda layout: layout.layers.get("layer1").set(0, "&kp A"),
            lambda layout: layout.layers.get("layer2").set(0, "&kp B"),
            lambda layout: layout.behaviors.add_hold_tap("test_ht", "&kp C", "&mo 1"),
        ]

        # Execute batch
        result = layout.batch_operation(operations)

        # Verify chainable
        assert result is layout

        # Verify operations were executed
        assert len(layout.layers.names) == 2
        assert layout.layers.get("layer1").get(0).to_str() == "&kp A"
        assert layout.layers.get("layer2").get(0).to_str() == "&kp B"
        assert layout.behaviors.has_hold_tap("test_ht")

    def test_query_capabilities(self) -> None:
        """Test query and search functionality."""
        layout = Layout.create_empty("test", "Query Test")

        # Add multiple layers
        layout.layers.add_multiple(["base", "gaming", "programming", "gaming_pro"])

        # Test layer finding
        gaming_layers = layout.find_layers(lambda name: "gaming" in name)
        assert len(gaming_layers) == 2
        assert "gaming" in gaming_layers
        assert "gaming_pro" in gaming_layers

        # Test layer manager find
        prog_layers = layout.layers.find(lambda name: "prog" in name)
        assert len(prog_layers) == 1
        assert "programming" in prog_layers

    def test_statistics_and_introspection(self) -> None:
        """Test layout statistics and introspection."""
        layout = Layout.create_empty("test", "Stats Test")

        # Build a layout with data
        layout.layers.add("base").pad_to(10, "&trans")
        layout.layers.add("symbols").pad_to(5, "&kp A")
        layout.behaviors.add_hold_tap("hm1", "&kp A", "&mo 1")
        layout.behaviors.add_combo("combo1", [0, 1], "&kp ESC")

        # Get statistics
        stats = layout.get_statistics()

        # Verify statistics
        assert stats["keyboard"] == "test"
        assert stats["layer_count"] == 2
        assert stats["total_bindings"] == 15  # 10 + 5
        assert stats["behavior_counts"]["hold_taps"] == 1
        assert stats["behavior_counts"]["combos"] == 1
        assert stats["layer_sizes"]["base"] == 10
        assert stats["layer_sizes"]["symbols"] == 5
        assert stats["avg_layer_size"] == 7.5
        assert stats["max_layer_size"] == 10
        assert stats["min_layer_size"] == 5


class TestErrorHandling:
    """Test comprehensive error handling with clear messages."""

    def test_layer_not_found_error(self) -> None:
        """Test helpful layer not found errors."""
        layout = Layout.create_empty("test", "Error Test")
        layout.layers.add("existing_layer")

        with pytest.raises(LayerNotFoundError) as exc_info:
            layout.layers.get("nonexistent")

        error = exc_info.value
        assert "nonexistent" in str(error)
        assert "existing_layer" in str(error)  # Should suggest available layers
        assert error.layer_name == "nonexistent"
        assert "existing_layer" in error.details["available_layers"]

    def test_layer_exists_error(self) -> None:
        """Test layer already exists error."""
        layout = Layout.create_empty("test", "Error Test")
        layout.layers.add("existing_layer")

        with pytest.raises(LayerExistsError) as exc_info:
            layout.layers.add("existing_layer")

        error = exc_info.value
        assert "existing_layer" in str(error)
        assert "already exists" in str(error)
        assert error.layer_name == "existing_layer"

    def test_validation_errors_with_details(self) -> None:
        """Test validation errors provide helpful details."""
        layout = Layout.create_empty("", "Test")  # Empty keyboard name

        with pytest.raises(Exception) as exc_info:  # ValidationError
            layout.validate()

        # Error should mention missing keyboard name
        assert "Keyboard name is required" in str(exc_info.value)


class TestTypeHintsAndIDESupport:
    """Test that type hints work correctly for IDE support."""

    def test_return_types_for_chaining(self) -> None:
        """Test that return types support method chaining."""
        layout = Layout.create_empty("test", "Type Test")

        # These should all type-check correctly
        layer_manager_result = layout.layers.add("test")
        assert hasattr(layer_manager_result, "set")  # LayerProxy methods

        layer_proxy_result = layer_manager_result.set(0, "&kp A")
        assert hasattr(layer_proxy_result, "set")  # Still LayerProxy

        layout_result = layer_proxy_result.copy_from("test")
        assert hasattr(layout_result, "set")  # Still LayerProxy

        behavior_result = layout.behaviors.add_hold_tap("test", "&kp A", "&mo 1")
        assert hasattr(behavior_result, "add_combo")  # BehaviorManager methods

    def test_property_access_types(self) -> None:
        """Test property access returns correct types."""
        layout = Layout.create_empty("test", "Type Test")
        layout.layers.add("test").set(0, "&kp A")

        # Property access should return correct types
        layer_names = layout.layers.names
        assert isinstance(layer_names, list)
        assert all(isinstance(name, str) for name in layer_names)

        layer_count = layout.layers.count
        assert isinstance(layer_count, int)

        layer_proxy = layout.layers.get("test")
        binding = layer_proxy.get(0)
        assert hasattr(binding, "value")  # LayoutBinding


class TestPerformanceRequirements:
    """Test performance requirements are met."""

    def test_fluent_api_performance_overhead(self) -> None:
        """Test that fluent API has minimal performance overhead."""
        import time

        # Create a reasonably sized layout
        layout = Layout.create_empty("test", "Performance Test")

        # Time fluent operations
        start_time = time.time()

        for i in range(10):
            layer_name = f"layer_{i}"
            layout.layers.add(layer_name).pad_to(42, "&trans")

            # Add some behaviors
            layout.behaviors.add_hold_tap(f"ht_{i}", "&kp A", "&mo 1")
            layout.behaviors.add_combo(f"combo_{i}", [i, i + 1], "&kp ESC")

        # Save to measure serialization
        with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
            layout.save(tmp.name)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete well under 1 second for this size
        assert elapsed < 1.0, (
            f"Fluent API operations took {elapsed:.3f}s, expected <1.0s"
        )

    def test_memory_usage_reasonable(self) -> None:
        """Test that fluent API doesn't create excessive objects."""
        import gc

        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Create and manipulate layout
        layout = Layout.create_empty("test", "Memory Test")

        # Chain many operations to test object creation
        for i in range(50):
            layout.layers.add(f"layer_{i}")

        # Should not create excessive intermediate objects
        gc.collect()
        final_objects = len(gc.get_objects())

        # Allow reasonable object growth but not excessive
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, (
            f"Created {object_growth} objects, may indicate memory leak"
        )


class TestBackwardCompatibility:
    """Test that existing usage patterns still work."""

    def test_non_fluent_usage_still_works(self) -> None:
        """Test that non-fluent usage patterns still work."""
        layout = Layout.create_empty("test", "Compatibility Test")

        # Non-fluent style should work
        layout.layers.add("base")
        layer_proxy = layout.layers.get("base")
        layer_proxy.set(0, "&kp A")
        layer_proxy.set(1, "&kp B")

        # Verify it worked
        assert layout.layers.get("base").get(0).to_str() == "&kp A"
        assert layout.layers.get("base").get(1).to_str() == "&kp B"

    def test_direct_data_access_preserved(self) -> None:
        """Test that direct data access is preserved."""
        layout = Layout.create_empty("test", "Data Access Test")
        layout.layers.add("test").set(0, "&kp A")

        # Direct data access should work
        assert hasattr(layout, "data")
        assert layout.data.keyboard == "test"
        assert len(layout.data.layer_names) == 1
        assert "test" in layout.data.layer_names
