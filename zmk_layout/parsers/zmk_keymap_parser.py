"""ZMK keymap parser for reverse engineering keymaps to JSON layouts."""

# logging module not needed anymore since we don't use isEnabledFor
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Protocol

from zmk_layout.models.base import LayoutBaseModel
from zmk_layout.models.core import LayoutBinding
from zmk_layout.models.metadata import LayoutData

from .ast_nodes import DTNode, DTValue

# Import actual implementations
from .keymap_processors import FullKeymapProcessor, TemplateAwareProcessor
from .parsing_models import ParsingContext


def create_full_keymap_processor(logger: "LayoutLogger | None" = None) -> "ProcessorProtocol":
    """Create a full keymap processor with all features."""
    return FullKeymapProcessor(logger=logger)


def create_template_aware_processor(logger: "LayoutLogger | None" = None) -> "ProcessorProtocol":
    """Create a template-aware keymap processor."""
    return TemplateAwareProcessor(logger=logger)


if TYPE_CHECKING:
    from zmk_layout.models.keymap import ConfigDirective, KeymapComment, KeymapInclude
    from zmk_layout.providers import ConfigurationProvider, LayoutLogger

    class KeyboardProfile:
        """Placeholder for KeyboardProfile until extracted."""

        def __init__(self) -> None:
            self.name: str = "unknown"

        @property
        def keyboard_name(self) -> str:
            return self.name

    class ProcessorProtocol(Protocol):
        def process(self, context: ParsingContext) -> LayoutData | None: ...


class ModelFactory:
    """Factory for creating keymap model instances."""

    def create_comment(self, comment_dict: dict[str, object]) -> Any:
        """Create KeymapComment from dictionary."""
        # Import here to avoid circular imports
        try:
            from zmk_layout.models.keymap import KeymapComment

            return KeymapComment(**comment_dict)  # type: ignore[arg-type]
        except ImportError:
            # Fallback to basic dict if keymap models not available
            return comment_dict

    def create_include(self, include_dict: dict[str, object]) -> Any:
        """Create KeymapInclude from dictionary."""
        try:
            from zmk_layout.models.keymap import KeymapInclude

            return KeymapInclude(**include_dict)  # type: ignore[arg-type]
        except ImportError:
            return include_dict

    def create_directive(self, directive_dict: dict[str, object]) -> Any:
        """Create ConfigDirective from dictionary."""
        try:
            from zmk_layout.models.keymap import ConfigDirective

            return ConfigDirective(**directive_dict)  # type: ignore[arg-type]
        except ImportError:
            return directive_dict


class ParsingMode(str, Enum):
    """Keymap parsing modes."""

    FULL = "full"
    TEMPLATE_AWARE = "template"


class ParsingMethod(str, Enum):
    """Keymap parsing method."""

    AST = "ast"  # AST-based parsing
    REGEX = "regex"  # Legacy regex-based parsing


class KeymapParseResult(LayoutBaseModel):
    """Result of keymap parsing operation."""

    success: bool
    layout_data: LayoutData | None = None
    errors: list[str] = []
    warnings: list[str] = []
    parsing_mode: ParsingMode
    parsing_method: ParsingMethod = ParsingMethod.AST
    extracted_sections: dict[str, object] = {}


