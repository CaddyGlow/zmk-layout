"""Stub implementation for lark device tree parser.

This module provides stub functions for the lark-based device tree parser.
The actual implementation would use the lark parsing library but this provides
type information and fallback behavior.
"""

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from .ast_nodes import DTComment, DTNode, DTProperty, DTValue


class LarkToDTTransformer:
    """Transform Lark parse tree to DTNode objects."""

    def __init__(self) -> None:
        """Initialize transformer."""
        self.comments: list[DTComment] = []

    def transform(self, tree: Any) -> list["DTNode"]:
        """Transform parse tree to list of DTNode objects.

        Args:
            tree: Lark parse tree

        Returns:
            List of DTNode objects
        """
        from .ast_nodes import DTNode

        nodes = []
        root = DTNode(name="", label="")  # Root node

        # Process all items including comments
        for item in tree.children:
            if hasattr(item, "data"):
                if item.data == "node":
                    node = self._transform_node(item)
                    if node:
                        nodes.append(node)
                        root.add_child(node)
                elif item.data == "comment":
                    comment = self._transform_comment(item)
                    if comment:
                        self.comments.append(comment)
            else:
                # Handle terminal tokens like SINGLE_LINE_COMMENT and MULTI_LINE_COMMENT
                token_type = getattr(item, "type", None)
                if token_type in ["SINGLE_LINE_COMMENT", "MULTI_LINE_COMMENT"]:
                    comment = self._transform_comment_token(item)
                    if comment:
                        self.comments.append(comment)

        # Attach collected comments to root
        root.comments.extend(self.comments)

        return nodes if nodes else [root]

    def _transform_node(self, node_tree: Any) -> "DTNode":
        """Transform a node tree to DTNode."""
        from .ast_nodes import DTNode

        name = ""
        label = ""

        # Extract node information from tree
        for child in node_tree.children:
            if hasattr(child, "data"):
                if child.data == "label":
                    label = str(child.children[0])
                elif child.data == "node_path":
                    name = self._extract_path(child)
                elif child.data == "property":
                    # Properties will be handled separately
                    pass

        node = DTNode(name=name, label=label)

        # Process properties and child nodes
        for child in node_tree.children:
            if hasattr(child, "data"):
                if child.data == "property":
                    prop = self._transform_property(child)
                    if prop:
                        node.add_property(prop)
                elif child.data == "node":
                    child_node = self._transform_node(child)
                    if child_node:
                        node.add_child(child_node)

        return node

    def _transform_property(self, prop_tree: Any) -> "DTProperty":
        """Transform property tree to DTProperty."""
        from .ast_nodes import DTProperty, DTValue, DTValueType

        name = ""
        values = []

        for child in prop_tree.children:
            if hasattr(child, "data"):
                if child.data == "property_name":
                    name = str(child.children[0])
                elif child.data == "property_values":
                    values = self._transform_property_values(child)

        # Create DTValue from values
        if not values:
            dt_value = None
        elif len(values) == 1:
            dt_value = values[0]
        else:
            # Multiple values - create array
            dt_value = DTValue(DTValueType.ARRAY, values)

        return DTProperty(name=name, value=dt_value)

    def _transform_property_values(self, values_tree: Any) -> list["DTValue"]:
        """Transform property values tree to list of DTValue."""
        from .ast_nodes import DTValue, DTValueType

        values = []

        for child in values_tree.children:
            if hasattr(child, "data") and child.data == "property_value_item":
                # Extract the actual value from property_value_item
                for value_child in child.children:
                    if hasattr(value_child, "data"):
                        if value_child.data == "string_value":
                            value_str = str(value_child.children[0]).strip("\"'")
                            values.append(DTValue(DTValueType.STRING, value_str))
                        elif value_child.data == "number_value":
                            num_str = str(value_child.children[0])
                            value = (
                                int(num_str, 16)
                                if num_str.startswith("0x")
                                else int(num_str)
                            )
                            values.append(DTValue(DTValueType.INTEGER, value))
                        elif value_child.data == "identifier_value":
                            identifier = str(value_child.children[0])
                            values.append(DTValue(DTValueType.STRING, identifier))
                        elif value_child.data == "reference_value":
                            ref = str(value_child.children[0])
                            values.append(DTValue(DTValueType.REFERENCE, ref))
                        elif value_child.data == "array_value":
                            array_values = self._transform_array_value(value_child)
                            values.append(DTValue(DTValueType.ARRAY, array_values))

        return values

    def _transform_array_value(self, array_tree: Any) -> list[str]:
        """Transform array value tree to list."""
        values = []

        for child in array_tree.children:
            if hasattr(child, "data") and child.data == "array_content":
                for item in child.children:
                    if hasattr(item, "data") and item.data == "array_item":
                        # Each array_item has array_token child(ren)
                        for token in item.children:
                            if hasattr(token, "data"):
                                if token.data == "array_token":
                                    # Array token can contain reference_token or be direct value
                                    if token.children:
                                        for token_child in token.children:
                                            if hasattr(token_child, "data"):
                                                if (
                                                    token_child.data
                                                    == "reference_token"
                                                ):
                                                    # Extract the reference name from reference_token
                                                    ref_name = str(
                                                        token_child.children[1]
                                                    )  # Skip & symbol
                                                    values.append(f"&{ref_name}")
                                                elif (
                                                    token_child.data == "function_call"
                                                ):
                                                    func_call = (
                                                        self._transform_function_call(
                                                            token_child
                                                        )
                                                    )
                                                    values.append(func_call)
                                            else:
                                                # Direct token value
                                                values.append(str(token_child))
                                    else:
                                        # Empty array_token - shouldn't happen but handle gracefully
                                        pass
                            else:
                                # Direct token (not wrapped in array_token)
                                values.append(str(token))

        return values

    def _transform_function_call(self, func_tree: Any) -> str:
        """Transform function call tree to string."""
        func_name = ""
        args = []

        for child in func_tree.children:
            if hasattr(child, "data"):
                if child.data == "function_args":
                    for arg in child.children:
                        if hasattr(arg, "data") and arg.data == "function_arg":
                            args.append(str(arg.children[0]))
            else:
                func_name = str(child)

        if args:
            return f"{func_name}({', '.join(args)})"
        return f"{func_name}()"

    def _extract_path(self, path_tree: Any) -> str:
        """Extract path from path tree."""
        path_parts = []

        for child in path_tree.children:
            if hasattr(child, "data") and child.data == "path_segment":
                segment = str(child.children[0])
                # Handle unit address if present
                if len(child.children) > 1:
                    unit_addr = str(child.children[1])
                    segment = f"{segment}@{unit_addr}"
                path_parts.append(segment)
            else:
                path_parts.append(str(child))

        return "/".join(path_parts) if path_parts else ""

    def _transform_comment(self, comment_tree: Any) -> "DTComment | None":
        """Transform comment tree to DTComment."""

        # Extract comment text from tree children
        for child in comment_tree.children:
            token_type = getattr(child, "type", None)
            if token_type in ["SINGLE_LINE_COMMENT", "MULTI_LINE_COMMENT"]:
                return self._transform_comment_token(child)

        return None

    def _transform_comment_token(self, token: Any) -> "DTComment":
        """Transform comment token to DTComment."""
        from .ast_nodes import DTComment

        comment_text = str(token.value) if hasattr(token, "value") else str(token)
        token_type = getattr(token, "type", "")
        line = getattr(token, "line", 1)
        column = getattr(token, "column", 1)

        # Use Lark's token type to determine if it's a block comment
        is_block = token_type == "MULTI_LINE_COMMENT"

        return DTComment(comment_text, line, column, is_block)


