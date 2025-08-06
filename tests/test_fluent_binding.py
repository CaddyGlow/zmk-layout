"""Test suite for fluent binding builders."""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from zmk_layout.builders.binding import BuildError, LayoutBindingBuilder
from zmk_layout.models.core import LayoutBinding


class TestLayoutBindingBuilder:
    """Test suite for LayoutBindingBuilder."""

    def test_simple_key_binding(self) -> None:
        """Test creating a simple key binding."""
        builder = LayoutBindingBuilder("&kp")
        binding = builder.key("A").build()

        assert binding.value == "&kp"
        assert len(binding.params) == 1
        assert binding.params[0].value == "A"
        assert binding.to_str() == "&kp A"

    def test_behavior_normalization(self) -> None:
        """Test that behavior is normalized with & prefix."""
        builder1 = LayoutBindingBuilder("kp")
        builder2 = LayoutBindingBuilder("&kp")

        binding1 = builder1.key("A").build()
        binding2 = builder2.key("A").build()

        assert binding1.value == "&kp"
        assert binding2.value == "&kp"
        assert binding1.to_str() == binding2.to_str()

    def test_modifier_chain(self) -> None:
        """Test creating nested modifier chains."""
        builder = LayoutBindingBuilder("&kp")
        binding = builder.modifier("LC").modifier("LS").key("A").build()

        assert binding.value == "&kp"
        assert len(binding.params) == 1

        # Check nested structure: LC(LS(A))
        lc_param = binding.params[0]
        assert lc_param.value == "LC"
        assert len(lc_param.params) == 1

        ls_param = lc_param.params[0]
        assert ls_param.value == "LS"
        assert len(ls_param.params) == 1

        a_param = ls_param.params[0]
        assert a_param.value == "A"
        assert len(a_param.params) == 0

        assert binding.to_str() == "&kp LC(LS(A))"

    def test_hold_tap_behavior(self) -> None:
        """Test creating hold-tap behaviors."""
        builder = LayoutBindingBuilder("&mt")
        binding = builder.hold_tap("LCTRL", "ESC").build()

        assert binding.value == "&mt"
        assert len(binding.params) == 2
        assert binding.params[0].value == "LCTRL"
        assert binding.params[1].value == "ESC"
        assert binding.to_str() == "&mt LCTRL ESC"

    def test_layer_tap_behavior(self) -> None:
        """Test creating layer-tap behaviors."""
        builder = LayoutBindingBuilder("&lt")
        binding = builder.hold_tap(1, "SPACE").build()

        assert binding.value == "&lt"
        assert len(binding.params) == 2
        assert binding.params[0].value == 1
        assert binding.params[1].value == "SPACE"
        assert binding.to_str() == "&lt 1 SPACE"

    def test_multiple_params(self) -> None:
        """Test adding multiple parameters."""
        builder = LayoutBindingBuilder("&macro")
        binding = builder.param("A").param("B").param("C").build()

        assert binding.value == "&macro"
        assert len(binding.params) == 3
        assert [p.value for p in binding.params] == ["A", "B", "C"]
        assert binding.to_str() == "&macro A B C"

    def test_nested_param(self) -> None:
        """Test nested parameter creation."""
        builder = LayoutBindingBuilder("&kp")
        binding = builder.nested_param("LC", "X").build()

        assert binding.value == "&kp"
        assert len(binding.params) == 1
        assert binding.params[0].value == "LC"
        assert binding.params[0].params[0].value == "X"
        assert binding.to_str() == "&kp LC(X)"

    def test_immutability(self) -> None:
        """Test that builder methods return new instances."""
        builder1 = LayoutBindingBuilder("&kp")
        builder2 = builder1.modifier("LC")
        builder3 = builder2.key("A")

        # Each builder should be a different instance
        assert builder1 is not builder2
        assert builder2 is not builder3

        # Original builder should be unchanged
        assert len(builder1._modifiers) == 0
        assert len(builder1._params) == 0

        # Intermediate builder should have modifier but no params
        assert len(builder2._modifiers) == 1
        assert len(builder2._params) == 0

        # Final builder should have params but no modifiers (consumed by key())
        assert len(builder3._modifiers) == 0
        assert len(builder3._params) == 1

    def test_caching(self) -> None:
        """Test that identical builders produce cached results."""
        builder1 = LayoutBindingBuilder("&kp").modifier("LC").key("A")
        builder2 = LayoutBindingBuilder("&kp").modifier("LC").key("A")

        binding1 = builder1.build()
        binding2 = builder2.build()

        # Should return the same cached instance
        assert binding1 is binding2

    def test_build_error(self) -> None:
        """Test that build errors include context."""
        # Create a builder that will fail (example with invalid state)
        builder = LayoutBindingBuilder("")

        with pytest.raises(BuildError) as exc_info:
            # Force an error by manually corrupting state
            builder._params = (None,)
            builder.build()

        assert "Builder state" in str(exc_info.value)

    def test_repr(self) -> None:
        """Test string representation for debugging."""
        builder = LayoutBindingBuilder("&kp").modifier("LC").modifier("LS")
        repr_str = repr(builder)

        assert "&kp" in repr_str
        assert "LC" in repr_str
        assert "LS" in repr_str
        assert "params=0" in repr_str


