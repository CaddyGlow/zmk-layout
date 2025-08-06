"""Chain composition utilities for combining and orchestrating pipelines."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from zmk_layout.core import Layout
    from zmk_layout.models.metadata import LayoutData
    from zmk_layout.parsers.keymap_processors import BaseKeymapProcessor
    from zmk_layout.processing.processor_pipeline import ProcessingPipeline
    from zmk_layout.processing.transformation_pipeline import TransformationPipeline
    from zmk_layout.validation import ValidationPipeline


class PipelineComposer:
    """Orchestrates multiple pipelines for complex workflows.

    This composer allows combining processing, transformation, and validation
    pipelines into complex workflows with error handling and rollback support.

    Examples:
        >>> composer = PipelineComposer()
        >>> result = (composer
        ...     .add_processing(processor_pipeline)
        ...     .add_transformation(transformation_pipeline)
        ...     .add_validation(validation_pipeline)
        ...     .with_rollback()
        ...     .execute(layout_data))
    """

    def __init__(self) -> None:
        """Initialize pipeline composer."""
        self._stages: list[tuple[str, Callable[[Any], Any]]] = []
        self._checkpoints: dict[str, Any] = {}
        self._rollback_enabled = False
        self._error_handler: Callable[[Exception, str], Any] | None = None

    def add_processing(
        self, pipeline: ProcessingPipeline, name: str = "processing"
    ) -> PipelineComposer:
        """Add processing pipeline stage.

        Args:
            pipeline: Processing pipeline to add
            name: Stage name for identification

        Returns:
            Self for chaining

        Examples:
            >>> composer = composer.add_processing(processor.pipeline())
        """
        self._stages.append((name, lambda data: pipeline.execute(data)))
        return self

    def add_transformation(
        self, pipeline: TransformationPipeline, name: str = "transformation"
    ) -> PipelineComposer:
        """Add transformation pipeline stage.

        Args:
            pipeline: Transformation pipeline to add
            name: Stage name for identification

        Returns:
            Self for chaining

        Examples:
            >>> composer = composer.add_transformation(TransformationPipeline(data))
        """
        self._stages.append((name, lambda _: pipeline.execute()))
        return self

    def add_validation(
        self,
        pipeline_factory: Callable[[Layout], ValidationPipeline],
        name: str = "validation",
    ) -> PipelineComposer:
        """Add validation pipeline stage.

        Args:
            pipeline_factory: Function to create validation pipeline from layout
            name: Stage name for identification

        Returns:
            Self for chaining

        Examples:
            >>> composer = composer.add_validation(lambda layout: ValidationPipeline(layout))
        """

        def validate(data: LayoutData) -> LayoutData:
            from zmk_layout.core import Layout

            # Create layout from data for validation
            layout = Layout.create_empty(data.title, data.notes or "")
            # Set the internal data
            layout._data = data
            validator = pipeline_factory(layout)
            # Run validation but return original data
            validation_result = validator.summary()
            if not validation_result.is_valid:
                # Store validation errors in variables
                if not data.variables:
                    data.variables = {}
                data.variables["validation_errors"] = [
                    str(e) for e in validation_result.errors
                ]
                data.variables["validation_warnings"] = [
                    str(w) for w in validation_result.warnings
                ]
            return data

        self._stages.append((name, validate))
        return self

    def add_custom_stage(
        self, name: str, operation: Callable[[Any], Any]
    ) -> PipelineComposer:
        """Add custom pipeline stage.

        Args:
            name: Stage name for identification
            operation: Custom operation to execute

        Returns:
            Self for chaining

        Examples:
            >>> composer = composer.add_custom_stage("normalize", lambda data: normalize(data))
        """
        self._stages.append((name, operation))
        return self

    def with_rollback(self) -> PipelineComposer:
        """Enable rollback on error.

        Returns:
            Self for chaining

        Examples:
            >>> composer = composer.with_rollback()
        """
        self._rollback_enabled = True
        return self

    def with_error_handler(
        self, handler: Callable[[Exception, str], Any]
    ) -> PipelineComposer:
        """Set custom error handler.

        Args:
            handler: Error handler function (exception, stage_name) -> Any

        Returns:
            Self for chaining

        Examples:
            >>> def handle_error(e: Exception, stage: str) -> None:
            ...     print(f"Error in {stage}: {e}")
            >>> composer = composer.with_error_handler(handle_error)
        """
        self._error_handler = handler
        return self

    def checkpoint(self, name: str) -> PipelineComposer:
        """Create checkpoint for rollback.

        Args:
            name: Checkpoint name

        Returns:
            Self for chaining

        Examples:
            >>> composer = composer.checkpoint("after_processing")
        """
        self._stages.append(
            (f"checkpoint_{name}", lambda data: self._save_checkpoint(name, data))
        )
        return self

    def _save_checkpoint(self, name: str, data: Any) -> Any:
        """Save data checkpoint.

        Args:
            name: Checkpoint name
            data: Data to checkpoint

        Returns:
            Original data (pass-through)
        """
        # Deep copy the data for checkpointing
        import copy

        self._checkpoints[name] = copy.deepcopy(data)
        return data

    def execute(self, initial_data: LayoutData) -> LayoutData:
        """Execute all pipeline stages in sequence.

        Args:
            initial_data: Initial layout data

        Returns:
            Final processed data

        Raises:
            Exception: If error occurs and no error handler is set

        Examples:
            >>> result = composer.execute(layout_data)
        """
        data = initial_data
        last_checkpoint_data = initial_data

        for stage_name, operation in self._stages:
            try:
                # Execute stage
                data = operation(data)

                # If this was a checkpoint stage, update the last checkpoint
                if stage_name.startswith("checkpoint_"):
                    last_checkpoint_data = data

            except Exception as e:
                if self._error_handler:
                    self._error_handler(e, stage_name)

                if self._rollback_enabled:
                    # Rollback to last checkpoint
                    return last_checkpoint_data

                # Re-raise if no error handling
                raise

        return data


class WorkflowBuilder:
    """Builder for creating common workflow patterns.

    This builder provides pre-configured workflows for common tasks like
    QMK migration, layout optimization, and validation.

    Examples:
        >>> workflow = WorkflowBuilder.qmk_migration_workflow()
        >>> result = workflow.execute(qmk_layout_data)
    """

    @staticmethod
    def qmk_migration_workflow() -> PipelineComposer:
        """Create QMK to ZMK migration workflow.

        Returns:
            Configured pipeline composer for QMK migration

        Examples:
            >>> workflow = WorkflowBuilder.qmk_migration_workflow()
            >>> zmk_layout = workflow.execute(qmk_layout)
        """
        from zmk_layout.processing import TransformationPipeline
        from zmk_layout.validation import ValidationPipeline

        composer = PipelineComposer()

        # Add transformation stage
        def transform_stage(data: LayoutData) -> LayoutData:
            pipeline = TransformationPipeline(data).migrate_from_qmk().optimize_layers()
            return pipeline.execute()

        # Add validation stage
        def validate_stage(layout: Layout) -> ValidationPipeline:
            return (
                ValidationPipeline(layout)
                .validate_bindings()
                .validate_layer_references()
                .validate_layer_accessibility()
            )

        return (
            composer.add_custom_stage("transform", transform_stage)
            .add_validation(validate_stage)
            .with_rollback()
        )

    @staticmethod
    def layout_optimization_workflow(max_layers: int = 10) -> PipelineComposer:
        """Create layout optimization workflow.

        Args:
            max_layers: Maximum number of layers to keep

        Returns:
            Configured pipeline composer for layout optimization

        Examples:
            >>> workflow = WorkflowBuilder.layout_optimization_workflow(max_layers=8)
            >>> optimized = workflow.execute(layout_data)
        """
        from zmk_layout.processing import TransformationPipeline
        from zmk_layout.validation import ValidationPipeline

        composer = PipelineComposer()

        # Add optimization stage
        def optimize_stage(data: LayoutData) -> LayoutData:
            pipeline = TransformationPipeline(data).optimize_layers(max_layers)
            return pipeline.execute()

        # Add validation stage
        def validate_stage(layout: Layout) -> ValidationPipeline:
            return (
                ValidationPipeline(layout)
                .validate_bindings()
                .validate_layer_references()
                .validate_layer_accessibility()
                .validate_key_positions()
            )

        return (
            composer.add_custom_stage("optimize", optimize_stage)
            .checkpoint("after_optimization")
            .add_validation(validate_stage)
            .with_rollback()
        )

    @staticmethod
    def home_row_mods_workflow(
        mod_config: dict[str, Any] | None = None,
    ) -> PipelineComposer:
        """Create home row mods application workflow.

        Args:
            mod_config: Home row mods configuration

        Returns:
            Configured pipeline composer for applying home row mods

        Examples:
            >>> workflow = WorkflowBuilder.home_row_mods_workflow()
            >>> with_hrm = workflow.execute(layout_data)
        """
        from zmk_layout.processing import TransformationPipeline
        from zmk_layout.validation import ValidationPipeline

        composer = PipelineComposer()

        # Add home row mods stage
        def hrm_stage(data: LayoutData) -> LayoutData:
            pipeline = TransformationPipeline(data).apply_home_row_mods(mod_config)
            return pipeline.execute()

        # Add validation stage
        def validate_stage(layout: Layout) -> ValidationPipeline:
            return (
                ValidationPipeline(layout)
                .validate_bindings()
                .validate_behavior_references()
                .validate_modifier_consistency()
                .validate_hold_tap_timing()
            )

        return composer.add_custom_stage("apply_hrm", hrm_stage).add_validation(
            validate_stage
        )

    @staticmethod
    def full_processing_workflow(
        processor: BaseKeymapProcessor, ast_roots: list[Any]
    ) -> PipelineComposer:
        """Create full keymap processing workflow.

        Args:
            processor: Keymap processor instance
            ast_roots: AST root nodes

        Returns:
            Configured pipeline composer for full processing

        Examples:
            >>> workflow = WorkflowBuilder.full_processing_workflow(processor, ast_roots)
            >>> processed = workflow.execute(layout_data)
        """
        from zmk_layout.processing import ProcessingPipeline
        from zmk_layout.validation import ValidationPipeline

        composer = PipelineComposer()

        # Create processing pipeline
        processing = (
            ProcessingPipeline(processor)
            .extract_defines(ast_roots)
            .extract_layers(ast_roots)
            .normalize_bindings()
            .transform_behaviors()
            .validate_bindings()
        )

        # Add validation stage
        def validate_stage(layout: Layout) -> ValidationPipeline:
            return (
                ValidationPipeline(layout)
                .validate_bindings()
                .validate_layer_references()
                .validate_key_positions()
                .validate_behavior_references()
                .validate_layer_accessibility()
            )

        return (
            composer.add_processing(processing)
            .checkpoint("after_processing")
            .add_validation(validate_stage)
        )


def compose_pipelines(*pipelines: Any) -> PipelineComposer:
    """Compose multiple pipelines into a single workflow.

    Args:
        *pipelines: Variable number of pipeline instances

    Returns:
        Configured pipeline composer

    Examples:
        >>> from zmk_layout.processing import ProcessingPipeline, TransformationPipeline
        >>> from zmk_layout.validation import ValidationPipeline
        >>>
        >>> workflow = compose_pipelines(
        ...     processing_pipeline,
        ...     transformation_pipeline,
        ...     validation_pipeline
        ... )
        >>> result = workflow.execute(layout_data)
    """
    composer = PipelineComposer()

    for i, pipeline in enumerate(pipelines):
        # Detect pipeline type and add appropriately
        pipeline_type = type(pipeline).__name__

        if "ProcessingPipeline" in pipeline_type:
            composer.add_processing(pipeline, f"processing_{i}")
        elif "TransformationPipeline" in pipeline_type:
            composer.add_transformation(pipeline, f"transformation_{i}")
        elif "ValidationPipeline" in pipeline_type:
            # For validation, we need a factory function
            # Use default argument to capture the current pipeline value
            def validation_factory(layout: Layout, p: Any = pipeline) -> Any:
                return p

            composer.add_validation(validation_factory, f"validation_{i}")
        else:
            # Add as custom stage
            # Use default argument to capture the current pipeline value
            def custom_stage(data: Any, p: Any = pipeline) -> Any:
                return p.execute(data)

            composer.add_custom_stage(f"pipeline_{i}", custom_stage)

    return composer
