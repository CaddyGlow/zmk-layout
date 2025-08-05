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
)
from .types import ConfigValue, LayerBindings, LayerIndex, ParamValue, TemplateNumeric

__all__ = [
    # Base and core models
    "LayoutBaseModel",
    "LayoutParam",
    "LayoutBinding",
    "LayoutLayer",
    # Type definitions
    "ParamValue",
    "ConfigValue",
    "LayerIndex",
    "TemplateNumeric",
    "LayerBindings",
    # Behavior models
    "HoldTapBehavior",
    "ComboBehavior",
    "MacroBehavior",
    "TapDanceBehavior",
    "StickyKeyBehavior",
    "CapsWordBehavior",
    "ModMorphBehavior",
    "InputProcessor",
    "InputListenerNode",
    "InputListener",
    "BehaviorList",
    # Keymap models
    "KeymapComment",
    "KeymapInclude",
    "ConfigDirective",
    "DependencyInfo",
    "KeymapMetadata",
    # Metadata models
    "ConfigParameter",
    "LayoutMetadata",
    "LayoutData",
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
