"""Provider factory for creating layout domain providers."""

from dataclasses import dataclass
from typing import Any

from .configuration import ConfigurationProvider
from .file import FileProvider
from .logger import LayoutLogger
from .template import TemplateProvider


@dataclass
class LayoutProviders:
    """Collection of all providers needed by the layout domain.

    This dataclass aggregates all provider interfaces required for
    layout operations, enabling clean dependency injection.
    """

    configuration: ConfigurationProvider
    template: TemplateProvider
    logger: LayoutLogger
    file: FileProvider


class DefaultLogger:
    """Default logger implementation using Python's standard logging."""
    
    def __init__(self, name: str = "zmk_layout"):
        import logging
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        self._logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs: Any) -> None:
        self._logger.exception(message, extra=kwargs)


class DefaultFileProvider:
    """Default file provider implementation using pathlib."""
    
    def read_text(self, path: Any, encoding: str = "utf-8") -> str:
        from pathlib import Path
        return Path(path).read_text(encoding=encoding)
    
    def write_text(self, path: Any, content: str, encoding: str = "utf-8") -> None:
        from pathlib import Path
        Path(path).write_text(content, encoding=encoding)
    
    def exists(self, path: Any) -> bool:
        from pathlib import Path
        return Path(path).exists()
    
    def mkdir(self, path: Any, parents: bool = False, exist_ok: bool = False) -> None:
        from pathlib import Path
        Path(path).mkdir(parents=parents, exist_ok=exist_ok)


class DefaultTemplateProvider:
    """Default template provider with basic string substitution."""
    
    def render_string(self, template: str, context: dict[str, Any]) -> str:
        """Basic template rendering using str.format()."""
        try:
            return template.format(**context)
        except KeyError as e:
            raise ValueError(f"Template variable not found in context: {e}") from e
    
    def has_template_syntax(self, content: str) -> bool:
        """Check for basic template syntax."""
        template_patterns = ["{", "}", "{{", "}}", "${"]
        return any(pattern in content for pattern in template_patterns)
    
    def escape_content(self, content: str) -> str:
        """Basic escaping by doubling braces."""  
        return content.replace("{", "{{").replace("}", "}}")


class DefaultConfigurationProvider:
    """Default configuration provider with minimal implementation."""
    
    def get_behavior_definitions(self) -> list[Any]:
        from .configuration import SystemBehavior
        # Basic ZMK behaviors
        return [
            SystemBehavior("kp", "Key press"),
            SystemBehavior("trans", "Transparent"),
            SystemBehavior("none", "No operation"),
            SystemBehavior("mt", "Mod-tap"),
            SystemBehavior("lt", "Layer-tap"),
        ]
    
    def get_include_files(self) -> list[str]:
        return [
            "zmk/include/dt-bindings/zmk/keys.h",
            "zmk/include/dt-bindings/zmk/bt.h"
        ]
    
    def get_validation_rules(self) -> dict[str, Any]:
        return {
            "max_layers": 10,
            "key_positions": list(range(80)),  # Generic 80-key support
            "supported_behaviors": ["kp", "trans", "none", "mt", "lt"]
        }
    
    def get_template_context(self) -> dict[str, Any]:
        return {
            "keyboard_name": "generic_keyboard",
            "firmware_version": "3.2.0"
        }
    
    def get_kconfig_options(self) -> dict[str, Any]:
        return {}
    
    def get_formatting_config(self) -> dict[str, Any]:
        return {
            "key_gap": 1,
            "base_indent": 4,
            "rows": []
        }


def create_default_providers() -> LayoutProviders:
    """Create a set of default providers for basic functionality.
    
    These providers offer minimal functionality to get started.
    For full features, external implementations should be provided.
    
    Returns:
        LayoutProviders with default implementations
    """
    return LayoutProviders(
        configuration=DefaultConfigurationProvider(),
        template=DefaultTemplateProvider(),
        logger=DefaultLogger(),
        file=DefaultFileProvider()
    )