class TestLayoutBindingFluentMethods:
    """Test suite for fluent methods on LayoutBinding class."""

    def test_builder_class_method(self) -> None:
        """Test creating builder from LayoutBinding class."""
        binding = LayoutBinding.builder("&kp").key("A").build()

        assert binding.value == "&kp"
        assert binding.to_str() == "&kp A"

    def test_with_param(self) -> None:
        """Test adding parameter to existing binding."""
        binding1 = LayoutBinding(value="&kp", params=[])
        binding2 = binding1.with_param("A")

        # Should return new instance
        assert binding1 is not binding2

        # Original should be unchanged
        assert len(binding1.params) == 0

        # New binding should have parameter
        assert len(binding2.params) == 1
        assert binding2.params[0].value == "A"
        assert binding2.to_str() == "&kp A"

    def test_with_modifier(self) -> None:
        """Test wrapping binding with modifier."""
        binding1 = LayoutBinding.from_str("&kp A")
        binding2 = binding1.with_modifier("LC")

        # Should return new instance
        assert binding1 is not binding2

        # Check nested structure
        assert binding2.params[0].value == "LC"
        assert binding2.params[0].params[0].value == "A"
        assert binding2.to_str() == "&kp LC(A)"

    def test_with_modifier_chain(self) -> None:
        """Test chaining multiple modifiers."""
        binding = (
            LayoutBinding.from_str("&kp A").with_modifier("LS").with_modifier("LC")
        )

        # Should create LC(LS(A))
        assert binding.to_str() == "&kp LC(LS(A))"

    def test_as_hold_tap(self) -> None:
        """Test converting to hold-tap behavior."""
        binding1 = LayoutBinding.from_str("&kp ESC")
        binding2 = binding1.as_hold_tap("LCTRL")

        assert binding2.value == "&mt"
        assert binding2.params[0].value == "LCTRL"
        assert binding2.params[1].value == "ESC"
        assert binding2.to_str() == "&mt LCTRL ESC"

    def test_as_layer_tap(self) -> None:
        """Test converting to layer-tap behavior."""
        binding1 = LayoutBinding.from_str("&kp SPACE")
        binding2 = binding1.as_layer_tap(1)

        assert binding2.value == "&lt"
        assert binding2.params[0].value == 1
        assert binding2.params[1].value == "SPACE"
        assert binding2.to_str() == "&lt 1 SPACE"

    def test_as_layer_tap_with_string(self) -> None:
        """Test layer-tap with string layer name."""
        binding1 = LayoutBinding.from_str("&kp ENTER")
        binding2 = binding1.as_layer_tap("nav")

        assert binding2.value == "&lt"
        assert binding2.params[0].value == "nav"
        assert binding2.params[1].value == "ENTER"
        assert binding2.to_str() == "&lt nav ENTER"


