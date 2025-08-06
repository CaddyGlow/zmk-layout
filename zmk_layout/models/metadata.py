"""Layout metadata and data models."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pydantic import (
    Field,
    field_serializer,
    model_validator,
)

from .base import LayoutBaseModel
from .types import ConfigValue, LayerBindings


if TYPE_CHECKING:
    from .behaviors import (
        CapsWordBehavior,
        ComboBehavior,
        HoldTapBehavior,
        InputListener,
        MacroBehavior,
        ModMorphBehavior,
        StickyKeyBehavior,
        TapDanceBehavior,
    )


class ConfigParameter(LayoutBaseModel):
    """Model for configuration parameters."""

    param_name: str = Field(alias="paramName")
    value: ConfigValue
    description: str | None = None


class LayoutMetadata(LayoutBaseModel):
    """Pydantic model for layout metadata fields."""

    # Required fields
    keyboard: str
    title: str

    # Optional metadata
    firmware_api_version: str = Field(default="1", alias="firmware_api_version")
    locale: str = Field(default="en-US")
    uuid: str = Field(default="")
    parent_uuid: str = Field(default="", alias="parent_uuid")
    date: datetime = Field(default_factory=datetime.now)

    @field_serializer("date", when_used="json")
    def serialize_date(self, dt: datetime) -> int:
        """Serialize date to Unix timestamp for JSON."""
        return int(dt.timestamp())

    creator: str = Field(default="")
    notes: str = Field(default="")
    tags: list[str] = Field(default_factory=list)

    # Variables for substitution
    variables: dict[str, Any] = Field(
        default_factory=dict,
        description="Global variables for substitution using ${variable_name} syntax",
    )

    # Configuration
    config_parameters: list[ConfigParameter] = Field(default_factory=list, alias="config_parameters")

    layer_names: list[str] = Field(default_factory=list, alias="layer_names")

    # Version tracking for layout management
    version: str = Field(default="1.0.0")
    base_version: str = Field(default="")  # Master version this is based on
    base_layout: str = Field(default="")  # e.g., "glorious-engrammer"


class LayoutData(LayoutMetadata):
    """Complete layout data model following Moergo API field names with aliases."""

    # User behavior definitions
    hold_taps: list["HoldTapBehavior"] = Field(default_factory=list, alias="holdTaps")
    combos: list["ComboBehavior"] = Field(default_factory=list)
    macros: list["MacroBehavior"] = Field(default_factory=list)
    tap_dances: list["TapDanceBehavior"] = Field(default_factory=list, alias="tapDances")
    sticky_keys: list["StickyKeyBehavior"] = Field(default_factory=list, alias="stickyKeys")
    caps_words: list["CapsWordBehavior"] = Field(default_factory=list, alias="capsWords")
    mod_morphs: list["ModMorphBehavior"] = Field(default_factory=list, alias="modMorphs")
    input_listeners: list["InputListener"] | None = Field(default=None, alias="inputListeners")

    # Essential structure fields
    layers: list[LayerBindings] = Field(default_factory=list)

    # Custom code
    custom_defined_behaviors: str = Field(default="", alias="custom_defined_behaviors")
    custom_devicetree: str = Field(default="", alias="custom_devicetree")

    @model_validator(mode="before")
    @classmethod
    def validate_data_structure(
        cls,
        data: dict[str, Any] | Any,
        _info: Any = None,
    ) -> dict[str, Any] | Any:
        """Validate basic data structure without template processing.

        This only handles basic data structure validation like date conversion.
        Template processing is handled separately by external providers.

        Args:
            data: Input data to validate
            _info: Pydantic validation info (unused)

        Returns:
            Validated data structure

        """
        if not isinstance(data, dict):
            return data

        # Convert integer timestamps to datetime objects for date fields
        if "date" in data and isinstance(data["date"], int):
            data["date"] = datetime.fromtimestamp(data["date"], tz=UTC)

        return data

    def _has_template_syntax(self, data: dict[str, Any]) -> bool:
        """Check if data contains template syntax patterns.

        Args:
            data: Dictionary to check for template patterns

        Returns:
            True if template syntax is detected

        """
        template_patterns = ["{{", "}}", "{%", "%}", "${", "}"]

        def check_value(value: dict[str, Any] | list[Any] | str | Any) -> bool:
            if isinstance(value, str):
                return any(pattern in value for pattern in template_patterns)
            if isinstance(value, dict):
                return any(check_value(v) for v in value.values())
            if isinstance(value, list):
                return any(check_value(item) for item in value)
            return False

        return check_value(data)


class LayoutResult(LayoutBaseModel):
    """Result model for layout operations."""

    success: bool = False
    messages: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    keymap_path: str | None = None
    conf_path: str | None = None

    def add_message(self, message: str) -> None:
        """Add a success message."""
        self.messages.append(message)

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
