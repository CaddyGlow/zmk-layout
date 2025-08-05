"""Section extractor for ZMK keymap parsing."""

from typing import Any, Protocol

from .ast_nodes import DTNode
from .parsing_models import ExtractedSection, ParsingContext


class BehaviorExtractorProtocol(Protocol):
    """Protocol for behavior extraction."""
    
    def extract_behaviors_as_models(
        self, 
        roots: list[DTNode], 
        content: str, 
        defines: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Extract behaviors from AST roots and return as models."""
        ...


class SectionExtractorProtocol(Protocol):
    """Protocol for section extraction."""
    
    def extract_sections(self, content: str, configs: list[Any]) -> dict[str, ExtractedSection]:
        """Extract sections from content."""
        ...
        
    def process_extracted_sections(self, sections: dict[str, ExtractedSection], context: ParsingContext) -> dict[str, Any]:
        """Process extracted sections."""
        ...
        
    @property
    def behavior_extractor(self) -> BehaviorExtractorProtocol:
        """Get behavior extractor."""
        ...


class StubBehaviorExtractor:
    """Stub implementation of behavior extractor."""
    
    def extract_behaviors_as_models(
        self, 
        roots: list[DTNode], 
        content: str, 
        defines: dict[str, str] | None = None
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
        
    def process_extracted_sections(self, sections: dict[str, ExtractedSection], context: ParsingContext) -> dict[str, Any]:
        """Stub implementation.""" 
        return {}
        
    @property
    def behavior_extractor(self) -> BehaviorExtractorProtocol:
        """Get behavior extractor."""
        return self._behavior_extractor


def create_section_extractor() -> SectionExtractorProtocol:
    """Create a section extractor."""
    return StubSectionExtractor()