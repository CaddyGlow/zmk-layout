"""Exception hierarchy for ZMK Layout operations."""

from typing import Any


class LayoutError(Exception):
    """Base exception for layout operations."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize layout error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class LayerError(LayoutError):
    """Base exception for layer operations."""

    def __init__(self, message: str, layer_name: str | None = None, details: dict[str, Any] | None = None) -> None:
        """Initialize layer error.

        Args:
            message: Error message
            layer_name: Name of the layer that caused the error
            details: Additional error details
        """
        super().__init__(message, details)
        self.layer_name = layer_name


class LayerNotFoundError(LayerError):
    """Layer not found in layout."""

    def __init__(self, layer_name: str, available_layers: list[str] | None = None) -> None:
        """Initialize layer not found error.

        Args:
            layer_name: Name of the missing layer
            available_layers: List of available layer names
        """
        message = f"Layer '{layer_name}' not found"
        if available_layers:
            message += f". Available layers: {', '.join(available_layers)}"

        super().__init__(message, layer_name, {"available_layers": available_layers or []})


class LayerExistsError(LayerError):
    """Layer already exists in layout."""

    def __init__(self, layer_name: str) -> None:
        """Initialize layer exists error.

        Args:
            layer_name: Name of the existing layer
        """
        message = f"Layer '{layer_name}' already exists"
        super().__init__(message, layer_name)


class LayerIndexError(LayerError):
    """Invalid layer index."""

    def __init__(self, index: int, layer_name: str | None = None, layer_size: int | None = None) -> None:
        """Initialize layer index error.

        Args:
            index: Invalid index
            layer_name: Name of the layer
            layer_size: Size of the layer
        """
        message = f"Index {index} out of range"
        if layer_name:
            message += f" for layer '{layer_name}'"
        if layer_size is not None:
            message += f" (layer size: {layer_size})"

        details = {"index": index, "layer_size": layer_size}
        super().__init__(message, layer_name, details)


class InvalidBindingError(LayoutError):
    """Invalid binding format or value."""

    def __init__(self, binding: str, reason: str | None = None, suggestions: list[str] | None = None) -> None:
        """Initialize invalid binding error.

        Args:
            binding: Invalid binding string
            reason: Reason why binding is invalid
            suggestions: Suggested corrections
        """
        message = f"Invalid binding: '{binding}'"
        if reason:
            message += f" - {reason}"
        if suggestions:
            message += f". Suggestions: {', '.join(suggestions)}"

        details = {"binding": binding, "reason": reason, "suggestions": suggestions or []}
        super().__init__(message, details)


class BehaviorError(LayoutError):
    """Base exception for behavior operations."""

    def __init__(self, message: str, behavior_name: str | None = None, details: dict[str, Any] | None = None) -> None:
        """Initialize behavior error.

        Args:
            message: Error message
            behavior_name: Name of the behavior that caused the error
            details: Additional error details
        """
        super().__init__(message, details)
        self.behavior_name = behavior_name


class BehaviorExistsError(BehaviorError):
    """Behavior already exists."""

    def __init__(self, behavior_name: str, behavior_type: str | None = None) -> None:
        """Initialize behavior exists error.

        Args:
            behavior_name: Name of the existing behavior
            behavior_type: Type of behavior (hold_tap, combo, etc.)
        """
        message = f"Behavior '{behavior_name}' already exists"
        if behavior_type:
            message += f" ({behavior_type})"

        super().__init__(message, behavior_name, {"behavior_type": behavior_type})


class BehaviorNotFoundError(BehaviorError):
    """Behavior not found."""

    def __init__(self, behavior_name: str, behavior_type: str | None = None) -> None:
        """Initialize behavior not found error.

        Args:
            behavior_name: Name of the missing behavior
            behavior_type: Type of behavior to search for
        """
        message = f"Behavior '{behavior_name}' not found"
        if behavior_type:
            message += f" ({behavior_type})"

        super().__init__(message, behavior_name, {"behavior_type": behavior_type})


class InvalidBehaviorError(BehaviorError):
    """Invalid behavior configuration."""

    def __init__(self, behavior_name: str, reason: str, behavior_type: str | None = None) -> None:
        """Initialize invalid behavior error.

        Args:
            behavior_name: Name of the invalid behavior
            reason: Reason why behavior is invalid
            behavior_type: Type of behavior
        """
        message = f"Invalid {behavior_type or 'behavior'} '{behavior_name}': {reason}"

        details = {"reason": reason, "behavior_type": behavior_type}
        super().__init__(message, behavior_name, details)


class ValidationError(LayoutError):
    """Layout validation error."""

    def __init__(self, message: str, validation_errors: list[str] | None = None) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            validation_errors: List of specific validation errors
        """
        if validation_errors:
            full_message = f"{message}\nValidation errors:\n" + "\n".join(f"  - {error}" for error in validation_errors)
        else:
            full_message = message

        super().__init__(full_message, {"validation_errors": validation_errors or []})


