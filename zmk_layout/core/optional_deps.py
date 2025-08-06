"""Optional dependency management with graceful fallbacks."""

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from zmk_layout.providers import TemplateProvider


def has_jinja2() -> bool:
    """Check if jinja2 is available."""
    try:
        import jinja2  # type: ignore[import-not-found] # noqa: F401

        return True
    except ImportError:
        return False


def has_lark() -> bool:
    """Check if lark parser is available."""
    try:
        import lark  # noqa: F401

        return True
    except ImportError:
        return False


def has_rich() -> bool:
    """Check if rich display library is available."""
    try:
        import rich  # type: ignore[import-not-found] # noqa: F401

        return True
    except ImportError:
        return False


def get_template_provider() -> "TemplateProvider":
    """Get template provider with fallback."""
    try:
        from zmk_layout.providers.factory import DefaultTemplateProvider

        return DefaultTemplateProvider()
    except ImportError:
        # If we can't import the fallback provider, create a minimal inline provider
        # that doesn't require any imports
        class NullTemplateProvider:
            def render_string(self, template: str, context: dict[str, Any] | None = None) -> str:
                return template

            def has_template_syntax(self, text: str) -> bool:
                return False

            def escape_content(self, content: str) -> str:
                return content

        return NullTemplateProvider()


def get_parser_provider() -> Any:
    """Get parser provider with fallback."""
    if has_lark():
        try:
            from lark import Lark

            class LarkParserProvider:
                def __init__(self) -> None:
                    # Basic device tree grammar for parsing
                    self.parser = Lark("""
                        start: item*
                        item: node | property | comment
                        node: NAME "{" item* "}" ";"?
                        property: NAME "=" value ";"
                        value: string | number | reference | array
                        array: "<" value* ">"
                        reference: "&" NAME
                        string: ESCAPED_STRING
                        number: NUMBER
                        comment: COMMENT

                        NAME: /[a-zA-Z_][a-zA-Z0-9_-]*/
                        COMMENT: /\\/\\/[^\\n]*/

                        %import common.ESCAPED_STRING
                        %import common.NUMBER
                        %import common.WS
                        %ignore WS
                        %ignore COMMENT
                    """)

                def parse(self, content: str) -> Any:
                    try:
                        return self.parser.parse(content)
                    except Exception:
                        return None

            return LarkParserProvider()
        except Exception:
            pass

    # Fallback basic parser
    class BasicParserProvider:
        def parse(self, content: str) -> Any:
            # Very basic parsing - just extract sections
            sections = {}
            lines = content.split("\n")
            current_section: list[str] = []
            section_name = None

            for line in lines:
                line = line.strip()
                if line.endswith("{"):
                    if current_section and section_name:
                        sections[section_name] = "\n".join(current_section)
                    section_name = line.rstrip(" {")
                    current_section = []
                elif line == "};" and section_name:
                    sections[section_name] = "\n".join(current_section)
                    section_name = None
                    current_section = []
                elif section_name:
                    current_section.append(line)

            return sections

    return BasicParserProvider()


def get_display_provider() -> Any:
    """Get display provider with fallback."""
    if has_rich():
        try:
            from rich.console import Console  # type: ignore[import-not-found]
            from rich.panel import Panel  # type: ignore[import-not-found]
            from rich.syntax import Syntax  # type: ignore[import-not-found]
            from rich.table import Table  # type: ignore[import-not-found]

            class RichDisplayProvider:
                def __init__(self) -> None:
                    self.console = Console()

                def print(self, *args: Any, **kwargs: Any) -> None:
                    self.console.print(*args, **kwargs)

                def print_table(self, data: list[dict[str, Any]], title: str = "") -> None:
                    if not data:
                        return

                    table = Table(title=title)
                    # Add columns based on first row keys
                    for key in data[0]:
                        table.add_column(str(key).title())

                    # Add rows
                    for row in data:
                        table.add_row(*[str(value) for value in row.values()])

                    self.console.print(table)

                def print_panel(self, content: str, title: str = "") -> None:
                    panel = Panel(content, title=title)
                    self.console.print(panel)

                def print_syntax(self, code: str, language: str = "yaml") -> None:
                    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
                    self.console.print(syntax)

            return RichDisplayProvider()
        except Exception:
            pass

    # Simple fallback display
    class SimpleDisplayProvider:
        def print(self, *args: Any, **kwargs: Any) -> None:
            print(*args, **kwargs)

        def print_table(self, data: list[dict[str, Any]], title: str = "") -> None:
            if title:
                print(f"\n{title}")
                print("=" * len(title))

            if not data:
                print("No data to display")
                return

            # Simple table formatting
            headers = list(data[0].keys())
            print("\t".join(headers))
            print("\t".join(["-" * len(h) for h in headers]))

            for row in data:
                print("\t".join([str(value) for value in row.values()]))

        def print_panel(self, content: str, title: str = "") -> None:
            if title:
                print(f"\n[{title}]")
            print(content)

        def print_syntax(self, code: str, language: str = "yaml") -> None:
            print(code)

    return SimpleDisplayProvider()


def require_optional_dependency(name: str, feature: str) -> None:
    """Raise helpful error for missing optional dependency.

    Args:
        name: Name of the missing package
        feature: Feature that requires the package

    Raises:
        ImportError: With helpful installation message
    """
    raise ImportError(
        f"The '{name}' package is required for {feature}. "
        f"Install it with: pip install zmk-layout[{_get_extra_name(name)}] "
        f"or pip install {name}"
    )


def _get_extra_name(package_name: str) -> str:
    """Map package name to extras name."""
    mapping = {"jinja2": "templating", "rich": "display", "lark": "parsing", "jsonpatch": "full"}
    return mapping.get(package_name, package_name)
