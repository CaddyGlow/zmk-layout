"""ZMK file content generation for keyboard layouts and behaviors."""

import logging
import re
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from zmk_layout.models.behaviors import (
    ComboBehavior,
    HoldTapBehavior,
    InputListener,
    MacroBehavior,
    SystemBehavior,
    TapDanceBehavior,
)
from zmk_layout.models.core import LayerBindings


# Real formatter implementations for ZMK behavior and layout formatting

if TYPE_CHECKING:
    from zmk_layout.models.metadata import LayoutData
    from zmk_layout.providers import (
        ConfigurationProvider,
        LayoutLogger,
        TemplateProvider,
    )

# Type aliases for external dependencies that need to be extracted
KeyboardProfile = Any


class BehaviorRegistry:
    """Registry for tracking and validating behaviors."""

    def __init__(self) -> None:
        """Initialize the behavior registry."""
        self._behaviors: dict[str, Any] = {}

    def register_behavior(self, behavior: Any) -> None:
        """Register a behavior for tracking and validation.

        Args:
            behavior: Behavior to register (SystemBehavior or similar)
        """
        if hasattr(behavior, "code") and hasattr(behavior, "name"):
            self._behaviors[behavior.code] = behavior
        elif hasattr(behavior, "name"):
            self._behaviors[behavior.name] = behavior

    def get_behavior(self, code: str) -> Any | None:
        """Get a registered behavior by code.

        Args:
            code: Behavior code to lookup

        Returns:
            Behavior if found, None otherwise
        """
        return self._behaviors.get(code)

    def is_registered(self, code: str) -> bool:
        """Check if a behavior is registered.

        Args:
            code: Behavior code to check

        Returns:
            True if behavior is registered
        """
        return code in self._behaviors

    def get_all_behaviors(self) -> dict[str, Any]:
        """Get all registered behaviors.

        Returns:
            Dictionary of all registered behaviors
        """
        return self._behaviors.copy()


class BehaviorFormatter:
    """Formatter for ZMK behavior bindings."""

    def __init__(self) -> None:
        """Initialize the behavior formatter."""
        self._behavior_reference_context = False

    def set_behavior_reference_context(self, enabled: bool) -> None:
        """Set whether we're formatting behavior references (for hold-tap bindings).

        Args:
            enabled: True if formatting behavior references, False for normal bindings
        """
        self._behavior_reference_context = enabled

    def format_binding(self, binding: Any) -> str:
        """Format a binding into proper ZMK syntax.

        Args:
            binding: LayoutBinding instance or string to format

        Returns:
            Formatted ZMK binding string like "&kp A", "&mt LCTRL SPACE"
        """
        # Handle string inputs (for compatibility)
        if isinstance(binding, str):
            return binding

        # Handle LayoutBinding objects
        if hasattr(binding, "value") and hasattr(binding, "params"):
            behavior = binding.value
            params = binding.params

            # Format parameters
            param_strings = []
            for param in params:
                param_strings.append(self._format_param(param))

            # Combine behavior with parameters
            if param_strings:
                return f"{behavior} {' '.join(param_strings)}"
            else:
                return str(behavior)

        # Fallback to string representation
        if hasattr(binding, "value"):
            return str(binding.value)
        return str(binding)

    def _format_param(self, param: Any) -> str:
        """Format a single parameter (LayoutParam).

        Args:
            param: LayoutParam instance to format

        Returns:
            Formatted parameter string
        """
        if not hasattr(param, "value"):
            return str(param)

        value = str(param.value)

        # Handle nested parameters (like modifier chains)
        if hasattr(param, "params") and param.params:
            nested_params = []
            for nested_param in param.params:
                nested_params.append(self._format_param(nested_param))

            if nested_params:
                return f"{value}({','.join(nested_params)})"

        return value


