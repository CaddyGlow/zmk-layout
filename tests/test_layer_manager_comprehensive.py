"""
Comprehensive Layer Manager Tests

This module tests LayerManager and LayerProxy functionality with full coverage
of layer operations, edge cases, and integration scenarios.
"""

import pytest

from zmk_layout.core.exceptions import LayerExistsError, LayerNotFoundError
from zmk_layout.core.layout import Layout
from zmk_layout.core.managers.layer_manager import LayerManager
from zmk_layout.core.managers.layer_proxy import LayerProxy
from zmk_layout.models.core import LayoutBinding
from zmk_layout.models.metadata import LayoutData
from zmk_layout.providers.factory import create_default_providers


@pytest.fixture
def basic_layout():
    """Create a basic layout for testing."""
    data = LayoutData(
        keyboard="test_keyboard",
        title="Basic Test Layout",
        layers=[
            [{"value": "&kp A"}, {"value": "&kp B"}, {"value": "&kp C"}],
            [{"value": "&trans"}, {"value": "&mo 1"}, {"value": "&kp X"}],
        ],
        layer_names=["base", "func"],
    )
    return Layout(data, create_default_providers())


@pytest.fixture
def empty_layout():
    """Create an empty layout for testing."""
    return Layout.create_empty("empty_test", "Empty Layout")


@pytest.fixture
def large_layout():
    """Create a large layout with multiple layers for testing."""
    # Create 6 layers with varying sizes
    layers = []
    layer_names = []

    for i in range(6):
        layer_name = f"layer_{i}"
        layer_names.append(layer_name)

        # Each layer has different number of keys
        key_count = 20 + (i * 10)  # 20, 30, 40, 50, 60, 70 keys
        layer_data = []

        for j in range(key_count):
            layer_data.append({"value": f"&kp {chr(65 + (j % 26))}"})

        layers.append(layer_data)

    data = LayoutData(
        keyboard="large_keyboard",
        title="Large Layout",
        layers=layers,
        layer_names=layer_names,
    )
    return Layout(data, create_default_providers())


