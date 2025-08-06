"""Provider protocols for ZMK layout library external dependencies.

This module defines the provider interface patterns that enable the layout library
to operate independently of specific implementations for configuration, templating,
logging, and file operations.
"""

from .configuration import ConfigurationProvider
from .factory import LayoutProviders
from .file import FileProvider
from .logger import LayoutLogger
from .template import TemplateProvider


__all__ = [
    "ConfigurationProvider",
    "FileProvider",
    "LayoutLogger",
    "LayoutProviders",
    "TemplateProvider",
]
