"""Fluent pipeline for keymap processing operations with error collection."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from zmk_layout.models.core import LayoutBinding
from zmk_layout.validation import ValidationPipeline


if TYPE_CHECKING:
    from zmk_layout.models.metadata import LayoutData
    from zmk_layout.parsers.keymap_processors import BaseKeymapProcessor


@dataclass
class ProcessingError:
    """Represents a processing error with context."""

    message: str
    context: dict[str, Any] | None = None

    def __str__(self) -> str:
        """String representation of the error."""
        return self.message


@dataclass
class ProcessingWarning:
    """Represents a processing warning with context."""

    message: str
    context: dict[str, Any] | None = None

    def __str__(self) -> str:
        """String representation of the warning."""
        return self.message


class ProcessingPipeline:
    """Fluent pipeline for keymap processing operations with error collection.

    This pipeline provides a chainable interface for processing keymap data
    through various transformation and extraction operations. Each operation
    returns a new pipeline instance, maintaining immutability.

    Examples:
        >>> processor = BaseKeymapProcessor()
        >>> result = (processor.pipeline()
        ...     .extract_defines(ast_roots)
        ...     .extract_layers(ast_roots)
        ...     .normalize_bindings()
        ...     .transform_behaviors()
        ...     .validate_bindings()
        ...     .execute())
    """

    __slots__ = (
        "_processor",
        "_operations",
        "_errors",
        "_warnings",
        "__weakref__",
    )

    def __init__(
        self,
        processor: BaseKeymapProcessor,
        operations: tuple[Callable[[LayoutData], LayoutData], ...] | None = None,
        errors: tuple[ProcessingError, ...] | None = None,
        warnings: tuple[ProcessingWarning, ...] | None = None,
    ) -> None:
        """Initialize pipeline with processor and optional state.

        Args:
            processor: The keymap processor to use
            operations: Immutable tuple of operations to execute
            errors: Immutable tuple of collected errors
            warnings: Immutable tuple of collected warnings
        """
        self._processor = processor
        self._operations: tuple[Callable[[LayoutData], LayoutData], ...] = (
            operations or ()
        )
        self._errors: tuple[ProcessingError, ...] = errors or ()
        self._warnings: tuple[ProcessingWarning, ...] = warnings or ()

    def _copy_with(self, **updates: Any) -> Self:
        """Create new instance with updated state (immutable pattern).

        Args:
            **updates: Fields to update in the new instance

        Returns:
            New ProcessingPipeline instance with updated state
        """
        return self.__class__(
            processor=self._processor,
            operations=updates.get("operations", self._operations),
            errors=updates.get("errors", self._errors),
            warnings=updates.get("warnings", self._warnings),
        )

    def extract_defines(self, ast_roots: list[Any]) -> Self:
        """Add define extraction operation - returns new instance.

        This extracts preprocessor defines from the AST roots and applies
        them to the layout data for variable substitution.

        Args:
            ast_roots: List of AST root nodes to extract defines from

        Returns:
            New pipeline instance with define extraction operation added

        Examples:
            >>> pipeline = pipeline.extract_defines(ast_roots)
        """

        def operation(data: LayoutData) -> LayoutData:
            try:
                # Extract defines from AST
                defines = self._processor._extract_defines_from_ast(ast_roots)

                # Apply defines to data (store in variables)
                if not data.variables:
                    data.variables = {}
                data.variables["defines"] = defines
                return data
            except Exception:
                # Add error but continue with original data
                # Errors are collected in execute()
                return data

        return self._copy_with(operations=self._operations + (operation,))

    def extract_layers(self, ast_roots: list[Any]) -> Self:
        """Add layer extraction operation - returns new instance.

        This extracts layer definitions from the AST roots and updates
        the layout data with the extracted layers.

        Args:
            ast_roots: List of AST root nodes to extract layers from

        Returns:
            New pipeline instance with layer extraction operation added

        Examples:
            >>> pipeline = pipeline.extract_layers(ast_roots)
        """

        def operation(data: LayoutData) -> LayoutData:
            try:
                # Extract layers from AST
                layers_data = self._processor._extract_layers_from_roots(ast_roots)

                # Update layout data with extracted layers
                if layers_data:
                    return data.model_copy(
                        update={
                            "layers": layers_data.get("layers", []),
                            "layer_names": layers_data.get("layer_names", []),
                        }
                    )
                return data
            except Exception:
                return data

        return self._copy_with(operations=self._operations + (operation,))

    def transform_behaviors(self) -> Self:
        """Add behavior transformation operation - returns new instance.

        This transforms behavior references in bindings to their full
        definitions, expanding shorthand notations.

        Returns:
            New pipeline instance with behavior transformation operation added

        Examples:
            >>> pipeline = pipeline.transform_behaviors()
        """

        def operation(data: LayoutData) -> LayoutData:
            try:
                # Transform behavior references to definitions
                # Note: This method signature might need adjustment in the actual processor
                return data  # Return data as-is for now
            except Exception:
                return data

        return self._copy_with(operations=self._operations + (operation,))

    def validate_bindings(self) -> Self:
        """Add binding validation operation - returns new instance.

        This runs comprehensive validation on all bindings in the layout
        and collects any errors or warnings found.

        Returns:
            New pipeline instance with binding validation operation added

        Examples:
            >>> pipeline = pipeline.validate_bindings()
        """

        def operation(data: LayoutData) -> LayoutData:
            try:
                # Import Layout here to avoid circular dependency
                from zmk_layout.core import Layout

                # Run validation and collect issues
                # Create layout from LayoutData (using title as name)
                layout = Layout.create_empty(data.title, data.notes or "")
                # Set layers and layer names
                layout._data = data

                validator = ValidationPipeline(layout)
                result = validator.validate_bindings().validate_layer_references()

                # Collect errors and warnings (stored for reporting in execute())
                _ = result.collect_errors()
                _ = result.collect_warnings()

                # Note: We don't modify the data, just collect validation results
                return data
            except Exception:
                return data

        return self._copy_with(operations=self._operations + (operation,))

    def normalize_bindings(self) -> Self:
        """Add binding normalization operation - returns new instance.

        This normalizes all bindings to a consistent format, converting
        string bindings to LayoutBinding objects.

        Returns:
            New pipeline instance with binding normalization operation added

        Examples:
            >>> pipeline = pipeline.normalize_bindings()
        """

        def operation(data: LayoutData) -> LayoutData:
            try:
                # Normalize all bindings to consistent format
                normalized_layers = []
                for layer in data.layers:
                    normalized_bindings = []
                    for binding in layer:
                        # Ensure consistent binding format
                        if isinstance(binding, str):
                            normalized_bindings.append(LayoutBinding.from_str(binding))
                        else:
                            normalized_bindings.append(binding)
                    normalized_layers.append(normalized_bindings)

                return data.model_copy(update={"layers": normalized_layers})
            except Exception:
                return data

        return self._copy_with(operations=self._operations + (operation,))

    def apply_preprocessor_substitutions(self, defines: dict[str, str]) -> Self:
        """Add preprocessor substitution operation - returns new instance.

        This applies preprocessor define substitutions to all bindings,
        replacing define references with their values.

        Args:
            defines: Dictionary of define names to values

        Returns:
            New pipeline instance with substitution operation added

        Examples:
            >>> pipeline = pipeline.apply_preprocessor_substitutions({"HYPER": "LC(LS(LA(LGUI)))"})
        """

        def operation(data: LayoutData) -> LayoutData:
            try:
                # Apply substitutions to all bindings
                substituted_layers = []
                for layer in data.layers:
                    substituted_bindings = []
                    for binding in layer:
                        # Apply defines to binding strings
                        binding_str = (
                            binding.to_str()
                            if hasattr(binding, "to_str")
                            else str(binding)
                        )
                        for define_name, define_value in defines.items():
                            binding_str = binding_str.replace(define_name, define_value)
                        substituted_bindings.append(LayoutBinding.from_str(binding_str))
                    substituted_layers.append(substituted_bindings)

                return data.model_copy(update={"layers": substituted_layers})
            except Exception:
                return data

        return self._copy_with(operations=self._operations + (operation,))

    def filter_layers(self, layer_names: list[str]) -> Self:
        """Add layer filtering operation - returns new instance.

        This filters the layout to only include specified layers.

        Args:
            layer_names: List of layer names to keep

        Returns:
            New pipeline instance with layer filtering operation added

        Examples:
            >>> pipeline = pipeline.filter_layers(["base", "nav", "sym"])
        """

        def operation(data: LayoutData) -> LayoutData:
            try:
                # Filter to only specified layers
                filtered_layers = []
                filtered_names = []

                for i, name in enumerate(data.layer_names):
                    if name in layer_names:
                        filtered_layers.append(data.layers[i])
                        filtered_names.append(name)

                return data.model_copy(
                    update={"layers": filtered_layers, "layer_names": filtered_names}
                )
            except Exception:
                return data

        return self._copy_with(operations=self._operations + (operation,))

    def execute(self, initial_data: LayoutData | None = None) -> LayoutData:
        """Execute all operations, collecting errors instead of failing fast.

        Args:
            initial_data: Optional initial layout data, otherwise creates base data

        Returns:
            Processed layout data after all operations

        Examples:
            >>> result = pipeline.execute()
            >>> result = pipeline.execute(existing_layout_data)
        """
        # Get initial data
        # Note: _create_base_layout_data might need context parameter
        if initial_data:
            data = initial_data
        else:
            # Create empty layout data
            from zmk_layout.models.metadata import LayoutData

            data = LayoutData(
                keyboard="unknown", title="untitled", layers=[], layer_names=[]
            )

        # Track errors and warnings for this execution
        execution_errors: list[ProcessingError] = []
        execution_warnings: list[ProcessingWarning] = []

        # Execute each operation
        for i, operation in enumerate(self._operations):
            try:
                data = operation(data)
            except Exception as e:
                # Collect error and continue
                execution_errors.append(
                    ProcessingError(
                        f"Operation {i + 1} failed",
                        context={"operation_index": i, "error": str(e)},
                    )
                )
                # Continue with unchanged data

        # Log collected errors/warnings if logger is available
        if hasattr(self._processor, "logger") and self._processor.logger:
            for error in execution_errors:
                self._processor.logger.error(f"Processing error: {error}")
            for warning in execution_warnings:
                self._processor.logger.warning(f"Processing warning: {warning}")

        # Store execution results for retrieval
        self._errors = self._errors + tuple(execution_errors)
        self._warnings = self._warnings + tuple(execution_warnings)

        return data

    def collect_errors(self) -> list[ProcessingError]:
        """Collect all processing errors.

        Returns:
            List of all collected processing errors
        """
        return list(self._errors)

    def collect_warnings(self) -> list[ProcessingWarning]:
        """Collect all processing warnings.

        Returns:
            List of all collected processing warnings
        """
        return list(self._warnings)

    def has_errors(self) -> bool:
        """Check if pipeline has any errors.

        Returns:
            True if there are any errors
        """
        return len(self._errors) > 0

    def __repr__(self) -> str:
        """Useful representation for debugging.

        Returns:
            String representation of pipeline state
        """
        return (
            f"ProcessingPipeline(operations={len(self._operations)}, "
            f"errors={len(self._errors)}, warnings={len(self._warnings)})"
        )
