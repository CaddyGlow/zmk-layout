"""Provider factory for creating layout domain providers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .configuration import ConfigurationProvider, SystemBehavior
    from .logger import LayoutLogger
    from .template import TemplateProvider
else:
    from .configuration import ConfigurationProvider
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


class DefaultLogger:
    """Default logger implementation using Python's standard logging."""

    def __init__(self, name: str = "zmk_layout") -> None:
        import logging

        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def info(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        extra: dict[str, str | int | float | bool | None] = kwargs
        self._logger.info(message, extra=extra)

    def error(
        self,
        message: str,
        exc_info: bool = False,
        **kwargs: str | int | float | bool | None,
    ) -> None:
        extra: dict[str, str | int | float | bool | None] = kwargs
        self._logger.error(message, exc_info=exc_info, extra=extra)

    def warning(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        extra: dict[str, str | int | float | bool | None] = kwargs
        self._logger.warning(message, extra=extra)

    def debug(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        extra: dict[str, str | int | float | bool | None] = kwargs
        self._logger.debug(message, extra=extra)

    def exception(
        self, message: str, **kwargs: str | int | float | bool | None
    ) -> None:
        extra: dict[str, str | int | float | bool | None] = kwargs
        self._logger.exception(message, extra=extra)


class DefaultTemplateProvider:
    """Default template provider with Jinja2 support and fallback."""

    def render_string(
        self, template: str, context: dict[str, str | int | float | bool | None]
    ) -> str:
        """Render template string using Jinja2 or basic format."""
        try:
            import jinja2
            from jinja2 import Environment, DictLoader
            
            # Create a Jinja2 environment with the template
            env = Environment(
                loader=DictLoader({"template": template}),
                trim_blocks=True,
                lstrip_blocks=True
            )
            template_obj = env.get_template("template")
            return template_obj.render(context)
        except ImportError:
            # Fallback to basic str.format()
            try:
                return template.format(**context)
            except KeyError as e:
                raise ValueError(f"Template variable not found in context: {e}") from e

    def render_template(
        self, template_path: str, context: dict[str, str | int | float | bool | None]
    ) -> str:
        """Render template file using Jinja2 or basic substitution."""
        from pathlib import Path
        
        template_file = Path(template_path)
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        template_content = template_file.read_text()
        
        try:
            import jinja2
            from jinja2 import Environment, FileSystemLoader
            
            # Create Jinja2 environment with the template directory
            env = Environment(
                loader=FileSystemLoader(template_file.parent),
                trim_blocks=True,
                lstrip_blocks=True
            )
            template_obj = env.get_template(template_file.name)
            return template_obj.render(context)
        except ImportError:
            # Fallback to simple variable replacement
            for key, value in context.items():
                template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
            return template_content

    def has_template_syntax(self, content: str) -> bool:
        """Check for Jinja2 or basic template syntax."""
        jinja2_patterns = ["{%", "%}", "{{", "}}", "{#", "#}"]
        basic_patterns = ["{", "}", "${"]
        template_patterns = jinja2_patterns + basic_patterns
        return any(pattern in content for pattern in template_patterns)

    def escape_content(self, content: str) -> str:
        """Escape content for Jinja2 processing."""
        try:
            import jinja2
            # For Jinja2, we need to escape template syntax
            return (content
                    .replace("{%", "{{ '{%' }}")
                    .replace("%}", "{{ '%}' }}")
                    .replace("{{", "{{ '{{' }}")
                    .replace("}}", "{{ '}}' }}")
                    .replace("{#", "{{ '{#' }}")
                    .replace("#}", "{{ '#}' }}"))
        except ImportError:
            # Basic escaping by doubling braces
            return content.replace("{", "{{").replace("}", "}}")


class DefaultConfigurationProvider:
    """Default configuration provider with minimal implementation."""

    def get_behavior_definitions(self) -> list[SystemBehavior]:
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
            "zmk/include/dt-bindings/zmk/bt.h",
        ]

    def get_validation_rules(self) -> dict[str, int | list[int] | list[str]]:
        return {
            "max_layers": 10,
            "key_positions": list(range(80)),  # Generic 80-key support
            "supported_behaviors": ["kp", "trans", "none", "mt", "lt"],
        }

    def get_template_context(self) -> dict[str, str | int | float | bool | None]:
        return {"keyboard_name": "generic_keyboard", "firmware_version": "3.2.0"}

    def get_kconfig_options(self) -> dict[str, str | int | float | bool | None]:
        return {}

    def get_formatting_config(self) -> dict[str, int | list[str]]:
        return {"key_gap": 1, "base_indent": 4, "rows": []}

    def get_search_paths(self) -> list[Path]:
        return [Path.cwd()]


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
    )


def create_data_only_providers() -> LayoutProviders:
    """Create providers optimized for data-only operations.

    These are the same as default providers but with the understanding
    that they won't perform any file I/O operations.

    Returns:
        LayoutProviders suitable for data-only operations
    """
    return create_default_providers()