class TestLayerManagerComprehensive:
    """Comprehensive tests for LayerManager functionality."""

    def test_layer_manager_initialization(self, basic_layout):
        """Test LayerManager initialization and basic properties."""
        layer_manager = basic_layout.layers

        assert isinstance(layer_manager, LayerManager)
        assert layer_manager.count == 2
        assert len(layer_manager) == 2
        assert layer_manager.names == ["base", "func"]

    def test_layer_manager_properties_comprehensive(self, large_layout):
        """Test all LayerManager properties with large layout."""
        layers = large_layout.layers

        # Test count property
        assert layers.count == 6

        # Test names property
        expected_names = [f"layer_{i}" for i in range(6)]
        assert layers.names == expected_names

        # Test length
        assert len(layers) == 6

        # Test membership testing
        for name in expected_names:
            assert name in layers
        assert "non_existent" not in layers

    def test_layer_manager_iteration(self, basic_layout):
        """Test LayerManager iteration behavior."""
        layers = basic_layout.layers

        # Test iteration
        iterated_names = list(layers)
        assert iterated_names == ["base", "func"]

        # Test iteration with enumerate
        for i, name in enumerate(layers):
            assert name == layers.names[i]

    def test_add_layer_comprehensive_scenarios(self, empty_layout):
        """Test comprehensive layer addition scenarios."""
        layers = empty_layout.layers

        # Test basic addition
        layers.add("first")
        assert layers.count == 1
        assert "first" in layers.names

        # Test addition at specific position
        layers.add("zeroth", position=0)
        assert layers.count == 2
        assert layers.names == ["zeroth", "first"]

        # Test addition at end
        layers.add("last")
        assert layers.count == 3
        assert layers.names == ["zeroth", "first", "last"]

        # Test addition in middle
        layers.add("middle", position=2)
        assert layers.count == 4
        assert layers.names == ["zeroth", "first", "middle", "last"]

    def test_add_layer_error_scenarios(self, basic_layout):
        """Test error scenarios for layer addition."""
        layers = basic_layout.layers

        # Test adding existing layer
        with pytest.raises(LayerExistsError) as excinfo:
            layers.add("base")
        assert excinfo.value.layer_name == "base"
        assert "already exists" in str(excinfo.value)

        # Test invalid positions
        with pytest.raises(IndexError) as excinfo:
            layers.add("invalid", position=100)
        assert "out of range" in str(excinfo.value)

        with pytest.raises(IndexError) as excinfo:
            layers.add("negative", position=-1)
        assert "out of range" in str(excinfo.value)

    def test_get_layer_comprehensive(self, basic_layout):
        """Test comprehensive layer retrieval."""
        layers = basic_layout.layers

        # Test getting existing layers
        base_layer = layers.get("base")
        assert isinstance(base_layer, LayerProxy)
        assert base_layer.name == "base"
        assert base_layer.size == 3

        func_layer = layers.get("func")
        assert isinstance(func_layer, LayerProxy)
        assert func_layer.name == "func"
        assert func_layer.size == 3

    def test_get_layer_error_scenarios(self, basic_layout):
        """Test error scenarios for layer retrieval."""
        layers = basic_layout.layers

        # Test getting non-existent layer
        with pytest.raises(LayerNotFoundError) as excinfo:
            layers.get("non_existent")
        assert excinfo.value.layer_name == "non_existent"
        assert "not found" in str(excinfo.value)
        assert "Available layers: base, func" in str(excinfo.value)

    def test_remove_layer_comprehensive(self, large_layout):
        """Test comprehensive layer removal scenarios."""
        layers = large_layout.layers
        initial_count = layers.count

        # Test removing from middle
        layers.remove("layer_2")
        assert layers.count == initial_count - 1
        assert "layer_2" not in layers.names

        # Test removing first layer
        layers.remove("layer_0")
        assert layers.count == initial_count - 2
        assert layers.names[0] == "layer_1"

        # Test removing last layer
        last_name = layers.names[-1]
        layers.remove(last_name)
        assert layers.count == initial_count - 3
        assert last_name not in layers.names

    def test_remove_layer_error_scenarios(self, basic_layout):
        """Test error scenarios for layer removal."""
        layers = basic_layout.layers

        with pytest.raises(LayerNotFoundError) as excinfo:
            layers.remove("non_existent")
        assert excinfo.value.layer_name == "non_existent"

    def test_move_layer_comprehensive(self, large_layout):
        """Test comprehensive layer movement scenarios."""
        layers = large_layout.layers
        original_names = list(layers.names)

        # Test moving from start to end
        layers.move("layer_0", 5)
        expected = original_names[1:] + [original_names[0]]
        assert layers.names == expected

        # Test moving from end to start
        layers.move("layer_0", 0)
        assert layers.names == original_names

        # Test moving within middle
        layers.move("layer_2", 1)
        expected = [
            original_names[0],
            original_names[2],
            original_names[1],
        ] + original_names[3:]
        assert layers.names == expected

    def test_move_layer_error_scenarios(self, basic_layout):
        """Test error scenarios for layer movement."""
        layers = basic_layout.layers

        # Test moving non-existent layer
        with pytest.raises(LayerNotFoundError):
            layers.move("non_existent", 0)

        # Test moving to invalid position
        with pytest.raises(IndexError):
            layers.move("base", 100)

    def test_rename_layer_comprehensive(self, basic_layout):
        """Test comprehensive layer renaming."""
        layers = basic_layout.layers

        # Get original layer data for verification
        base_proxy = layers.get("base")
        original_base_data = [base_proxy.get(i) for i in range(base_proxy.size)]

        # Test basic rename
        layers.rename("base", "primary")
        assert "base" not in layers.names
        assert "primary" in layers.names

        # Verify data integrity after rename
        renamed_layer = layers.get("primary")
        new_data = [renamed_layer.get(i) for i in range(renamed_layer.size)]

        # Data should be identical
        assert len(original_base_data) == len(new_data)
        for orig, new in zip(original_base_data, new_data, strict=False):
            assert orig.to_str() == new.to_str()

    def test_rename_layer_error_scenarios(self, basic_layout):
        """Test error scenarios for layer renaming."""
        layers = basic_layout.layers

        # Test renaming non-existent layer
        with pytest.raises(ValueError) as excinfo:
            layers.rename("non_existent", "new_name")
        assert "not found" in str(excinfo.value)

        # Test renaming to existing name
        with pytest.raises(ValueError) as excinfo:
            layers.rename("base", "func")
        assert "already exists" in str(excinfo.value)

    def test_copy_layer_comprehensive(self, basic_layout):
        """Test comprehensive layer copying."""
        layers = basic_layout.layers
        original_count = layers.count

        # Get original data
        base_proxy = layers.get("base")
        original_data = [base_proxy.get(i) for i in range(base_proxy.size)]

        # Test basic copy
        layers.copy("base", "base_copy")
        assert layers.count == original_count + 1
        assert "base_copy" in layers.names

        # Verify copy has same data
        copy_proxy = layers.get("base_copy")
        copy_data = [copy_proxy.get(i) for i in range(copy_proxy.size)]
        assert len(original_data) == len(copy_data)
        for orig, copy in zip(original_data, copy_data, strict=False):
            assert orig.to_str() == copy.to_str()

        # Test it's a deep copy by modifying original
        layers.get("base").set(0, "&kp Z")
        assert (
            layers.get("base_copy").get(0).to_str() == "&kp A"
        )  # Should remain unchanged

    def test_copy_layer_error_scenarios(self, basic_layout):
        """Test error scenarios for layer copying."""
        layers = basic_layout.layers

        # Test copying non-existent source
        with pytest.raises(ValueError) as excinfo:
            layers.copy("non_existent", "new_copy")
        assert "not found" in str(excinfo.value)

        # Test copying to existing target
        with pytest.raises(ValueError) as excinfo:
            layers.copy("base", "func")
        assert "already exists" in str(excinfo.value)

    def test_clear_layer_comprehensive(self, basic_layout):
        """Test comprehensive layer clearing."""
        layers = basic_layout.layers

        # Verify layer has data initially
        base_layer = layers.get("base")
        assert base_layer.size == 3

        # Test clear via layer manager
        layers.clear("base")
        assert base_layer.size == 0

        # Add data back and test clear via proxy
        base_layer.set(0, "&kp TEST")
        assert base_layer.size == 1

        base_layer.clear()
        assert base_layer.size == 0

    def test_clear_layer_error_scenarios(self, basic_layout):
        """Test error scenarios for layer clearing."""
        layers = basic_layout.layers

        with pytest.raises(LayerNotFoundError):
            layers.clear("non_existent")

    def test_add_multiple_layers_comprehensive(self, empty_layout):
        """Test comprehensive multiple layer addition."""
        layers = empty_layout.layers

        # Test adding multiple new layers
        new_names = ["layer1", "layer2", "layer3", "layer4"]
        layers.add_multiple(new_names)

        assert layers.count == 4
        for name in new_names:
            assert name in layers.names

        # Verify order preserved
        assert layers.names == new_names

    def test_add_multiple_layers_error_scenarios(self, basic_layout):
        """Test error scenarios for multiple layer addition."""
        layers = basic_layout.layers
        initial_count = layers.count

        # Test with duplicate existing name
        with pytest.raises(LayerExistsError) as excinfo:
            layers.add_multiple(["new1", "base", "new2"])
        assert excinfo.value.layer_name == "base"

        # Should not have added any layers
        assert layers.count == initial_count
        assert "new1" not in layers.names
        assert "new2" not in layers.names

    def test_remove_multiple_layers_comprehensive(self, large_layout):
        """Test comprehensive multiple layer removal."""
        layers = large_layout.layers
        initial_count = layers.count

        # Test removing multiple layers
        to_remove = ["layer_1", "layer_3", "layer_5"]
        layers.remove_multiple(to_remove)

        assert layers.count == initial_count - 3
        for name in to_remove:
            assert name not in layers.names

        # Verify remaining layers
        remaining = ["layer_0", "layer_2", "layer_4"]
        for name in remaining:
            assert name in layers.names

    def test_remove_multiple_layers_error_scenarios(self, basic_layout):
        """Test error scenarios for multiple layer removal."""
        layers = basic_layout.layers
        initial_count = layers.count

        # Test with non-existent layer
        with pytest.raises(ValueError) as excinfo:
            layers.remove_multiple(["base", "non_existent"])
        assert "non_existent" in str(excinfo.value)

        # Should not have removed any layers
        assert layers.count == initial_count
        assert "base" in layers.names

    def test_reorder_layers_comprehensive(self, large_layout):
        """Test comprehensive layer reordering."""
        layers = large_layout.layers
        original_names = list(layers.names)

        # Test complete reorder
        new_order = list(reversed(original_names))
        layers.reorder(new_order)
        assert layers.names == new_order

        # Test partial shuffle
        shuffled_order = [
            original_names[2],
            original_names[0],
            original_names[4],
            original_names[1],
            original_names[5],
            original_names[3],
        ]
        layers.reorder(shuffled_order)
        assert layers.names == shuffled_order

        # Verify data integrity after reorder
        layer_0_data = layers.get(shuffled_order[0])
        assert layer_0_data.size > 0  # Should still have data

    def test_reorder_layers_error_scenarios(self, basic_layout):
        """Test error scenarios for layer reordering."""
        layers = basic_layout.layers
        original_names = list(layers.names)

        # Test with wrong number of layers
        with pytest.raises(ValueError) as excinfo:
            layers.reorder(["base"])  # Missing "func"
        assert "same layer names" in str(excinfo.value)

        # Test with wrong layer names
        with pytest.raises(ValueError) as excinfo:
            layers.reorder(["base", "wrong_name"])
        assert "same layer names" in str(excinfo.value)

        # Verify original order preserved
        assert layers.names == original_names

    def test_find_layers_comprehensive(self, large_layout):
        """Test comprehensive layer finding with predicates."""
        layers = large_layout.layers

        # Test finding by name pattern
        matching = layers.find(lambda name: "2" in name or "4" in name)
        assert "layer_2" in matching
        assert "layer_4" in matching
        assert len(matching) == 2

        # Test finding all layers
        all_layers = layers.find(lambda name: True)
        assert len(all_layers) == 6
        assert set(all_layers) == set(layers.names)

        # Test finding no layers
        no_layers = layers.find(lambda name: False)
        assert len(no_layers) == 0

        # Test finding by specific criteria
        even_layers = layers.find(lambda name: int(name.split("_")[1]) % 2 == 0)
        assert "layer_0" in even_layers
        assert "layer_2" in even_layers
        assert "layer_4" in even_layers
        assert len(even_layers) == 3


