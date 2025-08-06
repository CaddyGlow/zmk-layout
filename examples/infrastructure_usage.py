#!/usr/bin/env python3
"""Examples demonstrating Phase 4 infrastructure components."""

import time
from pathlib import Path
from typing import Any

from zmk_layout.infrastructure import (
    ChainInspector,
    DebugFormatter,
    ProviderBuilder,
    TemplateContextBuilder,
)
from zmk_layout.infrastructure.performance import (
    LazyProperty,
    LRUCache,
    get_performance_monitor,
    memoize,
    profile,
)
from zmk_layout.processing.chain_composition import (
    PipelineComposer,
    WorkflowBuilder,
)

# ============================================================================
# Provider Configuration Examples
# ============================================================================


def provider_configuration_example():
    """Demonstrate provider configuration."""
    print("\n=== Provider Configuration Example ===\n")

    # Create custom file adapter
    class SimpleFileAdapter:
        """Simple file adapter for demonstration."""

        def read_file(self, path: Path) -> str:
            """Read file contents."""
            return path.read_text()

        def write_file(self, path: Path, content: str) -> None:
            """Write file contents."""
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

        def exists(self, path: Path) -> bool:
            """Check if file exists."""
            return path.exists()

    # Configure providers fluently
    providers = (
        ProviderBuilder()
        .with_file_adapter(SimpleFileAdapter())
        .enable_caching(size=512)
        .enable_debug_mode()
        .enable_performance_tracking()
        .from_environment()
        .validate()
        .build()
    )

    print(f"Caching enabled: {providers.enable_caching}")
    print(f"Cache size: {providers.cache_size}")
    print(f"Debug mode: {providers.debug_mode}")
    print(f"Performance tracking: {providers.performance_tracking}")

    return providers


# ============================================================================
# Template Context Building Examples
# ============================================================================


def template_context_example():
    """Demonstrate template context building."""
    print("\n=== Template Context Building Example ===\n")

    from zmk_layout.models.core import LayoutBinding
    from zmk_layout.models.metadata import LayoutData

    # Create sample layout data
    layout_data = LayoutData(
        keyboard="glove80",
        title="Example Layout",
        layers=[
            [LayoutBinding.from_str("&kp A"), LayoutBinding.from_str("&kp B")],
            [LayoutBinding.from_str("&mo 1"), LayoutBinding.from_str("&trans")],
        ],
        layer_names=["base", "lower"],
        notes="Example layout for demonstration",
    )

    # Build comprehensive context
    context = (
        TemplateContextBuilder()
        # Layout information
        .with_layout(layout_data)
        # Generation metadata
        .with_generation_metadata(author="Example Author", version="1.0.0")
        # Custom variables
        .with_custom_vars(theme="dark", layout_style="ergonomic", custom_setting="value")
        # Feature flags
        .with_features(home_row_mods=True, mouse_keys=False, rgb_underglow=True, oled_display=False)
        # DTSI content
        .with_dtsi_content(
            layer_defines="#define BASE 0\n#define LOWER 1", keymap_node='keymap { compatible = "zmk,keymap"; }'
        )
        # Validate and build
        .validate_completeness()
        .build()
    )

    # Preview context
    print(f"Keyboard: {context.keyboard}")
    print(f"Title: {context.title}")
    print(f"Layers: {context.layer_count}")
    print(f"Features: {list(context.features.keys())}")
    print(f"Custom vars: {list(context.custom_vars.keys())}")

    return context


# ============================================================================
# Performance Optimization Examples
# ============================================================================