class ZMKKeymapParser:
    """Parser for converting ZMK keymap files back to glovebox JSON layouts.

    Supports two parsing modes:
    1. FULL: Parse complete standalone keymap files
    2. TEMPLATE_AWARE: Use keyboard profile templates to extract only user data
    """

    def __init__(
        self,
        configuration_provider: "ConfigurationProvider | None" = None,
        logger: "LayoutLogger | None" = None,
        processors: dict[ParsingMode, "ProcessorProtocol"] | None = None,
    ) -> None:
        """Initialize the keymap parser with explicit dependencies.

        Args:
            configuration_provider: Configuration provider for profiles
            logger: Logger for structured logging
            processors: Dictionary of parsing mode to processor instances
        """
        super().__init__()
        self.model_factory = ModelFactory()
        self.defines: dict[str, str] = {}
        self.configuration_provider = configuration_provider
        self.logger = logger

        # Initialize processors for different parsing modes
        self.processors = processors or {
            ParsingMode.FULL: create_full_keymap_processor(logger=logger),
            ParsingMode.TEMPLATE_AWARE: create_template_aware_processor(logger=logger),
        }

    def _resolve_binding_string(self, binding_str: str) -> str:
        """Resolve defines in a binding string.

        Args:
            binding_str: Binding string that may contain defines

        Returns:
            Binding string with defines resolved
        """
        if not self.defines:
            return binding_str

        # Split the binding string into tokens
        tokens = binding_str.split()
        resolved_tokens = []

        for token in tokens:
            # Check if token is a define (but not a behavior reference starting with &)
            if not token.startswith("&") and token in self.defines:
                resolved = self.defines[token]
                if self.logger:
                    self.logger.debug("Resolved define", token=token, resolved=resolved)
                resolved_tokens.append(resolved)
            else:
                resolved_tokens.append(token)

        return " ".join(resolved_tokens)

    def parse_keymap(
        self,
        keymap_file: Path,
        mode: ParsingMode = ParsingMode.TEMPLATE_AWARE,
        profile: Optional["KeyboardProfile"] = None,
        method: ParsingMethod = ParsingMethod.AST,
    ) -> KeymapParseResult:
        """Parse ZMK keymap file to JSON layout.

        Args:
            keymap_file: Path to .keymap file
            mode: Parsing mode (full or template-aware)
            keyboard_profile: Keyboard profile name (required for template-aware mode)
            method: Parsing method (always AST now)

        Returns:
            KeymapParseResult with layout data or errors
        """
        result = KeymapParseResult(
            success=False,
            parsing_mode=mode,
            parsing_method=method,
        )

        try:
            # Read keymap file content
            if not keymap_file.exists():
                result.errors.append(f"Keymap file not found: {keymap_file}")
                return result

            keymap_content = keymap_file.read_text(encoding="utf-8")

            # Get extraction configuration
            # TODO: currently not implemented in profile parser will used a default
            extraction_config = self._get_extraction_config(profile)

            # Create parsing context
            keyboard_name = profile.keyboard_name if profile else "unknown"
            title = f"{keymap_file.stem}"  # file name without extension

            context = ParsingContext(
                keymap_content=keymap_content,
                title=title,
                keyboard_name=keyboard_name,
                extraction_config=extraction_config,
            )

            # Use appropriate processor
            processor = self.processors[mode]
            layout_data = processor.process(context)

            # Add metedata
            if layout_data:
                layout_data.date = datetime.now()
                layout_data.creator = "glovebox"
                layout_data.notes = f"Automatically generated from keymap file {keymap_file.name}"

                result.layout_data = layout_data
                result.success = True
                result.extracted_sections = getattr(context, "extracted_sections", {})

            # Transfer context errors and warnings to result
            result.errors.extend(context.errors)
            result.warnings.extend(context.warnings)

        except Exception as e:
            if self.logger:
                self.logger.error("Failed to parse keymap", exc_info=True, error=str(e))
            result.errors.append(f"Parsing failed: {e}")

        return result

    def _get_extraction_config(
        self,
        profile: Optional["KeyboardProfile"] = None,
    ) -> list[str] | None:
        """Get extraction configuration from profile or use default.

        Args:
            keyboard_profile: Keyboard profile

        Returns:
            List of extraction section names or None
        """
        if profile:
            try:
                # Check if profile has custom extraction config
                # TODO: currently not implemented in profile
                if hasattr(profile, "keymap_extraction") and profile.keymap_extraction:
                    extraction_sections = profile.keymap_extraction.sections
                    # Return the list of section names - the profile.keymap_extraction.sections is just a list of strings
                    return list(extraction_sections)
            except Exception as e:
                if self.logger:
                    self.logger.warning(
                        "Failed to load extraction config from profile",
                        profile_name=profile.keyboard_name
                        if (profile and hasattr(profile, "keyboard_name"))
                        else "unknown",
                        error=str(e),
                        exc_info=True,
                    )

        # Return None for default configuration
        return None

    def _get_template_path(self, profile: "KeyboardProfile") -> Path | None:
        """Get template file path from keyboard profile.

        Args:
            profile: Keyboard profile object

        Returns:
            Path to template file or None if not found
        """
        try:
            # Check if profile has keymap template configuration
            if hasattr(profile, "keymap") and profile.keymap and hasattr(profile.keymap, "keymap_dtsi_file"):
                # External template file
                template_file = profile.keymap.keymap_dtsi_file
                if template_file:
                    # Resolve relative to profile config directory if available
                    if hasattr(profile, "config_path") and profile.config_path:
                        config_dir = Path(profile.config_path).parent
                        return Path(config_dir / template_file)
                    else:
                        # Fallback to treating template_file as relative to built-in keyboards
                        package_path = Path(__file__).parent.parent.parent.parent
                        return Path(package_path / "keyboards" / template_file)

            # Fallback to default template location in the project
            project_root = Path(__file__).parent.parent.parent.parent
            return Path(project_root / "keyboards" / "config" / "templates" / "keymap.dtsi.j2")

        except Exception as e:
            if self.logger:
                self.logger.warning("Could not determine template path", error=str(e))
            return None

    def _extract_balanced_node(self, content: str, node_name: str) -> str | None:
        """Extract a device tree node with balanced brace matching.

        Args:
            content: Full content to search
            node_name: Name of node to extract

        Returns:
            Node content including braces, or None if not found
        """
        # Find the start of the node
        pattern = rf"{node_name}\s*\{{"
        match = re.search(pattern, content)

        if not match:
            return None

        start_pos = match.start()
        brace_start = match.end() - 1  # Position of opening brace

        # Count braces to find the matching closing brace
        brace_count = 1
        pos = brace_start + 1

        while pos < len(content) and brace_count > 0:
            char = content[pos]
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
            pos += 1

        if brace_count == 0:
            # Found matching brace
            return content[start_pos:pos]
        else:
            return None

    def _extract_layers_from_ast(self, root: DTNode) -> dict[str, object] | None:
        """Extract layer definitions from AST."""
        try:
            keymap_node = None

            # Log the root node structure for debugging
            if self.logger:
                self.logger.debug(
                    "Searching for keymap node in root",
                    root_name=root.name,
                    children_count=len(root.children.keys()),
                )

            # Method 1: Direct check if root is keymap
            if root.name == "keymap":
                keymap_node = root
                if self.logger:
                    self.logger.debug("Found keymap node as root node")

            # Method 2: Try direct path lookup
            if not keymap_node:
                keymap_node = root.find_node_by_path("/keymap")
                if keymap_node and self.logger:
                    self.logger.debug("Found keymap node via path /keymap")

            # Method 3: For main root nodes (name=""), look for keymap child directly
            if not keymap_node and root.name == "":
                keymap_node = root.get_child("keymap")
                if keymap_node and self.logger:
                    self.logger.debug("Found keymap node as direct child of main root")

            # Method 4: Recursive search through all child nodes
            if not keymap_node:
                keymap_node = self._find_keymap_node_recursive(root)
                if keymap_node and self.logger:
                    self.logger.debug("Found keymap node via recursive search")

            if not keymap_node:
                if self.logger:
                    # Log the full tree structure for debugging
                    self._log_ast_structure(root, level=0, max_level=2)
                    self.logger.warning("No keymap node found in AST")
                return None

            layer_names = []
            layers = []

            for child_name, child_node in keymap_node.children.items():
                if child_name.startswith("layer_"):
                    layer_name = child_name[6:]
                    layer_names.append(layer_name)

                    bindings_prop = child_node.get_property("bindings")
                    if bindings_prop and bindings_prop.value:
                        bindings = self._convert_ast_bindings(bindings_prop.value)
                        layers.append(bindings)
                    else:
                        layers.append([])

            if not layer_names:
                if self.logger:
                    self.logger.warning("No layer definitions found in keymap node")
                return None

            return {"layer_names": layer_names, "layers": layers}

        except Exception as e:
            if self.logger:
                self.logger.warning("Failed to extract layers from AST", error=str(e))
            return None

    def _find_keymap_node_recursive(self, node: DTNode) -> DTNode | None:
        """Recursively search for keymap node in the AST.

        Args:
            node: Node to search from

        Returns:
            Keymap DTNode if found, None otherwise
        """
        # Check all children of current node
        for child_name, child_node in node.children.items():
            if child_name == "keymap":
                return child_node

            # Recursively search in child nodes
            found = self._find_keymap_node_recursive(child_node)
            if found:
                return found

        return None

    def _log_ast_structure(self, node: DTNode, level: int = 0, max_level: int = 2) -> None:
        """Log AST structure for debugging.

        Args:
            node: Node to log
            level: Current depth level
            max_level: Maximum depth to log
        """
        if level > max_level:
            return

        indent = "  " * level
        if self.logger:
            self.logger.debug(
                "AST Node structure",
                indent=indent,
                name=node.name,
                children_count=len(node.children.keys()),
                properties_count=len(node.properties.keys()),
            )

        # Log children recursively
        for _child_name, child_node in node.children.items():
            self._log_ast_structure(child_node, level + 1, max_level)

    def _convert_ast_bindings(self, bindings_value: DTValue) -> list[LayoutBinding]:
        """Convert AST bindings value to LayoutBinding objects.

        Args:
            bindings_value: DTValue containing bindings

        Returns:
            List of LayoutBinding objects
        """
        bindings: list[LayoutBinding] = []

        if not bindings_value or not bindings_value.value:
            return bindings

        # Handle array of bindings
        if isinstance(bindings_value.value, list):
            # Group behavior references with their parameters
            # In device tree syntax, <&kp Q &hm LCTRL A> means two bindings: "&kp Q" and "&hm LCTRL A"
            i = 0
            values = bindings_value.value
            while i < len(values):
                item = str(values[i]).strip()

                # Check if this is a behavior reference
                if item.startswith("&"):
                    # Look for parameters following this behavior
                    binding_parts = [item]
                    i += 1

                    # Collect parameters until we hit another behavior reference or end of array
                    while i < len(values):
                        next_item = str(values[i]).strip()
                        # Stop if we hit another behavior reference
                        if next_item.startswith("&"):
                            break
                        # Collect this parameter
                        binding_parts.append(next_item)
                        i += 1

                    # Join the parts to form the complete binding
                    binding_str = " ".join(binding_parts)

                    # Log the binding string for debugging parameter issues
                    if self.logger:
                        self.logger.debug(
                            "Converting binding",
                            binding_str=binding_str,
                            binding_parts_count=len(binding_parts),
                        )

                    try:
                        # Preprocess for MoErgo edge cases
                        preprocessed_binding_str = self._preprocess_moergo_binding_edge_cases(binding_str)

                        # Resolve defines in the binding string
                        resolved_binding_str = self._resolve_binding_string(preprocessed_binding_str)

                        # Use the existing LayoutBinding.from_str method
                        binding = LayoutBinding.from_str(resolved_binding_str)
                        bindings.append(binding)

                        # Debug log the parsed parameters
                        if self.logger:
                            [str(p.value) for p in binding.params]
                            self.logger.debug(
                                "Parsed binding",
                                binding_value=binding.value,
                                param_count=len(binding.params),
                            )
                    except Exception as e:
                        if self.logger:
                            self.logger.error(
                                "Failed to parse binding",
                                binding_str=binding_str,
                                error=str(e),
                                exc_info=True,
                            )
                        # Create fallback binding with empty params
                        bindings.append(LayoutBinding(value=binding_parts[0], params=[]))
                else:
                    # Standalone parameter without behavior - this shouldn't happen in well-formed keymap
                    if self.logger:
                        self.logger.warning(
                            "Found standalone parameter without behavior reference",
                            parameter=item,
                        )
                    i += 1
        else:
            # Single binding
            binding_str = str(bindings_value.value).strip()
            if binding_str:
                try:
                    # Preprocess for MoErgo edge cases
                    preprocessed_binding_str = self._preprocess_moergo_binding_edge_cases(binding_str)

                    # Resolve defines in the binding string
                    resolved_binding_str = self._resolve_binding_string(preprocessed_binding_str)

                    binding = LayoutBinding.from_str(resolved_binding_str)
                    bindings.append(binding)
                except Exception as e:
                    if self.logger:
                        self.logger.error(
                            "Failed to parse single binding",
                            binding_str=binding_str,
                            error=str(e),
                            exc_info=True,
                        )
                    bindings.append(LayoutBinding(value=binding_str, params=[]))

        return bindings

    def _convert_comment_to_model(self, comment_dict: dict[str, object]) -> "KeymapComment":
        """Convert comment dictionary to KeymapComment model instance.

        Args:
            comment_dict: Dictionary with comment data

        Returns:
            KeymapComment model instance
        """
        if self.model_factory is None:
            raise RuntimeError("ModelFactory not initialized")
        result = self.model_factory.create_comment(comment_dict)
        # Import here to avoid circular imports
        from zmk_layout.models.keymap import KeymapComment

        if not isinstance(result, KeymapComment):
            # Fallback - create from dict if factory returned dict
            if isinstance(result, dict):
                return KeymapComment(**result)
            raise TypeError(f"Expected KeymapComment, got {type(result)}")
        return result

    def _convert_include_to_model(self, include_dict: dict[str, object]) -> "KeymapInclude":
        """Convert include dictionary to KeymapInclude model instance.

        Args:
            include_dict: Dictionary with include data

        Returns:
            KeymapInclude model instance
        """
        if self.model_factory is None:
            raise RuntimeError("ModelFactory not initialized")
        result = self.model_factory.create_include(include_dict)
        # Import here to avoid circular imports
        from zmk_layout.models.keymap import KeymapInclude

        if not isinstance(result, KeymapInclude):
            # Fallback - create from dict if factory returned dict
            if isinstance(result, dict):
                return KeymapInclude(**result)
            raise TypeError(f"Expected KeymapInclude, got {type(result)}")
        return result

    def _convert_directive_to_model(self, directive_dict: dict[str, object]) -> "ConfigDirective":
        """Convert config directive dictionary to ConfigDirective model instance.

        Args:
            directive_dict: Dictionary with directive data

        Returns:
            ConfigDirective model instance
        """
        if self.model_factory is None:
            raise RuntimeError("ModelFactory not initialized")
        result = self.model_factory.create_directive(directive_dict)
        # Import here to avoid circular imports
        from zmk_layout.models.keymap import ConfigDirective

        if not isinstance(result, ConfigDirective):
            # Fallback - create from dict if factory returned dict
            if isinstance(result, dict):
                return ConfigDirective(**result)
            raise TypeError(f"Expected ConfigDirective, got {type(result)}")
        return result

    def _preprocess_moergo_binding_edge_cases(self, binding_str: str) -> str:
        """Preprocess binding string to handle MoErgo JSON edge cases.

        Args:
            binding_str: Original binding string

        Returns:
            Preprocessed binding string with edge cases handled
        """
        # Edge case 1: Transform &sys_reset to &reset
        if binding_str == "&sys_reset":
            if self.logger:
                self.logger.debug("Transforming &sys_reset to &reset for MoErgo compatibility")
            return "&reset"

        # Edge case 2: Handle &magic parameter cleanup
        # Convert "&magic LAYER_Magic 0" to "&magic" (remove nested params)
        if binding_str.startswith("&magic "):
            parts = binding_str.split()
            if len(parts) >= 3 and parts[1].startswith("LAYER_") and parts[2] == "0":
                if self.logger:
                    self.logger.debug(
                        "Cleaning up &magic parameters for MoErgo compatibility",
                        original=binding_str,
                        cleaned="&magic",
                    )
                return "&magic"

        return binding_str