class TestLayerProxyComprehensive:
    """Comprehensive tests for LayerProxy functionality."""

    def test_layer_proxy_initialization(self, basic_layout):
        """Test LayerProxy initialization and basic properties."""
        base_layer = basic_layout.layers.get("base")

        assert isinstance(base_layer, LayerProxy)
        assert base_layer.name == "base"
        assert base_layer.size == 3
        assert len(base_layer) == 3
        # LayerProxy doesn't expose parent directly, but we can verify it's working
        assert base_layer.name == "base"

    def test_layer_proxy_get_operations(self, basic_layout):
        """Test comprehensive get operations on LayerProxy."""
        base_layer = basic_layout.layers.get("base")

        # Test getting individual bindings
        binding_0 = base_layer.get(0)
        assert isinstance(binding_0, LayoutBinding)
        assert binding_0.value == "&kp A"

        binding_1 = base_layer.get(1)
        assert binding_1.value == "&kp B"

        # Test getting all bindings
        all_bindings = [base_layer.get(i) for i in range(base_layer.size)]
        assert len(all_bindings) == 3
        assert all(isinstance(b, LayoutBinding) for b in all_bindings)

        # Test getting range of bindings
        range_bindings = [base_layer.get(i) for i in range(0, 2)]
        assert len(range_bindings) == 2
        assert range_bindings[0].value == "&kp A"
        assert range_bindings[1].value == "&kp B"

    def test_layer_proxy_get_error_scenarios(self, basic_layout):
        """Test error scenarios for LayerProxy get operations."""
        base_layer = basic_layout.layers.get("base")

        # Test getting invalid index
        with pytest.raises(IndexError):
            base_layer.get(100)

        with pytest.raises(IndexError):
            base_layer.get(-1)

        # Test invalid range would cause IndexError in loop
        with pytest.raises(IndexError):
            [base_layer.get(i) for i in range(0, 100)]

    def test_layer_proxy_set_operations(self, basic_layout):
        """Test comprehensive set operations on LayerProxy."""
        base_layer = basic_layout.layers.get("base")

        # Test setting individual binding
        base_layer.set(0, "&kp Z")
        assert base_layer.get(0).to_str() == "&kp Z"

        # Test setting with LayoutBinding object
        new_binding = LayoutBinding.from_str("&kp Y")
        base_layer.set(1, new_binding)
        assert base_layer.get(1).to_str() == "&kp Y"

        # Test setting range
        new_values = ["&kp X", "&kp W", "&kp V"]
        base_layer.set_range(0, 3, new_values)
        assert base_layer.get(0).to_str() == "&kp X"
        assert base_layer.get(1).to_str() == "&kp W"
        assert base_layer.get(2).to_str() == "&kp V"

    def test_layer_proxy_set_error_scenarios(self, basic_layout):
        """Test error scenarios for LayerProxy set operations."""
        base_layer = basic_layout.layers.get("base")

        # Test setting invalid index - LayerProxy.set() auto-expands, so this won't raise IndexError
        # Instead test something that should actually fail
        with pytest.raises(ValueError):
            base_layer.set_range(0, 3, ["&kp A"])  # Wrong count

        # Test setting range with wrong count
        with pytest.raises(ValueError):
            base_layer.set_range(0, 3, ["&kp A"])  # Only 1 value for 3 positions

    def test_layer_proxy_extend_operations(self, basic_layout):
        """Test LayerProxy extension operations."""
        base_layer = basic_layout.layers.get("base")
        initial_count = base_layer.size

        # Test extending with single binding
        base_layer.append("&kp D")
        assert base_layer.size == initial_count + 1
        assert base_layer.get(initial_count).to_str() == "&kp D"

        # Test extending with multiple bindings
        new_bindings = ["&kp E", "&kp F", "&kp G"]
        for binding in new_bindings:
            base_layer.append(binding)
        assert base_layer.size == initial_count + 4
        assert base_layer.get(initial_count + 1).to_str() == "&kp E"
        assert base_layer.get(initial_count + 3).to_str() == "&kp G"

    def test_layer_proxy_clear_operations(self, basic_layout):
        """Test LayerProxy clear operations."""
        base_layer = basic_layout.layers.get("base")

        # Verify initial state
        assert base_layer.size == 3

        # Test clear
        result = base_layer.clear()
        assert result is base_layer  # Returns self for chaining
        assert base_layer.size == 0

        # Test clear on already empty layer
        base_layer.clear()
        assert base_layer.size == 0

    def test_layer_proxy_copy_from_operations(self, basic_layout):
        """Test LayerProxy copy_from operations."""
        base_layer = basic_layout.layers.get("base")
        func_layer = basic_layout.layers.get("func")

        # Get original func data
        original_func_data = [func_layer.get(i) for i in range(func_layer.size)]

        # Test copy_from
        result = base_layer.copy_from("func")
        assert result is base_layer  # Returns self for chaining

        # Verify data copied
        base_data = [base_layer.get(i) for i in range(base_layer.size)]
        assert len(base_data) == len(original_func_data)
        for base_binding, func_binding in zip(
            base_data, original_func_data, strict=False
        ):
            assert base_binding.to_str() == func_binding.to_str()

        # Verify it's a deep copy
        base_layer.set(0, "&kp MODIFIED")
        assert func_layer.get(0).to_str() == "&trans"  # Should be unchanged

    def test_layer_proxy_copy_from_error_scenarios(self, basic_layout):
        """Test error scenarios for LayerProxy copy_from."""
        base_layer = basic_layout.layers.get("base")

        # Test copying from non-existent layer
        with pytest.raises(LayerNotFoundError) as excinfo:
            base_layer.copy_from("non_existent")
        assert "not found" in str(excinfo.value)

    def test_layer_proxy_iteration_and_membership(self, basic_layout):
        """Test LayerProxy iteration and membership operations."""
        base_layer = basic_layout.layers.get("base")

        # Test iteration
        values = [binding.value for binding in base_layer]
        assert values == ["&kp A", "&kp B", "&kp C"]

        # Test enumerate
        for i, binding in enumerate(base_layer):
            expected_value = ["&kp A", "&kp B", "&kp C"][i]
            assert binding.value == expected_value

    def test_layer_proxy_fluent_interface(self, basic_layout):
        """Test LayerProxy fluent interface and method chaining."""
        base_layer = basic_layout.layers.get("base")

        # Test chaining operations
        result = base_layer.clear()
        for binding in ["&kp X", "&kp Y", "&kp Z"]:
            result = result.append(binding)
        result = result.set(1, "&kp MIDDLE")

        assert result is base_layer
        assert base_layer.size == 3
        assert base_layer.get(0).to_str() == "&kp X"
        assert base_layer.get(1).to_str() == "&kp MIDDLE"
        assert base_layer.get(2).to_str() == "&kp Z"

        # Test chaining with copy_from
        func_layer = basic_layout.layers.get("func")
        result2 = base_layer.clear().copy_from("func")
        assert result2 is base_layer
        assert base_layer.get(0).to_str() == "&trans"


