"""Stub implementation for lark device tree parser.

This module provides stub functions for the lark-based device tree parser.
The actual implementation would use the lark parsing library but this provides
type information and fallback behavior.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ast_nodes import DTNode


def parse_dt_lark(text: str) -> "list[DTNode]":
    """Parse device tree source using Lark parser.

    This is a stub implementation that raises ImportError to trigger fallback.

    Args:
        text: Device tree source text

    Returns:
        List of DTNode objects

    Raises:
        ImportError: Always raised to trigger fallback to regular parser
    """
    raise ImportError("lark_dt_parser stub - fallback to regular parser")


def parse_dt_lark_safe(text: str) -> "tuple[list[DTNode], list[str]]":
    """Parse device tree source using Lark parser with error handling.

    This is a stub implementation that raises ImportError to trigger fallback.

    Args:
        text: Device tree source text

    Returns:
        Tuple of (parsed nodes, error messages)

    Raises:
        ImportError: Always raised to trigger fallback to regular parser
    """
    raise ImportError("lark_dt_parser stub - fallback to regular parser")