def create_zmk_keymap_parser(
    processors: dict[ParsingMode, "ProcessorProtocol"] | None = None,
) -> ZMKKeymapParser:
    """Create ZMK keymap parser instance with explicit dependencies.

    Args:
        template_adapter: Optional template adapter (uses create_template_adapter() if None)
        processors: Optional processors dictionary (uses default processors if None)

    Returns:
        Configured ZmkKeymapParser instance with all dependencies injected
    """
    return ZMKKeymapParser(
        processors=processors,
    )


def create_zmk_keymap_parser_from_profile(
    profile: "KeyboardProfile",  # noqa: ARG001
) -> ZMKKeymapParser:
    """Create ZMK keymap parser instance configured for a specific keyboard profile.

    This factory function follows the CLAUDE.md pattern of profile-based configuration
    loading, similar to other domains in the codebase.

    Args:
        profile: Keyboard profile containing configuration for the parser
        template_adapter: Optional template adapter (uses create_template_adapter() if None)

    Returns:
        Configured ZmkKeymapParser instance with profile-specific settings
    """
    # Create parser with dependencies
    parser = create_zmk_keymap_parser()

    # Configure parser based on profile settings
    # This could include profile-specific parsing preferences, template paths, etc.
    # For now, we return the standard parser, but this provides the extension point
    # for profile-based configuration

    return parser
