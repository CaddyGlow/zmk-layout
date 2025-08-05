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
        import lark  # type: ignore[import-not-found] # noqa: F401

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
    if has_jinja2():
        # TODO: Implement Jinja2TemplateProvider when needed
        from zmk_layout.providers.factory import DefaultTemplateProvider

        return DefaultTemplateProvider()
    else:
        from zmk_layout.providers.factory import DefaultTemplateProvider

        return DefaultTemplateProvider()


def get_parser_provider() -> Any:
    """Get parser provider with fallback."""
    if has_lark():
        # TODO: Implement Lark-based parser
        pass
    # TODO: Implement fallback parser
    return None


def get_display_provider() -> Any:
    """Get display provider with fallback."""
    if has_rich():
        # TODO: Implement Rich-based display
        pass
    # TODO: Implement simple display
    return None


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