def performance_optimization_example():
    """Demonstrate performance optimization utilities."""
    print("\n=== Performance Optimization Example ===\n")

    # 1. LRU Cache
    print("1. LRU Cache Demo:")
    cache = LRUCache(maxsize=3)

    # Add items
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    cache.put("key3", "value3")

    # Access key2 (makes it most recently used)
    _ = cache.get("key2")

    # Add key4 (evicts key1 as least recently used)
    cache.put("key4", "value4")

    # Check what's in cache
    print(f"  key1: {cache.get('key1')}")  # None (evicted)
    print(f"  key2: {cache.get('key2')}")  # value2
    print(f"  Cache stats: {cache.stats()}")

    # 2. Memoization
    print("\n2. Memoization Demo:")

    @memoize(maxsize=10)
    def fibonacci(n: int) -> int:
        """Compute fibonacci number (cached)."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    # First call: computes
    start = time.perf_counter()
    result1 = fibonacci(30)
    time1 = time.perf_counter() - start

    # Second call: cached
    start = time.perf_counter()
    result2 = fibonacci(30)
    time2 = time.perf_counter() - start

    print(f"  First call: {time1 * 1000:.3f}ms, result={result1}")
    print(f"  Second call: {time2 * 1000:.3f}ms, result={result2}")
    print(f"  Speedup: {time1 / time2:.1f}x")
    print(f"  Cache stats: {fibonacci.cache_stats()}")

    # 3. Lazy Properties
    print("\n3. Lazy Property Demo:")

    class LayoutAnalyzer:
        """Analyzer with lazy properties."""

        def __init__(self, data: str):
            self.data = data
            self.compute_count = 0

        @LazyProperty
        def analysis_result(self) -> dict[str, Any]:
            """Expensive analysis (computed once)."""
            self.compute_count += 1
            time.sleep(0.1)  # Simulate expensive computation
            return {"length": len(self.data), "words": len(self.data.split())}

    analyzer = LayoutAnalyzer("sample layout data")
    print(f"  Compute count before: {analyzer.compute_count}")

    # First access: computes
    result1 = analyzer.analysis_result
    print(f"  First access: {result1}")
    print(f"  Compute count after first: {analyzer.compute_count}")

    # Second access: cached
    result2 = analyzer.analysis_result
    print(f"  Second access: {result2}")
    print(f"  Compute count after second: {analyzer.compute_count}")

    # 4. Performance Monitoring
    print("\n4. Performance Monitoring Demo:")
    monitor = get_performance_monitor()

    @profile("example_operation")
    def example_operation(n: int) -> int:
        """Example operation to profile."""
        total = 0
        for i in range(n):
            total += i * i
        return total

    # Run operations with monitoring
    with monitor.measure("manual_measurement"):
        time.sleep(0.05)
        _ = example_operation(10000)

    # Multiple runs for statistics
    for _ in range(5):
        _ = example_operation(10000)

    # Print report
    monitor.print_report()


# ============================================================================
# Debug Tools Examples
# ============================================================================


def debug_tools_example():
    """Demonstrate debug tools."""
    print("\n=== Debug Tools Example ===\n")

    from zmk_layout.builders.binding import LayoutBindingBuilder

    # 1. Chain Inspector
    print("1. Chain Inspector Demo:")
    inspector = ChainInspector()

    # Wrap builder for inspection
    builder = inspector.wrap(LayoutBindingBuilder("&kp"))

    # Use builder (all calls tracked)
    binding = builder.modifier("LC").modifier("LS").key("A").build()

    print(f"  Result: {binding.to_str()}")

    # Inspect chain
    inspector.print_chain_history()
    inspector.print_performance_summary()

    # 2. Debug Formatter
    print("\n2. Debug Formatter Demo:")
    formatter = DebugFormatter(max_depth=2, max_width=60)

    # Format complex object
    complex_obj = {
        "name": "Test Layout",
        "layers": [
            {"name": "base", "bindings": ["&kp A", "&kp B", "&kp C"]},
            {"name": "lower", "bindings": ["&mo 1", "&trans", "&trans"]},
        ],
        "metadata": {"author": "Test", "version": "1.0.0", "created": "2025-01-01"},
    }

    formatted = formatter.format(complex_obj)
    print("  Formatted object:")
    for line in formatted.split("\n")[:10]:  # First 10 lines
        print(f"    {line}")

    # 3. Builder State
    print("\n3. Builder State Demo:")
    from zmk_layout.infrastructure.debug_tools import BuilderState

    # Create builder
    test_builder = LayoutBindingBuilder("&mt").hold_tap("LCTRL", "A").with_tapping_term(200)

    # Capture state
    state = BuilderState.from_builder(test_builder)

    print(f"  Class: {state.class_name}")
    print(f"  Methods called: {state.method_calls[:3]}")  # First 3
    print(f"  Current binding: {state.attributes.get('_binding', {}).get('value')}")


# ============================================================================
# Pipeline Composition Examples
# ============================================================================


def pipeline_composition_example():
    """Demonstrate pipeline composition."""
    print("\n=== Pipeline Composition Example ===\n")

    from zmk_layout.models.core import LayoutBinding
    from zmk_layout.models.metadata import LayoutData

    # Create sample data
    layout_data = LayoutData(
        keyboard="test",
        title="Pipeline Test",
        layers=[
            [LayoutBinding.from_str("KC_A"), LayoutBinding.from_str("MO(1)")],
            [LayoutBinding.from_str("_______"), LayoutBinding.from_str("KC_B")],
        ],
        layer_names=["base", "lower"],
    )

    # 1. Basic Composition
    print("1. Basic Pipeline Composition:")

    def transform_stage(data: LayoutData) -> LayoutData:
        """Example transformation stage."""
        # Convert KC_ to &kp
        for layer in data.layers:
            for i, binding in enumerate(layer):
                if binding.value.startswith("KC_"):
                    key = binding.value[3:]
                    layer[i] = LayoutBinding.from_str(f"&kp {key}")
        return data

    def optimize_stage(data: LayoutData) -> LayoutData:
        """Example optimization stage."""
        # Replace _______ with &trans
        for layer in data.layers:
            for i, binding in enumerate(layer):
                if binding.value == "_______":
                    layer[i] = LayoutBinding.from_str("&trans")
        return data

    composer = (
        PipelineComposer()
        .add_custom_stage("transform", transform_stage)
        .add_custom_stage("optimize", optimize_stage)
        .with_rollback()
    )

    result = composer.execute(layout_data)

    print("  Original binding: KC_A")
    print(f"  Transformed: {result.layers[0][0].to_str()}")
    print("  Original binding: _______")
    print(f"  Optimized: {result.layers[1][0].to_str()}")

    # 2. Pre-built Workflow
    print("\n2. Pre-built QMK Migration Workflow:")

    # Reset to QMK-style data
    qmk_data = LayoutData(
        keyboard="test",
        title="QMK Layout",
        layers=[
            [LayoutBinding.from_str("KC_A"), LayoutBinding.from_str("MO(1)")],
            [LayoutBinding.from_str("KC_TRNS"), LayoutBinding.from_str("KC_B")],
        ],
        layer_names=["base", "lower"],
    )

    workflow = WorkflowBuilder.qmk_migration_workflow()
    zmk_result = workflow.execute(qmk_data)

    print(f"  QMK: KC_A -> ZMK: {zmk_result.layers[0][0].to_str()}")
    print(f"  QMK: MO(1) -> ZMK: {zmk_result.layers[0][1].to_str()}")

    # 3. Error Handling
    print("\n3. Pipeline with Error Handling:")

    def failing_stage(data: LayoutData) -> LayoutData:
        """Stage that might fail."""
        if len(data.layers) > 1:
            raise ValueError("Intentional error for demonstration")
        return data

    def error_handler(exc: Exception, stage: str) -> None:
        """Handle pipeline errors."""
        print(f"  Error handled in stage '{stage}': {exc}")

    composer = (
        PipelineComposer()
        .add_custom_stage("transform", transform_stage)
        .checkpoint("after_transform")
        .add_custom_stage("failing", failing_stage)
        .with_rollback()
        .with_error_handler(error_handler)
    )

    # Execute with error handling
    rollback_result = composer.execute(layout_data)
    print(f"  Rolled back to checkpoint: {rollback_result.layers[0][0].to_str()}")


# ============================================================================
# Integration Example
# ============================================================================


def full_integration_example():
    """Complete integration of all Phase 4 components."""
    print("\n=== Full Integration Example ===\n")

    from zmk_layout.models.core import LayoutBinding
    from zmk_layout.models.metadata import LayoutData

    # Setup monitoring
    monitor = get_performance_monitor()

    with monitor.measure("full_workflow"):
        # 1. Configure providers
        providers = ProviderBuilder().enable_caching(size=256).enable_performance_tracking().build()

        print("1. Providers configured")

        # 2. Create sample data
        layout_data = LayoutData(
            keyboard="integration_test",
            title="Integration Example",
            layers=[
                [LayoutBinding.from_str("&kp A")] * 10,
                [LayoutBinding.from_str("&trans")] * 10,
            ],
            layer_names=["base", "lower"],
        )

        # 3. Create workflow with monitoring
        def monitored_transform(data: LayoutData) -> LayoutData:
            with monitor.measure("transformation"):
                # Simulate transformation
                time.sleep(0.01)
                return data

        workflow = (
            PipelineComposer()
            .add_custom_stage("transform", monitored_transform)
            .checkpoint("after_transform")
            .execute(layout_data)
        )

        print("2. Workflow executed")

        # 4. Build template context
        context = (
            TemplateContextBuilder()
            .with_layout(workflow)
            .with_generation_metadata(author="Integration Test", version="1.0.0")
            .with_features(performance_tracking=True, debug_mode=True)
            .build()
        )

        print("3. Template context built")

        # 5. Debug output
        formatter = DebugFormatter(max_depth=1)
        summary = {
            "keyboard": context.keyboard,
            "layers": context.layer_count,
            "features": len(context.features),
            "providers": {
                "caching": providers.enable_caching,
                "cache_size": providers.cache_size,
            },
        }

        print("4. Summary:")
        print(formatter.format(summary))

    # 6. Performance report
    print("\n5. Performance Report:")
    monitor.print_report()

    # 7. Cache statistics
    print("\n6. Cache Statistics:")
    if hasattr(LayoutBinding, "_result_cache"):
        cache = LayoutBinding._result_cache
        if hasattr(cache, "stats"):
            stats = cache.stats()
            print(f"   Cache size: {stats['size']}/{stats['maxsize']}")
            print(f"   Hit rate: {stats['hit_rate']:.2%}")


# ============================================================================
# Main Execution
# ============================================================================


def main():
    """Run all examples."""
    print("=" * 70)
    print("Phase 4: Infrastructure & Polish - Examples")
    print("=" * 70)

    # Run examples
    provider_configuration_example()
    template_context_example()
    performance_optimization_example()
    debug_tools_example()
    pipeline_composition_example()
    full_integration_example()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
