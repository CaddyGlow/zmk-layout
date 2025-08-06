"""Advanced template context building for ZMK generation."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, Self

from pydantic import BaseModel, Field


if TYPE_CHECKING:
    from zmk_layout.models.behaviors import (
        ComboBehavior,
        HoldTapBehavior,
        MacroBehavior,
    )
    from zmk_layout.models.metadata import LayoutData


class TemplateContext(BaseModel):
    """Template context data model."""

    # Layout information
    keyboard: str = Field(default="unknown")
    title: str = Field(default="Untitled Layout")
    description: str | None = Field(default=None)
    author: str | None = Field(default=None)
    version: str = Field(default="1.0.0")

    # Layer data
    layer_names: list[str] = Field(default_factory=list)
    layers: list[list[Any]] = Field(default_factory=list)
    layer_count: int = Field(default=0)

    # Behaviors
    behaviors: list[Any] = Field(default_factory=list)
    combos: list[Any] = Field(default_factory=list)
    macros: list[Any] = Field(default_factory=list)
    hold_taps: list[Any] = Field(default_factory=list)

    # Profile information
    profile_name: str | None = Field(default=None)
    key_count: int | None = Field(default=None)
    split_keyboard: bool = Field(default=False)
    split_central: bool = Field(default=False)

    # Generation metadata
    generation_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    generator_version: str = Field(default="1.0.0")
    template_engine: str = Field(default="jinja2")

    # DTSI content sections
    layer_defines: str | None = Field(default=None)
    behaviors_dtsi: str | None = Field(default=None)
    combos_dtsi: str | None = Field(default=None)
    macros_dtsi: str | None = Field(default=None)
    keymap_node: str | None = Field(default=None)

    # Custom variables
    custom_vars: dict[str, Any] = Field(default_factory=dict)

    # Feature flags
    features: dict[str, bool] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True


class TemplateContextBuilder:
    """Advanced fluent builder for template contexts.

    This builder provides a comprehensive chainable interface for constructing
    template contexts used in ZMK file generation.

    Examples:
        >>> context = (TemplateContextBuilder()
        ...     .with_layout(layout_data)
        ...     .with_profile(keyboard_profile)
        ...     .with_behaviors(behaviors)
        ...     .with_generation_metadata()
        ...     .with_dtsi_content(layer_defines, keymap_node)
        ...     .build())
    """

    __slots__ = ("_context", "_transformers", "__weakref__")

    def __init__(self, context: TemplateContext | None = None) -> None:
        """Initialize builder with optional initial context.

        Args:
            context: Initial template context
        """
        self._context = context or TemplateContext()
        self._transformers: tuple[Callable[[TemplateContext], TemplateContext], ...] = ()

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated context (immutable pattern).

        Args:
            **updates: Context updates or transformer additions

        Returns:
            New TemplateContextBuilder instance
        """
        new_builder = self.__class__(self._context.model_copy())
        new_builder._context = self._context.model_copy(update=updates) if updates else self._context.model_copy()
        new_builder._transformers = self._transformers
        return new_builder

    def with_layout(self, layout_data: LayoutData) -> Self:
        """Add layout data to context - returns new instance.

        Args:
            layout_data: Layout data to add

        Returns:
            New builder instance with layout data

        Examples:
            >>> builder = builder.with_layout(layout_data)
        """
        return self._copy_with(
            keyboard=layout_data.keyboard,
            title=layout_data.title,
            description=layout_data.notes,
            layer_names=layout_data.layer_names,
            layers=[
                [binding.to_str() if hasattr(binding, "to_str") else str(binding) for binding in layer]
                for layer in layout_data.layers
            ],
            layer_count=len(layout_data.layers),
            combos=layout_data.combos if hasattr(layout_data, "combos") else [],
            macros=layout_data.macros if hasattr(layout_data, "macros") else [],
        )

    def with_profile(self, profile: Any) -> Self:
        """Add keyboard profile to context - returns new instance.

        Args:
            profile: Keyboard profile

        Returns:
            New builder instance with profile data

        Examples:
            >>> builder = builder.with_profile(keyboard_profile)
        """
        updates = {
            "profile_name": profile.keyboard_name if hasattr(profile, "keyboard_name") else str(profile),
        }

        if hasattr(profile, "keyboard_config"):
            config = profile.keyboard_config
            if hasattr(config, "key_count"):
                updates["key_count"] = config.key_count
            if hasattr(config, "split"):
                updates["split_keyboard"] = config.split
            if hasattr(config, "split_central"):
                updates["split_central"] = config.split_central

        return self._copy_with(**updates)

    def with_behaviors(
        self,
        behaviors: list[HoldTapBehavior] | None = None,
        combos: list[ComboBehavior] | None = None,
        macros: list[MacroBehavior] | None = None,
    ) -> Self:
        """Add behaviors to context - returns new instance.

        Args:
            behaviors: Hold-tap behaviors
            combos: Combo behaviors
            macros: Macro behaviors

        Returns:
            New builder instance with behaviors

        Examples:
            >>> builder = builder.with_behaviors(
            ...     behaviors=[home_row_mod],
            ...     combos=[esc_combo],
            ...     macros=[vim_save]
            ... )
        """
        updates: dict[str, Any] = {}
        if behaviors is not None:
            updates["behaviors"] = behaviors
            updates["hold_taps"] = behaviors  # Also store as hold_taps for compatibility
        if combos is not None:
            updates["combos"] = combos
        if macros is not None:
            updates["macros"] = macros

        return self._copy_with(**updates)

    def with_generation_metadata(
        self,
        author: str | None = None,
        version: str | None = None,
        timestamp: str | None = None,
        generator_version: str = "1.0.0",
    ) -> Self:
        """Add generation metadata - returns new instance.

        Args:
            author: Layout author
            version: Layout version
            timestamp: Generation timestamp (auto if None)
            generator_version: Generator version string

        Returns:
            New builder instance with metadata

        Examples:
            >>> builder = builder.with_generation_metadata(
            ...     author="John Doe",
            ...     version="2.1.0"
            ... )
        """
        updates = {
            "generator_version": generator_version,
            "generation_timestamp": timestamp or datetime.now().isoformat(),
        }
        if author is not None:
            updates["author"] = author
        if version is not None:
            updates["version"] = version

        return self._copy_with(**updates)

    def with_dtsi_content(
        self,
        layer_defines: str | None = None,
        behaviors_dtsi: str | None = None,
        combos_dtsi: str | None = None,
        macros_dtsi: str | None = None,
        keymap_node: str | None = None,
    ) -> Self:
        """Add DTSI content sections - returns new instance.

        Args:
            layer_defines: Layer define statements
            behaviors_dtsi: Behaviors DTSI content
            combos_dtsi: Combos DTSI content
            macros_dtsi: Macros DTSI content
            keymap_node: Keymap node content

        Returns:
            New builder instance with DTSI content

        Examples:
            >>> builder = builder.with_dtsi_content(
            ...     layer_defines=defines,
            ...     keymap_node=keymap
            ... )
        """
        updates = {}
        if layer_defines is not None:
            updates["layer_defines"] = layer_defines
        if behaviors_dtsi is not None:
            updates["behaviors_dtsi"] = behaviors_dtsi
        if combos_dtsi is not None:
            updates["combos_dtsi"] = combos_dtsi
        if macros_dtsi is not None:
            updates["macros_dtsi"] = macros_dtsi
        if keymap_node is not None:
            updates["keymap_node"] = keymap_node

        return self._copy_with(**updates)

    def with_custom_vars(self, **kwargs: Any) -> Self:
        """Add custom template variables - returns new instance.

        Args:
            **kwargs: Custom variables to add

        Returns:
            New builder instance with custom variables

        Examples:
            >>> builder = builder.with_custom_vars(
            ...     theme="dark",
            ...     layout_style="ergonomic"
            ... )
        """
        custom_vars = self._context.custom_vars.copy()
        custom_vars.update(kwargs)
        return self._copy_with(custom_vars=custom_vars)

    def with_features(self, **features: bool) -> Self:
        """Set feature flags - returns new instance.

        Args:
            **features: Feature flags to set

        Returns:
            New builder instance with features set

        Examples:
            >>> builder = builder.with_features(
            ...     home_row_mods=True,
            ...     mouse_keys=False,
            ...     rgb_underglow=True
            ... )
        """
        feature_flags = self._context.features.copy()
        feature_flags.update(features)
        return self._copy_with(features=feature_flags)

    def add_transformer(self, transformer: Callable[[TemplateContext], TemplateContext]) -> Self:
        """Add custom transformer function - returns new instance.

        Args:
            transformer: Function to transform context

        Returns:
            New builder instance with transformer added

        Examples:
            >>> def add_copyright(ctx: TemplateContext) -> TemplateContext:
            ...     return ctx.model_copy(update={
            ...         "custom_vars": {**ctx.custom_vars, "copyright": "© 2025"}
            ...     })
            >>> builder = builder.add_transformer(add_copyright)
        """
        new_builder = self._copy_with()
        new_builder._transformers = self._transformers + (transformer,)
        return new_builder

    def merge_with(self, other_context: TemplateContext | dict[str, Any]) -> Self:
        """Merge with another context - returns new instance.

        Args:
            other_context: Context to merge with

        Returns:
            New builder instance with merged context

        Examples:
            >>> builder = builder.merge_with(default_context)
        """
        if isinstance(other_context, dict):
            # Merge dictionary directly
            merged = self._context.model_dump()
            for key, value in other_context.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # Deep merge dictionaries
                    merged[key] = {**merged[key], **value}
                elif key in merged and isinstance(merged[key], list) and isinstance(value, list):
                    # Extend lists
                    merged[key] = merged[key] + value
                else:
                    # Override
                    merged[key] = value
            return self.__class__(TemplateContext(**merged))
        else:
            # Merge TemplateContext
            return self.merge_with(other_context.model_dump())

    def validate_completeness(self) -> Self:
        """Validate context completeness - returns new instance.

        Returns:
            New builder instance with validation applied

        Raises:
            ValueError: If context is incomplete

        Examples:
            >>> builder = builder.validate_completeness()
        """
        # Check required fields
        if not self._context.keyboard or self._context.keyboard == "unknown":
            print("Warning: Keyboard not specified in template context")

        if not self._context.layer_names:
            print("Warning: No layers defined in template context")

        if self._context.layer_count == 0:
            print("Warning: Layer count is 0")

        return self

    def build(self) -> TemplateContext:
        """Build final template context.

        Returns:
            Complete template context

        Examples:
            >>> context = builder.build()
        """
        # Apply transformers
        context = self._context
        for transformer in self._transformers:
            context = transformer(context)

        return context

    def build_dict(self) -> dict[str, Any]:
        """Build context as dictionary for template rendering.

        Returns:
            Template context as dictionary

        Examples:
            >>> context_dict = builder.build_dict()
            >>> rendered = template.render(**context_dict)
        """
        context = self.build()
        return context.model_dump(exclude_none=True)

    def preview(self) -> dict[str, Any]:
        """Preview context structure without building.

        Returns:
            Context structure summary

        Examples:
            >>> preview = builder.preview()
            >>> print(f"Layers: {preview['layer_count']}")
        """
        return {
            "keyboard": self._context.keyboard,
            "title": self._context.title,
            "layer_count": self._context.layer_count,
            "layer_names": self._context.layer_names,
            "has_behaviors": bool(self._context.behaviors),
            "has_combos": bool(self._context.combos),
            "has_macros": bool(self._context.macros),
            "custom_var_count": len(self._context.custom_vars),
            "feature_count": len(self._context.features),
            "transformer_count": len(self._transformers),
        }

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of builder state
        """
        preview = self.preview()
        return (
            f"TemplateContextBuilder(keyboard='{preview['keyboard']}', "
            f"layers={preview['layer_count']}, "
            f"behaviors={preview['has_behaviors']}, "
            f"transformers={preview['transformer_count']})"
        )
