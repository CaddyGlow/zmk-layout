"""ZMK Layout Library - Standalone library for ZMK keyboard layout manipulation.

This library provides a fluent API for working with ZMK keyboard layouts,
enabling easy parsing, modification, and generation of layout files.
"""

__version__ = "0.1.0"

# Import core classes
from .core.layout import Layout

# Import core models
from .models import (
    ComboBehavior,
    HoldTapBehavior,
    LayoutBaseModel,
    LayoutBinding,
    LayoutData,
    LayoutLayer,
    LayoutParam,
    MacroBehavior,
)

# Import provider interfaces
from .providers import (
    ConfigurationProvider,
    FileProvider,
    LayoutLogger,
    LayoutProviders,
    TemplateProvider,
)
from .providers.factory import create_default_providers


__all__ = [
    "__version__",
    # Core classes
    "Layout",
    # Core models
    "LayoutBaseModel",
    "LayoutParam",
    "LayoutBinding",
    "LayoutLayer",
    "LayoutData",
    # Behavior models
    "HoldTapBehavior",
    "ComboBehavior",
    "MacroBehavior",
    # Provider interfaces
    "ConfigurationProvider",
    "TemplateProvider",
    "LayoutLogger",
    "FileProvider",
    "LayoutProviders",
    # Factory functions
    "create_default_providers",
]
