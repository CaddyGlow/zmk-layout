"""Fluent pipeline for layout transformation and migration operations."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Self

from zmk_layout.models.core import LayoutBinding


if TYPE_CHECKING:
    from zmk_layout.models.behaviors import ComboBehavior, MacroBehavior
    from zmk_layout.models.metadata import LayoutData


class TransformationPipeline:
    """Fluent pipeline for layout transformation and migration operations.

    This pipeline provides a chainable interface for transforming layouts
    between different formats, migrating legacy configurations, and applying
    bulk modifications.

    Examples:
        >>> pipeline = TransformationPipeline(layout_data)
        >>> result = (pipeline
        ...     .migrate_from_qmk()
        ...     .remap_keys(key_mapping)
        ...     .optimize_layers()
        ...     .apply_home_row_mods(mod_config)
        ...     .execute())
    """

    __slots__ = (
        "_layout_data",
        "_transformations",
        "_metadata",
        "__weakref__",
    )

    def __init__(
        self,
        layout_data: LayoutData,
        transformations: tuple[Callable[[LayoutData], LayoutData], ...] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize pipeline with layout data and optional state.

        Args:
            layout_data: The layout data to transform
            transformations: Immutable tuple of transformation functions
            metadata: Transformation metadata and context
        """
        self._layout_data = layout_data
        self._transformations: tuple[Callable[[LayoutData], LayoutData], ...] = transformations or ()
        self._metadata: dict[str, Any] = metadata or {}

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated state (immutable pattern).

        Args:
            **updates: Fields to update in the new instance

        Returns:
            New TransformationPipeline instance with updated state
        """
        return self.__class__(
            layout_data=updates.get("layout_data", self._layout_data),
            transformations=updates.get("transformations", self._transformations),
            metadata=updates.get("metadata", self._metadata.copy()),
        )

    def migrate_from_qmk(self, qmk_keymap: dict[str, Any] | None = None) -> Self:
        """Add QMK to ZMK migration transformation - returns new instance.

        This transforms a QMK keymap configuration to ZMK format, handling
        common conversions like KC_ to &kp, layer functions, and mods.

        Args:
            qmk_keymap: Optional QMK keymap data to merge

        Returns:
            New pipeline instance with QMK migration transformation added

        Examples:
            >>> pipeline = pipeline.migrate_from_qmk(qmk_config)
        """

        def transformation(data: LayoutData) -> LayoutData:
            # QMK to ZMK key mapping
            qmk_to_zmk = {
                "KC_": "&kp ",
                "MO(": "&mo ",
                "LT(": "&lt ",
                "TG(": "&tog ",
                "TO(": "&to ",
                "OSL(": "&sl ",
                "OSM(": "&sk ",
                "LCTL(": "LC(",
                "LSFT(": "LS(",
                "LALT(": "LA(",
                "LGUI(": "LG(",
                "RCTL(": "RC(",
                "RSFT(": "RS(",
                "RALT(": "RA(",
                "RGUI(": "RG(",
                "_______": "&trans",
                "XXXXXXX": "&none",
                "KC_TRNS": "&trans",
                "KC_NO": "&none",
            }

            # Transform each layer
            transformed_layers = []
            for layer in data.layers:
                transformed_bindings = []
                for binding in layer:
                    binding_str = binding.to_str() if hasattr(binding, "to_str") else str(binding)

                    # Handle bindings that already have & prefix
                    if binding_str.startswith("&KC_"):
                        # Convert &KC_ prefixes to &kp
                        binding_str = "&kp " + binding_str[4:]
                    elif binding_str.startswith("&"):
                        # Handle other &-prefixed QMK codes
                        # Remove the & prefix to apply conversions
                        inner_str = binding_str[1:]
                        if inner_str.startswith("MO("):
                            binding_str = "&mo " + inner_str[3:-1]
                        elif inner_str.startswith("LT("):
                            binding_str = "&lt " + inner_str[3:-1]
                        elif inner_str.startswith("TG("):
                            binding_str = "&tog " + inner_str[3:-1]
                        elif inner_str.startswith("TO("):
                            binding_str = "&to " + inner_str[3:-1]
                        elif inner_str == "_______":
                            binding_str = "&trans"
                        elif inner_str == "XXXXXXX":
                            binding_str = "&none"
                    else:
                        # Apply other QMK to ZMK conversions for non-& prefixed codes
                        for qmk_pattern, zmk_replacement in qmk_to_zmk.items():
                            binding_str = binding_str.replace(qmk_pattern, zmk_replacement)

                    transformed_bindings.append(LayoutBinding.from_str(binding_str))
                transformed_layers.append(transformed_bindings)

            # Update variables to indicate migration
            new_variables = data.variables.copy()
            new_variables["migrated_from"] = "qmk"

            return data.model_copy(update={"layers": transformed_layers, "variables": new_variables})

        return self._copy_with(transformations=self._transformations + (transformation,))

    def remap_keys(self, key_mapping: dict[str, str]) -> Self:
        """Add key remapping transformation - returns new instance.

        This applies a key remapping to all bindings in the layout,
        useful for adapting layouts to different physical keyboards.

        Args:
            key_mapping: Dictionary mapping old key codes to new ones

        Returns:
            New pipeline instance with key remapping transformation added

        Examples:
            >>> pipeline = pipeline.remap_keys({"SPACE": "SPC", "ENTER": "RET"})
        """

        def transformation(data: LayoutData) -> LayoutData:
            # Apply key remapping to all layers
            remapped_layers = []
            for layer in data.layers:
                remapped_bindings = []
                for binding in layer:
                    binding_str = binding.to_str() if hasattr(binding, "to_str") else str(binding)

                    # Apply key mappings
                    for old_key, new_key in key_mapping.items():
                        # Handle both bare keys and within binding contexts
                        binding_str = binding_str.replace(f" {old_key}", f" {new_key}")
                        binding_str = binding_str.replace(f"({old_key})", f"({new_key})")

                    remapped_bindings.append(LayoutBinding.from_str(binding_str))
                remapped_layers.append(remapped_bindings)

            return data.model_copy(update={"layers": remapped_layers})

        return self._copy_with(transformations=self._transformations + (transformation,))

    def optimize_layers(self, max_layer_count: int = 10) -> Self:
        """Add layer optimization transformation - returns new instance.

        This optimizes the layer structure by removing unused layers,
        merging similar layers, and reordering for efficiency.

        Args:
            max_layer_count: Maximum number of layers to keep

        Returns:
            New pipeline instance with layer optimization transformation added

        Examples:
            >>> pipeline = pipeline.optimize_layers(max_layer_count=8)
        """

        def transformation(data: LayoutData) -> LayoutData:
            # Analyze layer usage
            layer_usage = {}
            for i, layer_name in enumerate(data.layer_names):
                # Count non-transparent bindings
                non_trans = sum(
                    1
                    for binding in data.layers[i]
                    if not (hasattr(binding, "value") and binding.value == "&trans" or str(binding) == "&trans")
                )
                layer_usage[layer_name] = non_trans

            # Sort layers by usage (most used first)
            sorted_layers = sorted(layer_usage.items(), key=lambda x: x[1], reverse=True)

            # Keep only the most used layers up to max_layer_count
            optimized_names = []
            optimized_layers = []

            for layer_name, _ in sorted_layers[:max_layer_count]:
                idx = data.layer_names.index(layer_name)
                optimized_names.append(layer_name)
                optimized_layers.append(data.layers[idx])

            # Update layer references in bindings
            layer_mapping = {
                old_idx: new_idx
                for new_idx, name in enumerate(optimized_names)
                for old_idx, old_name in enumerate(data.layer_names)
                if old_name == name
            }

            # Fix layer references in bindings
            fixed_layers = []
            for layer in optimized_layers:
                fixed_bindings = []
                for binding in layer:
                    if (
                        hasattr(binding, "value")
                        and binding.value in ["&mo", "&lt", "&sl", "&to", "&tog"]
                        and binding.params
                        and len(binding.params) > 0
                    ):
                        old_layer = int(binding.params[0].value)
                        new_layer = layer_mapping.get(old_layer, old_layer)
                        binding = binding.model_copy(
                            update={
                                "params": [binding.params[0].model_copy(update={"value": str(new_layer)})]
                                + list(binding.params[1:])
                            }
                        )
                    fixed_bindings.append(binding)
                fixed_layers.append(fixed_bindings)

            return data.model_copy(update={"layers": fixed_layers, "layer_names": optimized_names})

        return self._copy_with(transformations=self._transformations + (transformation,))

    def apply_home_row_mods(self, mod_config: dict[str, Any] | None = None) -> Self:
        """Add home row mods transformation - returns new instance.

        This applies home row modifier configuration to the base layer,
        converting regular keys to hold-tap behaviors.

        Args:
            mod_config: Configuration for home row mods (positions, mods, timing)

        Returns:
            New pipeline instance with home row mods transformation added

        Examples:
            >>> pipeline = pipeline.apply_home_row_mods({
            ...     "left": {"positions": [10, 11, 12, 13], "mods": ["LSFT", "LCTL", "LALT", "LGUI"]},
            ...     "right": {"positions": [16, 17, 18, 19], "mods": ["RGUI", "RALT", "RCTL", "RSFT"]}
            ... })
        """
        mod_config = mod_config or {
            "left": {"positions": [10, 11, 12, 13], "mods": ["LSFT", "LCTL", "LALT", "LGUI"]},
            "right": {"positions": [16, 17, 18, 19], "mods": ["RGUI", "RALT", "RCTL", "RSFT"]},
            "tapping_term": 200,
            "flavor": "balanced",
        }

        def transformation(data: LayoutData) -> LayoutData:
            if not data.layers:
                return data

            # Apply home row mods to base layer (layer 0)
            base_layer = list(data.layers[0])

            # Create hold-tap behaviors for configured positions
            for side_config in ["left", "right"]:
                if side_config in mod_config:
                    positions = mod_config[side_config].get("positions", [])
                    mods = mod_config[side_config].get("mods", [])

                    for pos, mod in zip(positions, mods, strict=False):
                        if pos < len(base_layer):
                            # Get the original key
                            original = base_layer[pos]
                            original_str = original.to_str() if hasattr(original, "to_str") else str(original)

                            # Extract the key code
                            if original_str.startswith("&kp "):
                                key = original_str[4:]
                                # Create hold-tap behavior
                                behavior_name = f"hm_{side_config[0]}"  # hm_l or hm_r
                                hold_tap = f"&{behavior_name} {mod} {key}"
                                base_layer[pos] = LayoutBinding.from_str(hold_tap)

            # Update layers
            updated_layers = [base_layer] + list(data.layers[1:])

            # Add home row mod behaviors to variables
            new_variables = data.variables.copy()
            new_variables["home_row_mods"] = {
                "enabled": True,
                "config": mod_config,
            }

            return data.model_copy(update={"layers": updated_layers, "variables": new_variables})

        return self._copy_with(transformations=self._transformations + (transformation,))

    def add_combo_layer(self, combos: list[ComboBehavior]) -> Self:
        """Add combo layer transformation - returns new instance.

        This adds combo definitions to the layout metadata for generation.

        Args:
            combos: List of combo behaviors to add

        Returns:
            New pipeline instance with combo layer transformation added

        Examples:
            >>> from zmk_layout.builders import ComboBuilder
            >>> combo = ComboBuilder("copy").positions([12, 13]).binding("&kp LC(C)").build()
            >>> pipeline = pipeline.add_combo_layer([combo])
        """

        def transformation(data: LayoutData) -> LayoutData:
            # Add combos directly to the data model
            existing_combos = list(data.combos)
            new_combos = existing_combos + combos

            return data.model_copy(update={"combos": new_combos})

        return self._copy_with(transformations=self._transformations + (transformation,))

    def add_macro_layer(self, macros: list[MacroBehavior]) -> Self:
        """Add macro layer transformation - returns new instance.

        This adds macro definitions to the layout metadata for generation.

        Args:
            macros: List of macro behaviors to add

        Returns:
            New pipeline instance with macro layer transformation added

        Examples:
            >>> from zmk_layout.builders import MacroBuilder
            >>> macro = MacroBuilder("vim_save").tap("&kp ESC").tap("&kp COLON").tap("&kp W").build()
            >>> pipeline = pipeline.add_macro_layer([macro])
        """

        def transformation(data: LayoutData) -> LayoutData:
            # Add macros directly to the data model
            existing_macros = list(data.macros)
            new_macros = existing_macros + macros

            return data.model_copy(update={"macros": new_macros})

        return self._copy_with(transformations=self._transformations + (transformation,))

    def rename_layers(self, name_mapping: dict[str, str]) -> Self:
        """Add layer renaming transformation - returns new instance.

        This renames layers according to the provided mapping.

        Args:
            name_mapping: Dictionary mapping old names to new names

        Returns:
            New pipeline instance with layer renaming transformation added

        Examples:
            >>> pipeline = pipeline.rename_layers({"layer_0": "base", "layer_1": "nav"})
        """

        def transformation(data: LayoutData) -> LayoutData:
            # Rename layers
            new_names = []
            for name in data.layer_names:
                new_names.append(name_mapping.get(name, name))

            return data.model_copy(update={"layer_names": new_names})

        return self._copy_with(transformations=self._transformations + (transformation,))

    def merge_layers(self, source_layer: str | int, target_layer: str | int) -> Self:
        """Add layer merging transformation - returns new instance.

        This merges a source layer into a target layer, with source
        bindings taking precedence over target for non-transparent keys.

        Args:
            source_layer: Source layer name or index
            target_layer: Target layer name or index

        Returns:
            New pipeline instance with layer merging transformation added

        Examples:
            >>> pipeline = pipeline.merge_layers("symbols", "numbers")
        """

        def transformation(data: LayoutData) -> LayoutData:
            # Resolve layer indices
            source_idx = source_layer if isinstance(source_layer, int) else data.layer_names.index(source_layer)
            target_idx = target_layer if isinstance(target_layer, int) else data.layer_names.index(target_layer)

            # Merge layers
            merged_layer = []
            source = data.layers[source_idx]
            target = data.layers[target_idx]

            for i in range(max(len(source), len(target))):
                if i < len(source):
                    source_binding = source[i]
                    source_str = source_binding.to_str() if hasattr(source_binding, "to_str") else str(source_binding)
                    if source_str != "&trans":
                        merged_layer.append(source_binding)
                    elif i < len(target):
                        merged_layer.append(target[i])
                    else:
                        merged_layer.append(LayoutBinding.from_str("&trans"))
                elif i < len(target):
                    merged_layer.append(target[i])

            # Update layers (remove source, update target)
            new_layers = []
            new_names = []
            for i, (name, layer) in enumerate(zip(data.layer_names, data.layers, strict=False)):
                if i == source_idx:
                    continue  # Skip source layer
                elif i == target_idx:
                    new_layers.append(merged_layer)
                    new_names.append(name)
                else:
                    new_layers.append(layer)
                    new_names.append(name)

            return data.model_copy(update={"layers": new_layers, "layer_names": new_names})

        return self._copy_with(transformations=self._transformations + (transformation,))

    def execute(self) -> LayoutData:
        """Execute all transformations in sequence.

        Returns:
            Transformed layout data after all transformations

        Examples:
            >>> result = pipeline.execute()
        """
        data = self._layout_data

        # Execute each transformation
        for transformation in self._transformations:
            data = transformation(data)

        return data

    def preview(self) -> dict[str, Any]:
        """Preview transformation metadata without executing.

        Returns:
            Dictionary containing transformation metadata

        Examples:
            >>> preview = pipeline.preview()
            >>> print(f"Transformations to apply: {preview['transformation_count']}")
        """
        return {
            "transformation_count": len(self._transformations),
            "layout_title": self._layout_data.title,
            "layer_count": len(self._layout_data.layers),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of pipeline state
        """
        return (
            f"TransformationPipeline(layout='{self._layout_data.title}', transformations={len(self._transformations)})"
        )
