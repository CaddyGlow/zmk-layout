"""Stub implementation for ZMK keymap parser.

This module provides stub classes for the ZMK keymap parser.
The actual implementation would be extracted from the main glovebox system.
"""

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from .ast_nodes import DTNode


class ZmkKeymapParser:
    """Stub implementation of ZMK keymap parser."""

    def __init__(self) -> None:
        """Initialize the parser."""
        self.defines: dict[str, Any] = {}

    def _extract_layers_from_ast(self, root: "DTNode") -> dict[str, Any] | None:
        """Extract layer information from AST.

        This is a stub implementation.

        Args:
            root: The root DTNode to extract from

        Returns:
            Dictionary containing layer information or None
        """
        # Stub implementation - actual would parse the AST
        return None
