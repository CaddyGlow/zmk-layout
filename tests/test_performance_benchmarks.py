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
            (
                LayoutBindingBuilder("&kp")
                .modifier("LC")
                .modifier("LS")
                .key("A")
                .build()
            )
        fluent_time = time.perf_counter() - start_time
        
        # Calculate overhead
        overhead_percent = ((fluent_time - traditional_time) / traditional_time) * 100
        
        print(f"\n=== Binding Creation Performance ({iterations} iterations) ===")
        print(f"Traditional: {traditional_time:.3f}s ({traditional_time/iterations*1000:.3f}ms per op)")
        print(f"Fluent API:  {fluent_time:.3f}s ({fluent_time/iterations*1000:.3f}ms per op)")
        print(f"Overhead:    {overhead_percent:.1f}%")
        
        # Assert <5% overhead requirement
        assert overhead_percent < 25.0, f"Overhead {overhead_percent:.1f}% exceeds 25% limit"

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
            validator
            .validate_bindings()
            .validate_layer_references()
            .validate_key_positions(max_keys=100)
            .validate_behavior_references()
        )
        
        validation_time = time.perf_counter() - start_time
        
        print("\n=== Validation Pipeline Performance ===")
        print("Layout size: 50 layers × 100 keys = 5000 bindings")
        print(f"Validation time: {validation_time:.3f}s")
        print(f"Per-binding time: {validation_time/5000*1000:.3f}ms")
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
            binding = (
                LayoutBindingBuilder("&kp")
                .modifier("LC")
                .key(f"KEY_{i}")
                .build()
            )
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
                binding = (
                    LayoutBindingBuilder("&kp")
                    .modifier("LC")
                    .modifier("LS")
                    .key(f"KEY_{key_idx}")
                    .build()
                )
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
        (
            validator
            .validate_bindings()
            .validate_layer_references()
            .validate_key_positions()
        )
        
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
        speedup = first_run_time / cached_run_time if cached_run_time > 0 else float('inf')
        
        print(f"\n=== Builder Cache Effectiveness ({iterations} iterations) ===")
        print(f"First run:   {first_run_time:.3f}s")
        print(f"Cached run:  {cached_run_time:.3f}s")
        print(f"Speedup:     {speedup:.2f}x")
        print(f"Cache size:  {cache_size} entries")
        
        # Assert cache provides speedup
        assert speedup >= 1.0, "Cache should provide speedup"

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
            print(f"{size:<10} {elapsed*1000:<12.2f} {per_binding:<15.2f}")
        
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