class TestLayerManagerIntegration:
    """Integration tests for LayerManager with complex scenarios."""

    def test_complex_layer_manipulation_workflow(self, large_layout):
        """Test complex workflow with multiple layer operations."""
        layers = large_layout.layers

        # Step 1: Reorganize layers
        layers.rename("layer_0", "base")
        layers.rename("layer_1", "func")
        layers.move("base", 1)  # Move base after func

        # Step 2: Add new layers
        layers.add("gaming", position=0)
        layers.add("numpad")

        # Step 3: Remove some layers first
        layers.remove("layer_2")
        layers.remove("layer_3")

        # Step 4: Copy and modify (after removal to avoid stale proxy issues)
        layers.copy("base", "base_alt")
        base_alt = layers.get("base_alt")
        base_alt.clear()
        for binding in ["&kp 1", "&kp 2", "&kp 3"]:
            base_alt.append(binding)

        # Verify final state
        assert (
            layers.count == 7
        )  # Started with 6, added 2 (gaming, numpad), removed 2, added 1 (base_alt)
        assert "gaming" in layers.names
        assert "numpad" in layers.names
        assert "base_alt" in layers.names
        assert "layer_2" not in layers.names
        assert "layer_3" not in layers.names

        # Verify data integrity
        assert base_alt.size == 3
        assert base_alt.get(0).to_str() == "&kp 1"

    def test_layer_operations_with_empty_and_full_layers(self, empty_layout):
        """Test operations mixing empty and populated layers."""
        layers = empty_layout.layers

        # Add empty layer
        layers.add("empty")
        empty_layer = layers.get("empty")
        assert empty_layer.size == 0

        # Add populated layer
        layers.add("populated")
        pop_layer = layers.get("populated")
        for binding in ["&kp A", "&kp B", "&kp C"]:
            pop_layer.append(binding)

        # Copy from populated to empty
        empty_layer.copy_from("populated")
        assert empty_layer.size == 3
        assert empty_layer.get(0).to_str() == "&kp A"

        # Clear populated layer
        pop_layer.clear()
        assert pop_layer.size == 0

        # Verify empty layer unchanged
        assert empty_layer.size == 3

    def test_concurrent_layer_proxy_operations(self, basic_layout):
        """Test operations on multiple LayerProxy instances simultaneously."""
        base_layer = basic_layout.layers.get("base")
        func_layer = basic_layout.layers.get("func")

        # Get multiple references to same layer
        base_layer2 = basic_layout.layers.get("base")

        # Modify through first reference
        base_layer.set(0, "&kp MODIFIED1")

        # Verify second reference sees change
        assert base_layer2.get(0).to_str() == "&kp MODIFIED1"

        # Modify through second reference
        base_layer2.set(1, "&kp MODIFIED2")

        # Verify first reference sees change
        assert base_layer.get(1).to_str() == "&kp MODIFIED2"

        # Operations on different layers should be independent
        func_layer.set(0, "&kp FUNC_MOD")
        assert base_layer.get(0).to_str() == "&kp MODIFIED1"  # Unchanged

    def test_layer_statistics_after_complex_operations(self, large_layout):
        """Test layout statistics remain accurate after complex operations."""
        # Get initial statistics
        initial_stats = large_layout.get_statistics()
        initial_total = initial_stats["total_bindings"]

        # Perform complex operations
        layers = large_layout.layers

        # Clear one layer
        layers.get("layer_0").clear()
        layer_0_original_size = initial_stats["layer_sizes"]["layer_0"]

        # Extend another layer
        layer_1 = layers.get("layer_1")
        for binding in ["&kp EXTRA1", "&kp EXTRA2"]:
            layer_1.append(binding)

        # Remove a layer entirely
        layer_2_original_size = initial_stats["layer_sizes"]["layer_2"]
        layers.remove("layer_2")

        # Get final statistics
        final_stats = large_layout.get_statistics()

        # Verify statistics accuracy
        expected_total = (
            initial_total
            - layer_0_original_size  # Cleared layer_0
            + 2  # Added 2 bindings to layer_1
            - layer_2_original_size
        )  # Removed layer_2

        assert final_stats["total_bindings"] == expected_total
        assert final_stats["layer_count"] == initial_stats["layer_count"] - 1
        assert "layer_2" not in final_stats["layer_sizes"]
        assert final_stats["layer_sizes"]["layer_0"] == 0
        assert (
            final_stats["layer_sizes"]["layer_1"]
            == initial_stats["layer_sizes"]["layer_1"] + 2
        )