class LayoutFormatter:
    """Formatter for keyboard layout grids."""

    def __init__(self) -> None:
        """Initialize the layout formatter."""
        pass

    def generate_layer_layout(
        self,
        layer_data: Any,
        profile: Any = None,
        base_indent: str = "            ",
        **kwargs: Any,
    ) -> str:
        """Generate formatted layout grid for a layer's bindings.

        Args:
            layer_data: Layer bindings (list of strings) or layer object with bindings
            profile: Optional keyboard profile for layout-specific formatting
            base_indent: Base indentation for grid lines
            **kwargs: Additional formatting options

        Returns:
            Formatted grid string with proper indentation and spacing
        """
        # Extract bindings from various input formats
        bindings = []

        if isinstance(layer_data, list):
            bindings = layer_data
        elif hasattr(layer_data, "bindings"):
            bindings = layer_data.bindings
        else:
            return str(layer_data)

        if not bindings:
            return f"{base_indent}// Empty layer"

        # Determine grid layout based on keyboard profile or binding count
        rows, cols = self._determine_grid_layout(len(bindings), profile)

        # Format bindings into grid
        grid_lines = []

        for row in range(rows):
            row_bindings = []

            for col in range(cols):
                index = row * cols + col
                if index < len(bindings):
                    binding_str = str(bindings[index])
                    # Pad bindings for alignment
                    row_bindings.append(f"{binding_str:<12}")
                else:
                    # Fill incomplete rows with padding
                    row_bindings.append("            ")

            # Join row bindings with proper spacing
            row_line = f"{base_indent}{' '.join(row_bindings).rstrip()}"
            grid_lines.append(row_line)

        return "\n".join(grid_lines)

    def _determine_grid_layout(
        self, binding_count: int, profile: Any = None
    ) -> tuple[int, int]:
        """Determine the grid layout (rows, cols) for the given binding count.

        Args:
            binding_count: Number of key bindings
            profile: Optional keyboard profile with layout info

        Returns:
            Tuple of (rows, cols)
        """
        # Common keyboard layouts
        if binding_count == 42:  # Corne 3x6+3
            return (
                4,
                12,
            )  # 3 main rows + 1 thumb row, but format as 4x12 for simplicity
        elif binding_count == 36:  # Planck/similar
            return (3, 12)
        elif binding_count == 58:  # Lily58
            return (4, 15)  # Approximate
        elif binding_count == 60:  # Standard 60%
            return (5, 12)
        elif binding_count == 104:  # Full-size
            return (6, 18)
        else:
            # Default: try to make a reasonable rectangular grid
            rows = max(3, int((binding_count**0.5) * 0.7))  # Favor wider layouts
            cols = (binding_count + rows - 1) // rows  # Ceiling division
            return (rows, cols)


