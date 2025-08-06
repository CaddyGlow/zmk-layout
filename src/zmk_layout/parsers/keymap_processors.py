"""Keymap processing strategies for different parsing modes."""

# logging module not needed anymore since we don't use isEnabledFor
from typing import TYPE_CHECKING, Any

from zmk_layout.models.metadata import LayoutData

from .ast_nodes import DTNode
from .parsing_models import ParsingContext, get_default_extraction_config
from .section_extractor import SectionExtractorProtocol, create_section_extractor

if TYPE_CHECKING:
    from zmk_layout.providers import LayoutLogger


class BaseKeymapProcessor:
    """Base class for keymap processors with common functionality."""

    def __init__(
        self,
        logger: "LayoutLogger | None" = None,
        section_extractor: "SectionExtractorProtocol | None" = None,
    ) -> None:
        """Initialize base processor.

        Args:
            logger: Optional logger for structured logging
            section_extractor: Optional section extractor
        """
        self.logger = logger
        self.section_extractor = section_extractor or create_section_extractor(logger=logger)

    def process(self, context: "ParsingContext") -> LayoutData | None:
        """Process keymap content according to parsing strategy."""
        raise NotImplementedError("Subclasses must implement process method")

    def _extract_defines_from_ast(self, roots: list[DTNode]) -> dict[str, str]:
        """Extract all #define statements from parsed AST.

        Args:
            roots: List of root DTNode objects

        Returns:
            Dictionary mapping define names to their values
        """
        defines = {}

        # Look for preprocessor directives in all root nodes
        for root in roots:
            for conditional in root.conditionals:
                if conditional.directive == "define":
                    # Parse the define content: "NAME VALUE"
                    parts = conditional.condition.split(None, 1)  # Split on first whitespace
                    if len(parts) >= 2:
                        name = parts[0]
                        value = parts[1]
                        defines[name] = value
                        if self.logger:
                            self.logger.debug("Found define", name=name, value=value)
                    elif len(parts) == 1:
                        # Define without value (just the name)
                        name = parts[0]
                        defines[name] = ""
                        if self.logger:
                            self.logger.debug("Found define without value", name=name)

        return defines

    def _resolve_define(self, token: str, defines: dict[str, str]) -> str:
        """Resolve a token against the defines dictionary.

        Args:
            token: Token to check for define replacement
            defines: Dictionary of define mappings

        Returns:
            Resolved value if token is a define, otherwise the original token
        """
        if token in defines:
            resolved = defines[token]
            if self.logger:
                self.logger.debug("Resolved define", token=token, resolved=resolved)
            return resolved
        return token

    def _create_base_layout_data(self, context: ParsingContext) -> LayoutData:
        """Create base layout data with default values."""
        keyboard_name = context.keyboard_name
        # Handle cases where keyboard_name includes path like "glove80/main"
        if "/" in keyboard_name:
            keyboard_name = keyboard_name.split("/")[0]
        return LayoutData(keyboard=keyboard_name, title=context.title)

    def _transform_behavior_references_to_definitions(self, dtsi_content: str) -> str:
        """Transform behavior references (&name) to proper node definitions (name).

        Handles any behavior reference pattern, not just input listeners.

        Args:
            dtsi_content: Raw DTSI content with behavior references

        Returns:
            Transformed content with proper node definitions
        """
        import re

        # Transform behavior references (&name) to proper node definitions (name)
        # This handles any behavior reference, not just input listeners

        def transform_behavior_reference(match: Any) -> str:
            behavior_name = match.group(1)
            body = match.group(2)

            # Determine compatible string based on behavior name pattern
            if behavior_name.endswith("_input_listener"):
                compatible_line = '    compatible = "zmk,input-listener";\n'
            else:
                # For other behavior references, we'll let the AST converter determine the type
                compatible_line = '    compatible = "zmk,behavior";\n'

            # Insert compatible property at the beginning of the body
            lines = body.split("\n")
            if len(lines) > 1:
                # Insert after the opening brace
                transformed_body = lines[0] + "\n" + compatible_line + "\n".join(lines[1:])
            else:
                transformed_body = compatible_line + body

            return f"{behavior_name} {{{transformed_body}}};"

        # Generic pattern to match any behavior references: &name { ... };
        pattern = r"&(\w+)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\};"

        transformed = re.sub(pattern, transform_behavior_reference, dtsi_content, flags=re.DOTALL)

        # Count transformations
        import re as regex_module

        if self.logger:
            self.logger.debug(
                "Transformed behavior references to definitions",
                reference_count=len(regex_module.findall(r"&\w+", dtsi_content)),
            )

        return transformed

    def _extract_layers_from_roots(
        self, roots: list[DTNode], defines: dict[str, str] | None = None
    ) -> dict[str, object] | None:
        """Extract layer definitions from AST roots.

        Args:
            roots: List of parsed device tree root nodes
            defines: Optional dictionary of preprocessor defines for resolution

        Returns:
            Dictionary with layer_names and layers lists
        """
        # Import here to avoid circular dependency
        from .zmk_keymap_parser import ZMKKeymapParser

        temp_parser = ZMKKeymapParser()
        if defines:
            temp_parser.defines = defines

        for root in roots:
            layers_data = temp_parser._extract_layers_from_ast(root)
            if layers_data:
                return layers_data

        return None

    def _extract_behaviors_and_metadata(
        self, roots: list[DTNode], content: str, defines: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Extract behaviors from AST roots.

        Args:
            roots: List of parsed device tree root nodes
            content: Original keymap content
            defines: Optional dictionary of preprocessor defines for resolution

        Returns:
            Dictionary of behavior models
        """
        # Extract behaviors using AST converter with comment support
        if self.section_extractor is None:
            return {}
        behavior_models = self.section_extractor.behavior_extractor.extract_behaviors_as_models(roots, content, defines)
        return behavior_models

    def _populate_behaviors_in_layout(self, layout_data: LayoutData, converted_behaviors: dict[str, Any]) -> None:
        """Populate layout data with converted behaviors.

        Args:
            layout_data: Layout data to populate
            converted_behaviors: Converted behavior data
        """
        if converted_behaviors.get("hold_taps"):
            layout_data.hold_taps = converted_behaviors["hold_taps"]

        if converted_behaviors.get("macros"):
            layout_data.macros = converted_behaviors["macros"]

        if converted_behaviors.get("combos"):
            layout_data.combos = converted_behaviors["combos"]

        if converted_behaviors.get("tap_dances"):
            layout_data.tap_dances = converted_behaviors["tap_dances"]

        if converted_behaviors.get("sticky_keys"):
            layout_data.sticky_keys = converted_behaviors["sticky_keys"]

        if converted_behaviors.get("caps_words"):
            layout_data.caps_words = converted_behaviors["caps_words"]

        if converted_behaviors.get("mod_morphs"):
            layout_data.mod_morphs = converted_behaviors["mod_morphs"]

        if converted_behaviors.get("input_listeners"):
            if layout_data.input_listeners is None:
                layout_data.input_listeners = []
            layout_data.input_listeners.extend(converted_behaviors["input_listeners"])


class FullKeymapProcessor(BaseKeymapProcessor):
    """Processor for full keymap parsing mode.

    This mode parses complete standalone keymap files without template awareness.
    """

    def process(self, context: ParsingContext) -> LayoutData | None:
        """Process complete keymap file using AST approach.

        Args:
            context: Parsing context with keymap content

        Returns:
            Parsed LayoutData or None if parsing fails
        """
        try:
            # Transform behavior references (&name) to proper definitions before parsing
            # This handles input listeners and other behavior references in full mode
            transformed_content = self._transform_behavior_references_to_definitions(context.keymap_content)

            # Parse content into AST using enhanced parser for comment support
            try:
                from .dt_parser import parse_dt_multiple_safe

                roots, parse_errors = parse_dt_multiple_safe(transformed_content)
                # Convert DTParseError objects to strings
                if parse_errors:
                    context.warnings.extend([str(error) for error in parse_errors])
            except ImportError:
                # Fallback to Lark parser if enhanced parser not available
                try:
                    from .dt_parser import parse_dt_lark_safe

                    roots, parse_error_strings = parse_dt_lark_safe(transformed_content)
                    # These are already strings
                    if parse_error_strings:
                        context.warnings.extend(parse_error_strings)
                except ImportError:
                    roots, parse_error_strings = [], ["Lark parser not available"]
                    # These are already strings
                    if parse_error_strings:
                        context.warnings.extend(parse_error_strings)

            if not roots:
                context.errors.append("Failed to parse device tree AST")
                return None

            # Extract all #define statements from AST
            context.defines = self._extract_defines_from_ast(roots)
            if context.defines and self.logger:
                self.logger.info("Extracted define statements from keymap", define_count=len(context.defines))

            # Create base layout data with enhanced metadata
            layout_data = self._create_base_layout_data(context)

            # Extract layers using AST from all roots with defines
            layers_data = self._extract_layers_from_roots(roots, context.defines)
            if layers_data:
                from typing import cast

                from zmk_layout.models.core import LayoutBinding

                layout_data.layer_names = cast(list[str], layers_data["layer_names"])
                layout_data.layers = cast(list[list[LayoutBinding]], layers_data["layers"])

            # Extract behaviors (use transformed content for metadata extraction too)
            behaviors_dict = self._extract_behaviors_and_metadata(roots, transformed_content, context.defines)

            # Populate behaviors directly (already converted by AST converter)
            self._populate_behaviors_in_layout(layout_data, behaviors_dict)

            layout_data.custom_defined_behaviors = ""
            layout_data.custom_devicetree = ""

            return layout_data

        except Exception as e:
            if self.logger:
                self.logger.error("Full keymap parsing failed", error=str(e), exc_info=True)
            context.errors.append(f"Full parsing failed: {e}")
            return None


class TemplateAwareProcessor(BaseKeymapProcessor):
    """Processor for template-aware parsing mode.

    This mode uses keyboard profile templates to extract only user-defined data.
    """

    def process(self, context: ParsingContext) -> LayoutData | None:
        """Process keymap using template awareness.

        Args:
            context: Parsing context with keymap content and profile

        Returns:
            Parsed LayoutData or None if parsing fails
        """
        try:
            # Parse the beginning of the keymap to extract defines
            # We only need to parse up to where the actual device tree content starts
            try:
                from .dt_parser import parse_dt_multiple_safe

                # Parse the full content to extract defines (they appear at the top)
                roots, parse_errors = parse_dt_multiple_safe(context.keymap_content)
                if roots:
                    context.defines = self._extract_defines_from_ast(roots)
                    if context.defines and self.logger:
                        self.logger.info(
                            "Extracted define statements from keymap",
                            define_count=len(context.defines),
                        )
            except Exception as e:
                if self.logger:
                    self.logger.debug("Could not extract defines", error=str(e))
                # Continue anyway - defines are optional

            layout_data = self._create_base_layout_data(context)

            # Use configured extraction or default
            extraction_config = context.extraction_config or get_default_extraction_config()
            
            if self.logger:
                self.logger.debug("Template processing using extraction config", config_count=len(extraction_config))

            # Extract sections using template-aware approach (only user content)
            if self.section_extractor is None:
                extracted_sections = {}
                if self.logger:
                    self.logger.warning("No section extractor available")
            else:
                extracted_sections = self.section_extractor.extract_sections(
                    context.keymap_content, extraction_config
                )
                if self.logger:
                    self.logger.debug("Section extraction completed", sections_found=len(extracted_sections), sections=list(extracted_sections.keys()))
            
            # Store extracted sections in context for result
            context.extracted_sections = extracted_sections

            # Apply transformation to extracted sections BEFORE processing
            transformed_sections = {}
            for section_name, section in extracted_sections.items():
                if section.type in ("input_listener", "behavior", "macro", "combo"):
                    # Apply transformation to section content before processing
                    # Ensure content is a string before transformation
                    if isinstance(section.content, str):
                        transformed_content: str | dict[str, object] | list[object] = (
                            self._transform_behavior_references_to_definitions(section.content)
                        )
                    else:
                        # Skip transformation for non-string content
                        transformed_content = section.content
                    # Create new section with transformed content
                    from .parsing_models import ExtractedSection

                    transformed_sections[section_name] = ExtractedSection(
                        name=section.name,
                        content=transformed_content,
                        raw_content=section.raw_content,
                        type=section.type,
                    )
                else:
                    # Keep other sections as-is
                    transformed_sections[section_name] = section

            # Process extracted sections with transformations applied
            if self.section_extractor is None:
                processed_data = {}
            else:
                processed_data = self.section_extractor.process_extracted_sections(transformed_sections, context)

            # Populate layout data with processed sections
            self._populate_layout_from_processed_data(layout_data, processed_data)

            return layout_data

        except Exception as e:
            if self.logger:
                self.logger.error("Template-aware parsing failed", error=str(e), exc_info=True)
            context.errors.append(f"Template-aware parsing failed: {e}")
            return None

    def _populate_layout_from_processed_data(self, layout_data: LayoutData, processed_data: dict[str, Any]) -> None:
        """Populate layout data from processed section data.

        Args:
            layout_data: Layout data to populate
            processed_data: Processed data from sections
        """
        # Populate layers
        if "layers" in processed_data:
            layers = processed_data["layers"]
            from typing import cast

            from zmk_layout.models.core import LayoutBinding

            layout_data.layer_names = cast(list[str], layers["layer_names"])
            layout_data.layers = cast(list[list[LayoutBinding]], layers["layers"])

        # Populate behaviors
        if "behaviors" in processed_data:
            behaviors = processed_data["behaviors"]
            layout_data.hold_taps = behaviors.get("hold_taps", [])

        # Populate macros and combos
        if "macros" in processed_data:
            layout_data.macros = processed_data["macros"]

        if "combos" in processed_data:
            layout_data.combos = processed_data["combos"]

        # Handle custom devicetree content
        if "custom_devicetree" in processed_data:
            layout_data.custom_devicetree = processed_data["custom_devicetree"]

        if "custom_defined_behaviors" in processed_data:
            custom_behaviors = processed_data["custom_defined_behaviors"]
            # Convert empty device tree structure to empty string
            if custom_behaviors and custom_behaviors.strip() in (
                "/ {\n};",
                "/ { };",
                "/{\n};",
                "/{};",
            ):
                layout_data.custom_defined_behaviors = ""
            else:
                layout_data.custom_defined_behaviors = custom_behaviors

        # Handle input listeners - convert to JSON models instead of storing as raw DTSI
        if "input_listeners" in processed_data:
            input_listeners_data = processed_data["input_listeners"]
            if self.logger:
                self.logger.debug(
                    "Processing input listeners data",
                    data_type=type(input_listeners_data).__name__,
                )
            if isinstance(input_listeners_data, str):
                # This is raw DTSI content, need to parse and convert to models
                self._convert_input_listeners_from_dtsi(layout_data, input_listeners_data)
            elif isinstance(input_listeners_data, list):
                # Already converted to models
                if layout_data.input_listeners is None:
                    layout_data.input_listeners = []
                layout_data.input_listeners.extend(input_listeners_data)
            else:
                if self.logger:
                    self.logger.warning(
                        "Unexpected input listeners data type",
                        data_type=type(input_listeners_data).__name__,
                    )

        # Store raw content for template variables
        self._store_raw_content_for_templates(layout_data, processed_data)

    def _convert_input_listeners_from_dtsi(self, layout_data: LayoutData, input_listeners_dtsi: str) -> None:
        """Convert raw input listeners DTSI content to JSON models.

        Args:
            layout_data: Layout data to populate with converted input listeners
            input_listeners_dtsi: Raw DTSI content containing input listener definitions
        """
        try:
            # Parse the DTSI content into AST nodes
            from .dt_parser import parse_dt_lark_safe

            # The section extractor provides behavior references (starting with &) rather than definitions
            # Convert references to definitions for proper AST parsing
            dtsi_content = input_listeners_dtsi.strip()

            # First attempt: try parsing as-is (for complete device tree structures)
            roots, parse_errors = parse_dt_lark_safe(dtsi_content)

            # If parsing failed and content doesn't start with '/', try transforming and wrapping it
            if (not roots or parse_errors) and not dtsi_content.startswith("/"):
                if self.logger:
                    self.logger.debug(
                        "Initial parse failed, attempting to transform behavior references to definitions"
                    )

                # Transform behavior references (&name) to proper definitions (name)
                # Also add compatible strings for input listeners
                transformed_content = self._transform_behavior_references_to_definitions(dtsi_content)

                # Wrap transformed behavior definitions in device tree structure
                wrapped_content = f"/ {{\n{transformed_content}\n}};"
                roots, parse_errors = parse_dt_lark_safe(wrapped_content)

                if parse_errors and self.logger:
                    self.logger.warning(
                        "Parse errors while converting wrapped input listeners",
                        error_count=len(parse_errors) if isinstance(parse_errors, list) else 1,
                    )

            if not roots:
                if self.logger:
                    self.logger.warning("No AST roots found in input listeners DTSI content after wrapping attempt")
                return

            # Use the behavior extractor to convert input listener nodes
            if self.section_extractor is None:
                behavior_models = {}
            else:
                behavior_models = self.section_extractor.behavior_extractor.extract_behaviors_as_models(
                    roots, dtsi_content
                )

            # Extract input listeners from behavior models
            if behavior_models.get("input_listeners"):
                if layout_data.input_listeners is None:
                    layout_data.input_listeners = []
                input_listeners = behavior_models["input_listeners"]
                if isinstance(input_listeners, list):
                    layout_data.input_listeners.extend(input_listeners)
                if self.logger:
                    self.logger.debug(
                        "Converted input listeners from DTSI to JSON models",
                        listener_count=len(layout_data.input_listeners),
                    )
                # Debug the structure of converted input listeners
                if layout_data.input_listeners and self.logger:
                    self.logger.debug(
                        "Input listeners converted",
                        total_listeners=len(layout_data.input_listeners),
                    )
            else:
                if self.logger:
                    self.logger.debug("No input listeners found in DTSI content")

        except Exception as e:
            if self.logger:
                self.logger.error(
                    "Failed to convert input listeners from DTSI",
                    error=str(e),
                    exc_info=True,
                )

    def _store_raw_content_for_templates(self, layout_data: LayoutData, processed_data: dict[str, Any]) -> None:
        """Store raw section content for template rendering.

        Args:
            layout_data: Layout data to populate
            processed_data: Processed data containing raw content
        """
        if not hasattr(layout_data, "variables") or layout_data.variables is None:
            layout_data.variables = {}

        # Map raw content to template variable names
        raw_mappings = {
            "behaviors_raw": "user_behaviors_dtsi",
            "macros_raw": "user_macros_dtsi",
            "combos_raw": "combos_dtsi",
        }

        for data_key, template_var in raw_mappings.items():
            if data_key in processed_data:
                layout_data.variables[template_var] = processed_data[data_key]


def create_full_keymap_processor(
    section_extractor: "SectionExtractorProtocol | None" = None,
    logger: "LayoutLogger | None" = None,
) -> FullKeymapProcessor:
    """Create full keymap processor with AST.

    Args:
        section_extractor: Optional section extractor
        logger: Optional logger for structured logging

    Returns:
        Configured FullKeymapProcessor instance
    """
    if section_extractor is None:
        section_extractor = create_section_extractor(logger=logger)

    return FullKeymapProcessor(logger=logger, section_extractor=section_extractor)


def create_template_aware_processor(
    section_extractor: "SectionExtractorProtocol | None" = None,
    logger: "LayoutLogger | None" = None,
) -> TemplateAwareProcessor:
    """Create template-aware processor with AST converter for each section

    Args:
        section_extractor: Optional section extractor
        logger: Optional logger for structured logging

    Returns:
        Configured TemplateAwareProcessor instance
    """
    if section_extractor is None:
        section_extractor = create_section_extractor(logger=logger)

    return TemplateAwareProcessor(
        logger=logger,
        section_extractor=section_extractor,
    )
