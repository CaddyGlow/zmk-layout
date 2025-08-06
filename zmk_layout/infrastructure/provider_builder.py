"""Fluent builder for provider configuration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, Self

from pydantic import BaseModel, Field


if TYPE_CHECKING:
    pass


class FileAdapterProtocol(Protocol):
    """Protocol for file operations."""

    def read_file(self, path: Path) -> str:
        """Read file contents."""
        ...

    def write_file(self, path: Path, content: str) -> None:
        """Write file contents."""
        ...

    def exists(self, path: Path) -> bool:
        """Check if file exists."""
        ...


class TemplateAdapterProtocol(Protocol):
    """Protocol for template operations."""

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with context."""
        ...

    def render_string(self, template_str: str, context: dict[str, Any]) -> str:
        """Render a template string with context."""
        ...


class LoggerProtocol(Protocol):
    """Protocol for logging operations."""

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        ...


class ConfigurationProviderProtocol(Protocol):
    """Protocol for configuration provider."""

    def get_profile(self, keyboard: str) -> Any:
        """Get keyboard profile."""
        ...

    def list_profiles(self) -> list[str]:
        """List available profiles."""
        ...


class ProviderConfig(BaseModel):
    """Configuration for provider setup."""

    file_adapter: Any | None = Field(default=None)  # Protocol types don't work directly
    template_adapter: Any | None = Field(default=None)
    logger: Any | None = Field(default=None)
    configuration_provider: Any | None = Field(default=None)
    enable_caching: bool = Field(default=True)
    cache_size: int = Field(default=256)
    debug_mode: bool = Field(default=False)
    performance_tracking: bool = Field(default=False)

    model_config = {"arbitrary_types_allowed": True}