class ZMKGenerator:
    """Generator for complete ZMK file content from layout data."""

    def __init__(
        self,
        configuration_provider: "ConfigurationProvider | None" = None,
        template_provider: "TemplateProvider | None" = None,
        logger: "LayoutLogger | None" = None,
    ) -> None:
        """Initialize with provider dependencies.

        Args:
            configuration_provider: Provider for configuration data
            template_provider: Provider for template processing
            logger: Logger for structured logging
        """
        self.configuration_provider = configuration_provider
        self.template_provider = template_provider
        self.logger = logger or logging.getLogger(__name__)

        # Use real implementations for formatters
        self._behavior_formatter = BehaviorFormatter()
        self._behavior_registry = BehaviorRegistry()
        self._layout_formatter = LayoutFormatter()

    def generate_layer_defines(
        self, profile: KeyboardProfile, layer_names: list[str]
    ) -> str:
        """Generate #define statements for layers.

        Args:
            profile: Keyboard profile containing configuration
            layer_names: List of layer names

        Returns:
            String with #define statements for each layer
        """
        defines = []
        layer_define_pattern = profile.keyboard_config.zmk.patterns.layer_define
        for i, name in enumerate(layer_names):
            define_name = re.sub(r"\W|^(?=\d)", "_", name)
            define_line = layer_define_pattern.format(
                layer_name=define_name, layer_index=i
            )
            defines.append(define_line)
        return "\n".join(defines)

    def generate_behaviors_dtsi(
        self, profile: KeyboardProfile, hold_taps_data: Sequence[HoldTapBehavior]
    ) -> str:
        """Generate ZMK behaviors node string from hold-tap behavior models.

        Args:
            profile: Keyboard profile containing configuration
            hold_taps_data: List of hold-tap behavior models

        Returns:
            DTSI behaviors node content as string
        """
        if not hold_taps_data:
            return ""

        # Extract key position map from profile for use with hold-tap positions
        key_position_map = {}
        # Build a default key position map if needed
        for i in range(profile.keyboard_config.key_count):
            key_position_map[f"KEY_{i}"] = i

        dtsi_parts = []

        for ht in hold_taps_data:
            name = ht.name
            if not name:
                if self.logger:
                    self.logger.warning(
                        "Skipping hold-tap behavior with missing 'name'."
                    )
                continue

            node_name = name[1:] if name.startswith("&") else name
            bindings = ht.bindings
            tapping_term = ht.tapping_term_ms
            flavor = ht.flavor
            quick_tap = ht.quick_tap_ms
            require_idle = ht.require_prior_idle_ms
            hold_on_release = ht.hold_trigger_on_release
            hold_key_positions_indices = ht.hold_trigger_key_positions

            required_bindings = (
                profile.keyboard_config.zmk.validation_limits.required_holdtap_bindings
            )
            if len(bindings) != required_bindings:
                if self.logger:
                    self.logger.warning(
                        f"Behavior '{name}' requires exactly {required_bindings} bindings (hold, tap). "
                        f"Found {len(bindings)}. Skipping."
                    )
                continue

            # Register the behavior (placeholder - requires behavior registry)
            if self._behavior_registry:
                self._behavior_registry.register_behavior(
                    SystemBehavior(
                        code=ht.name,
                        name=ht.name,
                        description=ht.description,
                        expected_params=2,
                        origin="user_hold_tap",
                        params=[],
                    )
                )

            label = (ht.description or node_name).split("\n")
            label = [f"// {line}" for line in label]

            dtsi_parts.extend(label)
            dtsi_parts.append(f"{node_name}: {node_name} {{")
            compatible_string = profile.keyboard_config.zmk.compatible_strings.hold_tap
            dtsi_parts.append(f'    compatible = "{compatible_string}";')
            dtsi_parts.append("    #binding-cells = <2>;")

            if tapping_term is not None:
                dtsi_parts.append(f"    tapping-term-ms = <{tapping_term}>;")

            # Format bindings - placeholder implementation
            formatted_bindings = []
            if self._behavior_formatter:
                # Set context flag for hold-tap binding formatting
                self._behavior_formatter.set_behavior_reference_context(True)
                try:
                    for binding_ref in bindings:
                        # bindings are now strings, just use as-is (e.g., "&kp", "&lt")
                        formatted_bindings.append(binding_ref)
                finally:
                    # Always reset context flag
                    self._behavior_formatter.set_behavior_reference_context(False)
            else:
                # Fallback: use bindings as-is
                formatted_bindings = list(bindings)

            if len(formatted_bindings) == required_bindings:
                if required_bindings == 2:
                    dtsi_parts.append(
                        f"    bindings = <{formatted_bindings[0]}>, <{formatted_bindings[1]}>;"
                    )
                else:
                    # Handle other cases if required_bindings is configurable to other values
                    bindings_str = ", ".join(f"<{b}>" for b in formatted_bindings)
                    dtsi_parts.append(f"    bindings = {bindings_str};")
            else:
                # Generate error placeholders based on required count
                error_bindings = ", ".join("<&error>" for _ in range(required_bindings))
                dtsi_parts.append(f"    bindings = {error_bindings};")

            if flavor is not None:
                allowed_flavors = profile.keyboard_config.zmk.hold_tap_flavors
                if flavor in allowed_flavors:
                    dtsi_parts.append(f'    flavor = "{flavor}";')
                else:
                    if self.logger:
                        self.logger.warning(
                            f"Invalid flavor '{flavor}' for behavior '{name}'. Allowed: {allowed_flavors}. Omitting."
                        )

            if quick_tap is not None:
                dtsi_parts.append(f"    quick-tap-ms = <{quick_tap}>;")

            if require_idle is not None:
                dtsi_parts.append(f"    require-prior-idle-ms = <{require_idle}>;")

            if (
                hold_key_positions_indices is not None
                and len(hold_key_positions_indices) > 0
            ):
                pos_numbers = [str(idx) for idx in hold_key_positions_indices]
                dtsi_parts.append(
                    f"    hold-trigger-key-positions = <{' '.join(pos_numbers)}>;"
                )

            if hold_on_release:
                dtsi_parts.append("    hold-trigger-on-release;")

            if ht.retro_tap:
                dtsi_parts.append("    retro-tap;")

            dtsi_parts.append("};")
            dtsi_parts.append("")

        # Remove last blank line if present
        if dtsi_parts:
            dtsi_parts.pop()
        return "\n".join(self._indent_array(dtsi_parts, " " * 8))

    def generate_tap_dances_dtsi(
        self, profile: KeyboardProfile, tap_dances_data: Sequence[TapDanceBehavior]
    ) -> str:
        """Generate ZMK tap dance behaviors from tap dance behavior models.

        Args:
            profile: Keyboard profile containing configuration
            tap_dances_data: List of tap dance behavior models

        Returns:
            DTSI behaviors node content as string
        """
        if not tap_dances_data:
            return ""

        dtsi_parts = []
        valid_tap_dances = []

        for td in tap_dances_data:
            name = td.name
            if not name:
                if self.logger:
                    self.logger.warning("Skipping tap-dance with missing name")
                continue

            description = td.description or ""
            tapping_term = td.tapping_term_ms
            bindings = td.bindings

            if not bindings or len(bindings) < 2:
                if self.logger:
                    self.logger.warning(
                        f"Tap dance '{name}' requires at least 2 bindings, found {len(bindings) if bindings else 0}. Skipping."
                    )
                continue

            # This is a valid tap dance, add it to our list
            valid_tap_dances.append(td)

        # If no valid tap dances, return empty string
        if not valid_tap_dances:
            return ""

        dtsi_parts.append("behaviors {")

        for td in valid_tap_dances:
            name = td.name
            description = td.description or ""
            tapping_term = td.tapping_term_ms
            bindings = td.bindings

            # Register the tap dance behavior (placeholder)
            if self._behavior_registry:
                self._behavior_registry.register_behavior(
                    SystemBehavior(
                        code=td.name,
                        name=td.name,
                        description=td.description,
                        expected_params=0,  # Tap dances typically take 0 params
                        origin="user_tap_dance",
                        params=[],
                    )
                )

            # Add description as comment
            if description:
                comment_lines = description.split("\n")
                for line in comment_lines:
                    dtsi_parts.append(f"    // {line}")

            dtsi_parts.append(f"    {name}: {name} {{")
            compatible_string = "zmk,behavior-tap-dance"
            dtsi_parts.append(f'        compatible = "{compatible_string}";')

            if description:
                dtsi_parts.append(f'        label = "{description}";')

            dtsi_parts.append("        #binding-cells = <0>;")

            if tapping_term is not None:
                dtsi_parts.append(f"        tapping-term-ms = <{tapping_term}>;")

            # Format bindings
            if bindings:
                formatted_bindings = []
                for binding in bindings:
                    # Format the binding to DTSI format
                    if self._behavior_formatter:
                        binding_str = self._behavior_formatter.format_binding(binding)
                    else:
                        binding_str = str(binding)  # Fallback
                    formatted_bindings.append(f"<{binding_str}>")

                bindings_line = ", ".join(formatted_bindings)
                dtsi_parts.append(f"        bindings = {bindings_line};")

            dtsi_parts.append("    };")
            dtsi_parts.append("")

        # Remove last empty line if present (before adding closing brace)
        if len(dtsi_parts) > 1 and dtsi_parts[-1] == "":
            dtsi_parts.pop()
        dtsi_parts.append("};")

        # Remove any trailing empty line at the very end
        if dtsi_parts and dtsi_parts[-2] == "":
            dtsi_parts.pop(-2)

        return "\n".join(dtsi_parts)

    def generate_macros_dtsi(
        self, profile: KeyboardProfile, macros_data: Sequence[MacroBehavior]
    ) -> str:
        """Generate ZMK macros node string from macro behavior models.

        Args:
            profile: Keyboard profile containing configuration
            macros_data: List of macro behavior models

        Returns:
            DTSI macros node content as string
        """
        if not macros_data:
            return ""

        dtsi_parts: list[str] = []

        for macro in macros_data:
            name = macro.name
            if not name:
                if self.logger:
                    self.logger.warning("Skipping macro with missing name")
                continue

            node_name = name[1:] if name.startswith("&") else name
            description = (macro.description or node_name).split("\n")
            description = [f"// {line}" for line in description]

            bindings = macro.bindings
            params = macro.params or []
            wait_ms = macro.wait_ms
            tap_ms = macro.tap_ms

            # Check for empty bindings
            if not bindings:
                if self.logger:
                    self.logger.warning(f"Macro '{name}' has no bindings. Skipping.")
                continue

            # Set compatible string and binding-cells based on macro parameters
            compatible_strings = profile.keyboard_config.zmk.compatible_strings

            if not params:
                compatible = compatible_strings.macro
                binding_cells = "0"
            elif len(params) == 1:
                compatible = compatible_strings.macro_one_param
                binding_cells = "1"
            elif len(params) == 2:
                compatible = compatible_strings.macro_two_param
                binding_cells = "2"
            else:
                max_params = (
                    profile.keyboard_config.zmk.validation_limits.max_macro_params
                )
                if self.logger:
                    self.logger.warning(
                        f"Macro '{name}' has {len(params)} params, not supported. Max: {max_params}."
                    )
                continue
            # Register the macro behavior (placeholder)
            if self._behavior_registry:
                self._behavior_registry.register_behavior(
                    SystemBehavior(
                        code=macro.name,
                        name=macro.name,
                        description=macro.description,
                        expected_params=2,
                        origin="user_macro",
                        params=[],
                    )
                )

            macro_parts = []

            if description:
                macro_parts.extend(description)
            macro_parts.append(f"{node_name}: {node_name} {{")
            macro_parts.append(f'    label = "{name.upper()}";')
            macro_parts.append(f'    compatible = "{compatible}";')
            macro_parts.append(f"    #binding-cells = <{binding_cells}>;")
            if tap_ms is not None:
                macro_parts.append(f"    tap-ms = <{tap_ms}>;")
            if wait_ms is not None:
                macro_parts.append(f"    wait-ms = <{wait_ms}>;")
            if bindings:
                if self._behavior_formatter:
                    bindings_str = "\n                , ".join(
                        f"<{self._behavior_formatter.format_binding(b)}>"
                        for b in bindings
                    )
                else:
                    bindings_str = "\n                , ".join(
                        f"<{str(b)}>" for b in bindings
                    )
                macro_parts.append(f"    bindings = {bindings_str};")
            macro_parts.append("};")
            dtsi_parts.extend(self._indent_array(macro_parts, "        "))
            dtsi_parts.append("")

        # Remove last blank line if present
        if dtsi_parts:
            dtsi_parts.pop()
        return "\n".join(dtsi_parts)

    def generate_combos_dtsi(
        self,
        profile: KeyboardProfile,
        combos_data: Sequence[ComboBehavior],
        layer_names: list[str],
    ) -> str:
        """Generate ZMK combos node string from combo behavior models.

        Args:
            profile: Keyboard profile containing configuration
            combos_data: List of combo behavior models
            layer_names: List of layer names

        Returns:
            DTSI combos node content as string
        """
        if not combos_data:
            return ""

        # Extract key position map from profile for use with combo positions
        key_position_map = {}
        # Build a default key position map if needed
        for i in range(profile.keyboard_config.key_count):
            key_position_map[f"KEY_{i}"] = i

        # First, collect all valid combos
        valid_combos = []

        for combo in combos_data:
            name = combo.name
            if not name:
                if self.logger:
                    self.logger.warning("Skipping combo with missing name")
                continue

            binding_data = combo.binding
            key_positions_indices = combo.key_positions

            if not binding_data or not key_positions_indices:
                if self.logger:
                    self.logger.warning(
                        f"Combo '{name}' is missing binding or keyPositions. Skipping."
                    )
                continue

            # Check for empty bindings like &none
            if (
                binding_data
                and hasattr(binding_data, "value")
                and binding_data.value in ["&none"]
            ):
                if self.logger:
                    self.logger.warning(f"Combo '{name}' has no bindings. Skipping.")
                continue

            # Check key position count
            if len(key_positions_indices) < 2:
                if self.logger:
                    self.logger.warning(
                        f"Combo '{name}' requires at least 2 key positions, found {len(key_positions_indices)}. Skipping."
                    )
                continue

            # This combo is valid, add it to our list
            valid_combos.append(combo)

        # If no valid combos, return empty string
        if not valid_combos:
            return ""

        # Generate DTSI structure for valid combos
        dtsi_parts = ["combos {"]
        combos_compatible = profile.keyboard_config.zmk.compatible_strings.combos
        dtsi_parts.append(f'    compatible = "{combos_compatible}";')

        for combo in valid_combos:
            name = combo.name
            node_name = re.sub(r"\W|^(?=\d)", "_", name)
            binding_data = combo.binding
            key_positions_indices = combo.key_positions
            timeout = combo.timeout_ms
            layers_spec = combo.layers

            description_lines = (combo.description or node_name).split("\n")
            label = "\n".join([f"    // {line}" for line in description_lines])

            dtsi_parts.append(f"{label}")
            dtsi_parts.append(f"    combo_{node_name} {{")

            if timeout is not None:
                dtsi_parts.append(f"        timeout-ms = <{timeout}>;")

            key_pos_defines = [
                str(key_position_map.get(str(idx), idx))
                for idx in key_positions_indices
            ]
            dtsi_parts.append(f"        key-positions = <{' '.join(key_pos_defines)}>;")

            if self._behavior_formatter:
                formatted_binding = self._behavior_formatter.format_binding(
                    binding_data
                )
            else:
                formatted_binding = str(binding_data)  # Fallback
            dtsi_parts.append(f"        bindings = <{formatted_binding}>;")

            # Format layers
            if layers_spec and layers_spec != [-1]:
                combo_layer_indices = []
                for layer_id in layers_spec:
                    # Use layer index directly instead of define statement
                    if layer_id < len(layer_names):
                        combo_layer_indices.append(str(layer_id))
                    else:
                        if self.logger:
                            self.logger.warning(
                                f"Combo '{name}' specifies unknown layer '{layer_id}'. Ignoring this layer."
                            )

                if combo_layer_indices:
                    dtsi_parts.append(
                        f"        layers = <{' '.join(combo_layer_indices)}>;"
                    )

            dtsi_parts.append("    };")
            dtsi_parts.append("")

        # Remove last blank line if present
        if dtsi_parts and dtsi_parts[-1] == "":
            dtsi_parts.pop()
        dtsi_parts.append("};")
        return "\n".join(self._indent_array(dtsi_parts))

    def generate_input_listeners_node(
        self, profile: KeyboardProfile, input_listeners_data: Sequence[InputListener]
    ) -> str:
        """Generate input listener nodes string from input listener models.

        Args:
            profile: Keyboard profile containing configuration
            input_listeners_data: List of input listener models

        Returns:
            DTSI input listeners node content as string
        """
        if not input_listeners_data:
            return ""

        dtsi_parts = []
        for listener in input_listeners_data:
            listener_code = listener.code
            if not listener_code:
                if self.logger:
                    self.logger.warning("Skipping input listener with missing 'code'.")
                continue

            dtsi_parts.append(f"{listener_code} {{")

            global_processors = listener.input_processors
            if global_processors:
                processors_str = " ".join(
                    f"{p.code} {' '.join(map(str, p.params))}".strip()
                    for p in global_processors
                )
                if processors_str:
                    dtsi_parts.append(f"    input-processors = <{processors_str}>;")

            nodes = listener.nodes
            if not nodes:
                if self.logger:
                    self.logger.warning(
                        f"Input listener '{listener_code}' has no nodes defined."
                    )
            else:
                for node in nodes:
                    node_code = node.code
                    if not node_code:
                        if self.logger:
                            self.logger.warning(
                                f"Skipping node in listener '{listener_code}' with missing 'code'."
                            )
                        continue

                    # dtsi_parts.append("")
                    dtsi_parts.append(f"    // {node.description or node_code}")
                    dtsi_parts.append(f"    {node_code} {{")

                    layers = node.layers
                    if layers:
                        layers_str = " ".join(map(str, layers))
                        dtsi_parts.append(f"        layers = <{layers_str}>;")

                    node_processors = node.input_processors
                    if node_processors:
                        node_processors_str = " ".join(
                            f"{p.code} {' '.join(map(str, p.params))}".strip()
                            for p in node_processors
                        )
                        if node_processors_str:
                            dtsi_parts.append(
                                f"        input-processors = <{node_processors_str}>;"
                            )

                    dtsi_parts.append("    };")

            dtsi_parts.append("};")

        return "\n".join(dtsi_parts)
        # return "\n".join(self._indent_array(dtsi_parts))

    def generate_keymap_node(
        self,
        profile: KeyboardProfile,
        layer_names: list[str],
        layers_data: list[LayerBindings],
    ) -> str:
        """Generate ZMK keymap node string from layer data.

        Args:
            profile: Keyboard profile containing all configuration
            layer_names: List of layer names
            layers_data: List of layer bindings

        Returns:
            DTSI keymap node content as string
        """
        # Create the keymap opening
        keymap_compatible = profile.keyboard_config.zmk.compatible_strings.keymap
        dtsi_parts = ["keymap {", f'    compatible = "{keymap_compatible}";']

        if not layers_data:
            # Still generate valid keymap structure even with no layers
            dtsi_parts.append("};")
            return "\n".join(self._indent_array(dtsi_parts))

        # Process each layer
        for _i, (layer_name, layer_bindings) in enumerate(
            zip(layer_names, layers_data, strict=False)
        ):
            # Format layer comment and opening
            define_name = re.sub(r"\W|^(?=\d)", "_", layer_name)
            dtsi_parts.append("")
            # dtsi_parts.append(f"    // Layer {i}: {layer_name}")
            dtsi_parts.append(f"    layer_{define_name} {{")
            # dtsi_parts.append(f'        label = "{layer_name}";')
            dtsi_parts.append("        bindings = <")

            # Format layer bindings
            formatted_bindings = []
            for binding in layer_bindings:
                if self._behavior_formatter:
                    formatted_binding = self._behavior_formatter.format_binding(binding)
                else:
                    formatted_binding = str(binding)  # Fallback
                formatted_bindings.append(formatted_binding)

            # Format the bindings using the layout formatter with custom indent for DTSI
            if self._layout_formatter:
                formatted_grid_str = self._layout_formatter.generate_layer_layout(
                    formatted_bindings, profile=profile, base_indent=""
                )
                # Split the formatted string into lines for consistent handling
                formatted_grid = (
                    formatted_grid_str.split("\n") if formatted_grid_str else []
                )
            else:
                # Fallback: simple grid formatting
                formatted_grid = [
                    f"            {binding}" for binding in formatted_bindings
                ]

            # Add the formatted grid
            dtsi_parts.extend(formatted_grid)

            # Add layer closing
            dtsi_parts.append("        >;")
            dtsi_parts.append("    };")

        # Add keymap closing
        dtsi_parts.append("};")

        return "\n".join(self._indent_array(dtsi_parts))

    def generate_kconfig_conf(
        self,
        keymap_data: "LayoutData",
        profile: KeyboardProfile,
    ) -> tuple[str, dict[str, int]]:
        """Generate kconfig content and settings from keymap data.

        Args:
            keymap_data: Keymap data with configuration parameters
            profile: Keyboard profile with kconfig options

        Returns:
            Tuple of (kconfig_content, kconfig_settings)
        """
        # Generate basic kconfig content (stub implementation)
        kconfig_lines = [
            "# Generated Kconfig configuration",
            "# This is a basic configuration for ZMK",
            "",
            'CONFIG_ZMK_KEYBOARD_NAME="'
            + (
                profile.keyboard_name
                if profile and hasattr(profile, "keyboard_name")
                else "unknown"
            )
            + '"',
            "",
        ]

        # Add any additional kconfig settings based on keymap data
        kconfig_settings = {}

        if hasattr(keymap_data, "combos") and keymap_data.combos:
            kconfig_lines.append("CONFIG_ZMK_COMBO_MAX_PRESSED_COMBOS=20")
            kconfig_settings["ZMK_COMBO_MAX_PRESSED_COMBOS"] = 20

        if hasattr(keymap_data, "hold_taps") and keymap_data.hold_taps:
            kconfig_lines.append("CONFIG_ZMK_KSCAN_DEBOUNCE_PRESS_MS=1")
            kconfig_lines.append("CONFIG_ZMK_KSCAN_DEBOUNCE_RELEASE_MS=5")
            kconfig_settings["ZMK_KSCAN_DEBOUNCE_PRESS_MS"] = 1
            kconfig_settings["ZMK_KSCAN_DEBOUNCE_RELEASE_MS"] = 5

        return "\n".join(kconfig_lines), kconfig_settings

    def _indent_array(self, lines: list[str], indent: str = "    ") -> list[str]:
        """Indent all lines in an array with the specified indent string."""
        return [f"{indent}{line}" for line in lines]


def create_zmk_generator(
    configuration_provider: "ConfigurationProvider | None" = None,
    template_provider: "TemplateProvider | None" = None,
    logger: "LayoutLogger | None" = None,
) -> ZMKGenerator:
    """Create a new ZMKGenerator instance.

    Args:
        configuration_provider: Provider for configuration data
        template_provider: Provider for template processing
        logger: Logger for structured logging

    Returns:
        Configured ZMKGenerator instance
    """
    return ZMKGenerator(
        configuration_provider=configuration_provider,
        template_provider=template_provider,
        logger=logger,
    )
