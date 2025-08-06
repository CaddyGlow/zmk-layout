"""Tests for ValidationPipeline with immutable state management."""

import pytest

from zmk_layout.core import Layout
from zmk_layout.models.core import LayoutBinding
from zmk_layout.validation import (
    ValidationError,
    ValidationPipeline,
    ValidationState,
    ValidationSummary,
    ValidationWarning,
)


class TestValidationPipeline:
    """Test suite for ValidationPipeline."""

    def test_initial_state(self) -> None:
        """Test initial validation state."""
        layout = Layout.create_empty("test", "Test Layout")
        validator = ValidationPipeline(layout)
        
        assert validator.is_valid()
        assert len(validator.collect_errors()) == 0
        assert len(validator.collect_warnings()) == 0

    def test_validate_bindings_invalid_syntax(self) -> None:
        """Test validation of invalid binding syntax."""
        layout = Layout.create_empty("test", "Test Layout")
        # Manually create an invalid binding
        from zmk_layout.models.core import LayoutBinding
        invalid_binding = LayoutBinding(value="kp", params=[])  # Missing & prefix
        layer = layout.layers.add("base")
        layer.bindings.append(invalid_binding)
        
        validator = ValidationPipeline(layout)
        result = validator.validate_bindings()
        
        assert not result.is_valid()
        errors = result.collect_errors()
        assert len(errors) >= 1  # May have both syntax and unknown behavior errors
        assert "Invalid binding syntax" in errors[0].message
        assert errors[0].context["layer"] == "base"
        assert errors[0].context["position"] == 0

    def test_validate_bindings_valid(self) -> None:
        """Test validation of valid bindings."""
        layout = Layout.create_empty("test", "Test Layout")
        layer = layout.layers.add("base")
        layer.set(0, "&kp A")
        layer.set(1, "&mt LCTRL ESC")
        layer.set(2, "&trans")
        
        validator = ValidationPipeline(layout)
        result = validator.validate_bindings()
        
        assert result.is_valid()
        assert len(result.collect_errors()) == 0

    def test_validate_layer_references_out_of_bounds(self) -> None:
        """Test validation of out-of-bounds layer references."""
        layout = Layout.create_empty("test", "Test Layout")
        layout.layers.add("base").set(0, "&mo 5")  # Only 1 layer exists
        
        validator = ValidationPipeline(layout)
        result = validator.validate_layer_references()
        
        assert not result.is_valid()
        errors = result.collect_errors()
        assert len(errors) >= 1  # May have both syntax and unknown behavior errors
        assert "Layer reference out of bounds" in errors[0].message
        assert errors[0].context["reference"] == 5

    def test_validate_layer_references_valid(self) -> None:
        """Test validation of valid layer references."""
        layout = Layout.create_empty("test", "Test Layout")
        layout.layers.add("base").set(0, "&mo 1")
        layout.layers.add("nav").set(0, "&to 0")
        
        validator = ValidationPipeline(layout)
        result = validator.validate_layer_references()
        
        assert result.is_valid()
        assert len(result.collect_errors()) == 0

    def test_validate_layer_references_string(self) -> None:
        """Test validation of string layer references."""
        layout = Layout.create_empty("test", "Test Layout")
        layout.layers.add("base").set(0, "&mo nav")  # String reference
        layout.layers.add("nav")
        
        validator = ValidationPipeline(layout)
        result = validator.validate_layer_references()
        
        assert result.is_valid()
        assert len(result.collect_errors()) == 0

    def test_validate_layer_references_unknown_string(self) -> None:
        """Test validation of unknown string layer references."""
        layout = Layout.create_empty("test", "Test Layout")
        layout.layers.add("base").set(0, "&mo unknown_layer")
        
        validator = ValidationPipeline(layout)
        result = validator.validate_layer_references()
        
        assert not result.is_valid()
        errors = result.collect_errors()
        assert len(errors) >= 1  # May have both syntax and unknown behavior errors
        assert "Unknown layer reference" in errors[0].message

    def test_validate_key_positions_warning(self) -> None:
        """Test key position validation warnings."""
        layout = Layout.create_empty("test", "Test Layout")
        layer = layout.layers.add("base")
        
        # Add more than max_keys bindings
        for i in range(45):
            layer.set(i, "&trans")
        
        validator = ValidationPipeline(layout)
        result = validator.validate_key_positions(max_keys=42)
        
        assert result.is_valid()  # Warnings don't invalidate
        warnings = result.collect_warnings()
        assert len(warnings) == 1
        assert "more than recommended" in warnings[0].message
        assert warnings[0].context["count"] == 45

    def test_validate_key_positions_error(self) -> None:
        """Test key position validation errors for extreme counts."""
        layout = Layout.create_empty("test", "Test Layout")
        layer = layout.layers.add("base")
        
        # Add way too many bindings
        for i in range(250):
            layer.set(i, "&trans")
        
        validator = ValidationPipeline(layout)
        result = validator.validate_key_positions()
        
        assert not result.is_valid()
        errors = result.collect_errors()
        assert len(errors) >= 1  # May have both syntax and unknown behavior errors
        assert "unusually high key count" in errors[0].message

    def test_validate_behavior_references(self) -> None:
        """Test custom behavior reference validation."""
        layout = Layout.create_empty("test", "Test Layout")
        layer = layout.layers.add("base")
        layer.set(0, "&hm_l LCTRL A")  # Custom hold-tap
        layer.set(1, "&hrm_r RSHIFT B")  # Custom hold-tap
        
        validator = ValidationPipeline(layout)
        result = validator.validate_behavior_references()
        
        assert result.is_valid()  # Just warnings for now
        warnings = result.collect_warnings()
        assert len(warnings) == 1
        assert "custom behavior references" in warnings[0].message
        assert "&hm_l" in warnings[0].context["behaviors"]

    def test_immutability(self) -> None:
        """Test that validation steps return new instances."""
        layout = Layout.create_empty("test", "Test Layout")
        validator1 = ValidationPipeline(layout)
        validator2 = validator1.validate_bindings()
        validator3 = validator2.validate_layer_references()
        
        # Each should be a different instance
        assert validator1 is not validator2
        assert validator2 is not validator3
        
        # Original should have no errors
        assert len(validator1.collect_errors()) == 0
        
        # Each step accumulates state
        assert validator1._state is not validator2._state
        assert validator2._state is not validator3._state

    def test_chained_validation(self) -> None:
        """Test chaining multiple validation steps."""
        layout = Layout.create_empty("test", "Test Layout")
        layer = layout.layers.add("base")
        # Manually create an invalid binding
        from zmk_layout.models.core import LayoutBinding
        layer.bindings.append(LayoutBinding(value="kp", params=[]))  # Invalid syntax
        layer.set(1, "&mo 5")  # Invalid layer reference
        
        validator = ValidationPipeline(layout)
        result = (
            validator
            .validate_bindings()
            .validate_layer_references()
            .validate_key_positions(max_keys=10)
        )
        
        assert not result.is_valid()
        errors = result.collect_errors()
        # We expect at least 3 errors: syntax + unknown behavior for "kp", and layer reference for "&mo 5"
        assert len(errors) >= 3

    def test_validation_summary(self) -> None:
        """Test validation summary generation."""
        layout = Layout.create_empty("test", "Test Layout")
        layer = layout.layers.add("base")
        # Manually create an invalid binding
        from zmk_layout.models.core import LayoutBinding
        layer.bindings.append(LayoutBinding(value="invalid", params=[]))  # Error
        
        # Add many keys for warning
        for i in range(50):
            layer.set(i + 1, "&trans")
        
        validator = ValidationPipeline(layout)
        result = validator.validate_bindings().validate_key_positions(max_keys=42)
        
        summary = result.summary()
        assert isinstance(summary, ValidationSummary)
        assert not summary.is_valid
        # We expect at least 1 error (could be 2: syntax + unknown behavior)
        assert len(summary.errors) >= 1
        assert len(summary.warnings) == 1

    def test_validation_state_namedtuple(self) -> None:
        """Test ValidationState as immutable NamedTuple."""
        state = ValidationState(errors=(), warnings=())
        
        # NamedTuple is immutable
        with pytest.raises(AttributeError):
            state.errors = ()  # type: ignore
        
        # Can create new state with updated values
        error = ValidationError("Test error")
        new_state = ValidationState(
            errors=state.errors + (error,),
            warnings=state.warnings,
        )
        
        assert len(new_state.errors) == 1
        assert len(state.errors) == 0  # Original unchanged

    def test_repr(self) -> None:
        """Test string representation."""
        layout = Layout.create_empty("test", "Test Layout")
        validator = ValidationPipeline(layout)
        
        repr_str = repr(validator)
        assert "ValidationPipeline" in repr_str
        assert "errors=0" in repr_str
        assert "warnings=0" in repr_str
        assert "valid=True" in repr_str

    def test_error_context(self) -> None:
        """Test that errors include helpful context."""
        layout = Layout.create_empty("test", "Test Layout")
        from zmk_layout.models.core import LayoutBinding
        layer = layout.layers.add("base")
        layer.bindings.append(LayoutBinding(value="invalid", params=[]))
        
        validator = ValidationPipeline(layout)
        result = validator.validate_bindings()
        
        errors = result.collect_errors()
        
        # Check that we have errors with context
        assert len(errors) >= 1
        for error in errors:
            assert error.context is not None
            assert "layer" in error.context
            assert "position" in error.context
            assert "binding" in error.context

    def test_validate_combo_positions(self) -> None:
        """Test combo position validation."""
        layout = Layout.create_empty("test", "Test Layout")
        layer = layout.layers.add("base")
        
        # Add 10 keys to the layer
        for i in range(10):
            layer.set(i, "&kp A")
        
        # Add combo with valid positions
        if hasattr(layout, "combos"):
            layout.combos.add("test_combo", key_positions=[0, 1], binding="&kp ESC")
            
            validator = ValidationPipeline(layout)
            result = validator.validate_combo_positions()
            
            assert result.is_valid()
            assert len(result.collect_errors()) == 0

    def test_complex_validation_scenario(self) -> None:
        """Test a complex validation scenario with multiple issues."""
        layout = Layout.create_empty("test", "Test Layout")
        from zmk_layout.models.core import LayoutBinding
        
        # Layer 1: base
        base = layout.layers.add("base")
        base.set(0, "&kp A")  # Valid
        base.bindings.append(LayoutBinding(value="invalid", params=[]))  # Invalid syntax
        base.set(2, "&mo 3")  # Invalid layer ref
        
        # Layer 2: nav
        nav = layout.layers.add("nav")
        nav.set(0, "&to 0")  # Valid
        nav.bindings.append(LayoutBinding(value="&unknown_behavior", params=[]))  # Unknown behavior
        
        # Add many keys for warning
        for i in range(50):
            nav.set(i + 2, "&trans")
        
        # Run full validation
        validator = ValidationPipeline(layout)
        result = (
            validator
            .validate_bindings()
            .validate_layer_references()
            .validate_key_positions(max_keys=42)
            .validate_behavior_references()
        )
        
        # Check results
        assert not result.is_valid()
        
        errors = result.collect_errors()
        assert len(errors) >= 3  # At least 3 errors
        
        warnings = result.collect_warnings()
        assert len(warnings) >= 1  # At least 1 warning
        
        # Verify summary
        summary = result.summary()
        assert not summary.is_valid
        assert len(summary.errors) == len(errors)
        assert len(summary.warnings) == len(warnings)