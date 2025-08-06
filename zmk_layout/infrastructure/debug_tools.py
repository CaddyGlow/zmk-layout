"""Debug formatters and chain introspection tools for fluent APIs."""

from __future__ import annotations

import json
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


@dataclass
class BuilderState:
    """Captures builder state for debugging."""

    class_name: str
    attributes: dict[str, Any]
    method_calls: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    stack_trace: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "class_name": self.class_name,
            "attributes": self.attributes,
            "method_calls": self.method_calls,
            "timestamp": self.timestamp,
            "stack_trace": self.stack_trace,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class ChainInspector:
    """Inspector for fluent chain debugging and introspection.

    This inspector provides tools for understanding and debugging fluent chains,
    including state tracking, performance monitoring, and error analysis.

    Examples:
        >>> inspector = ChainInspector()
        >>> builder = inspector.wrap(LayoutBindingBuilder("&kp"))
        >>> binding = builder.modifier("LC").key("A").build()
        >>> inspector.print_chain_history()
    """

    def __init__(self) -> None:
        """Initialize chain inspector."""
        self._history: list[BuilderState] = []
        self._performance_data: dict[str, list[float]] = {}
        self._error_states: list[tuple[BuilderState, Exception]] = []
        self._enabled = True

    def wrap(self, builder: Any) -> Any:
        """Wrap a builder for inspection.

        Args:
            builder: Builder instance to wrap

        Returns:
            Wrapped builder with inspection

        Examples:
            >>> wrapped = inspector.wrap(my_builder)
        """
        if not self._enabled:
            return builder

        class InspectedBuilder:
            """Wrapper that tracks builder calls."""

            def __init__(self, target: Any, inspector: ChainInspector) -> None:
                self._target = target
                self._inspector = inspector
                self._capture_state()

            def _capture_state(self) -> None:
                """Capture current builder state."""
                state = BuilderState(
                    class_name=self._target.__class__.__name__,
                    attributes=self._get_attributes(),
                    stack_trace=traceback.format_stack()[
                        -5:-1
                    ],  # Skip inspector frames
                )
                self._inspector._history.append(state)

            def _get_attributes(self) -> dict[str, Any]:
                """Extract builder attributes."""
                attrs = {}
                for attr_name in dir(self._target):
                    if not attr_name.startswith("_") and not callable(
                        getattr(self._target, attr_name)
                    ):
                        try:
                            attrs[attr_name] = getattr(self._target, attr_name)
                        except Exception:
                            attrs[attr_name] = "<Unable to access>"
                return attrs

            def __getattr__(self, name: str) -> Any:
                """Intercept method calls for tracking."""
                attr = getattr(self._target, name)
                if not callable(attr):
                    return attr

                def wrapped_method(*args: Any, **kwargs: Any) -> Any:
                    # Record method call
                    if self._inspector._history:
                        call_str = f"{name}({self._format_args(args, kwargs)})"
                        self._inspector._history[-1].method_calls.append(call_str)

                    # Measure performance
                    start_time = time.perf_counter()
                    try:
                        result = attr(*args, **kwargs)
                        elapsed = time.perf_counter() - start_time
                        self._inspector._record_performance(name, elapsed)

                        # Wrap result if it's a builder
                        if (
                            hasattr(result, "__class__")
                            and "Builder" in result.__class__.__name__
                        ):
                            return InspectedBuilder(result, self._inspector)
                        return result
                    except Exception as e:
                        # Record error state
                        if self._inspector._history:
                            self._inspector._error_states.append(
                                (self._inspector._history[-1], e)
                            )
                        raise

                return wrapped_method

            def _format_args(
                self, args: tuple[Any, ...], kwargs: dict[str, Any]
            ) -> str:
                """Format method arguments for display."""
                parts = []
                for arg in args:
                    if isinstance(arg, str):
                        parts.append(f'"{arg}"')
                    else:
                        parts.append(str(arg))
                for key, value in kwargs.items():
                    if isinstance(value, str):
                        parts.append(f'{key}="{value}"')
                    else:
                        parts.append(f"{key}={value}")
                return ", ".join(parts)

            def __repr__(self) -> str:
                """Delegate representation to target."""
                return f"Inspected({repr(self._target)})"

        return InspectedBuilder(builder, self)

    def _record_performance(self, method_name: str, elapsed: float) -> None:
        """Record method performance data.

        Args:
            method_name: Name of the method
            elapsed: Execution time in seconds
        """
        if method_name not in self._performance_data:
            self._performance_data[method_name] = []
        self._performance_data[method_name].append(elapsed)

    def print_chain_history(self) -> None:
        """Print the chain execution history."""
        print("\n=== Chain Execution History ===")
        for i, state in enumerate(self._history, 1):
            print(f"\nStep {i}: {state.class_name}")
            print(f"  Timestamp: {state.timestamp}")
            if state.method_calls:
                print("  Method calls:")
                for call in state.method_calls:
                    print(f"    - {call}")
            if state.attributes:
                print("  State:")
                for key, value in state.attributes.items():
                    print(f"    {key}: {value}")

    def print_performance_summary(self) -> None:
        """Print performance summary."""
        print("\n=== Performance Summary ===")
        for method_name, times in self._performance_data.items():
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            total_time = sum(times)
            print(f"\n{method_name}:")
            print(f"  Calls: {len(times)}")
            print(f"  Total: {total_time * 1000:.3f}ms")
            print(f"  Average: {avg_time * 1000:.3f}ms")
            print(f"  Min: {min_time * 1000:.3f}ms")
            print(f"  Max: {max_time * 1000:.3f}ms")

    def print_error_analysis(self) -> None:
        """Print error analysis."""
        if not self._error_states:
            print("\n=== No Errors Detected ===")
            return

        print("\n=== Error Analysis ===")
        for i, (state, error) in enumerate(self._error_states, 1):
            print(f"\nError {i}: {error.__class__.__name__}")
            print(f"  Message: {str(error)}")
            print(f"  Builder: {state.class_name}")
            if state.method_calls:
                print(f"  Last method: {state.method_calls[-1]}")
            print("  Stack trace:")
            for frame in state.stack_trace[-3:]:  # Show last 3 frames
                print(f"    {frame.strip()}")

    def get_state_at_step(self, step: int) -> BuilderState | None:
        """Get builder state at specific step.

        Args:
            step: Step number (1-based)

        Returns:
            Builder state at step or None

        Examples:
            >>> state = inspector.get_state_at_step(3)
        """
        if 0 < step <= len(self._history):
            return self._history[step - 1]
        return None

    def export_history(self, filepath: str) -> None:
        """Export history to JSON file.

        Args:
            filepath: Path to export file

        Examples:
            >>> inspector.export_history("chain_debug.json")
        """
        data = {
            "history": [state.to_dict() for state in self._history],
            "performance": {
                method: {
                    "calls": len(times),
                    "total_ms": sum(times) * 1000,
                    "avg_ms": sum(times) / len(times) * 1000,
                }
                for method, times in self._performance_data.items()
            },
            "errors": [
                {"state": state.to_dict(), "error": str(error)}
                for state, error in self._error_states
            ],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def clear(self) -> None:
        """Clear all inspection data."""
        self._history.clear()
        self._performance_data.clear()
        self._error_states.clear()

    def disable(self) -> None:
        """Disable inspection (for production)."""
        self._enabled = False

    def enable(self) -> None:
        """Enable inspection."""
        self._enabled = True


class DebugFormatter:
    """Formatter for debugging fluent API objects.

    This formatter provides detailed string representations of fluent API
    objects for debugging purposes.

    Examples:
        >>> formatter = DebugFormatter()
        >>> print(formatter.format(my_builder))
    """

    def __init__(self, max_depth: int = 3, max_width: int = 80) -> None:
        """Initialize debug formatter.

        Args:
            max_depth: Maximum nesting depth to display
            max_width: Maximum line width for output
        """
        self.max_depth = max_depth
        self.max_width = max_width

    def format(self, obj: Any, depth: int = 0) -> str:
        """Format object for debugging.

        Args:
            obj: Object to format
            depth: Current nesting depth

        Returns:
            Formatted string representation

        Examples:
            >>> formatted = formatter.format(my_builder)
        """
        if depth > self.max_depth:
            return "..."

        "  " * depth

        if isinstance(obj, BaseModel):
            return self._format_pydantic(obj, depth)
        elif hasattr(obj, "__dict__"):
            return self._format_object(obj, depth)
        elif isinstance(obj, dict):
            return self._format_dict(obj, depth)
        elif isinstance(obj, list | tuple):
            return self._format_sequence(obj, depth)
        else:
            return repr(obj)

    def _format_pydantic(self, obj: BaseModel, depth: int) -> str:
        """Format Pydantic model."""
        indent = "  " * depth
        lines = [f"{obj.__class__.__name__}("]
        for field_name, field_value in obj.model_dump().items():
            if field_value is not None:
                formatted_value = self.format(field_value, depth + 1)
                lines.append(f"{indent}  {field_name}={formatted_value},")
        lines.append(f"{indent})")
        return "\n".join(lines)

    def _format_object(self, obj: Any, depth: int) -> str:
        """Format regular object."""
        indent = "  " * depth
        class_name = obj.__class__.__name__
        lines = [f"{class_name}("]

        # Get relevant attributes
        for attr_name in sorted(dir(obj)):
            if attr_name.startswith("_") or callable(getattr(obj, attr_name, None)):
                continue
            try:
                value = getattr(obj, attr_name)
                formatted_value = self.format(value, depth + 1)
                lines.append(f"{indent}  {attr_name}={formatted_value},")
            except Exception:
                continue

        lines.append(f"{indent})")
        return "\n".join(lines)

    def _format_dict(self, obj: dict[Any, Any], depth: int) -> str:
        """Format dictionary."""
        if not obj:
            return "{}"

        indent = "  " * depth
        lines = ["{"]
        for key, value in obj.items():
            formatted_key = repr(key) if isinstance(key, str) else str(key)
            formatted_value = self.format(value, depth + 1)
            lines.append(f"{indent}  {formatted_key}: {formatted_value},")
        lines.append(f"{indent}}}")
        return "\n".join(lines)

    def _format_sequence(self, obj: list[Any] | tuple[Any, ...], depth: int) -> str:
        """Format list or tuple."""
        if not obj:
            return "[]" if isinstance(obj, list) else "()"

        if len(obj) <= 3 and all(
            isinstance(item, str | int | float | bool) for item in obj
        ):
            # Format short simple sequences inline
            items = [repr(item) if isinstance(item, str) else str(item) for item in obj]
            result = (
                f"[{', '.join(items)}]"
                if isinstance(obj, list)
                else f"({', '.join(items)})"
            )
            if len(result) <= self.max_width:
                return result

        # Format longer or complex sequences multiline
        indent = "  " * depth
        bracket = "[" if isinstance(obj, list) else "("
        end_bracket = "]" if isinstance(obj, list) else ")"
        lines = [bracket]
        for item in obj:
            formatted = self.format(item, depth + 1)
            lines.append(f"{indent}  {formatted},")
        lines.append(f"{indent}{end_bracket}")
        return "\n".join(lines)

    def format_chain(self, *builders: Any) -> str:
        """Format a chain of builders.

        Args:
            *builders: Builder instances in chain order

        Returns:
            Formatted chain representation

        Examples:
            >>> formatted = formatter.format_chain(builder1, builder2, builder3)
        """
        lines = ["=== Fluent Chain ==="]
        for i, builder in enumerate(builders, 1):
            lines.append(f"\nStep {i}:")
            lines.append(self.format(builder, 1))
        return "\n".join(lines)


def create_debug_context() -> tuple[ChainInspector, DebugFormatter]:
    """Create a debug context with inspector and formatter.

    Returns:
        Tuple of (inspector, formatter)

    Examples:
        >>> inspector, formatter = create_debug_context()
        >>> wrapped_builder = inspector.wrap(my_builder)
    """
    return ChainInspector(), DebugFormatter()


def debug_chain(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to automatically debug fluent chains.

    Args:
        func: Function that creates a fluent chain

    Returns:
        Wrapped function with debugging

    Examples:
        >>> @debug_chain
        ... def create_binding():
        ...     return LayoutBinding.builder("&kp").modifier("LC").key("A").build()
    """
    inspector = ChainInspector()

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # Check if first arg is a builder
            if (
                args
                and hasattr(args[0], "__class__")
                and "Builder" in args[0].__class__.__name__
            ):
                # Wrap the builder
                wrapped_args = (inspector.wrap(args[0]),) + args[1:]
                result = func(*wrapped_args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Print debug info if there were method calls
            if inspector._history and inspector._history[-1].method_calls:
                print(f"\n[DEBUG] {func.__name__} chain:")
                for call in inspector._history[-1].method_calls:
                    print(f"  -> {call}")

            return result
        except Exception as e:
            print(f"\n[ERROR] in {func.__name__}: {e}")
            inspector.print_error_analysis()
            raise
        finally:
            if inspector._performance_data:
                total_time = sum(
                    sum(times) for times in inspector._performance_data.values()
                )
                if total_time > 0.001:  # Only show if > 1ms
                    print(f"[PERF] Total time: {total_time * 1000:.3f}ms")

    return wrapper
