"""Performance optimizations and caching for fluent APIs."""

from __future__ import annotations

import contextlib
import functools
import hashlib
import time
import weakref
from collections import OrderedDict
from collections.abc import Callable
from threading import RLock
from typing import Any, TypeVar


T = TypeVar("T")


class LRUCache:
    """Thread-safe LRU cache implementation.

    This cache provides a least-recently-used eviction policy with
    configurable size and thread safety.

    Examples:
        >>> cache = LRUCache(maxsize=256)
        >>> cache.put("key", "value")
        >>> result = cache.get("key")
    """

    def __init__(self, maxsize: int = 256) -> None:
        """Initialize LRU cache.

        Args:
            maxsize: Maximum cache size
        """
        self.maxsize = maxsize
        self.cache: OrderedDict[Any, Any] = OrderedDict()
        self.lock = RLock()
        self.hits = 0
        self.misses = 0

    def get(self, key: Any) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None

        Examples:
            >>> value = cache.get("my_key")
        """
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def put(self, key: Any, value: Any) -> None:
        """Put value in cache.

        Args:
            key: Cache key
            value: Value to cache

        Examples:
            >>> cache.put("key", "value")
        """
        with self.lock:
            if key in self.cache:
                # Update and move to end
                self.cache.move_to_end(key)
            self.cache[key] = value
            # Evict oldest if needed
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics dictionary

        Examples:
            >>> stats = cache.stats()
            >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }


class WeakCache:
    """Weak reference cache for memory-efficient caching.

    This cache uses weak references to allow garbage collection of
    cached values when not in use elsewhere.

    Examples:
        >>> cache = WeakCache()
        >>> cache.put("key", large_object)
    """

    def __init__(self) -> None:
        """Initialize weak cache."""
        self.cache: weakref.WeakValueDictionary[Any, Any] = (
            weakref.WeakValueDictionary()
        )
        self.lock = RLock()

    def get(self, key: Any) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired

        Examples:
            >>> value = cache.get("my_key")
        """
        with self.lock:
            return self.cache.get(key)

    def put(self, key: Any, value: Any) -> None:
        """Put value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be weakref-able)

        Examples:
            >>> cache.put("key", value)
        """
        with self.lock, contextlib.suppress(TypeError):
            # Value doesn't support weak references
            self.cache[key] = value

    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.cache.clear()


def memoize(maxsize: int = 128) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for memoizing function results.

    Args:
        maxsize: Maximum cache size

    Returns:
        Memoization decorator

    Examples:
        >>> @memoize(maxsize=256)
        ... def expensive_function(x, y):
        ...     return x ** y
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = LRUCache(maxsize=maxsize)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create cache key from arguments
            key = _make_key(args, kwargs)
            result = cache.get(key)
            if result is None:
                result = func(*args, **kwargs)
                cache.put(key, result)
            return result

        wrapper.cache = cache  # type: ignore
        wrapper.cache_clear = cache.clear  # type: ignore
        wrapper.cache_stats = cache.stats  # type: ignore
        return wrapper

    return decorator


def _make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Create cache key from function arguments.

    Args:
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Convert arguments to hashable form
    key_parts = []

    for arg in args:
        if isinstance(arg, str | int | float | bool | type(None)):
            key_parts.append(str(arg))
        elif hasattr(arg, "__dict__"):
            # For objects, use their attributes
            key_parts.append(str(sorted(arg.__dict__.items())))
        else:
            key_parts.append(str(arg))

    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}={value}")

    # Create hash of key parts
    key_str = "|".join(key_parts)
    return hashlib.md5(key_str.encode()).hexdigest()


class LazyProperty:
    """Lazy property decorator for expensive computations.

    This decorator computes a property value once and caches it for
    subsequent access.

    Examples:
        >>> class MyClass:
        ...     @LazyProperty
        ...     def expensive_property(self):
        ...         return compute_expensive_value()
    """

    def __init__(self, func: Callable[[Any], Any]) -> None:
        """Initialize lazy property.

        Args:
            func: Property function
        """
        self.func = func
        self.attr_name = f"_lazy_{func.__name__}"
        # Copy function metadata manually since update_wrapper doesn't work with descriptors
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__ or ""
        self.__module__ = getattr(func, "__module__", "") or ""
        self.__qualname__ = getattr(func, "__qualname__", "") or ""
        self.__annotations__ = getattr(func, "__annotations__", {})

    def __get__(self, obj: Any, objtype: type[Any] | None = None) -> Any:
        """Get property value.

        Args:
            obj: Object instance
            objtype: Object type

        Returns:
            Property value
        """
        if obj is None:
            return self

        # Check if already computed
        if not hasattr(obj, self.attr_name):
            # Compute and cache
            setattr(obj, self.attr_name, self.func(obj))

        return getattr(obj, self.attr_name)

    def __set__(self, obj: Any, value: Any) -> None:
        """Set property value.

        Args:
            obj: Object instance
            value: New value
        """
        setattr(obj, self.attr_name, value)

    def __delete__(self, obj: Any) -> None:
        """Delete cached value.

        Args:
            obj: Object instance
        """
        if hasattr(obj, self.attr_name):
            delattr(obj, self.attr_name)


