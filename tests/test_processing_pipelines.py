"""Tests for Phase 3 processing and transformation pipelines."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from zmk_layout.core import Layout
from zmk_layout.models.core import LayoutBinding
from zmk_layout.models.metadata import LayoutData
from zmk_layout.processing import (
    PipelineComposer,
    ProcessingPipeline,
    TransformationPipeline,
    WorkflowBuilder,
    compose_pipelines,
)
from zmk_layout.validation import ValidationPipeline


class TestProcessingPipeline:
    """Test suite for ProcessingPipeline."""

    def test_extract_defines(self) -> None:
        """Test define extraction from AST."""
        # Create mock processor
        processor = MagicMock()
        processor._extract_defines_from_ast.return_value = {"HYPER": "LC(LS(LA(LGUI)))", "MEH": "LC(LS(LA))"}
        processor._create_base_layout_data.return_value = LayoutData(
            keyboard="test", title="Test Layout", layers=[], layer_names=[]
        )

        # Create pipeline and extract defines
        pipeline = ProcessingPipeline(processor)
        ast_roots = [MagicMock(), MagicMock()]

        result = pipeline.extract_defines(ast_roots).execute()

        # Verify define extraction was called
        processor._extract_defines_from_ast.assert_called_once_with(ast_roots)

        # Check variables was updated
        assert result.variables is not None
        assert "defines" in result.variables
        assert result.variables["defines"]["HYPER"] == "LC(LS(LA(LGUI)))"

    def test_extract_layers(self) -> None:
        """Test layer extraction from AST."""
        processor = MagicMock()
        processor._extract_layers_from_roots.return_value = {
            "layers": [["&kp A", "&kp B"], ["&kp C", "&kp D"]],
            "layer_names": ["base", "nav"],
        }
        processor._create_base_layout_data.return_value = LayoutData(
            keyboard="test", title="Test", layers=[], layer_names=[]
        )

        pipeline = ProcessingPipeline(processor)
        ast_roots = [MagicMock()]

        result = pipeline.extract_layers(ast_roots).execute()

        # Verify layers were extracted
        assert len(result.layers) == 2
        assert len(result.layer_names) == 2
        assert result.layer_names == ["base", "nav"]

    def test_normalize_bindings(self) -> None:
        """Test binding normalization."""
        processor = MagicMock()
        initial_data = LayoutData(
            keyboard="test",
            title="Test",
            layers=[
                [LayoutBinding.from_str("&kp A"), LayoutBinding.from_str("&trans"), LayoutBinding.from_str("&kp LC(C)")]
            ],
            layer_names=["base"],
        )

        pipeline = ProcessingPipeline(processor)
        result = pipeline.normalize_bindings().execute(initial_data)

        # All bindings should be LayoutBinding objects
        assert all(isinstance(binding, LayoutBinding) for layer in result.layers for binding in layer)

        # Check specific binding values
        assert result.layers[0][0].value == "&kp"
        assert result.layers[0][1].value == "&trans"

    def test_apply_preprocessor_substitutions(self) -> None:
        """Test preprocessor define substitutions."""
        processor = MagicMock()
        initial_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[[LayoutBinding.from_str("&kp HYPER"), LayoutBinding.from_str("&kp MEH")]],
            layer_names=["base"],
        )

        defines = {"HYPER": "LC(LS(LA(LGUI)))", "MEH": "LC(LS(LA))"}

        pipeline = ProcessingPipeline(processor)
        result = pipeline.apply_preprocessor_substitutions(defines).execute(initial_data)

        # Check substitutions were applied
        assert "LC(LS(LA(LGUI)))" in result.layers[0][0].to_str()
        assert "LC(LS(LA))" in result.layers[0][1].to_str()

    def test_filter_layers(self) -> None:
        """Test layer filtering."""
        processor = MagicMock()
        initial_data = LayoutData(
            keyboard="test",
            title="Test",
            layers=[
                [LayoutBinding.from_str("&kp A")],
                [LayoutBinding.from_str("&kp B")],
                [LayoutBinding.from_str("&kp C")],
                [LayoutBinding.from_str("&kp D")],
            ],
            layer_names=["base", "nav", "sym", "num"],
        )

        pipeline = ProcessingPipeline(processor)
        result = pipeline.filter_layers(["base", "sym"]).execute(initial_data)

        # Only requested layers should remain
        assert len(result.layers) == 2
        assert result.layer_names == ["base", "sym"]
        # Check first binding of each layer
        assert result.layers[0][0].to_str() == "&kp A"
        assert result.layers[1][0].to_str() == "&kp C"

    def test_error_collection(self) -> None:
        """Test that errors are collected rather than failing fast."""
        processor = MagicMock()
        processor._extract_defines_from_ast.side_effect = Exception("Define extraction failed")
        initial_data = LayoutData(
            keyboard="test", title="Test", layers=[], layer_names=[]
        )

        pipeline = ProcessingPipeline(processor)
        ast_roots = [MagicMock()]

        # Should not raise, but collect error
        result = pipeline.extract_defines(ast_roots).execute(initial_data)

        # Data should be unchanged
        assert result.title == "Test"

    def test_pipeline_chaining(self) -> None:
        """Test chaining multiple operations."""
        processor = MagicMock()
        processor._extract_defines_from_ast.return_value = {"TEST": "value"}
        processor._extract_layers_from_roots.return_value = {"layers": [["&kp A"]], "layer_names": ["base"]}
        processor._transform_behavior_references_to_definitions.return_value = LayoutData(
            keyboard="test", title="test", layers=[[LayoutBinding.from_str("&kp A")]], layer_names=["base"]
        )
        processor._create_base_layout_data.return_value = LayoutData(
            keyboard="test", title="Test", layers=[], layer_names=[]
        )

        pipeline = (
            ProcessingPipeline(processor)
            .extract_defines([MagicMock()])
            .extract_layers([MagicMock()])
            .normalize_bindings()
            .transform_behaviors()
        )

        result = pipeline.execute()

        # All operations should have been applied
        assert result.layer_names == ["base"]
        assert len(result.layers) == 1


class TestTransformationPipeline:
    """Test suite for TransformationPipeline."""

    def test_migrate_from_qmk(self) -> None:
        """Test QMK to ZMK migration."""
        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[
                [LayoutBinding.from_str("KC_A"), LayoutBinding.from_str("MO(1)"), LayoutBinding.from_str("_______")]
            ],
            layer_names=["base"],
        )

        pipeline = TransformationPipeline(layout_data)
        result = pipeline.migrate_from_qmk().execute()

        # Check conversions
        assert result.layers[0][0].to_str() == "&kp A"
        assert result.layers[0][1].to_str() == "&mo 1"
        assert result.layers[0][2].to_str() == "&trans"

        # Check variables
        assert result.variables is not None
        assert result.variables.get("migrated_from") == "qmk"

    def test_remap_keys(self) -> None:
        """Test key remapping."""
        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[[LayoutBinding.from_str("&kp SPACE"), LayoutBinding.from_str("&kp ENTER")]],
            layer_names=["base"],
        )

        key_mapping = {"SPACE": "SPC", "ENTER": "RET"}

        pipeline = TransformationPipeline(layout_data)
        result = pipeline.remap_keys(key_mapping).execute()

        # Check remapping
        assert "SPC" in result.layers[0][0].to_str()
        assert "RET" in result.layers[0][1].to_str()

    def test_optimize_layers(self) -> None:
        """Test layer optimization."""
        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[
                [LayoutBinding.from_str("&kp A")],  # Many keys
                [LayoutBinding.from_str("&trans")],  # All transparent
                [LayoutBinding.from_str("&kp B")],  # Few keys
            ],
            layer_names=["base", "empty", "nav"],
        )

        pipeline = TransformationPipeline(layout_data)
        result = pipeline.optimize_layers(max_layer_count=2).execute()

        # Should keep only the most used layers
        assert len(result.layers) <= 2
        assert "empty" not in result.layer_names  # Empty layer should be removed

    def test_apply_home_row_mods(self) -> None:
        """Test home row mods application."""
        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[[LayoutBinding.from_str(f"&kp KEY_{i}") for i in range(30)]],
            layer_names=["base"],
        )

        mod_config = {
            "left": {"positions": [10, 11, 12, 13], "mods": ["LSFT", "LCTL", "LALT", "LGUI"]},
            "tapping_term": 200,
        }

        pipeline = TransformationPipeline(layout_data)
        result = pipeline.apply_home_row_mods(mod_config).execute()

        # Check that home row positions have been modified
        assert "&hm_l" in result.layers[0][10].to_str()
        assert "LSFT" in result.layers[0][10].to_str()

        # Check variables
        assert result.variables is not None
        assert result.variables.get("home_row_mods", {}).get("enabled") is True

    def test_add_combo_layer(self) -> None:
        """Test adding combo definitions."""
        layout_data = LayoutData(keyboard="test", title="Test", layers=[[]], layer_names=["base"])

        from zmk_layout.builders import ComboBuilder

        combo = ComboBuilder("copy").positions([12, 13]).binding("&kp LC(C)").timeout(50).build()

        pipeline = TransformationPipeline(layout_data)
        result = pipeline.add_combo_layer([combo]).execute()

        # Check combos were added
        assert len(result.combos) == 1
        assert result.combos[0].name == "copy"

    def test_rename_layers(self) -> None:
        """Test layer renaming."""
        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[[], [], []],
            layer_names=["layer_0", "layer_1", "layer_2"],
        )

        name_mapping = {"layer_0": "base", "layer_1": "navigation", "layer_2": "symbols"}

        pipeline = TransformationPipeline(layout_data)
        result = pipeline.rename_layers(name_mapping).execute()

        # Check renamed layers
        assert result.layer_names == ["base", "navigation", "symbols"]

    def test_merge_layers(self) -> None:
        """Test layer merging."""
        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[
                [LayoutBinding.from_str("&kp A"), LayoutBinding.from_str("&trans")],
                [LayoutBinding.from_str("&trans"), LayoutBinding.from_str("&kp B")],
            ],
            layer_names=["source", "target"],
        )

        pipeline = TransformationPipeline(layout_data)
        result = pipeline.merge_layers("source", "target").execute()

        # Source layer should be removed, target should have merged bindings
        assert len(result.layers) == 1
        assert "source" not in result.layer_names
        assert result.layers[0][0].to_str() == "&kp A"  # From source
        assert result.layers[0][1].to_str() == "&kp B"  # From target


class TestValidationPipelineEnhancements:
    """Test suite for enhanced ValidationPipeline features."""

    def test_validate_modifier_consistency(self) -> None:
        """Test modifier consistency validation."""
        layout = Layout.create_empty("test", "Test Layout")
        layer = layout.layers.add("base")

        # Add imbalanced modifiers
        for i in range(10):
            layer.set(i, "&kp LSFT")
        layer.set(10, "&kp RSFT")  # Only one right shift

        validator = ValidationPipeline(layout)
        result = validator.validate_modifier_consistency()

        # Should warn about imbalance
        warnings = result.collect_warnings()
        assert any("Imbalanced modifier usage" in str(w) for w in warnings)

    def test_validate_hold_tap_timing(self) -> None:
        """Test hold-tap timing validation."""
        layout = Layout.create_empty("test", "Test Layout")

        # Mock behaviors attribute
        mock_behavior = MagicMock()
        mock_behavior.name = "hm_l"
        mock_behavior.tapping_term_ms = 100  # Too low
        # Create a mock behaviors manager with proper interface
        behaviors_mock = MagicMock()
        behaviors_mock.all.return_value = [mock_behavior]
        # Access the private attribute to set it for testing
        layout._behaviors = behaviors_mock

        validator = ValidationPipeline(layout)
        result = validator.validate_hold_tap_timing()

        # Should warn about low tapping term
        warnings = result.collect_warnings()
        assert any("low tapping term" in str(w) for w in warnings)

    def test_validate_layer_accessibility(self) -> None:
        """Test layer accessibility validation."""
        layout = Layout.create_empty("test", "Test Layout")

        # Create layers with one unreachable
        base = layout.layers.add("base")
        layout.layers.add("nav")
        layout.layers.add("unreachable")

        # Add layer navigation from base to nav only
        base.set(0, "&mo 1")  # Can reach nav
        # No way to reach layer 2 (unreachable)

        validator = ValidationPipeline(layout)
        result = validator.validate_layer_accessibility()

        # Should warn about unreachable layer
        warnings = result.collect_warnings()
        assert any("not reachable from base layer" in str(w) for w in warnings)


class TestPipelineComposer:
    """Test suite for PipelineComposer."""

    def test_compose_multiple_pipelines(self) -> None:
        """Test composing processing and transformation pipelines."""
        # Create mock pipelines
        processor = MagicMock()
        processor._create_base_layout_data.return_value = LayoutData(
            keyboard="test", title="Test", layers=[], layer_names=[]
        )

        processing = ProcessingPipeline(processor)
        layout_data = LayoutData(keyboard="test", title="Test", layers=[], layer_names=[])
        transformation = TransformationPipeline(layout_data)

        # Compose pipelines
        composer = PipelineComposer()
        composer.add_processing(processing).add_transformation(transformation)

        # Execute composition
        result = composer.execute(layout_data)

        # Should return layout data
        assert isinstance(result, LayoutData)

    def test_checkpoint_and_rollback(self) -> None:
        """Test checkpoint creation and rollback on error."""
        layout_data = LayoutData(keyboard="test", title="Test", layers=[], layer_names=[])

        # Create composer with rollback
        composer = PipelineComposer()

        # Add checkpoint BEFORE the modification
        composer.checkpoint("before_modify")

        # Add successful stage
        composer.add_custom_stage("modify", lambda data: data.model_copy(update={"title": "modified"}))

        # Add checkpoint after the modification
        composer.checkpoint("after_modify")

        # Add another successful stage
        composer.add_custom_stage("modify2", lambda data: data.model_copy(update={"title": "modified2"}))

        # Add failing stage
        def failing_stage(data: LayoutData) -> LayoutData:
            raise Exception("Intentional failure")

        composer.add_custom_stage("fail", failing_stage)

        # Enable rollback
        composer.with_rollback()

        # Execute with error handling
        error_called = False

        def error_handler(e: Exception, stage: str) -> None:
            nonlocal error_called
            error_called = True
            assert stage == "fail"

        composer.with_error_handler(error_handler)

        # Should rollback to last checkpoint (after_modify)
        result = composer.execute(layout_data)

        # Check rollback worked - should roll back to "after_modify" checkpoint which has "modified"
        assert error_called
        assert result.title == "modified"  # Should have rolled back to after_modify checkpoint

    def test_custom_error_handler(self) -> None:
        """Test custom error handler."""
        layout_data = LayoutData(keyboard="test", title="Test", layers=[], layer_names=[])

        composer = PipelineComposer()

        # Add failing stage
        def failing_stage(data: LayoutData) -> LayoutData:
            raise ValueError("Test error")

        composer.add_custom_stage("fail", failing_stage)

        # Track error handling
        handled_error = None
        handled_stage = None

        def error_handler(e: Exception, stage: str) -> None:
            nonlocal handled_error, handled_stage
            handled_error = e
            handled_stage = stage

        composer.with_error_handler(error_handler)

        # Execute (should not raise due to handler)
        with pytest.raises(ValueError):
            composer.execute(layout_data)

        # Error should have been handled
        assert isinstance(handled_error, ValueError)
        assert handled_stage == "fail"


class TestWorkflowBuilder:
    """Test suite for WorkflowBuilder."""

    def test_qmk_migration_workflow(self) -> None:
        """Test QMK migration workflow creation."""
        workflow = WorkflowBuilder.qmk_migration_workflow()

        # Should have transformation and validation stages
        assert len(workflow._stages) >= 2
        assert any("transform" in stage[0] for stage in workflow._stages)
        assert any("validation" in stage[0] for stage in workflow._stages)

        # Should have rollback enabled
        assert workflow._rollback_enabled

    def test_layout_optimization_workflow(self) -> None:
        """Test layout optimization workflow."""
        workflow = WorkflowBuilder.layout_optimization_workflow(max_layers=8)

        # Should have optimization and validation stages
        assert len(workflow._stages) >= 2
        assert any("optimize" in stage[0] for stage in workflow._stages)
        assert any("checkpoint" in stage[0] for stage in workflow._stages)

    def test_home_row_mods_workflow(self) -> None:
        """Test home row mods workflow."""
        workflow = WorkflowBuilder.home_row_mods_workflow()

        # Should have HRM application and validation
        assert len(workflow._stages) >= 2
        assert any("hrm" in stage[0] for stage in workflow._stages)

    def test_full_processing_workflow(self) -> None:
        """Test full processing workflow."""
        processor = MagicMock()
        ast_roots = [MagicMock()]

        workflow = WorkflowBuilder.full_processing_workflow(processor, ast_roots)

        # Should have processing and validation stages
        assert len(workflow._stages) >= 2
        assert any("processing" in stage[0] for stage in workflow._stages)
        assert any("checkpoint" in stage[0] for stage in workflow._stages)


class TestComposeFunction:
    """Test suite for compose_pipelines function."""

    def test_compose_different_pipeline_types(self) -> None:
        """Test composing different pipeline types."""
        # Create mock pipelines
        processor = MagicMock()
        processing = ProcessingPipeline(processor)

        layout_data = LayoutData(keyboard="test", title="Test", layers=[], layer_names=[])
        transformation = TransformationPipeline(layout_data)

        layout = Layout.create_empty("test", "Test")
        validation = ValidationPipeline(layout)

        # Compose all three types
        workflow = compose_pipelines(processing, transformation, validation)

        # Should have stages for each pipeline
        assert len(workflow._stages) == 3
        assert any("processing" in stage[0] for stage in workflow._stages)
        assert any("transformation" in stage[0] for stage in workflow._stages)
        assert any("validation" in stage[0] for stage in workflow._stages)
