"""User behavior models for keyboard layouts."""

from typing import TYPE_CHECKING

from pydantic import Field, field_validator

from .base import LayoutBaseModel
from .types import LayerIndex, ParamValue, TemplateNumeric


if TYPE_CHECKING:
    from .core import LayoutBinding


class HoldTapBehavior(LayoutBaseModel):
    """Model for hold-tap behavior definitions."""

    name: str
    description: str | None = ""
    bindings: list[str] = Field(default_factory=list)
    tapping_term_ms: TemplateNumeric = Field(default=None, alias="tappingTermMs")
    quick_tap_ms: TemplateNumeric = Field(default=None, alias="quickTapMs")
    flavor: str | None = None
    hold_trigger_on_release: bool | None = Field(
        default=None, alias="holdTriggerOnRelease"
    )
    require_prior_idle_ms: TemplateNumeric = Field(
        default=None, alias="requirePriorIdleMs"
    )
    hold_trigger_key_positions: list[int] | None = Field(
        default=None, alias="holdTriggerKeyPositions"
    )
    retro_tap: bool | None = Field(default=None, alias="retroTap")
    tap_behavior: str | None = Field(default=None, alias="tapBehavior")
    hold_behavior: str | None = Field(default=None, alias="holdBehavior")

    @field_validator("flavor")
    @classmethod
    def validate_flavor(cls, v: str | None) -> str | None:
        """Validate hold-tap flavor."""
        if v is not None:
            valid_flavors = [
                "tap-preferred",
                "hold-preferred",
                "balanced",
                "tap-unless-interrupted",
            ]
            if v not in valid_flavors:
                msg = f"Invalid flavor: {v}. Must be one of {valid_flavors}"
                raise ValueError(msg) from None
        return v

    @field_validator("bindings")
    @classmethod
    def validate_bindings_count(cls, v: list[str]) -> list[str]:
        """Validate that hold-tap has exactly 2 bindings."""
        expected_bindings_count = 2
        if len(v) != expected_bindings_count:
            msg = f"Hold-tap behavior requires exactly {expected_bindings_count} bindings, found {len(v)}"
            raise ValueError(msg) from None
        return v


class ComboBehavior(LayoutBaseModel):
    """Model for combo definitions."""

    name: str
    description: str | None = ""
    timeout_ms: TemplateNumeric = Field(default=None, alias="timeoutMs")
    key_positions: list[int] = Field(alias="keyPositions")
    layers: list[LayerIndex] | None = None
    binding: "LayoutBinding" = Field()
    behavior: str | None = Field(default=None, alias="behavior")

    @field_validator("key_positions")
    @classmethod
    def validate_key_positions(cls, v: list[int]) -> list[int]:
        """Validate key positions are valid."""
        if not v:
            msg = "Combo must have at least one key position"
            raise ValueError(msg) from None
        for pos in v:
            if not isinstance(pos, int) or pos < 0:
                msg = f"Invalid key position: {pos}"
                raise ValueError(msg) from None
        return v


class MacroBehavior(LayoutBaseModel):
    """Model for macro definitions."""

    name: str
    description: str | None = ""
    wait_ms: TemplateNumeric = Field(default=None, alias="waitMs")
    tap_ms: TemplateNumeric = Field(default=None, alias="tapMs")
    bindings: list["LayoutBinding"] = Field(default_factory=list)
    params: list[ParamValue] | None = None

    @field_validator("params")
    @classmethod
    def validate_params_count(
        cls, v: list[ParamValue] | None
    ) -> list[ParamValue] | None:
        """Validate macro parameter count."""
        max_params = 2
        if v is not None and len(v) > max_params:
            msg = f"Macro cannot have more than {max_params} parameters, found {len(v)}"
            raise ValueError(msg) from None
        return v


class TapDanceBehavior(LayoutBaseModel):
    """Model for tap-dance behavior definitions."""

    name: str
    description: str | None = ""
    tapping_term_ms: TemplateNumeric = Field(default=None, alias="tappingTermMs")
    bindings: list["LayoutBinding"] = Field(default_factory=list)

    @field_validator("bindings")
    @classmethod
    def validate_bindings_count(cls, v: list["LayoutBinding"]) -> list["LayoutBinding"]:
        """Validate tap-dance bindings count."""
        min_bindings = 2
        max_bindings = 5
        if len(v) < min_bindings:
            msg = f"Tap-dance must have at least {min_bindings} bindings"
            raise ValueError(msg) from None
        if len(v) > max_bindings:
            msg = f"Tap-dance cannot have more than {max_bindings} bindings"
            raise ValueError(msg) from None
        return v


class StickyKeyBehavior(LayoutBaseModel):
    """Model for sticky-key behavior definitions."""

    name: str
    description: str | None = ""
    release_after_ms: TemplateNumeric = Field(default=None, alias="releaseAfterMs")
    quick_release: bool = Field(default=False, alias="quickRelease")
    lazy: bool = Field(default=False)
    ignore_modifiers: bool = Field(default=False, alias="ignoreModifiers")
    bindings: list["LayoutBinding"] = Field(default_factory=list)


class CapsWordBehavior(LayoutBaseModel):
    """Model for caps-word behavior definitions."""

    name: str
    description: str | None = ""
    continue_list: list[str] = Field(default_factory=list, alias="continueList")
    mods: int | None = Field(default=None)


class ModMorphBehavior(LayoutBaseModel):
    """Model for mod-morph behavior definitions."""

    name: str
    description: str | None = ""
    mods: int
    bindings: list["LayoutBinding"] = Field(default_factory=list)
    keep_mods: int | None = Field(default=None, alias="keepMods")

    @field_validator("bindings")
    @classmethod
    def validate_bindings_count(cls, v: list["LayoutBinding"]) -> list["LayoutBinding"]:
        """Validate mod-morph bindings count."""
        expected_bindings_count = 2
        if len(v) != expected_bindings_count:
            msg = f"Mod-morph must have exactly {expected_bindings_count} bindings"
            raise ValueError(msg) from None
        return v


class InputProcessor(LayoutBaseModel):
    """Model for input processors."""

    code: str
    params: list[ParamValue] = Field(default_factory=list)


class InputListenerNode(LayoutBaseModel):
    """Model for input listener nodes."""

    code: str
    description: str | None = ""
    layers: list[LayerIndex] = Field(default_factory=list)
    input_processors: list[InputProcessor] = Field(
        default_factory=list, alias="inputProcessors"
    )


class InputListener(LayoutBaseModel):
    """Model for input listeners."""

    code: str
    input_processors: list[InputProcessor] = Field(
        default_factory=list, alias="inputProcessors"
    )
    nodes: list[InputListenerNode] = Field(default_factory=list)


class SystemBehavior(LayoutBaseModel):
    """Model for system-defined behaviors."""

    code: str
    name: str
    description: str | None = ""
    expected_params: int = 0
    origin: str = "system"
    params: list[ParamValue] = Field(default_factory=list)


# Type alias for collections of behaviors
BehaviorList = list[
    HoldTapBehavior
    | ComboBehavior
    | MacroBehavior
    | TapDanceBehavior
    | StickyKeyBehavior
    | CapsWordBehavior
    | ModMorphBehavior
    | SystemBehavior
]
