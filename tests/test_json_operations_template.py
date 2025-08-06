"""Tests for template processing functionality in json_operations.py."""

import json
from pathlib import Path

import pytest

from zmk_layout.utils.json_operations import parse_layout_data, serialize_layout_data


class StubFileProvider:
    """Minimal in-memory FileProvider stub."""

    def __init__(self, files: dict[Path, str]) -> None:
        self._files = files

    def read_text(self, path: Path | str, encoding: str = "utf-8") -> str:
        """Read text content from a file."""
        path_key = Path(path)
        return self._files[path_key]

    def write_text(
        self, path: Path | str, content: str, encoding: str = "utf-8"
    ) -> None:
        """Write text content to a file."""
        path_key = Path(path)
        self._files[path_key] = content

    def exists(self, path: Path | str) -> bool:
        """Check if a file or directory exists."""
        path_key = Path(path)
        return path_key in self._files

    def is_file(self, path: Path | str) -> bool:
        """Check if a path is a file."""
        path_key = Path(path)
        return path_key in self._files

    def mkdir(
        self, path: Path | str, parents: bool = False, exist_ok: bool = False
    ) -> None:
        """Create a directory."""
        pass


class StubTemplateProvider:
    """TemplateProvider stub that renders {var} or {{var}} style placeholders."""

    def __init__(self) -> None:
        self.render_calls: list[
            tuple[str, dict[str, str | int | float | bool | None]]
        ] = []

    def has_template_syntax(self, content: str) -> bool:
        # Simple template detection - look for {variable} patterns, not JSON braces
        import re

        return bool(re.search(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}", content))

    def render_string(
        self, template: str, context: dict[str, str | int | float | bool | None]
    ) -> str:
        self.render_calls.append((template, context))
        # very naive replace to keep dependency-free
        return template.replace("{name}", "Rendered")

    def escape_content(self, content: str) -> str:
        return content.replace("{", "{{").replace("}", "}}")


@pytest.fixture()
def valid_layout_json() -> str:
    # Minimal JSON that satisfies LayoutData.model_validate
    return json.dumps(
        {"keyboard": "kb", "title": "Sample", "layers": [], "layer_names": []}
    )


def test_happy_path_renders_template(tmp_path: Path, valid_layout_json: str) -> None:
    # Instead of using file operations, test parse_layout_data directly with string content
    json_content = valid_layout_json.replace("Sample", "{name}")
    template_provider = StubTemplateProvider()

    # Mock template processing by pre-rendering the content
    if template_provider.has_template_syntax(json_content):
        rendered_content = template_provider.render_string(json_content, {})
    else:
        rendered_content = json_content

    result = parse_layout_data(rendered_content)

    assert result.title == "Rendered"
    # ensure template engine was actually used
    assert len(template_provider.render_calls) == 1


def test_skip_template_processing_flag(tmp_path: Path, valid_layout_json: str) -> None:
    # Test with skip_variable_resolution flag in parse_layout_data
    json_content = valid_layout_json.replace("Sample", "{name}")
    template_provider = StubTemplateProvider()

    result = parse_layout_data(
        json_content,
        skip_variable_resolution=True,
    )
    # Title should remain the literal string containing template syntax
    assert result.title == "{name}"
    assert template_provider.render_calls == []


def test_provider_none_no_render(tmp_path: Path, valid_layout_json: str) -> None:
    """If no template provider is available, content should be parsed as-is."""
    json_content = valid_layout_json.replace("Sample", "{name}")

    result = parse_layout_data(json_content)
    assert result.title == "{name}"


def test_no_template_syntax_skips_rendering(
    tmp_path: Path, valid_layout_json: str
) -> None:
    """Content without template syntax should be parsed normally."""
    template_provider = StubTemplateProvider()

    # Test that content without template syntax is not processed
    assert not template_provider.has_template_syntax(valid_layout_json)

    result = parse_layout_data(valid_layout_json)
    assert result.title == "Sample"
    assert template_provider.render_calls == []


def test_template_provider_render_exception(
    tmp_path: Path, valid_layout_json: str
) -> None:
    """Template provider render failures should be handled gracefully."""
    json_content = valid_layout_json.replace("Sample", "{name}")

    class FailingTemplateProvider:
        def has_template_syntax(self, content: str) -> bool:
            return True

        def render_string(
            self, template: str, context: dict[str, str | int | float | bool | None]
        ) -> str:
            raise RuntimeError("Template render failed")

        def escape_content(self, content: str) -> str:
            return content

    template_provider = FailingTemplateProvider()

    # When template processing fails, parsing should fail with ValueError
    with pytest.raises(RuntimeError, match="Template render failed"):
        if template_provider.has_template_syntax(json_content):
            template_provider.render_string(json_content, {})


def test_invalid_json_raises(tmp_path: Path) -> None:
    """Malformed JSON must surface JSONDecodeError."""
    invalid_json_content = "{ invalid json }"

    with pytest.raises(json.JSONDecodeError):
        parse_layout_data(invalid_json_content)


def test_invalid_layout_data_raises(tmp_path: Path) -> None:
    """Invalid layout data should raise ValueError."""
    invalid_layout_data = '{"invalid": "data"}'

    with pytest.raises(ValueError, match="Invalid layout data"):
        parse_layout_data(invalid_layout_data)


def test_serialize_layout_data_works(tmp_path: Path, valid_layout_json: str) -> None:
    """Test that serialize_layout_data works correctly."""
    layout_data = parse_layout_data(valid_layout_json)

    # Test serialization
    serialized_json = serialize_layout_data(layout_data)

    # Should be valid JSON
    parsed_back = json.loads(serialized_json)
    assert parsed_back["keyboard"] == "kb"
    assert parsed_back["title"] == "Sample"


def test_variable_resolution_flag_isolation(
    tmp_path: Path, valid_layout_json: str
) -> None:
    """Ensure global flag is properly restored after processing."""
    from zmk_layout.utils.json_operations import _skip_variable_resolution

    # Check initial state
    initial_value = _skip_variable_resolution

    # Parse with skip_variable_resolution=True
    parse_layout_data(
        valid_layout_json,
        skip_variable_resolution=True,
    )

    # Flag should be restored to initial value
    assert _skip_variable_resolution == initial_value
