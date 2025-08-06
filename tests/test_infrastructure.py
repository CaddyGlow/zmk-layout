"""Tests for Phase 4 infrastructure components."""

from __future__ import annotations

import json
import os
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest

from zmk_layout.infrastructure import (
    BuilderState,
    ChainInspector,
    DebugFormatter,
    ProviderBuilder,
    TemplateContext,
    TemplateContextBuilder,
)
from zmk_layout.infrastructure.performance import (
    LazyProperty,
    LRUCache,
    PerformanceMonitor,
    WeakCache,
    get_performance_monitor,
    memoize,
    profile,
)
from zmk_layout.models.behaviors import ComboBehavior, HoldTapBehavior, MacroBehavior
from zmk_layout.models.core import LayoutBinding
from zmk_layout.models.metadata import LayoutData


class TestProviderBuilder:
    """Test suite for ProviderBuilder."""

    def test_basic_provider_configuration(self) -> None:
        """Test basic provider configuration."""
        file_adapter = MagicMock()
        template_adapter = MagicMock()
        logger = MagicMock()

        config = (
            ProviderBuilder()
            .with_file_adapter(file_adapter)
            .with_template_adapter(template_adapter)
            .with_logger(logger)
            .build()
        )

        assert config.file_adapter is file_adapter
        assert config.template_adapter is template_adapter
        assert config.logger is logger

    def test_caching_configuration(self) -> None:
        """Test caching configuration."""
        config = ProviderBuilder().enable_caching(size=512).build()

        assert config.enable_caching is True
        assert config.cache_size == 512

        config = ProviderBuilder().enable_caching().disable_caching().build()

        assert config.enable_caching is False

    def test_debug_and_performance_modes(self) -> None:
        """Test debug and performance tracking modes."""
        config = (
            ProviderBuilder().enable_debug_mode().enable_performance_tracking().build()
        )

        assert config.debug_mode is True
        assert config.performance_tracking is True

    def test_environment_configuration(self) -> None:
        """Test configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "ZMK_LAYOUT_DEBUG": "true",
                "ZMK_LAYOUT_PERFORMANCE": "true",
                "ZMK_LAYOUT_CACHE_SIZE": "1024",
            },
        ):
            config = ProviderBuilder().from_environment().build()

            assert config.debug_mode is True
            assert config.performance_tracking is True
            assert config.cache_size == 1024
            assert config.enable_caching is True

    def test_immutable_builder_pattern(self) -> None:
        """Test that builder methods return new instances."""
        builder1 = ProviderBuilder()
        builder2 = builder1.enable_debug_mode()
        builder3 = builder2.enable_caching()

        assert builder1 is not builder2
        assert builder2 is not builder3
        assert builder1._config.debug_mode is False
        assert builder2._config.debug_mode is True
        assert builder3._config.enable_caching is True

    def test_builder_repr(self) -> None:
        """Test builder string representation."""
        file_adapter = MagicMock()
        logger = MagicMock()

        builder = (
            ProviderBuilder()
            .with_file_adapter(file_adapter)
            .with_logger(logger)
            .enable_caching(256)
            .enable_debug_mode()
        )

        repr_str = repr(builder)
        assert "file" in repr_str
        assert "logger" in repr_str
        assert "caching(256)" in repr_str
        assert "debug" in repr_str


class TestTemplateContextBuilder:
    """Test suite for TemplateContextBuilder."""

    def test_basic_context_building(self) -> None:
        """Test basic template context building."""
        layout_data = LayoutData(
            keyboard="test_keyboard",
            title="Test Layout",
            notes="Test description",
            layers=[[]],
            layer_names=["base"],
        )

        context = TemplateContextBuilder().with_layout(layout_data).build()

        assert context.keyboard == "test_keyboard"
        assert context.title == "Test Layout"
        assert context.description == "Test description"
        assert context.layer_names == ["base"]
        assert context.layer_count == 1

    def test_profile_integration(self) -> None:
        """Test keyboard profile integration."""
        profile = MagicMock()
        profile.keyboard_name = "crkbd"
        profile.keyboard_config.key_count = 42
        profile.keyboard_config.split = True

        context = TemplateContextBuilder().with_profile(profile).build()

        assert context.profile_name == "crkbd"
        assert context.key_count == 42
        assert context.split_keyboard is True

    def test_behaviors_integration(self) -> None:
        """Test behaviors integration."""
        # Create proper behavior objects instead of MagicMocks
        behaviors = [HoldTapBehavior(name="hm", bindings=["&kp", "&kp"])]
        # Create a proper LayoutBinding for combos
        from zmk_layout.models.core import LayoutParam

        mock_binding = LayoutBinding(value="&kp", params=[LayoutParam(value="A")])
        combos = [ComboBehavior(name="copy", keyPositions=[0, 1], binding=mock_binding)]
        macros = [MacroBehavior(name="vim_save")]

        context = (
            TemplateContextBuilder()
            .with_behaviors(behaviors=behaviors, combos=combos, macros=macros)
            .build()
        )

        assert context.behaviors == behaviors
        assert context.combos == combos
        assert context.macros == macros
        assert context.hold_taps == behaviors  # Compatibility

    def test_generation_metadata(self) -> None:
        """Test generation metadata."""
        context = (
            TemplateContextBuilder()
            .with_generation_metadata(
                author="John Doe", version="2.1.0", generator_version="1.5.0"
            )
            .build()
        )

        assert context.author == "John Doe"
        assert context.version == "2.1.0"
        assert context.generator_version == "1.5.0"
        assert context.generation_timestamp  # Should be set

    def test_dtsi_content(self) -> None:
        """Test DTSI content sections."""
        context = (
            TemplateContextBuilder()
            .with_dtsi_content(
                layer_defines="#define BASE 0",
                behaviors_dtsi="behaviors {}",
                keymap_node="keymap {}",
            )
            .build()
        )

        assert context.layer_defines == "#define BASE 0"
        assert context.behaviors_dtsi == "behaviors {}"
        assert context.keymap_node == "keymap {}"

    def test_custom_variables(self) -> None:
        """Test custom variables."""
        context = (
            TemplateContextBuilder()
            .with_custom_vars(theme="dark", layout_style="ergonomic")
            .build()
        )

        assert context.custom_vars["theme"] == "dark"
        assert context.custom_vars["layout_style"] == "ergonomic"

    def test_feature_flags(self) -> None:
        """Test feature flags."""
        context = (
            TemplateContextBuilder()
            .with_features(home_row_mods=True, mouse_keys=False, rgb_underglow=True)
            .build()
        )

        assert context.features["home_row_mods"] is True
        assert context.features["mouse_keys"] is False
        assert context.features["rgb_underglow"] is True

    def test_custom_transformer(self) -> None:
        """Test custom transformer function."""

        def add_copyright(ctx: TemplateContext) -> TemplateContext:
            return ctx.model_copy(
                update={"custom_vars": {**ctx.custom_vars, "copyright": "© 2025"}}
            )

        context = TemplateContextBuilder().add_transformer(add_copyright).build()

        assert context.custom_vars["copyright"] == "© 2025"

    def test_context_merging(self) -> None:
        """Test context merging."""
        base_context = TemplateContext(keyboard="base", custom_vars={"a": 1})

        context = (
            TemplateContextBuilder()
            .merge_with(base_context)
            .with_custom_vars(b=2)
            .build()
        )

        assert context.keyboard == "base"
        assert context.custom_vars["a"] == 1
        assert context.custom_vars["b"] == 2

    def test_build_dict(self) -> None:
        """Test building as dictionary."""
        context_dict = (
            TemplateContextBuilder().with_custom_vars(test="value").build_dict()
        )

        assert isinstance(context_dict, dict)
        assert context_dict["custom_vars"]["test"] == "value"

    def test_preview(self) -> None:
        """Test context preview."""
        layout_data = LayoutData(
            keyboard="test",
            title="Test",
            layers=[[], []],
            layer_names=["base", "nav"],
        )

        preview = TemplateContextBuilder().with_layout(layout_data).preview()

        assert preview["keyboard"] == "test"
        assert preview["layer_count"] == 2
        assert preview["layer_names"] == ["base", "nav"]


class TestDebugTools:
    """Test suite for debug tools."""

    def test_builder_state_capture(self) -> None:
        """Test BuilderState captures builder information."""
        state = BuilderState(
            class_name="TestBuilder",
            attributes={"value": 42},
            method_calls=["method1()", "method2('arg')"],
        )

        assert state.class_name == "TestBuilder"
        assert state.attributes["value"] == 42
        assert len(state.method_calls) == 2

        # Test JSON serialization
        json_str = state.to_json()
        data = json.loads(json_str)
        assert data["class_name"] == "TestBuilder"

    def test_chain_inspector_wrapping(self) -> None:
        """Test ChainInspector wraps and tracks builder calls."""
        inspector = ChainInspector()

        # Create mock builder
        class MockBuilder:
            def __init__(self, value: int) -> None:
                self.value = value

            def increment(self) -> MockBuilder:
                return MockBuilder(self.value + 1)

            def double(self) -> MockBuilder:
                return MockBuilder(self.value * 2)

            def build(self) -> int:
                return self.value

        wrapped = inspector.wrap(MockBuilder(5))
        result = wrapped.increment().double().build()

        assert result == 12  # (5 + 1) * 2
        assert len(inspector._history) > 0

    def test_chain_inspector_performance_tracking(self) -> None:
        """Test performance tracking in ChainInspector."""
        inspector = ChainInspector()

        class SlowBuilder:
            def slow_method(self) -> SlowBuilder:
                time.sleep(0.01)  # 10ms
                return self

        wrapped = inspector.wrap(SlowBuilder())
        wrapped.slow_method()

        assert "slow_method" in inspector._performance_data
        assert inspector._performance_data["slow_method"][0] >= 0.01

    def test_debug_formatter(self) -> None:
        """Test DebugFormatter formats objects correctly."""
        formatter = DebugFormatter()

        # Test dict formatting
        data = {"key": "value", "nested": {"inner": 42}}
        formatted = formatter.format(data)
        assert "key" in formatted
        assert "value" in formatted
        assert "inner" in formatted

        # Test list formatting
        data_list = [1, 2, 3]
        formatted = formatter.format(data_list)
        assert "[" in formatted
        assert "1" in formatted

    def test_chain_inspector_export(self) -> None:
        """Test exporting chain history."""
        inspector = ChainInspector()

        class TestBuilder:
            def method(self) -> TestBuilder:
                return self

        wrapped = inspector.wrap(TestBuilder())
        wrapped.method()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            inspector.export_history(temp_file.name)
            temp_path = temp_file.name

        try:
            with open(temp_path) as f:
                data = json.load(f)
            assert "history" in data
            assert "performance" in data
        finally:
            os.unlink(temp_path)


class TestPerformanceOptimizations:
    """Test suite for performance optimizations."""

    def test_lru_cache(self) -> None:
        """Test LRU cache functionality."""
        cache = LRUCache(maxsize=3)

        # Test basic put/get
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)

        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.get("c") == 3

        # Test eviction
        cache.put("d", 4)  # Should evict "a"
        assert cache.get("a") is None
        assert cache.get("d") == 4

        # Test statistics
        stats = cache.stats()
        assert stats["size"] == 3
        assert stats["hits"] > 0

    def test_weak_cache(self) -> None:
        """Test weak reference cache."""
        cache = WeakCache()

        # Create object that supports weak references
        class TestObject:
            def __init__(self, value: int) -> None:
                self.value = value

        obj = TestObject(42)
        cache.put("key", obj)

        # Object should be retrievable while referenced
        assert cache.get("key") is obj

        # After deleting reference, should be None (after GC)
        del obj
        import gc

        gc.collect()
        assert cache.get("key") is None

    def test_memoize_decorator(self) -> None:
        """Test memoization decorator."""
        call_count = 0

        @memoize(maxsize=10)
        def expensive_function(x: int, y: int) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        # First call should execute
        result1 = expensive_function(2, 3)
        assert result1 == 5
        assert call_count == 1

        # Second call with same args should use cache
        result2 = expensive_function(2, 3)
        assert result2 == 5
        assert call_count == 1  # Not incremented

        # Different args should execute
        result3 = expensive_function(3, 4)
        assert result3 == 7
        assert call_count == 2

    def test_lazy_property(self) -> None:
        """Test lazy property decorator."""
        compute_count = 0

        class TestClass:
            @LazyProperty
            def expensive_property(self) -> int:
                nonlocal compute_count
                compute_count += 1
                return 42

        obj = TestClass()

        # First access should compute
        value1: int = obj.expensive_property
        assert value1 == 42
        assert compute_count == 1

        # Second access should use cached value
        value2: int = obj.expensive_property
        assert value2 == 42
        assert compute_count == 1  # Not incremented

    @pytest.mark.performance
    def test_performance_monitor(self) -> None:
        """Test performance monitoring."""
        monitor = PerformanceMonitor()

        # Test measurement
        with monitor.measure("test_operation"):
            time.sleep(0.01)  # 10ms

        stats = monitor.get_stats("test_operation")
        assert stats["count"] == 1
        assert stats["total"] >= 0.01

        # Test counter
        monitor.increment("test_counter", 5)
        assert monitor.counters["test_counter"] == 5

    def test_profile_decorator(self) -> None:
        """Test profiling decorator."""
        monitor = get_performance_monitor()
        monitor.clear()

        @profile("test_function")
        def test_function() -> int:
            time.sleep(0.01)
            return 42

        result = test_function()
        assert result == 42

        stats = monitor.get_stats("test_function")
        assert stats["count"] == 1
        assert stats["total"] >= 0.01

    def test_cache_thread_safety(self) -> None:
        """Test thread safety of LRU cache."""
        import threading

        cache = LRUCache(maxsize=100)
        errors = []

        def worker(start: int) -> None:
            try:
                for i in range(start, start + 10):
                    cache.put(f"key_{i}", i)
                    value = cache.get(f"key_{i}")
                    assert value == i
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(0, 100, 10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0


class TestIntegration:
    """Integration tests for Phase 4 components."""

    def test_provider_builder_with_template_context(self) -> None:
        """Test ProviderBuilder integration with TemplateContextBuilder."""
        # Create providers
        file_adapter = MagicMock()
        template_adapter = MagicMock()

        ProviderBuilder().with_file_adapter(file_adapter).with_template_adapter(
            template_adapter
        ).enable_caching().build()

        # Create template context
        layout_data = LayoutData(
            keyboard="test",
            title="Test Layout",
            layers=[[]],
            layer_names=["base"],
        )

        context = (
            TemplateContextBuilder()
            .with_layout(layout_data)
            .with_generation_metadata(author="Test Author")
            .build()
        )

        # Simulate template rendering
        template_adapter.render.return_value = "rendered content"

        result = template_adapter.render("template.j2", context.model_dump())
        assert result == "rendered content"

    def test_debug_tools_with_performance_monitoring(self) -> None:
        """Test debug tools integration with performance monitoring."""
        inspector = ChainInspector()
        monitor = PerformanceMonitor()

        class TestBuilder:
            def operation(self) -> TestBuilder:
                with monitor.measure("builder_operation"):
                    time.sleep(0.01)
                return self

        wrapped = inspector.wrap(TestBuilder())
        wrapped.operation()

        # Check both systems captured the operation
        assert "operation" in inspector._performance_data
        assert "builder_operation" in monitor.measurements

    def test_full_infrastructure_workflow(self) -> None:
        """Test complete infrastructure workflow."""
        # Set up providers
        config = (
            ProviderBuilder()
            .enable_debug_mode()
            .enable_performance_tracking()
            .enable_caching(size=256)
            .from_environment()
            .validate()
            .build()
        )

        # Create layout data
        layout_data = LayoutData(
            keyboard="crkbd",
            title="Corne Layout",
            layers=[[]],
            layer_names=["base"],
        )

        # Build template context
        context = (
            TemplateContextBuilder()
            .with_layout(layout_data)
            .with_generation_metadata(author="Developer", version="1.0.0")
            .with_features(home_row_mods=True, rgb_underglow=False)
            .with_custom_vars(theme="minimal")
            .validate_completeness()
            .build()
        )

        # Verify everything is properly configured
        assert config.debug_mode is True
        assert config.performance_tracking is True
        assert config.enable_caching is True
        assert config.cache_size == 256

        assert context.keyboard == "crkbd"
        assert context.author == "Developer"
        assert context.features["home_row_mods"] is True
        assert context.custom_vars["theme"] == "minimal"
