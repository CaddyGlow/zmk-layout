"""Base model for ZMK layout library."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class LayoutBaseModel(BaseModel):
    """Base model for layout domain, independent of glovebox core.

    This class provides the same functionality as GloveboxBaseModel but without
    dependency on glovebox core infrastructure, enabling standalone library use.
    """

    model_config = ConfigDict(
        # Allow extra fields for flexibility
        extra="allow",
        # Strip whitespace from string fields
        str_strip_whitespace=True,
        # Use enum values in serialization
        use_enum_values=True,
        # Validate assignment after model creation
        validate_assignment=True,
        # allow to load with alias and name
        validate_by_alias=True,
        validate_by_name=True,
    )

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "json",
        by_alias: bool | None = True,
        exclude_unset: bool = False,
        exclude_none: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Override model_dump to default to using aliases.
        """
        # We explicitly set by_alias=True as the default for this method's signature.
        return super().model_dump(
            mode=mode,
            by_alias=by_alias,
            exclude_none=exclude_none,
            **kwargs,
        )

    def model_dump_json(
        self,
        *,
        by_alias: bool | None = True,
        exclude_unset: bool = False,
        exclude_none: bool = True,
        **kwargs: Any,
    ) -> str:
        """Override model_dump_json to default to using aliases.
        """
        return super().model_dump_json(
            by_alias=by_alias,
            exclude_none=exclude_none,
            **kwargs,
        )

    def to_dict(self, exclude_unset: bool = False) -> dict[str, Any]:
        """Export to dictionary with proper field aliases.

        Returns:
            Dictionary representation using JSON-compatible serialization

        """
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
            mode="json",
        )

    def to_json_string(self) -> str:
        """Export to JSON string."""
        import json

        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LayoutBaseModel":
        """Create instance from dictionary."""
        return cls.model_validate(data)

    def to_dict_python(self) -> dict[str, Any]:
        """Convert model to dictionary using Python serialization.

        Returns:
            Dictionary representation using Python types (e.g., datetime objects)

        """
        return self.model_dump(by_alias=True, exclude_unset=False, mode="python")
