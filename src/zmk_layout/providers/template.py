"""Template provider protocol for layout domain abstraction."""

from typing import Any, Protocol


class TemplateProvider(Protocol):
    """Protocol for providing template processing capabilities.

    This abstraction enables the layout library to operate independently
    of the specific template engine implementation (Jinja2, etc.).
    """

    def render_string(self, template: str, context: dict[str, Any]) -> str:
        """Render a template string with given context.

        Args:
            template: Template string with template syntax
            context: Dictionary of variables for template rendering

        Returns:
            Rendered content with template variables substituted
        """
        ...

    def has_template_syntax(self, content: str) -> bool:
        """Check if content contains template syntax requiring processing.

        Args:
            content: String content to check

        Returns:
            True if content contains template syntax, False otherwise
        """
        ...

    def escape_content(self, content: str) -> str:
        """Escape content to prevent template processing.

        Args:
            content: Content to escape

        Returns:
            Escaped content that won't be processed as template
        """
        ...