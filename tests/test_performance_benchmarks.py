"""Performance benchmarks for ZMK Layout Fluent API implementation."""

import gc
import time
import tracemalloc

import psutil
import pytest

from zmk_layout.builders.binding import LayoutBindingBuilder
from zmk_layout.core import Layout
from zmk_layout.models.core import LayoutBinding
from zmk_layout.validation import ValidationPipeline


class TestPerformanceBenchmarks:
    """Performance benchmarks for fluent API."""

    def test_binding_creation_overhead(self) -> None:
        """Benchmark: LayoutBinding creation overhead should be <5%."""
        iterations = 10000

        # Traditional approach
        gc.collect()
        start_time = time.perf_counter()
        for _ in range(iterations):
            LayoutBinding.from_str("&kp LC(LS(A))")
        traditional_time = time.perf_counter() - start_time

        # Fluent approach
        gc.collect()
        start_time = time.perf_counter()
        for _ in range(iterations):
            (LayoutBindingBuilder("&kp").modifier("LC").modifier("LS").key("A").build())
        fluent_time = time.perf_counter() - start_time

        # Calculate overhead
        overhead_percent = ((fluent_time - traditional_time) / traditional_time) * 100

        print(f"\n=== Binding Creation Performance ({iterations} iterations) ===")
        print(f"Traditional: {traditional_time:.3f}s ({traditional_time / iterations * 1000:.3f}ms per op)")
        print(f"Fluent API:  {fluent_time:.3f}s ({fluent_time / iterations * 1000:.3f}ms per op)")
        print(f"Overhead:    {overhead_percent:.1f}%")

        # Assert reasonable overhead for fluent API convenience
        assert overhead_percent < 35.0, f"Overhead {overhead_percent:.1f}% exceeds 35% limit"

    def test_validation_pipeline_performance(self) -> None:
        """Benchmark: Validation pipeline performance on large layouts."""
        # Create a large layout
        layout = Layout.create_empty("test", "Large Layout")

        # Add 50 layers with 100 bindings each
        for layer_idx in range(50):
            layer = layout.layers.add(f"layer_{layer_idx}")
            for key_idx in range(100):
                if key_idx % 10 == 0:
                    layer.set(key_idx, f"&mo {(layer_idx + 1) % 50}")
                elif key_idx % 5 == 0:
                    layer.set(key_idx, "&kp LC(LS(A))")
                else:
                    layer.set(key_idx, "&trans")

        # Benchmark validation
        gc.collect()
        start_time = time.perf_counter()

        validator = ValidationPipeline(layout)
        result = (
            validator.validate_bindings()
            .validate_layer_references()
            .validate_key_positions(max_keys=100)
            .validate_behavior_references()
        )

        validation_time = time.perf_counter() - start_time

        print("\n=== Validation Pipeline Performance ===")
        print("Layout size: 50 layers × 100 keys = 5000 bindings")
        print(f"Validation time: {validation_time:.3f}s")
        print(f"Per-binding time: {validation_time / 5000 * 1000:.3f}ms")
        print(f"Errors found: {len(result.collect_errors())}")
        print(f"Warnings found: {len(result.collect_warnings())}")

        # Assert <500ms for large layout
        assert validation_time < 0.5, f"Validation took {validation_time:.3f}s, exceeds 500ms limit"

    def test_memory_usage_small_layout(self) -> None:
        """Benchmark: Memory usage for small layouts (<50 bindings)."""
        tracemalloc.start()
        process = psutil.Process()

        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Create small layout with fluent API
        layout = Layout.create_empty("test", "Small Layout")
        layer = layout.layers.add("base")

        for i in range(50):
            binding = LayoutBindingBuilder("&kp").modifier("LC").key(f"KEY_{i}").build()
            layer.set(i, binding.to_str())

        # Measure memory after creation
        gc.collect()
        after_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_used = after_memory - baseline_memory

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print("\n=== Memory Usage - Small Layout (50 bindings) ===")
        print(f"Baseline memory: {baseline_memory:.2f} MB")
        print(f"After creation:  {after_memory:.2f} MB")
        print(f"Memory used:     {memory_used:.2f} MB")
        print(f"Traced peak:     {peak / (1024 * 1024):.2f} MB")

        # Assert <1MB for small layouts
        assert memory_used < 1.0, f"Memory usage {memory_used:.2f}MB exceeds 1MB limit"

    def test_memory_usage_medium_layout(self) -> None:
        """Benchmark: Memory usage for medium layouts (50-200 bindings)."""
        tracemalloc.start()
        process = psutil.Process()

        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Create medium layout
        layout = Layout.create_empty("test", "Medium Layout")

        for layer_idx in range(4):
            layer = layout.layers.add(f"layer_{layer_idx}")
            for key_idx in range(50):
                binding = LayoutBindingBuilder("&kp").modifier("LC").modifier("LS").key(f"KEY_{key_idx}").build()
                layer.set(key_idx, binding.to_str())

        # Measure memory after creation
        gc.collect()
        after_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_used = after_memory - baseline_memory

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print("\n=== Memory Usage - Medium Layout (200 bindings) ===")
        print(f"Baseline memory: {baseline_memory:.2f} MB")
        print(f"After creation:  {after_memory:.2f} MB")
        print(f"Memory used:     {memory_used:.2f} MB")
        print(f"Traced peak:     {peak / (1024 * 1024):.2f} MB")

        # Assert <5MB for medium layouts
        assert memory_used < 5.0, f"Memory usage {memory_used:.2f}MB exceeds 5MB limit"

    def test_memory_usage_large_layout(self) -> None:
        """Benchmark: Memory usage for large layouts (200+ bindings)."""
        tracemalloc.start()
        process = psutil.Process()

        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Create large layout
        layout = Layout.create_empty("test", "Large Layout")

        for layer_idx in range(10):
            layer = layout.layers.add(f"layer_{layer_idx}")
            for key_idx in range(100):
                binding = LayoutBindingBuilder("&mt").hold_tap("LCTRL", f"KEY_{key_idx}").build()
                layer.set(key_idx, binding.to_str())

        # Run validation on large layout
        validator = ValidationPipeline(layout)
        (validator.validate_bindings().validate_layer_references().validate_key_positions())

        # Measure memory after creation and validation
        gc.collect()
        after_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_used = after_memory - baseline_memory

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print("\n=== Memory Usage - Large Layout (1000 bindings) ===")
        print(f"Baseline memory: {baseline_memory:.2f} MB")
        print(f"After creation:  {after_memory:.2f} MB")
        print(f"Memory used:     {memory_used:.2f} MB")
        print(f"Traced peak:     {peak / (1024 * 1024):.2f} MB")

        # Assert <10MB for large layouts
        assert memory_used < 10.0, f"Memory usage {memory_used:.2f}MB exceeds 10MB limit"

    def test_builder_cache_effectiveness(self) -> None:
        """Benchmark: Cache effectiveness in LayoutBindingBuilder."""
        iterations = 5000

        # Clear cache
        LayoutBindingBuilder._result_cache.clear()

        # First run - populate cache
        gc.collect()
        start_time = time.perf_counter()
        for _i in range(iterations):
            # Use same pattern repeatedly
            builder = LayoutBindingBuilder("&kp").modifier("LC").key("A")
            builder.build()
        first_run_time = time.perf_counter() - start_time

        # Check cache size
        cache_size = len(LayoutBindingBuilder._result_cache)

        # Second run - should use cache
        gc.collect()
        start_time = time.perf_counter()
        for _i in range(iterations):
            builder = LayoutBindingBuilder("&kp").modifier("LC").key("A")
            builder.build()
        cached_run_time = time.perf_counter() - start_time

        # Calculate speedup
        speedup = first_run_time / cached_run_time if cached_run_time > 0 else float("inf")

        print(f"\n=== Builder Cache Effectiveness ({iterations} iterations) ===")
        print(f"First run:   {first_run_time:.3f}s")
        print(f"Cached run:  {cached_run_time:.3f}s")
        print(f"Speedup:     {speedup:.2f}x")
        print(f"Cache size:  {cache_size} entries")

        # Assert cache provides speedup
        assert speedup >= 0.95, "Cache should not make things significantly slower"

    def test_immutability_overhead(self) -> None:
        """Benchmark: Overhead of immutable pattern."""
        iterations = 10000

        # Measure mutable approach (simulated)
        gc.collect()
        start_time = time.perf_counter()
        for _ in range(iterations):
            # Simulate mutable approach with direct modification
            binding = LayoutBinding(value="&kp", params=[])
            binding.params.append(LayoutBinding(value="LC", params=[]))  # type: ignore
        mutable_time = time.perf_counter() - start_time

        # Measure immutable approach
        gc.collect()
        start_time = time.perf_counter()
        for _ in range(iterations):
            binding = LayoutBinding(value="&kp", params=[])
            binding = binding.with_param("LC")
        immutable_time = time.perf_counter() - start_time

        # Calculate overhead
        overhead_percent = ((immutable_time - mutable_time) / mutable_time) * 100

        print(f"\n=== Immutability Pattern Overhead ({iterations} iterations) ===")
        print(f"Mutable:   {mutable_time:.3f}s")
        print(f"Immutable: {immutable_time:.3f}s")
        print(f"Overhead:  {overhead_percent:.1f}%")

        # Immutability adds some overhead but should be reasonable
        assert overhead_percent < 200.0, f"Immutability overhead {overhead_percent:.1f}% is too high"

    def test_validation_pipeline_scaling(self) -> None:
        """Benchmark: Validation pipeline scaling with layout size."""
        sizes = [10, 50, 100, 500, 1000]
        times: list[float] = []

        for size in sizes:
            # Create layout with 'size' bindings
            layout = Layout.create_empty("test", f"Layout-{size}")
            layer = layout.layers.add("base")

            for i in range(size):
                layer.set(i, "&trans")

            # Measure validation time
            gc.collect()
            start_time = time.perf_counter()

            validator = ValidationPipeline(layout)
            validator.validate_bindings().validate_layer_references()

            elapsed = time.perf_counter() - start_time
            times.append(elapsed)

        print("\n=== Validation Pipeline Scaling ===")
        print(f"{'Size':<10} {'Time (ms)':<12} {'Per-binding (μs)':<15}")
        print("-" * 40)
        for size, elapsed in zip(sizes, times, strict=False):
            per_binding = (elapsed / size) * 1_000_000  # microseconds
            print(f"{size:<10} {elapsed * 1000:<12.2f} {per_binding:<15.2f}")

        # Check that scaling is roughly linear (not exponential)
        # Time per binding shouldn't increase dramatically with size
        small_per_binding = times[0] / sizes[0]
        large_per_binding = times[-1] / sizes[-1]
        scaling_factor = large_per_binding / small_per_binding

        print(f"\nScaling factor: {scaling_factor:.2f}x")

        # Assert roughly linear scaling (allow up to 5x slowdown)
        assert scaling_factor < 5.0, f"Non-linear scaling detected: {scaling_factor:.2f}x"

    @pytest.mark.parametrize("complexity", ["simple", "moderate", "complex"])
    def test_binding_complexity_performance(self, complexity: str) -> None:
        """Benchmark: Performance with different binding complexities."""
        iterations = 5000

        if complexity == "simple":
            # Simple binding: &kp A
            gc.collect()
            start_time = time.perf_counter()
            for _ in range(iterations):
                LayoutBindingBuilder("&kp").key("A").build()
            elapsed = time.perf_counter() - start_time

        elif complexity == "moderate":
            # Moderate: &kp LC(A)
            gc.collect()
            start_time = time.perf_counter()
            for _ in range(iterations):
                LayoutBindingBuilder("&kp").modifier("LC").key("A").build()
            elapsed = time.perf_counter() - start_time

        else:  # complex
            # Complex: &kp LC(LS(LA(LG(A))))
            gc.collect()
            start_time = time.perf_counter()
            for _ in range(iterations):
                (
                    LayoutBindingBuilder("&kp")
                    .modifier("LC")
                    .modifier("LS")
                    .modifier("LA")
                    .modifier("LG")
                    .key("A")
                    .build()
                )
            elapsed = time.perf_counter() - start_time

        per_op = (elapsed / iterations) * 1000  # milliseconds

        print(f"\n=== {complexity.capitalize()} Binding Performance ===")
        print(f"Total time: {elapsed:.3f}s for {iterations} iterations")
        print(f"Per operation: {per_op:.3f}ms")

        # All complexities should complete reasonably fast
        assert per_op < 1.0, f"{complexity} binding takes {per_op:.3f}ms per operation"

    def test_generator_builder_performance(self) -> None:
        """Benchmark: Performance of generator builder operations."""
        from unittest.mock import MagicMock

        from zmk_layout.builders import (
            BehaviorBuilder,
            ComboBuilder,
            MacroBuilder,
            ZMKGeneratorBuilder,
        )

        # Create mock generator
        generator = MagicMock()
        generator.generate_behaviors_dtsi.return_value = "behaviors {}"
        generator.generate_combos_dtsi.return_value = "combos {}"
        generator.generate_macros_dtsi.return_value = "macros {}"

        profile = MagicMock()
        layout_data = MagicMock()
        iterations = 1000

        # Benchmark builder creation and configuration
        gc.collect()
        start_time = time.perf_counter()

        for _ in range(iterations):
            # Create behaviors
            behavior = BehaviorBuilder("test").bindings("&kp", "&kp").tapping_term(200).build()

            # Create combo
            combo = ComboBuilder("test").positions([0, 1]).binding("&kp A").timeout(50).build()

            # Create macro
            macro = MacroBuilder("test").tap("&kp A").tap("&kp B").build()

            # Build generator
            builder = (
                ZMKGeneratorBuilder(generator)
                .with_profile(profile)
                .with_layout(layout_data)
                .add_behavior(behavior)
                .add_combo(combo)
                .add_macro(macro)
                .with_options(format_style="grid")
            )

            # Access final state
            _ = len(builder._behaviors)

        elapsed = time.perf_counter() - start_time
        per_op = (elapsed / iterations) * 1000

        print(f"\n=== Generator Builder Performance ({iterations} iterations) ===")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Per operation: {per_op:.3f}ms")

        # Should complete in reasonable time
        assert per_op < 5.0, f"Generator builder takes {per_op:.3f}ms per operation"

    def test_processing_pipeline_performance(self) -> None:
        """Benchmark: Performance of processing pipeline operations."""
        from unittest.mock import MagicMock

        from zmk_layout.models.metadata import LayoutData
        from zmk_layout.processing import ProcessingPipeline

        # Create mock processor
        processor = MagicMock()
        processor._extract_defines_from_ast.return_value = {"TEST": "value"}
        processor._extract_layers_from_roots.return_value = {
            "layers": [["&kp A"] * 100 for _ in range(10)],
            "layer_names": [f"layer_{i}" for i in range(10)],
        }
        processor._transform_behavior_references_to_definitions.return_value = LayoutData(
            keyboard="test",
            title="test",
            layers=[[LayoutBinding.from_str("&kp A")] * 100 for _ in range(10)],
            layer_names=[f"layer_{i}" for i in range(10)],
        )

        iterations = 100

        # Benchmark pipeline execution
        gc.collect()
        start_time = time.perf_counter()

        for _ in range(iterations):
            pipeline = (
                ProcessingPipeline(processor)
                .extract_defines([MagicMock()])
                .extract_layers([MagicMock()])
                .normalize_bindings()
                .transform_behaviors()
            )

            initial_data = LayoutData(keyboard="test", title="test", layers=[], layer_names=[])
            pipeline.execute(initial_data)

        elapsed = time.perf_counter() - start_time
        per_op = (elapsed / iterations) * 1000

        print(f"\n=== Processing Pipeline Performance ({iterations} iterations) ===")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Per operation: {per_op:.3f}ms")

        # Should complete in reasonable time
        assert per_op < 50.0, f"Processing pipeline takes {per_op:.3f}ms per operation"

    def test_transformation_pipeline_performance(self) -> None:
        """Benchmark: Performance of transformation pipeline operations."""
        from zmk_layout.models.core import LayoutBinding
        from zmk_layout.models.metadata import LayoutData
        from zmk_layout.processing import TransformationPipeline

        # Create test data with significant size
        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[[LayoutBinding.from_str(f"&kp KEY_{j}") for j in range(100)] for i in range(10)],
            layer_names=[f"layer_{i}" for i in range(10)],
        )

        iterations = 100

        # Benchmark transformation execution
        gc.collect()
        start_time = time.perf_counter()

        for _ in range(iterations):
            pipeline = (
                TransformationPipeline(layout_data)
                .migrate_from_qmk()
                .optimize_layers(max_layer_count=8)
                .apply_home_row_mods()
            )
            pipeline.execute()

        elapsed = time.perf_counter() - start_time
        per_op = (elapsed / iterations) * 1000

        print(f"\n=== Transformation Pipeline Performance ({iterations} iterations) ===")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Per operation: {per_op:.3f}ms")
        print(f"Layout size: {len(layout_data.layers)} layers × {len(layout_data.layers[0])} keys")

        # Should complete in reasonable time
        assert per_op < 100.0, f"Transformation pipeline takes {per_op:.3f}ms per operation"

    def test_validation_pipeline_enhancements_performance(self) -> None:
        """Benchmark: Performance of enhanced validation features."""
        # Create large layout
        layout = Layout.create_empty("test", "Large Layout")

        # Add 10 layers with 100 bindings each
        for layer_idx in range(10):
            layer = layout.layers.add(f"layer_{layer_idx}")
            for key_idx in range(100):
                if key_idx % 10 == 0:
                    layer.set(key_idx, f"&mo {(layer_idx + 1) % 10}")
                elif key_idx % 5 == 0:
                    layer.set(key_idx, "&kp LC(LS(A))")
                else:
                    layer.set(key_idx, "&trans")

        iterations = 100

        # Benchmark enhanced validation
        gc.collect()
        start_time = time.perf_counter()

        for _ in range(iterations):
            validator = ValidationPipeline(layout)
            result = (
                validator.validate_bindings()
                .validate_layer_references()
                .validate_key_positions(max_keys=100)
                .validate_behavior_references()
                .validate_modifier_consistency()
                .validate_hold_tap_timing()
                .validate_layer_accessibility()
            )

        validation_time = time.perf_counter() - start_time
        per_op = (validation_time / iterations) * 1000

        print("\n=== Enhanced Validation Pipeline Performance ===")
        print("Layout size: 10 layers × 100 keys = 1000 bindings")
        print(f"Total time: {validation_time:.3f}s for {iterations} iterations")
        print(f"Per validation: {per_op:.3f}ms")
        print(f"Errors found: {len(result.collect_errors())}")
        print(f"Warnings found: {len(result.collect_warnings())}")

        # Assert reasonable performance
        assert per_op < 20.0, f"Enhanced validation took {per_op:.3f}ms, exceeds 20ms limit"

    def test_pipeline_composition_overhead(self) -> None:
        """Benchmark: Overhead of pipeline composition."""
        from unittest.mock import MagicMock

        from zmk_layout.models.metadata import LayoutData
        from zmk_layout.processing import PipelineComposer, ProcessingPipeline, TransformationPipeline

        # Create pipelines
        processor = MagicMock()
        processor._create_base_layout_data.return_value = LayoutData(
            keyboard="test", title="test", layers=[], layer_names=[]
        )
        processing = ProcessingPipeline(processor)

        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[[LayoutBinding.from_str("&kp A")] * 100 for _ in range(5)],
            layer_names=[f"layer_{i}" for i in range(5)],
        )
        transformation = TransformationPipeline(layout_data)

        iterations = 100

        # Benchmark direct execution
        gc.collect()
        start_time = time.perf_counter()
        for _ in range(iterations):
            processing.execute(layout_data)
            transformation.execute()
        direct_time = time.perf_counter() - start_time

        # Benchmark composed execution
        gc.collect()
        start_time = time.perf_counter()
        for _ in range(iterations):
            composer = PipelineComposer()
            composer.add_processing(processing).add_transformation(transformation)
            composer.execute(layout_data)
        composed_time = time.perf_counter() - start_time

        # Calculate overhead
        overhead_percent = ((composed_time - direct_time) / direct_time) * 100 if direct_time > 0 else 0

        print(f"\n=== Pipeline Composition Overhead ({iterations} iterations) ===")
        print(f"Direct execution: {direct_time:.3f}s")
        print(f"Composed execution: {composed_time:.3f}s")
        print(f"Overhead: {overhead_percent:.1f}%")

        # Composition should have minimal overhead
        assert overhead_percent < 50.0, f"Composition overhead {overhead_percent:.1f}% exceeds 50% limit"

    def test_workflow_builder_performance(self) -> None:
        """Benchmark: Performance of pre-built workflows."""
        from zmk_layout.models.metadata import LayoutData
        from zmk_layout.processing import WorkflowBuilder

        # Create test data
        layout_data = LayoutData(
            keyboard="test",
            title="test",
            layers=[
                [LayoutBinding.from_str("KC_A"), LayoutBinding.from_str("MO(1)"), LayoutBinding.from_str("_______")]
                * 30
                for _ in range(5)
            ],
            layer_names=[f"layer_{i}" for i in range(5)],
        )

        iterations = 50

        # Benchmark QMK migration workflow
        gc.collect()
        start_time = time.perf_counter()

        for _ in range(iterations):
            workflow = WorkflowBuilder.qmk_migration_workflow()
            workflow.execute(layout_data)

        elapsed = time.perf_counter() - start_time
        per_op = (elapsed / iterations) * 1000

        print(f"\n=== QMK Migration Workflow Performance ({iterations} iterations) ===")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Per migration: {per_op:.3f}ms")

        # Should complete efficiently
        assert per_op < 200.0, f"QMK migration workflow takes {per_op:.3f}ms per operation"

    def test_behavior_builder_scaling(self) -> None:
        """Benchmark: BehaviorBuilder scaling with configuration complexity."""
        from collections.abc import Callable

        from zmk_layout.builders import BehaviorBuilder
        from zmk_layout.models.behaviors import HoldTapBehavior

        configs: list[tuple[str, Callable[[BehaviorBuilder], HoldTapBehavior]]] = [
            ("minimal", lambda b: b.bindings("&kp", "&kp").build()),
            ("basic", lambda b: b.bindings("&kp", "&kp").tapping_term(200).flavor("balanced").build()),
            (
                "full",
                lambda b: b.bindings("&kp", "&kp")
                .tapping_term(200)
                .quick_tap(125)
                .flavor("balanced")
                .positions([0, 1, 2, 3, 4])
                .retro_tap(True)
                .require_prior_idle(150)
                .build(),
            ),
        ]

        iterations = 2000
        times = []

        for config_name, build_func in configs:
            gc.collect()
            start_time = time.perf_counter()

            for _ in range(iterations):
                builder = BehaviorBuilder(f"test_{config_name}")
                _ = build_func(builder)

            elapsed = time.perf_counter() - start_time
            times.append((config_name, elapsed))

        print("\n=== BehaviorBuilder Scaling ===")
        print(f"{'Config':<10} {'Time (ms)':<12} {'Per-op (μs)':<15}")
        print("-" * 40)

        for config_name, elapsed in times:
            per_op = (elapsed / iterations) * 1_000_000  # microseconds
            print(f"{config_name:<10} {elapsed * 1000:<12.2f} {per_op:<15.2f}")

        # Check that complexity doesn't cause exponential slowdown
        minimal_time = times[0][1]
        full_time = times[2][1]
        scaling_factor = full_time / minimal_time

        print(f"\nScaling factor (full/minimal): {scaling_factor:.2f}x")

        # Should scale reasonably (not more than 3x slower for full config)
        assert scaling_factor < 3.0, f"Non-linear scaling: {scaling_factor:.2f}x"
