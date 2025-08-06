"""Section extractor for ZMK keymap parsing."""

import re
from typing import TYPE_CHECKING, Any, Protocol

from .ast_nodes import DTNode
from .parsing_models import (
    ExtractedSection,
    ExtractionConfig,
    ParsingContext,
    SectionProcessingResult,
)

if TYPE_CHECKING:
    from zmk_layout.providers import LayoutLogger


class BehaviorExtractorProtocol(Protocol):
    """Protocol for behavior extraction."""

    def extract_behaviors_as_models(
        self, roots: list[DTNode], content: str, defines: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Extract behaviors from AST roots and return as models."""
        ...


class SectionExtractorProtocol(Protocol):
    """Protocol for section extraction."""

    def extract_sections(self, content: str, configs: list[Any]) -> dict[str, ExtractedSection]:
        """Extract sections from content."""
        ...

    def process_extracted_sections(
        self, sections: dict[str, ExtractedSection], context: ParsingContext
    ) -> dict[str, Any]:
        """Process extracted sections."""
        ...

    @property
    def behavior_extractor(self) -> BehaviorExtractorProtocol:
        """Get behavior extractor."""
        ...


class UniversalBehaviorExtractor:
    """Universal behavior extractor that can extract all types of behaviors."""
    
    def __init__(self, logger: "LayoutLogger | None" = None) -> None:
        self.logger = logger
    
    def extract_behaviors_as_models(
        self, roots: list[DTNode], content: str, defines: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Extract behaviors from AST roots and convert to models."""
        # Simplified behavior extraction - for now just return empty dict
        # In a full implementation, this would walk the AST and extract behaviors
        return {
            "hold_taps": [],
            "macros": [], 
            "combos": [],
            "tap_dances": [],
            "sticky_keys": [],
            "caps_words": [],
            "mod_morphs": [],
            "input_listeners": []
        }


class SectionExtractor:
    """Extracts and processes sections from keymap content using configurable delimiters."""

    def __init__(
        self,
        behavior_extractor: BehaviorExtractorProtocol | None = None,
        logger: "LayoutLogger | None" = None,
    ) -> None:
        """Initialize section extractor with dependencies."""
        self.logger = logger
        self.behavior_extractor = behavior_extractor or UniversalBehaviorExtractor(logger)

    def extract_sections(
        self, content: str, configs: list[ExtractionConfig]
    ) -> dict[str, ExtractedSection]:
        """Extract all configured sections from keymap content."""
        sections = {}

        if self.logger:
            self.logger.debug("Extracting sections", config_count=len(configs))

        for config in configs:
            try:
                section = self._extract_single_section(content, config)
                if section:
                    sections[config.tpl_ctx_name] = section
                    if self.logger:
                        self.logger.debug(
                            "Extracted section",
                            section_name=config.tpl_ctx_name,
                            content_length=len(section.raw_content),
                        )
            except Exception as e:
                if self.logger:
                    self.logger.warning(
                        "Failed to extract section",
                        section_name=config.tpl_ctx_name,
                        error=str(e),
                    )

        return sections

    def process_extracted_sections(
        self, sections: dict[str, ExtractedSection], context: ParsingContext
    ) -> dict[str, Any]:
        """Process extracted sections based on their types."""
        processed = {}

        for section_name, section in sections.items():
            try:
                result = self._process_section_by_type(section, context)

                if result.success and result.data is not None:
                    processed[section.name] = result.data

                    # Store raw content for template variables if needed
                    if section.type in ("behavior", "macro", "combo", "input_listener"):
                        raw_key = (
                            f"{section_name}_raw"
                            if not section_name.endswith("_raw")
                            else section_name
                        )
                        processed[raw_key] = section.raw_content

                context.warnings.extend(result.warnings)

                if not result.success and result.error_message:
                    if self.logger:
                        self.logger.warning("Section processing failed", error=result.error_message)
                    context.errors.append(
                        f"Processing {section_name}: {result.error_message}"
                    )

            except Exception as e:
                if self.logger:
                    self.logger.error(
                        "Failed to process section",
                        section_name=section_name,
                        error=str(e),
                    )
                context.errors.append(f"Processing {section_name}: {e}")

        return processed

    def _extract_single_section(
        self, content: str, config: ExtractionConfig
    ) -> ExtractedSection | None:
        """Extract a single section using comment delimiters."""
        try:
            # Find start delimiter
            start_pattern = config.delimiter[0]
            start_match = re.search(
                start_pattern, content, re.IGNORECASE | re.MULTILINE
            )

            if not start_match:
                if self.logger:
                    self.logger.debug(
                        "No start delimiter found", 
                        section_name=config.tpl_ctx_name,
                        pattern=start_pattern
                    )
                return None

            # Find end delimiter
            search_start = start_match.end()
            end_pattern = config.delimiter[1] if len(config.delimiter) > 1 else r"\Z"
            end_match = re.search(
                end_pattern, content[search_start:], re.IGNORECASE | re.MULTILINE
            )

            if end_match:
                content_end = search_start + end_match.start()
            else:
                content_end = len(content)

            # Extract and clean content
            raw_content = content[search_start:content_end].strip()
            cleaned_content = self._clean_section_content(raw_content)

            if not cleaned_content:
                return None

            return ExtractedSection(
                name=config.layer_data_name,
                content=cleaned_content,
                raw_content=raw_content,
                type=config.type,
            )

        except re.error as e:
            if self.logger:
                self.logger.warning("Regex error extracting section", error=str(e))
            return None

    def _clean_section_content(self, content: str) -> str:
        """Clean extracted section content by removing empty lines and pure comments."""
        lines = []

        for line in content.split("\n"):
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Skip pure comment lines
            if stripped.startswith("//") or (
                stripped.startswith("/*") and stripped.endswith("*/")
            ):
                continue

            # Skip template comment lines
            if "{#" in stripped and "#}" in stripped:
                continue

            lines.append(line)

        return "\n".join(lines) if lines else ""

    def _process_section_by_type(
        self, section: ExtractedSection, context: ParsingContext | None = None
    ) -> SectionProcessingResult:
        """Process a section based on its type."""
        try:
            if section.type == "dtsi":
                return SectionProcessingResult(
                    success=True,
                    data=section.content,
                    raw_content=section.raw_content,
                )

            elif section.type in ("behavior", "macro", "combo"):
                return self._process_ast_section(section, context)

            elif section.type == "input_listener":
                # Input listeners need special handling - return as raw content
                return SectionProcessingResult(
                    success=True,
                    data=section.content,
                    raw_content=section.raw_content,
                )

            elif section.type == "keymap":
                return self._process_keymap_section(section, context)

            else:
                return SectionProcessingResult(
                    success=False,
                    error_message=f"Unknown section type: {section.type}",
                    raw_content=section.raw_content,
                )

        except Exception as e:
            if self.logger:
                self.logger.error("Failed to process section by type", error=str(e))
            return SectionProcessingResult(
                success=False,
                error_message=str(e),
                raw_content=section.raw_content,
            )

    def _process_ast_section(
        self, section: ExtractedSection, context: ParsingContext | None = None
    ) -> SectionProcessingResult:
        """Process a section using AST parsing for behaviors, macros, or combos."""
        try:
            # Use raw content for AST parsing to preserve comments
            content_raw = (
                section.raw_content if section.raw_content else section.content
            )

            # Ensure we have a string for parsing
            if not isinstance(content_raw, str):
                return SectionProcessingResult(
                    success=False,
                    error_message="Section content is not a string",
                    raw_content=section.raw_content,
                )

            # Parse section content as AST
            try:
                from .dt_parser import parse_dt_multiple_safe
                roots, parse_errors = parse_dt_multiple_safe(content_raw)
            except ImportError:
                return SectionProcessingResult(
                    success=False,
                    error_message="DT parser not available",
                    raw_content=section.raw_content,
                )

            if not roots:
                return SectionProcessingResult(
                    success=False,
                    error_message="Failed to parse as device tree AST",
                    raw_content=section.raw_content,
                    warnings=[str(e) for e in parse_errors] if parse_errors else [],
                )

            # Extract behaviors using AST converter
            defines = context.defines if context and hasattr(context, "defines") else None
            converted_behaviors = self.behavior_extractor.extract_behaviors_as_models(
                roots, content_raw, defines
            )

            # Return appropriate data based on section type
            if section.type == "behavior":
                data = converted_behaviors if converted_behaviors else {}
            elif section.type == "macro":
                data = converted_behaviors.get("macros", []) if converted_behaviors else []
            elif section.type == "combo":
                data = converted_behaviors.get("combos", []) if converted_behaviors else []
            else:
                data = converted_behaviors if converted_behaviors else {}

            return SectionProcessingResult(
                success=True,
                data=data,
                raw_content=section.raw_content,
                warnings=[str(e) for e in parse_errors] if parse_errors else [],
            )

        except Exception as e:
            if self.logger:
                self.logger.error("AST processing failed", error=str(e))
            return SectionProcessingResult(
                success=False,
                error_message=f"AST processing failed: {e}",
                raw_content=section.raw_content,
            )

    def _process_keymap_section(
        self, section: ExtractedSection, context: ParsingContext | None = None
    ) -> SectionProcessingResult:
        """Process a keymap section to extract layer information."""
        try:
            # For keymap sections, we need to parse layers
            if not isinstance(section.content, str):
                return SectionProcessingResult(
                    success=False,
                    error_message="Section content is not a string",
                    raw_content=section.raw_content,
                )

            # Parse section content as AST  
            try:
                from .dt_parser import parse_dt_multiple_safe
                roots, parse_errors = parse_dt_multiple_safe(section.content)
            except ImportError:
                return SectionProcessingResult(
                    success=False,
                    error_message="DT parser not available",
                    raw_content=section.raw_content,
                )

            if not roots:
                return SectionProcessingResult(
                    success=False,
                    error_message="Failed to parse keymap section as AST",
                    raw_content=section.raw_content,
                    warnings=[str(e) for e in parse_errors] if parse_errors else [],
                )

            # Extract layers using the ZMK keymap parser layer extraction method
            try:
                from .zmk_keymap_parser import ZMKKeymapParser
                temp_parser = ZMKKeymapParser()
                
                # Pass defines if available from context
                if context and hasattr(context, "defines"):
                    temp_parser.defines = context.defines
                
                # Try to extract layers from each root
                layers_data = None
                for root in roots:
                    potential_layers = temp_parser._extract_layers_from_ast(root)
                    if potential_layers:
                        layers_data = potential_layers
                        break
                
                if not layers_data:
                    # No layers found - but this might be OK for template mode
                    layers_data = {"layer_names": [], "layers": []}
                
            except Exception as e:
                if self.logger:
                    self.logger.warning("Failed to extract layers, using empty result", error=str(e))
                layers_data = {"layer_names": [], "layers": []}

            return SectionProcessingResult(
                success=True,
                data=layers_data,
                raw_content=section.raw_content,
                warnings=[str(e) for e in parse_errors] if parse_errors else [],
            )

        except Exception as e:
            if self.logger:
                self.logger.error("Keymap section processing failed", error=str(e))
            return SectionProcessingResult(
                success=False,
                error_message=f"Keymap processing failed: {e}",
                raw_content=section.raw_content,
            )


# Legacy stub classes for backward compatibility
class StubBehaviorExtractor:
    """Stub implementation of behavior extractor."""

    def extract_behaviors_as_models(
        self, roots: list[DTNode], content: str, defines: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Stub implementation."""
        return {}


class StubSectionExtractor:
    """Stub implementation of section extractor."""

    def __init__(self) -> None:
        self._behavior_extractor = StubBehaviorExtractor()

    def extract_sections(self, content: str, configs: list[Any]) -> dict[str, ExtractedSection]:
        """Stub implementation."""
        return {}

    def process_extracted_sections(
        self, sections: dict[str, ExtractedSection], context: ParsingContext
    ) -> dict[str, Any]:
        """Stub implementation."""
        return {}

    @property
    def behavior_extractor(self) -> BehaviorExtractorProtocol:
        """Get behavior extractor."""
        return self._behavior_extractor


def create_section_extractor(
    behavior_extractor: BehaviorExtractorProtocol | None = None,
    logger: "LayoutLogger | None" = None,
) -> SectionExtractorProtocol:
    """Create a section extractor with real implementation."""
    return SectionExtractor(
        behavior_extractor=behavior_extractor,
        logger=logger,
    )