class FileOperationError(LayoutError):
    """File operation error."""

    def __init__(self, message: str, file_path: str | None = None, operation: str | None = None) -> None:
        """Initialize file operation error.

        Args:
            message: Error message
            file_path: Path to the file that caused the error
            operation: Operation being performed (read, write, etc.)
        """
        full_message = message
        if file_path:
            full_message += f" (file: {file_path})"
        if operation:
            full_message += f" during {operation} operation"

        super().__init__(full_message, {"file_path": file_path, "operation": operation})


class ProviderError(LayoutError):
    """Provider-related error."""

    def __init__(self, message: str, provider_type: str | None = None) -> None:
        """Initialize provider error.

        Args:
            message: Error message
            provider_type: Type of provider that caused the error
        """
        full_message = message
        if provider_type:
            full_message += f" (provider: {provider_type})"

        super().__init__(full_message, {"provider_type": provider_type})


class ConfigurationError(LayoutError):
    """Configuration error."""

    def __init__(self, message: str, setting_name: str | None = None, setting_value: Any = None) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            setting_name: Name of the configuration setting
            setting_value: Value that caused the error
        """
        full_message = message
        if setting_name:
            full_message += f" (setting: {setting_name}"
            if setting_value is not None:
                full_message += f", value: {setting_value}"
            full_message += ")"

        super().__init__(full_message, {"setting_name": setting_name, "setting_value": setting_value})


# Convenience functions for creating common errors with helpful messages


def layer_not_found_error(layer_name: str, available_layers: list[str]) -> LayerNotFoundError:
    """Create a helpful layer not found error."""
    return LayerNotFoundError(layer_name, available_layers)


def invalid_binding_error_with_suggestions(binding: str) -> InvalidBindingError:
    """Create invalid binding error with suggestions."""
    suggestions = []

    # Common fixes
    if not binding.startswith("&"):
        suggestions.append(f"&{binding}")

    if binding in ["trans", "none"]:
        suggestions.append(f"&{binding}")

    # Common ZMK bindings
    common_bindings = ["&kp", "&mo", "&lt", "&mt", "&trans", "&none", "&to", "&tog"]
    suggestions.extend([b for b in common_bindings if binding.lower() in b.lower()])

    reason = "Binding must be a valid ZMK behavior"
    if not binding.strip():
        reason = "Binding cannot be empty"
    elif not binding.startswith("&"):
        reason = "ZMK bindings must start with '&'"

    return InvalidBindingError(binding, reason, suggestions[:3])  # Limit to 3 suggestions


def behavior_validation_error(behavior_name: str, behavior_type: str, issues: list[str]) -> InvalidBehaviorError:
    """Create behavior validation error with multiple issues."""
    reason = "; ".join(issues)
    return InvalidBehaviorError(behavior_name, reason, behavior_type)
