"""Keymap generator with fluent API for ZMK layouts.

This module provides a fluent API for generating ZMK keymap and configuration files
through the Layout class. It replaces the old config_generator.py with a cleaner,
more intuitive interface.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from zmk_layout.models import LayoutBinding, LayoutData


if TYPE_CHECKING:
    from zmk_layout.core.layout import Layout
    from zmk_layout.generators.zmk_generator import ZMKGenerator

logger = logging.getLogger(__name__)


class ExportManager:
    """Manager for export operations with fluent interface.

    This class provides the main entry point for all export operations
    from a Layout instance. It creates specialized builders for different
    export formats.
    """

    def __init__(self, layout: Layout) -> None:
        """Initialize export manager.

        Args:
            layout: Layout instance to export from
        """
        self._layout = layout
        self._zmk_generator: ZMKGenerator | None = None

    def keymap(self, profile: Any | None = None) -> KeymapBuilder:
        """Start keymap export chain.

        Args:
            profile: Optional keyboard profile for configuration

        Returns:
            KeymapBuilder for fluent configuration
        """
        return KeymapBuilder(self._layout, profile)

    def config(self, profile: Any | None = None) -> ConfigBuilder:
        """Start config export chain.

        Args:
            profile: Optional keyboard profile for configuration

        Returns:
            ConfigBuilder for fluent configuration
        """
        return ConfigBuilder(self._layout, profile)

    def to_dict(self) -> dict[str, Any]:
        """Export layout as dictionary.

        Returns:
            Layout data as dictionary
        """
        return self._layout.to_dict()

    def to_json(self, indent: int = 2) -> str:
        """Export layout as JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            Layout data as JSON string
        """
        import json

        return json.dumps(self.to_dict(), indent=indent)


class KeymapBuilder:
    """Fluent builder for keymap generation.

    This class provides a chainable interface for configuring and generating
    ZMK keymap files with various options and customizations.
    """

    def __init__(self, layout: Layout, profile: Any | None = None) -> None:
        """Initialize keymap builder.

        Args:
            layout: Layout instance to generate from
            profile: Optional keyboard profile
        """
        self._layout = layout
        self._profile = profile or self._create_default_profile()
        self._include_headers = True
        self._include_behaviors = True
        self._include_combos = True
        self._include_macros = True
        self._include_tap_dances = True
        self._template_path: str | None = None
        self._template_context: dict[str, Any] = {}
        self._zmk_generator: ZMKGenerator | None = None

        # Use default template from profile if available
        if (
            hasattr(self._profile, "keyboard_config")
            and hasattr(self._profile.keyboard_config, "keymap")
            and hasattr(self._profile.keyboard_config.keymap, "default_template_path")
        ):
            self._template_path = (
                self._profile.keyboard_config.keymap.default_template_path
            )

    def with_headers(self, include: bool = True) -> KeymapBuilder:
        """Include/exclude standard ZMK headers.

        Args:
            include: Whether to include headers

        Returns:
            Self for method chaining
        """
        self._include_headers = include
        return self

    def with_behaviors(self, include: bool = True) -> KeymapBuilder:
        """Include/exclude behavior definitions.

        Args:
            include: Whether to include behaviors

        Returns:
            Self for method chaining
        """
        self._include_behaviors = include
        return self

    def with_combos(self, include: bool = True) -> KeymapBuilder:
        """Include/exclude combo definitions.

        Args:
            include: Whether to include combos

        Returns:
            Self for method chaining
        """
        self._include_combos = include
        return self

    def with_macros(self, include: bool = True) -> KeymapBuilder:
        """Include/exclude macro definitions.

        Args:
            include: Whether to include macros

        Returns:
            Self for method chaining
        """
        self._include_macros = include
        return self

    def with_tap_dances(self, include: bool = True) -> KeymapBuilder:
        """Include/exclude tap dance definitions.

        Args:
            include: Whether to include tap dances

        Returns:
            Self for method chaining
        """
        self._include_tap_dances = include
        return self

    def with_template(self, template_path: str) -> KeymapBuilder:
        """Use custom template file.

        Args:
            template_path: Path to template file

        Returns:
            Self for method chaining
        """
        self._template_path = template_path
        return self

    def with_context(self, **kwargs: Any) -> KeymapBuilder:
        """Add custom template context variables.

        Args:
            **kwargs: Template context variables

        Returns:
            Self for method chaining
        """
        self._template_context.update(kwargs)
        return self

    def generate(self) -> str:
        """Generate final keymap content.

        Returns:
            Generated keymap content as string
        """
        # Get ZMK generator
        generator = self._get_zmk_generator()

        # Build template context
        context = self._build_context(generator)

        # If template is specified, use it
        if self._template_path:
            return self._render_template(context)

        # Otherwise, generate directly
        return self._generate_direct(generator, context)

    def _create_default_profile(self) -> Any:
        """Create a default keyboard profile.

        Returns:
            Default profile with minimal configuration
        """
        # Get keyboard name from layout data
        keyboard_name = self._layout.data.keyboard or "generic"

        # Create minimal profile
        return SimpleNamespace(
            keyboard_name=keyboard_name,
            firmware_version="1.0.0",
            keyboard_config=SimpleNamespace(
                key_count=len(self._layout.data.layers[0])
                if self._layout.data.layers
                else 42,
                zmk=SimpleNamespace(
                    compatible_strings=SimpleNamespace(
                        keymap="zmk,keymap",
                        hold_tap="zmk,behavior-hold-tap",
                        tap_dance="zmk,behavior-tap-dance",
                        macro="zmk,behavior-macro",
                        combos="zmk,combos",
                    ),
                    layout=SimpleNamespace(
                        keys=len(self._layout.data.layers[0])
                        if self._layout.data.layers
                        else 42
                    ),
                    patterns=SimpleNamespace(
                        kconfig_prefix="CONFIG_ZMK_",
                        layer_define="#define {layer_name} {layer_index}",
                    ),
                    validation_limits=SimpleNamespace(
                        required_holdtap_bindings=2, max_macro_params=32
                    ),
                ),
                keymap=SimpleNamespace(
                    header_includes=["behaviors.dtsi", "dt-bindings/zmk/keys.h"],
                    key_position_header="",
                    system_behaviors_dts="",
                    keymap_dtsi=None,
                    keymap_dtsi_file=None,
                ),
            ),
            kconfig_options={},
        )

    def _get_zmk_generator(self) -> ZMKGenerator:
        """Get or create ZMK generator instance.

        Returns:
            ZMK generator instance
        """
        if self._zmk_generator is None:
            from zmk_layout.generators.zmk_generator import ZMKGenerator

            providers = self._layout._providers
            self._zmk_generator = ZMKGenerator(
                configuration_provider=providers.configuration if providers else None,
                template_provider=providers.template if providers else None,
                logger=providers.logger if providers else None,
            )

        return self._zmk_generator

    def _build_context(self, generator: ZMKGenerator) -> dict[str, Any]:
        """Build template context for generation.

        Args:
            generator: ZMK generator instance

        Returns:
            Template context dictionary
        """
        layout_data = self._layout.data

        # Generate DTSI components based on flags
        layer_defines = generator.generate_layer_defines(
            self._profile, layout_data.layer_names
        )

        behaviors_dtsi = ""
        if self._include_behaviors and layout_data.hold_taps:
            behaviors_dtsi = generator.generate_behaviors_dtsi(
                self._profile, layout_data.hold_taps
            )

        tap_dances_dtsi = ""
        if self._include_tap_dances and layout_data.tap_dances:
            tap_dances_dtsi = generator.generate_tap_dances_dtsi(
                self._profile, layout_data.tap_dances
            )

        combos_dtsi = ""
        if self._include_combos and layout_data.combos:
            combos_dtsi = generator.generate_combos_dtsi(
                self._profile, layout_data.combos, layout_data.layer_names
            )

        macros_dtsi = ""
        if self._include_macros and layout_data.macros:
            macros_dtsi = generator.generate_macros_dtsi(
                self._profile, layout_data.macros
            )

        # Process layers to extract binding objects
        layers_data = self._process_layers(layout_data.layers)

        # Generate keymap node
        keymap_node = generator.generate_keymap_node(
            profile=self._profile,
            layer_names=layout_data.layer_names,
            layers_data=layers_data,
        )

        # Get resolved includes
        resolved_includes = self._get_resolved_includes()

        # Build and return context
        context = {
            "keyboard": layout_data.keyboard,
            "layer_names": layout_data.layer_names,
            "layers": layers_data,
            "layer_defines": layer_defines,
            "keymap_node": keymap_node,
            "user_behaviors_dtsi": behaviors_dtsi,
            "user_tap_dances_dtsi": tap_dances_dtsi,
            "combos_dtsi": combos_dtsi,
            "user_macros_dtsi": macros_dtsi,
            "resolved_includes": "\n".join(resolved_includes),
            "key_position_header": self._get_key_position_header(),
            "system_behaviors_dts": self._get_system_behaviors_dts(),
            "custom_defined_behaviors": layout_data.custom_defined_behaviors or "",
            "custom_devicetree": layout_data.custom_devicetree or "",
            "profile_name": f"{self._profile.keyboard_name}/{self._profile.firmware_version}",
            "firmware_version": self._profile.firmware_version,
            "generation_timestamp": datetime.now().isoformat(),
        }

        # Merge with custom context
        context.update(self._template_context)

        return context

    def _process_layers(self, layers: list[Any]) -> list[list[LayoutBinding]]:
        """Process layers to extract binding objects.

        Args:
            layers: Raw layer data

        Returns:
            Processed layer bindings
        """
        layers_data = []

        for layer in layers:
            if isinstance(layer, list):
                layer_bindings = []
                for binding in layer:
                    if isinstance(binding, LayoutBinding):
                        layer_bindings.append(binding)
                    elif isinstance(binding, dict):
                        # Convert dict to LayoutBinding
                        try:
                            layout_binding = LayoutBinding.model_validate(binding)
                            layer_bindings.append(layout_binding)
                        except Exception:
                            # Fallback: create from string
                            binding_str = binding.get("value", str(binding))
                            layout_binding = LayoutBinding.from_str(binding_str)
                            layer_bindings.append(layout_binding)
                    else:
                        # Convert string to LayoutBinding
                        layout_binding = LayoutBinding.from_str(str(binding))
                        layer_bindings.append(layout_binding)
                layers_data.append(layer_bindings)
            else:
                layers_data.append([])

        return layers_data

    def _get_resolved_includes(self) -> list[str]:
        """Get resolved include statements.

        Returns:
            List of #include statements
        """
        includes = []

        if (
            self._include_headers
            and hasattr(self._profile, "keyboard_config")
            and hasattr(self._profile.keyboard_config, "keymap")
            and hasattr(self._profile.keyboard_config.keymap, "header_includes")
        ):
            # Get includes from profile
            for include in self._profile.keyboard_config.keymap.header_includes:
                includes.append(f"#include <{include}>")

        return includes

    def _get_key_position_header(self) -> str:
        """Get key position header from profile.

        Returns:
            Key position header string
        """
        if (
            hasattr(self._profile, "keyboard_config")
            and hasattr(self._profile.keyboard_config, "keymap")
            and hasattr(self._profile.keyboard_config.keymap, "key_position_header")
        ):
            return self._profile.keyboard_config.keymap.key_position_header or ""
        return ""

    def _get_system_behaviors_dts(self) -> str:
        """Get system behaviors DTS from profile.

        Returns:
            System behaviors DTS string
        """
        if (
            hasattr(self._profile, "keyboard_config")
            and hasattr(self._profile.keyboard_config, "keymap")
            and hasattr(self._profile.keyboard_config.keymap, "system_behaviors_dts")
        ):
            return self._profile.keyboard_config.keymap.system_behaviors_dts or ""
        return ""

    def _render_template(self, context: dict[str, Any]) -> str:
        """Render template with context.

        Args:
            context: Template context

        Returns:
            Rendered template content
        """
        if not self._template_path:
            raise ValueError("Template path not specified")

        # Get template provider from layout
        providers = self._layout._providers
        if providers and providers.template:
            template_provider = providers.template
            if hasattr(template_provider, "render_template"):
                result = template_provider.render_template(self._template_path, context)
                return str(result)
            # Fallback for template providers without render_template method
            return self._simple_template_replacement(self._template_path, context)

        # Fallback: read template file and do simple replacement
        template_path = Path(self._template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {self._template_path}")

        template_content = template_path.read_text()

        # Simple variable replacement
        for key, value in context.items():
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))

        return template_content

    def _simple_template_replacement(
        self, template_path: str, context: dict[str, Any]
    ) -> str:
        """Simple template replacement fallback."""
        template_file = Path(template_path)
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        content = template_file.read_text()

        # Simple variable replacement
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))

        return content

    def _generate_direct(self, generator: ZMKGenerator, context: dict[str, Any]) -> str:
        """Generate keymap directly without template.

        Args:
            generator: ZMK generator instance
            context: Template context

        Returns:
            Generated keymap content
        """
        parts = []

        # Add header
        if self._include_headers:
            parts.append("/*")
            parts.append(f" * Copyright (c) {datetime.now().year} The ZMK Contributors")
            parts.append(" * SPDX-License-Identifier: MIT")
            parts.append(" */")
            parts.append("")

            # Add includes
            if context["resolved_includes"]:
                parts.append(context["resolved_includes"])
                parts.append("")

        # Add key position header if present
        if context["key_position_header"]:
            parts.append(context["key_position_header"])
            parts.append("")

        # Add layer defines
        if context["layer_defines"]:
            parts.append(context["layer_defines"])
            parts.append("")

        # Add custom defined behaviors
        if context["custom_defined_behaviors"]:
            parts.append(context["custom_defined_behaviors"])
            parts.append("")

        # Add behaviors
        if context["user_behaviors_dtsi"]:
            parts.append("/ {")
            parts.append(context["user_behaviors_dtsi"])
            parts.append("};")
            parts.append("")

        # Add tap dances
        if context["user_tap_dances_dtsi"]:
            parts.append("/ {")
            parts.append(context["user_tap_dances_dtsi"])
            parts.append("};")
            parts.append("")

        # Add combos
        if context["combos_dtsi"]:
            parts.append(context["combos_dtsi"])
            parts.append("")

        # Add macros
        if context["user_macros_dtsi"]:
            parts.append(context["user_macros_dtsi"])
            parts.append("")

        # Add system behaviors
        if context["system_behaviors_dts"]:
            parts.append(context["system_behaviors_dts"])
            parts.append("")

        # Add custom devicetree
        if context["custom_devicetree"]:
            parts.append(context["custom_devicetree"])
            parts.append("")

        # Add keymap node
        parts.append("/ {")
        parts.append(context["keymap_node"])
        parts.append("};")

        return "\n".join(parts)


class ConfigBuilder:
    """Fluent builder for config file generation.

    This class provides a chainable interface for configuring and generating
    ZMK configuration files with kconfig options.
    """

    def __init__(self, layout: Layout, profile: Any | None = None) -> None:
        """Initialize config builder.

        Args:
            layout: Layout instance to generate from
            profile: Optional keyboard profile
        """
        self._layout = layout
        self._profile = profile or self._create_default_profile()
        self._kconfig_options: dict[str, Any] = {}
        self._use_defaults = True
        self._zmk_generator: ZMKGenerator | None = None

    def with_options(self, **options: Any) -> ConfigBuilder:
        """Add kconfig options.

        Args:
            **options: Kconfig options to set

        Returns:
            Self for method chaining
        """
        self._kconfig_options.update(options)
        return self

    def with_defaults(self, use: bool = True) -> ConfigBuilder:
        """Include/exclude default options.

        Args:
            use: Whether to include defaults

        Returns:
            Self for method chaining
        """
        self._use_defaults = use
        return self

    def generate(self) -> tuple[str, dict[str, Any]]:
        """Generate config content and settings.

        Returns:
            Tuple of (config_content, kconfig_settings)
        """
        # Get ZMK generator
        generator = self._get_zmk_generator()

        # Merge config parameters from layout with additional options
        layout_data = self._layout.data

        # Convert additional options to config parameters
        if self._kconfig_options:
            # Create a copy of layout data with additional config parameters
            from zmk_layout.models.metadata import ConfigParameter

            config_params = (
                list(layout_data.config_parameters)
                if layout_data.config_parameters
                else []
            )

            for param_name, value in self._kconfig_options.items():
                # Check if parameter already exists
                existing = False
                for param in config_params:
                    if param.param_name == param_name:
                        param.value = value
                        existing = True
                        break

                if not existing:
                    config_params.append(
                        ConfigParameter(paramName=param_name, value=value)
                    )

            # Create modified layout data
            layout_data_dict = layout_data.model_dump()
            layout_data_dict["config_parameters"] = config_params
            layout_data = LayoutData.model_validate(layout_data_dict)

        # Generate kconfig using ZMKGenerator
        return generator.generate_kconfig_conf(layout_data, self._profile)

    def _create_default_profile(self) -> Any:
        """Create a default keyboard profile.

        Returns:
            Default profile with minimal configuration
        """
        # Get keyboard name from layout data
        keyboard_name = self._layout.data.keyboard or "generic"

        # Create minimal profile
        return SimpleNamespace(
            keyboard_name=keyboard_name,
            firmware_version="1.0.0",
            keyboard_config=SimpleNamespace(
                key_count=len(self._layout.data.layers[0])
                if self._layout.data.layers
                else 42,
                zmk=SimpleNamespace(
                    patterns=SimpleNamespace(kconfig_prefix="CONFIG_ZMK_"),
                    validation_limits=SimpleNamespace(
                        required_holdtap_bindings=2, max_macro_params=32
                    ),
                ),
            ),
            kconfig_options={},
        )

    def _get_zmk_generator(self) -> ZMKGenerator:
        """Get or create ZMK generator instance.

        Returns:
            ZMK generator instance
        """
        if self._zmk_generator is None:
            from zmk_layout.generators.zmk_generator import ZMKGenerator

            providers = self._layout._providers
            self._zmk_generator = ZMKGenerator(
                configuration_provider=providers.configuration if providers else None,
                template_provider=providers.template if providers else None,
                logger=providers.logger if providers else None,
            )

        return self._zmk_generator


# Export classes
__all__ = ["ExportManager", "KeymapBuilder", "ConfigBuilder"]