def parse_dt_lark(text: str) -> list["DTNode"]:
    """Parse device tree source using Lark parser.

    Args:
        text: Device tree source text

    Returns:
        List of DTNode objects

    Raises:
        ImportError: If lark is not available
        ParseError: If parsing fails
    """
    try:
        from pathlib import Path

        from lark import Lark, ParseError

        # DTNode, DTProperty, DTValue, DTValueType imported in transformer methods
    except ImportError as e:
        raise ImportError(f"lark parser not available: {e}") from e

    # Load grammar file
    grammar_path = Path(__file__).parent / "devicetree.lark"
    if not grammar_path.exists():
        raise ImportError("devicetree.lark grammar file not found")

    try:
        parser = Lark(grammar_path.read_text(), start="start", parser="lalr")
        tree = parser.parse(text)

        # Convert lark tree to DTNode objects
        transformer = LarkToDTTransformer()
        return transformer.transform(tree)
    except ParseError as e:
        # Convert lark ParseError to our format
        raise ParseError(f"Device tree parse error: {e}") from e


def parse_dt_lark_safe(text: str) -> "tuple[list[DTNode], list[str]]":
    """Parse device tree source using Lark parser with error handling.

    Args:
        text: Device tree source text

    Returns:
        Tuple of (parsed nodes, error messages)
    """
    try:
        nodes = parse_dt_lark(text)
        return nodes, []
    except ImportError as e:
        return [], [f"Lark parser not available: {e}"]
    except Exception as e:
        return [], [f"Parse error: {e}"]