class TestThreadSafety:
    """Test thread safety of the builder."""

    def test_concurrent_building(self) -> None:
        """Test that concurrent builds work correctly."""

        def build_binding(modifier: str, key: str) -> str:
            builder = LayoutBindingBuilder("&kp")
            binding = builder.modifier(modifier).key(key).build()
            return binding.to_str()

        # Run many concurrent builds
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(100):
                modifier = f"MOD{i % 5}"
                key = f"KEY{i}"
                future = executor.submit(build_binding, modifier, key)
                futures.append((future, modifier, key))

            # Verify all results are correct
            for future, modifier, key in futures:
                result = future.result()
                expected = f"&kp {modifier}({key})"
                assert result == expected

    def test_cache_thread_safety(self) -> None:
        """Test that cache is thread-safe."""

        def build_cached() -> "LayoutBinding":
            builder = LayoutBindingBuilder("&kp").modifier("LC").key("A")
            return builder.build()

        # Build the same binding concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(build_cached) for _ in range(100)]
            results = [f.result() for f in futures]

        # All should return the same cached instance
        first_result = results[0]
        for result in results[1:]:
            assert result is first_result


class TestFluentAPIEquivalence:
    """Test equivalence between fluent and traditional APIs."""

    @pytest.mark.parametrize(
        "behavior,params",
        [
            ("&kp", ["A"]),
            ("&kp", ["LC(A)"]),
            ("&mt", ["LCTRL", "ESC"]),
            ("&lt", [1, "SPACE"]),
            ("&mo", [2]),
            ("&none", []),
        ],
    )
    def test_traditional_fluent_equivalence(
        self, behavior: str, params: list[str | int]
    ) -> None:
        """Test that fluent and traditional APIs produce identical results."""
        # Traditional approach
        binding_str = (
            f"{behavior} {' '.join(str(p) for p in params)}" if params else behavior
        )
        traditional = LayoutBinding.from_str(binding_str)

        # Fluent approach
        builder = LayoutBindingBuilder(behavior)
        for param in params:
            if isinstance(param, str) and "(" in param:
                # Handle nested params like LC(A)
                parts = param.replace(")", "").split("(")
                builder = (
                    builder.nested_param(parts[0], parts[1])
                    if len(parts) == 2
                    else builder.param(param)
                )
            else:
                builder = builder.param(param)
        fluent = builder.build()

        # Compare string representations
        assert traditional.to_str() == fluent.to_str()

        # Compare model dumps
        assert traditional.model_dump() == fluent.model_dump()


@pytest.mark.performance
class TestPerformance:
    """Performance tests for fluent API."""

    def test_build_performance(self) -> None:
        """Test that building performance is acceptable."""
        iterations = 10000

        # Measure fluent API performance
        start_time = time.perf_counter()
        for _ in range(iterations):
            (LayoutBindingBuilder("&kp").modifier("LC").modifier("LS").key("A").build())
        fluent_time = time.perf_counter() - start_time

        # Measure traditional API performance
        start_time = time.perf_counter()
        for _ in range(iterations):
            LayoutBinding.from_str("&kp LC(LS(A))")
        traditional_time = time.perf_counter() - start_time

        # Calculate overhead
        overhead = (fluent_time - traditional_time) / traditional_time * 100

        # Print performance info
        print(f"\nPerformance Results ({iterations} iterations):")
        print(f"  Traditional: {traditional_time:.3f}s")
        print(f"  Fluent: {fluent_time:.3f}s")
        print(f"  Overhead: {overhead:.1f}%")

        # Assert overhead is reasonable (allow up to 35% for fluent API convenience)
        assert overhead < 35.0, f"Performance overhead too high: {overhead:.2f}%"

    def test_cache_effectiveness(self) -> None:
        """Test that caching improves performance."""
        iterations = 1000

        # First run - populates cache
        start_time = time.perf_counter()
        for _ in range(iterations):
            builder = LayoutBindingBuilder("&kp").modifier("LC").key("A")
            builder.build()
        first_run_time = time.perf_counter() - start_time

        # Second run - uses cache
        start_time = time.perf_counter()
        for _ in range(iterations):
            builder = LayoutBindingBuilder("&kp").modifier("LC").key("A")
            builder.build()
        second_run_time = time.perf_counter() - start_time

        # Second run should be faster or at least similar due to caching
        # Allow small variance due to system timing
        assert second_run_time <= first_run_time * 1.1  # Allow 10% variance

        print(f"\nCache Performance ({iterations} iterations):")
        print(f"  First run: {first_run_time:.3f}s")
        print(f"  Cached run: {second_run_time:.3f}s")
        print(f"  Speedup: {(first_run_time / second_run_time):.2f}x")
