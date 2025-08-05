"""Parsing models and data classes for ZMK keymap parsing."""

from typing import Any

from zmk_layout.models.base import LayoutBaseModel


class ParsingContext(LayoutBaseModel):
    """Context for parsing operations."""

    keyboard_name: str = ""
    title: str = ""
    keymap_content: str = ""
    warnings: list[str] = []
    errors: list[str] = []
    defines: dict[str, str] = {}
    extraction_config: dict[str, Any] | None = None
    extracted_sections: dict[str, Any] = {}


class ExtractedSection(LayoutBaseModel):
    """Extracted section from keymap content."""

    name: str
    content: str | dict[str, object] | list[object]
    raw_content: str
    type: str


class ExtractionConfig(LayoutBaseModel):
    """Configuration for extraction operations."""

    name: str = ""
    enabled: bool = True
    settings: dict[str, Any] = {}


def get_default_extraction_config() -> dict[str, Any]:
    """Get default extraction configuration."""
    return {}
