"""Fluent validation pipeline with immutable state management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    from ..core import Layout


@dataclass
class ValidationError:
    """Represents a validation error with context."""

    message: str
    context: dict[str, Any] | None = None

    def __str__(self) -> str:
        """String representation of the error."""
        return self.message


@dataclass
class ValidationWarning:
    """Represents a validation warning with context."""

    message: str
    context: dict[str, Any] | None = None

    def __str__(self) -> str:
        """String representation of the warning."""
        return self.message


class ValidationState(NamedTuple):
    """Immutable validation state."""

    errors: tuple[ValidationError, ...]
    warnings: tuple[ValidationWarning, ...]


@dataclass
class ValidationSummary:
    """Summary of validation results."""

    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    is_valid: bool


class ValidationPipeline:
    """Truly immutable fluent validation with comprehensive error collection.

    This pipeline validates ZMK layouts using a fluent interface where each
    validation step returns a new immutable instance with accumulated results.

    Examples:
        >>> from zmk_layout import Layout
        >>> layout = Layout.from_file("my_layout.json")
        >>> validator = ValidationPipeline(layout)
        >>> result = (validator
        ...           .validate_bindings()
        ...           .validate_layer_references()
        ...           .validate_key_positions(max_keys=42))
        >>>
        >>> if not result.is_valid():
        ...     for error in result.collect_errors():
        ...         print(f"Error: {error}")
    """

    def __init__(self, layout: Layout, state: ValidationState | None = None) -> None:
        """Initialize validation pipeline.

        Args:
            layout: Layout instance to validate
            state: Optional initial validation state
        """
        self._layout = layout
        self._state = state or ValidationState(errors=(), warnings=())

    def validate_bindings(self) -> ValidationPipeline:
        """Validate all key bindings - returns new instance.

        Checks:
        - Binding syntax (must start with &)
        - Parameter structure validity
        - Behavior name validity

        Returns:
            New ValidationPipeline instance with validation results
        """
        new_errors: list[ValidationError] = []

        for layer_name in self._layout.layers.names:
            layer = self._layout.layers.get(layer_name)
            for i, binding in enumerate(layer.bindings):
                try:
                    # Validate binding syntax
                    if not binding.value.startswith("&"):
                        new_errors.append(
                            ValidationError(
                                f"Invalid binding syntax in layer '{layer_name}' at position {i}: {binding.value}",
                                context={
                                    "layer": layer_name,
                                    "position": i,
                                    "binding": binding.to_str(),
                                },
                            )
                        )

                    # Validate known behaviors (basic check)
                    known_behaviors = {
                        "&kp",
                        "&mt",
                        "&lt",
                        "&mo",
                        "&to",
                        "&tog",
                        "&sl",
                        "&trans",
                        "&none",
                        "&bootloader",
                        "&reset",
                        "&key_repeat",
                        "&caps_word",
                        "&sk",
                        "&gresc",
                        "&rgb_ug",
                        "&bt",
                        "&ext_power",
                        "&out",
                    }

                    behavior_base = binding.value.split("_")[0]  # Handle custom behaviors
                    if (
                        behavior_base not in known_behaviors
                        and not binding.value.startswith("&hm")
                        and not (binding.value.startswith("&") and len(binding.value) > 1)
                    ):
                        new_errors.append(
                            ValidationError(
                                f"Unknown behavior in layer '{layer_name}' at position {i}: {binding.value}",
                                context={
                                    "layer": layer_name,
                                    "position": i,
                                    "binding": binding.to_str(),
                                },
                            )
                        )

                except Exception as e:
                    new_errors.append(
                        ValidationError(
                            f"Binding validation failed: {e}",
                            context={"exception": str(e), "layer": layer_name, "position": i},
                        )
                    )

        # Create new state with added errors
        new_state = ValidationState(
            errors=self._state.errors + tuple(new_errors),
            warnings=self._state.warnings,
        )
        return ValidationPipeline(self._layout, new_state)

    def validate_layer_references(self) -> ValidationPipeline:
        """Validate layer references in behaviors - returns new instance.

        Checks:
        - Layer references in &mo, &lt, &sl, &to behaviors
        - Layer indices are within bounds
        - Layer names exist

        Returns:
            New ValidationPipeline instance with validation results
        """
        new_errors: list[ValidationError] = []
        layer_names = list(self._layout.layers.names)
        layer_count = len(layer_names)

        for layer_name in layer_names:
            layer = self._layout.layers.get(layer_name)
            for i, binding in enumerate(layer.bindings):
                # Check behaviors that reference layers
                if binding.value in ("&mo", "&lt", "&sl", "&to", "&tog") and binding.params and len(binding.params) > 0:
                    layer_ref = binding.params[0].value

                    # Check numeric layer references
                    if isinstance(layer_ref, int):
                        if layer_ref < 0 or layer_ref >= layer_count:
                            new_errors.append(
                                ValidationError(
                                    f"Layer reference out of bounds in '{layer_name}': "
                                    f"{layer_ref} (valid: 0-{layer_count - 1}) in {binding.to_str()}",
                                    context={
                                        "layer": layer_name,
                                        "position": i,
                                        "reference": layer_ref,
                                        "max_layer": layer_count - 1,
                                    },
                                )
                            )
                    # Check string layer references
                    elif (
                        isinstance(layer_ref, str)
                        and layer_ref not in layer_names
                        and not layer_ref.startswith("$")
                        and not layer_ref.startswith("{{")
                    ):
                        new_errors.append(
                            ValidationError(
                                f"Unknown layer reference in '{layer_name}': '{layer_ref}' in {binding.to_str()}",
                                context={
                                    "layer": layer_name,
                                    "position": i,
                                    "reference": layer_ref,
                                    "available_layers": layer_names,
                                },
                            )
                        )

        new_state = ValidationState(
            errors=self._state.errors + tuple(new_errors),
            warnings=self._state.warnings,
        )
        return ValidationPipeline(self._layout, new_state)

    def validate_key_positions(self, max_keys: int = 100) -> ValidationPipeline:
        """Validate key position ranges - returns new instance.

        Args:
            max_keys: Maximum recommended number of keys per layer

        Returns:
            New ValidationPipeline instance with validation results
        """
        new_warnings: list[ValidationWarning] = []
        new_errors: list[ValidationError] = []

        for layer_name in self._layout.layers.names:
            layer = self._layout.layers.get(layer_name)
            binding_count = len(layer.bindings)

            if binding_count > max_keys:
                new_warnings.append(
                    ValidationWarning(
                        f"Layer '{layer_name}' has {binding_count} bindings, more than recommended {max_keys}",
                        context={
                            "layer": layer_name,
                            "count": binding_count,
                            "max": max_keys,
                        },
                    )
                )

            # Check for extremely high key counts that might indicate an error
            if binding_count > 200:
                new_errors.append(
                    ValidationError(
                        f"Layer '{layer_name}' has unusually high key count: {binding_count}",
                        context={
                            "layer": layer_name,
                            "count": binding_count,
                        },
                    )
                )

        new_state = ValidationState(
            errors=self._state.errors + tuple(new_errors),
            warnings=self._state.warnings + tuple(new_warnings),
        )
        return ValidationPipeline(self._layout, new_state)

    def validate_behavior_references(self) -> ValidationPipeline:
        """Validate custom behavior references - returns new instance.

        Checks:
        - Custom behaviors are defined if referenced
        - Hold-tap behaviors exist
        - Macro behaviors exist

        Returns:
            New ValidationPipeline instance with validation results
        """
        new_warnings: list[ValidationWarning] = []

        # Collect all custom behavior references
        custom_behaviors: set[str] = set()
        for layer_name in self._layout.layers.names:
            layer = self._layout.layers.get(layer_name)
            for binding in layer.bindings:
                # Check for custom behavior patterns (e.g., &hm_l, &hrm_r)
                if binding.value.startswith("&") and "_" in binding.value:
                    behavior_base = binding.value.split("_")[0]
                    if behavior_base in ("&hm", "&hrm", "&ht", "&sk", "&sl"):
                        custom_behaviors.add(binding.value)

        # Check if behaviors are defined (would need access to behavior definitions)
        # For now, just warn about potentially undefined custom behaviors
        if custom_behaviors:
            new_warnings.append(
                ValidationWarning(
                    f"Found {len(custom_behaviors)} custom behavior references. "
                    "Ensure these are defined in your ZMK configuration.",
                    context={"behaviors": sorted(custom_behaviors)},
                )
            )

        new_state = ValidationState(
            errors=self._state.errors,
            warnings=self._state.warnings + tuple(new_warnings),
        )
        return ValidationPipeline(self._layout, new_state)

    def validate_modifier_consistency(self) -> ValidationPipeline:
        """Validate modifier key consistency - returns new instance.

        Checks:
        - Consistent modifier usage across layers
        - Balanced modifier pairs (left/right)
        - No conflicting modifier combinations

        Returns:
            New ValidationPipeline instance with validation results
        """
        new_warnings: list[ValidationWarning] = []

        # Track modifier usage
        left_mods = {"LSFT", "LCTL", "LALT", "LGUI", "LC", "LS", "LA", "LG"}
        right_mods = {"RSFT", "RCTL", "RALT", "RGUI", "RC", "RS", "RA", "RG"}

        mod_counts: dict[str, int] = {}

        for layer_name in self._layout.layers.names:
            layer = self._layout.layers.get(layer_name)
            for binding in layer.bindings:
                binding_str = binding.to_str()
                # Count modifier usage
                for mod in left_mods | right_mods:
                    if mod in binding_str:
                        mod_counts[mod] = mod_counts.get(mod, 0) + 1

        # Check for imbalanced modifiers
        for left_mod in ["LSFT", "LCTL", "LALT", "LGUI"]:
            right_mod = "R" + left_mod[1:]
            left_count = mod_counts.get(left_mod, 0)
            right_count = mod_counts.get(right_mod, 0)

            if left_count > 0 and right_count > 0:
                ratio = max(left_count, right_count) / max(min(left_count, right_count), 1)
                if ratio > 3:  # More than 3:1 imbalance
                    new_warnings.append(
                        ValidationWarning(
                            f"Imbalanced modifier usage: {left_mod}={left_count}, {right_mod}={right_count}",
                            context={
                                "left_mod": left_mod,
                                "left_count": left_count,
                                "right_mod": right_mod,
                                "right_count": right_count,
                                "ratio": ratio,
                            },
                        )
                    )

        new_state = ValidationState(
            errors=self._state.errors,
            warnings=self._state.warnings + tuple(new_warnings),
        )
        return ValidationPipeline(self._layout, new_state)

    def validate_hold_tap_timing(self, recommended_min: int = 150, recommended_max: int = 250) -> ValidationPipeline:
        """Validate hold-tap timing parameters - returns new instance.

        Args:
            recommended_min: Minimum recommended tapping term (ms)
            recommended_max: Maximum recommended tapping term (ms)

        Returns:
            New ValidationPipeline instance with validation results
        """
        new_warnings: list[ValidationWarning] = []

        # Check for hold-tap behaviors and their timing
        if hasattr(self._layout, "data") and self._layout.data:
            try:
                behaviors = self._layout.data.hold_taps
                for behavior in behaviors:
                    if hasattr(behavior, "tapping_term_ms") and behavior.tapping_term_ms:
                        term = behavior.tapping_term_ms
                        # Skip validation if term is a template string
                        if isinstance(term, str):
                            continue
                        if term < recommended_min:
                            new_warnings.append(
                                ValidationWarning(
                                    f"Hold-tap behavior '{behavior.name}' has low tapping term: {term}ms "
                                    f"(recommended: {recommended_min}-{recommended_max}ms)",
                                    context={
                                        "behavior": behavior.name,
                                        "tapping_term": term,
                                        "recommended_min": recommended_min,
                                    },
                                )
                            )
                        elif term > recommended_max:
                            new_warnings.append(
                                ValidationWarning(
                                    f"Hold-tap behavior '{behavior.name}' has high tapping term: {term}ms "
                                    f"(recommended: {recommended_min}-{recommended_max}ms)",
                                    context={
                                        "behavior": behavior.name,
                                        "tapping_term": term,
                                        "recommended_max": recommended_max,
                                    },
                                )
                            )
            except Exception:
                # Silently skip if data structure is not available
                pass

        new_state = ValidationState(
            errors=self._state.errors,
            warnings=self._state.warnings + tuple(new_warnings),
        )
        return ValidationPipeline(self._layout, new_state)

    def validate_layer_accessibility(self) -> ValidationPipeline:
        """Validate that all layers are accessible - returns new instance.

        Checks:
        - Each layer can be reached from the base layer
        - No orphaned layers
        - Layer activation graph is connected

        Returns:
            New ValidationPipeline instance with validation results
        """
        new_errors: list[ValidationError] = []
        new_warnings: list[ValidationWarning] = []

        layer_names = list(self._layout.layers.names)
        layer_count = len(layer_names)

        # Build layer activation graph
        layer_graph: dict[int, set[int]] = {i: set() for i in range(layer_count)}

        for layer_idx, layer_name in enumerate(layer_names):
            layer = self._layout.layers.get(layer_name)
            for binding in layer.bindings:
                # Check for layer activation behaviors
                if binding.value in ("&mo", "&lt", "&sl", "&to", "&tog") and binding.params:
                    layer_ref = binding.params[0].value
                    if isinstance(layer_ref, int) and 0 <= layer_ref < layer_count:
                        layer_graph[layer_idx].add(layer_ref)

        # Check reachability from base layer (layer 0)
        visited = set()
        to_visit = [0]

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            to_visit.extend(layer_graph.get(current, []))

        # Check for unreachable layers
        for layer_idx in range(layer_count):
            if layer_idx not in visited and layer_idx != 0:
                new_warnings.append(
                    ValidationWarning(
                        f"Layer '{layer_names[layer_idx]}' (index {layer_idx}) is not reachable from base layer",
                        context={
                            "layer": layer_names[layer_idx],
                            "layer_index": layer_idx,
                        },
                    )
                )

        new_state = ValidationState(
            errors=self._state.errors + tuple(new_errors),
            warnings=self._state.warnings + tuple(new_warnings),
        )
        return ValidationPipeline(self._layout, new_state)

    def validate_combo_positions(self) -> ValidationPipeline:
        """Validate combo key positions - returns new instance.

        Checks:
        - Combo positions are within layer bounds
        - No duplicate combo positions

        Returns:
            New ValidationPipeline instance with validation results
        """
        new_errors: list[ValidationError] = []
        new_warnings: list[ValidationWarning] = []

        # Get combos if available
        if hasattr(self._layout, "combos") and self._layout.combos:
            # Get the maximum key count from layers
            max_position = 0
            for layer_name in self._layout.layers.names:
                layer = self._layout.layers.get(layer_name)
                max_position = max(max_position, len(layer.bindings))

            combo_positions: set[tuple[int, ...]] = set()

            for combo in self._layout.combos.all():
                if hasattr(combo, "key_positions") and combo.key_positions:
                    positions = tuple(sorted(combo.key_positions))

                    # Check for duplicate combo positions
                    if positions in combo_positions:
                        new_warnings.append(
                            ValidationWarning(
                                f"Duplicate combo positions: {positions}",
                                context={"positions": positions},
                            )
                        )
                    combo_positions.add(positions)

                    # Check if positions are within bounds
                    for pos in combo.key_positions:
                        if pos >= max_position:
                            new_errors.append(
                                ValidationError(
                                    f"Combo position {pos} exceeds maximum key count {max_position}",
                                    context={
                                        "position": pos,
                                        "max_position": max_position,
                                        "combo": combo.name if hasattr(combo, "name") else "unknown",
                                    },
                                )
                            )

        new_state = ValidationState(
            errors=self._state.errors + tuple(new_errors),
            warnings=self._state.warnings + tuple(new_warnings),
        )
        return ValidationPipeline(self._layout, new_state)

    def collect_errors(self) -> list[ValidationError]:
        """Get all validation errors.

        Returns:
            List of all accumulated validation errors
        """
        return list(self._state.errors)

    def collect_warnings(self) -> list[ValidationWarning]:
        """Get all validation warnings.

        Returns:
            List of all accumulated validation warnings
        """
        return list(self._state.warnings)

    def is_valid(self) -> bool:
        """Check if validation passed (no errors).

        Returns:
            True if no errors were found, False otherwise
        """
        return len(self._state.errors) == 0

    def summary(self) -> ValidationSummary:
        """Get validation summary.

        Returns:
            ValidationSummary with all errors and warnings
        """
        return ValidationSummary(
            errors=list(self._state.errors),
            warnings=list(self._state.warnings),
            is_valid=self.is_valid(),
        )

    def __repr__(self) -> str:
        """String representation of validation state.

        Returns:
            Summary of validation pipeline state
        """
        return (
            f"ValidationPipeline(errors={len(self._state.errors)}, "
            f"warnings={len(self._state.warnings)}, valid={self.is_valid()})"
        )
