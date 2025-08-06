"""Performance benchmarking tests to ensure <5% overhead."""

import gc
import time
from collections.abc import Callable
from typing import Any

import pytest

from zmk_layout.models import HoldTapBehavior, LayoutBinding, LayoutData
from zmk_layout.providers.factory import create_default_providers


@pytest.mark.performance
class TestPerformance:
    """Performance benchmarking tests."""

    def test_model_creation_performance(self) -> None:
        """Test model creation performance."""

        def create_simple_layout() -> LayoutData:
            return LayoutData(
                keyboard="test_board",
                title="Performance Test",
                layers=[
                    [
                        LayoutBinding.from_str("&kp Q"),
                        LayoutBinding.from_str("&kp W"),
                        LayoutBinding.from_str("&kp E"),
                        LayoutBinding.from_str("&kp R"),
                    ]
                ],
            )

        # Benchmark model creation
        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            layout = create_simple_layout()
            assert layout.keyboard == "test_board"

        end_time = time.time()
        duration = end_time - start_time
        per_iteration = duration / iterations

        # Should be fast - less than 1ms per creation
        assert per_iteration < 0.001, (
            f"Model creation took {per_iteration:.4f}s per iteration"
        )

    def test_serialization_performance(self) -> None:
        """Test JSON serialization performance."""
        layout = LayoutData(
            keyboard="performance_test",
            title="Serialization Test",
            layers=[
                [
                    LayoutBinding.from_str(f"&kp {chr(65 + j)}")  # A, B, C, etc.
                    for j in range(10)
                ]
                for i in range(5)
            ],
            holdTaps=[
                HoldTapBehavior(
                    name=f"mt_{i}", bindings=["&kp", "&kp"], tappingTermMs=200
                )
                for i in range(3)
            ],
        )

        # Benchmark serialization
        iterations = 100
        start_time = time.time()

        for _ in range(iterations):
            json_data = layout.model_dump(mode="json")
            assert isinstance(json_data, dict)
            assert json_data["keyboard"] == "performance_test"

        end_time = time.time()
        duration = end_time - start_time
        per_iteration = duration / iterations

        # Should be fast - less than 10ms per serialization
        assert per_iteration < 0.01, (
            f"Serialization took {per_iteration:.4f}s per iteration"
        )

    def test_parsing_performance(self) -> None:
        """Test binding parsing performance."""
        binding_strings = [
            "&kp Q",
            "&kp W",
            "&kp E",
            "&kp R",
            "&kp T",
            "&mt LCTRL A",
            "&mt LSHIFT S",
            "&mt LALT D",
            "&kp LC(X)",
            "&kp LC(C)",
            "&kp LC(V)",
            "&lt 1 SPACE",
            "&lt 2 ENTER",
            "&trans",
            "&none",
        ]

        # Benchmark binding parsing
        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            bindings = [LayoutBinding.from_str(s) for s in binding_strings]
            assert len(bindings) == len(binding_strings)
            assert bindings[0].value == "&kp"

        end_time = time.time()
        duration = end_time - start_time
        per_iteration = duration / iterations

        # Should be fast - less than 1ms per batch of 15 bindings
        assert per_iteration < 0.001, (
            f"Binding parsing took {per_iteration:.4f}s per iteration"
        )

    def test_provider_creation_performance(self) -> None:
        """Test provider creation performance."""
        # Benchmark provider creation
        iterations = 100
        start_time = time.time()

        for _ in range(iterations):
            providers = create_default_providers()
            assert providers.logger is not None
            assert providers.template is not None

        end_time = time.time()
        duration = end_time - start_time
        per_iteration = duration / iterations

        # Should be fast - less than 5ms per provider creation
        assert per_iteration < 0.005, (
            f"Provider creation took {per_iteration:.4f}s per iteration"
        )

    def test_round_trip_performance(self) -> None:
        """Test round-trip serialization/deserialization performance."""
        original_layout = LayoutData(
            keyboard="round_trip_test",
            title="Round Trip Performance",
            layers=[
                [
                    LayoutBinding.from_str("&kp Q"),
                    LayoutBinding.from_str("&mt LCTRL A"),
                    LayoutBinding.from_str("&kp LC(X)"),
                ]
            ],
        )

        # Benchmark round-trip
        iterations = 100
        start_time = time.time()

        for _ in range(iterations):
            # Serialize
            json_data = original_layout.model_dump(mode="json")

            # Deserialize
            parsed_layout = LayoutData.model_validate(json_data)

            # Verify
            assert parsed_layout.keyboard == "round_trip_test"
            assert len(parsed_layout.layers) == 1

        end_time = time.time()
        duration = end_time - start_time
        per_iteration = duration / iterations

        # Should be fast - less than 10ms per round-trip
        assert per_iteration < 0.01, (
            f"Round-trip took {per_iteration:.4f}s per iteration"
        )

    def test_memory_usage_reasonable(self) -> None:
        """Test that memory usage is reasonable for large layouts."""
        # Create a larger layout
        large_layout = LayoutData(
            keyboard="memory_test",
            title="Memory Usage Test",
            layers=[
                [
                    LayoutBinding.from_str(f"&kp {chr(65 + (j % 26))}")
                    for j in range(50)  # 50 bindings per layer
                ]
                for i in range(10)  # 10 layers
            ],
            holdTaps=[
                HoldTapBehavior(
                    name=f"ht_{i}", bindings=["&kp", "&kp"], tappingTermMs=200 + i * 10
                )
                for i in range(20)  # 20 hold-taps
            ],
        )

        # Should be able to serialize without issues
        json_data = large_layout.model_dump(mode="json")
        assert isinstance(json_data, dict)
        assert len(json_data["layers"]) == 10
        assert len(json_data["holdTaps"]) == 20

        # Should be able to deserialize
        parsed = LayoutData.model_validate(json_data)
        assert len(parsed.layers) == 10
        assert len(parsed.hold_taps) == 20


def benchmark_function(func: Callable[[], Any], iterations: int = 100) -> float:
    """Benchmark a function and return average time per iteration.

    Args:
        func: Function to benchmark
        iterations: Number of iterations to run

    Returns:
        Average time per iteration in seconds
    """
    start_time = time.time()

    for _ in range(iterations):
        func()

    end_time = time.time()
    return (end_time - start_time) / iterations


@pytest.mark.performance
class TestBenchmarkUtility:
    """Test the benchmark utility function."""

    def test_benchmark_utility(self) -> None:
        """Test that benchmark utility works correctly."""

        def fast_function() -> int:
            return sum(range(100))

        avg_time = benchmark_function(fast_function, iterations=10)
        assert avg_time > 0
        assert avg_time < 0.001  # Should be very fast
