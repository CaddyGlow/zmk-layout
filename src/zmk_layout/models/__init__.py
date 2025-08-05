"""ZMK Layout Models - Core data models for layout manipulation."""

from .base import LayoutBaseModel
from .behaviors import (
    BehaviorList,
    CapsWordBehavior,
    ComboBehavior,
    HoldTapBehavior,
    InputListener,
    InputListenerNode,
    InputProcessor,
    MacroBehavior,
    ModMorphBehavior,
    StickyKeyBehavior,
    TapDanceBehavior,
)
from .core import LayoutBinding, LayoutLayer, LayoutParam
from .keymap import (
    ConfigDirective,
    DependencyInfo,
    KeymapComment,
    KeymapInclude,
    KeymapMetadata,
)
from .metadata import (
    ConfigParameter,
    LayoutData,
    LayoutMetadata,
    LayoutResult,
)
from .types import ConfigValue, LayerBindings, LayerIndex, ParamValue, TemplateNumeric

__all__ = [  # noqa: RUF022
    # Base and core models
    "LayoutBaseModel",
    "LayoutBinding",
    "LayoutLayer",
    "LayoutParam",
    # Behavior models
    "BehaviorList",
    "CapsWordBehavior",
    "ComboBehavior",
    "HoldTapBehavior",
    "InputListener",
    "InputListenerNode",
    "InputProcessor",
    "MacroBehavior",
    "ModMorphBehavior",
    "StickyKeyBehavior",
    "TapDanceBehavior",
    # Keymap models
    "ConfigDirective",
    "DependencyInfo",
    "KeymapComment",
    "KeymapInclude",
    "KeymapMetadata",
    # Metadata models
    "ConfigParameter",
    "LayoutData",
    "LayoutMetadata",
    "LayoutResult",
    # Type definitions
    "ConfigValue",
    "LayerBindings",
    "LayerIndex",
    "ParamValue",
    "TemplateNumeric",
]

# Rebuild models to resolve forward references after all imports
LayoutParam.model_rebuild()
LayoutLayer.model_rebuild()
ComboBehavior.model_rebuild()
MacroBehavior.model_rebuild()
TapDanceBehavior.model_rebuild()
StickyKeyBehavior.model_rebuild()
ModMorphBehavior.model_rebuild()
LayoutData.model_rebuild()
LayoutResult.model_rebuild()