class ProviderBuilder:
    """Fluent builder for provider configuration.

    This builder provides a chainable interface for configuring providers
    used throughout the ZMK layout library.

    Examples:
        >>> providers = (ProviderBuilder()
        ...     .with_file_adapter(my_file_adapter)
        ...     .with_template_adapter(jinja_adapter)
        ...     .with_logger(structured_logger)
        ...     .enable_caching(size=512)
        ...     .enable_debug_mode()
        ...     .build())
    """

    __slots__ = ("_config", "__weakref__")

    def __init__(self, config: ProviderConfig | None = None) -> None:
        """Initialize builder with optional config.

        Args:
            config: Initial provider configuration
        """
        self._config = config or ProviderConfig()

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated config (immutable pattern).

        Args:
            **updates: Configuration updates

        Returns:
            New ProviderBuilder instance with updated config
        """
        new_config = self._config.model_copy(update=updates)
        return self.__class__(new_config)

    def with_file_adapter(self, adapter: FileAdapterProtocol) -> Self:
        """Set file adapter - returns new instance.

        Args:
            adapter: File operations adapter

        Returns:
            New builder instance with file adapter set

        Examples:
            >>> builder = builder.with_file_adapter(my_file_adapter)
        """
        return self._copy_with(file_adapter=adapter)

    def with_template_adapter(self, adapter: TemplateAdapterProtocol) -> Self:
        """Set template adapter - returns new instance.

        Args:
            adapter: Template rendering adapter

        Returns:
            New builder instance with template adapter set

        Examples:
            >>> builder = builder.with_template_adapter(jinja_adapter)
        """
        return self._copy_with(template_adapter=adapter)

    def with_logger(self, logger: LoggerProtocol) -> Self:
        """Set logger - returns new instance.

        Args:
            logger: Logger instance

        Returns:
            New builder instance with logger set

        Examples:
            >>> builder = builder.with_logger(structured_logger)
        """
        return self._copy_with(logger=logger)

    def with_configuration_provider(
        self, provider: ConfigurationProviderProtocol
    ) -> Self:
        """Set configuration provider - returns new instance.

        Args:
            provider: Configuration provider for keyboard profiles

        Returns:
            New builder instance with configuration provider set

        Examples:
            >>> builder = builder.with_configuration_provider(profile_provider)
        """
        return self._copy_with(configuration_provider=provider)

    def enable_caching(self, size: int = 256) -> Self:
        """Enable caching with specified size - returns new instance.

        Args:
            size: Cache size (number of entries)

        Returns:
            New builder instance with caching enabled

        Examples:
            >>> builder = builder.enable_caching(size=512)
        """
        return self._copy_with(enable_caching=True, cache_size=size)

    def disable_caching(self) -> Self:
        """Disable caching - returns new instance.

        Returns:
            New builder instance with caching disabled

        Examples:
            >>> builder = builder.disable_caching()
        """
        return self._copy_with(enable_caching=False)

    def enable_debug_mode(self) -> Self:
        """Enable debug mode - returns new instance.

        Returns:
            New builder instance with debug mode enabled

        Examples:
            >>> builder = builder.enable_debug_mode()
        """
        return self._copy_with(debug_mode=True)

    def enable_performance_tracking(self) -> Self:
        """Enable performance tracking - returns new instance.

        Returns:
            New builder instance with performance tracking enabled

        Examples:
            >>> builder = builder.enable_performance_tracking()
        """
        return self._copy_with(performance_tracking=True)

    def from_environment(self) -> Self:
        """Configure from environment variables - returns new instance.

        Returns:
            New builder instance configured from environment

        Examples:
            >>> builder = builder.from_environment()
        """
        import os

        updates: dict[str, Any] = {}

        if os.getenv("ZMK_LAYOUT_DEBUG") == "true":
            updates["debug_mode"] = True

        if os.getenv("ZMK_LAYOUT_PERFORMANCE") == "true":
            updates["performance_tracking"] = True

        if cache_size := os.getenv("ZMK_LAYOUT_CACHE_SIZE"):
            updates["enable_caching"] = True
            updates["cache_size"] = int(cache_size)

        if os.getenv("ZMK_LAYOUT_NO_CACHE") == "true":
            updates["enable_caching"] = False

        return self._copy_with(**updates) if updates else self

    def validate(self) -> Self:
        """Validate provider configuration - returns new instance.

        Returns:
            New builder instance with validated config

        Raises:
            ValueError: If configuration is invalid

        Examples:
            >>> builder = builder.validate()
        """
        # Validate required providers for certain operations
        if self._config.template_adapter and not self._config.file_adapter:
            print("Warning: Template adapter configured without file adapter")

        if self._config.performance_tracking and not self._config.logger:
            print("Warning: Performance tracking enabled without logger")

        return self

    def build(self) -> ProviderConfig:
        """Build final provider configuration.

        Returns:
            Configured provider configuration

        Examples:
            >>> config = builder.build()
        """
        # Apply defaults if needed
        config = self._config.model_copy()

        # Set up default logger if none provided
        if not config.logger and (config.debug_mode or config.performance_tracking):
            import logging

            logging.basicConfig(
                level=logging.DEBUG if config.debug_mode else logging.INFO
            )
            # Create a simple logger wrapper
            logger = logging.getLogger("zmk_layout")
            config.logger = logger

        return config

    def create_layout_service(self) -> Any:
        """Create layout service with configured providers.

        Returns:
            Configured layout service instance

        Examples:
            >>> service = builder.create_layout_service()
        """
        # This would integrate with the actual layout service
        # For now, return the config
        return self.build()

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of builder state
        """
        features = []
        if self._config.enable_caching:
            features.append(f"caching({self._config.cache_size})")
        if self._config.debug_mode:
            features.append("debug")
        if self._config.performance_tracking:
            features.append("perf")

        providers = []
        if self._config.file_adapter:
            providers.append("file")
        if self._config.template_adapter:
            providers.append("template")
        if self._config.logger:
            providers.append("logger")
        if self._config.configuration_provider:
            providers.append("config")

        return f"ProviderBuilder(providers=[{', '.join(providers)}], features=[{', '.join(features)}])"