class PerformanceMonitor:
    """Monitor performance of fluent API operations.

    This monitor tracks execution times, memory usage, and operation counts
    for performance analysis.

    Examples:
        >>> monitor = PerformanceMonitor()
        >>> with monitor.measure("operation"):
        ...     perform_operation()
        >>> monitor.print_report()
    """

    def __init__(self) -> None:
        """Initialize performance monitor."""
        self.measurements: dict[str, list[float]] = {}
        self.counters: dict[str, int] = {}
        self.lock = RLock()

    def measure(self, name: str) -> MeasurementContext:
        """Create measurement context.

        Args:
            name: Measurement name

        Returns:
            Measurement context manager

        Examples:
            >>> with monitor.measure("binding_creation"):
            ...     create_binding()
        """
        return MeasurementContext(self, name)

    def record(self, name: str, duration: float) -> None:
        """Record a measurement.

        Args:
            name: Measurement name
            duration: Duration in seconds
        """
        with self.lock:
            if name not in self.measurements:
                self.measurements[name] = []
            self.measurements[name].append(duration)

    def increment(self, name: str, count: int = 1) -> None:
        """Increment a counter.

        Args:
            name: Counter name
            count: Increment amount
        """
        with self.lock:
            if name not in self.counters:
                self.counters[name] = 0
            self.counters[name] += count

    def get_stats(self, name: str) -> dict[str, float]:
        """Get statistics for a measurement.

        Args:
            name: Measurement name

        Returns:
            Statistics dictionary

        Examples:
            >>> stats = monitor.get_stats("operation")
        """
        with self.lock:
            if name not in self.measurements:
                return {}

            times = self.measurements[name]
            return {
                "count": len(times),
                "total": sum(times),
                "mean": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
            }

    def print_report(self) -> None:
        """Print performance report."""
        print("\n=== Performance Report ===")

        if self.measurements:
            print("\nMeasurements:")
            for name, _times in sorted(self.measurements.items()):
                stats = self.get_stats(name)
                print(f"  {name}:")
                print(f"    Count: {stats['count']}")
                print(f"    Total: {stats['total'] * 1000:.3f}ms")
                print(f"    Mean: {stats['mean'] * 1000:.3f}ms")
                print(f"    Min: {stats['min'] * 1000:.3f}ms")
                print(f"    Max: {stats['max'] * 1000:.3f}ms")

        if self.counters:
            print("\nCounters:")
            for name, count in sorted(self.counters.items()):
                print(f"  {name}: {count}")

    def clear(self) -> None:
        """Clear all measurements."""
        with self.lock:
            self.measurements.clear()
            self.counters.clear()


class MeasurementContext:
    """Context manager for performance measurements."""

    def __init__(self, monitor: PerformanceMonitor, name: str) -> None:
        """Initialize measurement context.

        Args:
            monitor: Performance monitor
            name: Measurement name
        """
        self.monitor = monitor
        self.name = name
        self.start_time = 0.0

    def __enter__(self) -> MeasurementContext:
        """Enter measurement context."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit measurement context."""
        duration = time.perf_counter() - self.start_time
        self.monitor.record(self.name, duration)


# Global performance monitor instance
_global_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor.

    Returns:
        Global performance monitor instance

    Examples:
        >>> monitor = get_performance_monitor()
        >>> with monitor.measure("operation"):
        ...     perform_operation()
    """
    return _global_monitor


def profile(name: str | None = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for profiling function execution.

    Args:
        name: Profile name (defaults to function name)

    Returns:
        Profiling decorator

    Examples:
        >>> @profile("expensive_operation")
        ... def compute():
        ...     return expensive_computation()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        profile_name = name or func.__name__
        monitor = get_performance_monitor()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with monitor.measure(profile_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


class OptimizedBuilder:
    """Base class for optimized fluent builders.

    This class provides common optimization patterns for fluent builders,
    including caching, lazy evaluation, and efficient copying.
    """

    __slots__ = ("_cache", "_cache_key", "__weakref__")

    def __init__(self) -> None:
        """Initialize optimized builder."""
        self._cache: dict[str, Any] = {}
        self._cache_key: int | None = None

    def _invalidate_cache(self) -> None:
        """Invalidate cached values."""
        self._cache.clear()
        self._cache_key = None

    def _get_cached(self, key: str, compute: Callable[[], T]) -> T:
        """Get cached value or compute.

        Args:
            key: Cache key
            compute: Function to compute value

        Returns:
            Cached or computed value
        """
        if key not in self._cache:
            self._cache[key] = compute()
        # Type cast since we know the cache contains the computed value
        return self._cache[key]  # type: ignore[no-any-return]

    def _compute_cache_key(self) -> int:
        """Compute cache key for current state.

        Returns:
            Cache key hash
        """
        if self._cache_key is None:
            # Override in subclasses to compute based on state
            self._cache_key = id(self)
        return self._cache_key
