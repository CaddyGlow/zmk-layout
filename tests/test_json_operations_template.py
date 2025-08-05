"""Tests for template processing functionality in json_operations.py."""

import json
from pathlib import Path

import pytest

from zmk_layout.utils.json_operations import load_layout_file


class StubFileProvider:
    """Minimal in-memory FileProvider stub."""
    def __init__(self, files: dict[Path, str]) -> None:
        self._files = files

    def read_text(self, path: Path | str, encoding: str = "utf-8") -> str:
        """Read text content from a file."""
        path_key = Path(path)
        return self._files[path_key]

    def write_text(self, path: Path | str, content: str, encoding: str = "utf-8") -> None:
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

    def mkdir(self, path: Path | str, parents: bool = False, exist_ok: bool = False) -> None:
        """Create a directory."""
        pass


class StubTemplateProvider:
    """TemplateProvider stub that renders {var} or {{var}} style placeholders."""
    def __init__(self) -> None:
        self.render_calls: list[tuple[str, dict[str, str | int | float | bool | None]]] = []

    def has_template_syntax(self, content: str) -> bool:
        # Simple template detection - look for {variable} patterns, not JSON braces
        import re
        return bool(re.search(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', content))

    def render_string(self, template: str, context: dict[str, str | int | float | bool | None]) -> str:
        self.render_calls.append((template, context))
        # very naive replace to keep dependency-free
        return template.replace("{name}", "Rendered")

    def escape_content(self, content: str) -> str:
        return content.replace("{", "{{").replace("}", "}}")


@pytest.fixture()
def valid_layout_json() -> str:
    # Minimal JSON that satisfies LayoutData.model_validate
    return json.dumps({"keyboard": "kb", "title": "Sample", "layers": [], "layer_names": []})


def test_happy_path_renders_template(tmp_path: Path, valid_layout_json: str) -> None:
    path = tmp_path / "layout.json"
    file_provider = StubFileProvider({path: valid_layout_json.replace("Sample", "{name}")})
    template_provider = StubTemplateProvider()

    result = load_layout_file(
        path,
        file_provider=file_provider,
        template_provider=template_provider,
    )

    assert result.title == "Rendered"
    # ensure template engine was actually used
    assert len(template_provider.render_calls) == 1


def test_skip_template_processing_flag(tmp_path: Path, valid_layout_json: str) -> None:
    path = tmp_path / "layout.json"
    file_provider = StubFileProvider({path: valid_layout_json.replace("Sample", "{name}")})
    template_provider = StubTemplateProvider()

    result = load_layout_file(
        path,
        file_provider=file_provider,
        skip_template_processing=True,
        template_provider=template_provider,
    )
    # Title should remain the literal string containing template syntax
    assert result.title == "{name}"
    assert template_provider.render_calls == []


def test_provider_none_no_render(tmp_path: Path, valid_layout_json: str) -> None:
    """If no template provider is supplied, content must bypass rendering."""
    path = tmp_path / "layout.json"
    file_provider = StubFileProvider({path: valid_layout_json.replace("Sample", "{name}")})

    result = load_layout_file(
        path,
        file_provider=file_provider,
        template_provider=None,
    )
    assert result.title == "{name}"


def test_no_template_syntax_skips_rendering(tmp_path: Path, valid_layout_json: str) -> None:
    """Content without template syntax should skip rendering even with provider."""
    path = tmp_path / "layout.json"
    file_provider = StubFileProvider({path: valid_layout_json})
    template_provider = StubTemplateProvider()

    result = load_layout_file(
        path,
        file_provider=file_provider,
        template_provider=template_provider,
    )
    assert result.title == "Sample"
    assert template_provider.render_calls == []


def test_template_provider_render_exception(tmp_path: Path, valid_layout_json: str) -> None:
    """Template provider render failures should propagate as ValueError."""
    path = tmp_path / "layout.json"
    file_provider = StubFileProvider({path: valid_layout_json.replace("Sample", "{name}")})
    
    class FailingTemplateProvider:
        def has_template_syntax(self, content: str) -> bool:
            return True
        
        def render_string(self, template: str, context: dict[str, str | int | float | bool | None]) -> str:
            raise RuntimeError("Template render failed")
        
        def escape_content(self, content: str) -> str:
            return content
    
    template_provider = FailingTemplateProvider()

    with pytest.raises(ValueError, match="Invalid layout data"):
        load_layout_file(
            path,
            file_provider=file_provider,
            template_provider=template_provider,
        )


def test_invalid_json_raises(tmp_path: Path) -> None:
    """Malformed JSON must surface JSONDecodeError."""
    path = tmp_path / "layout.json"
    file_provider = StubFileProvider({path: "{ invalid json }"})
    template_provider = StubTemplateProvider()

    with pytest.raises(json.JSONDecodeError):
        load_layout_file(path, file_provider, template_provider=template_provider)


def test_file_not_found(tmp_path: Path) -> None:
    """Missing file should raise FileNotFoundError."""
    path = tmp_path / "nonexistent.json"
    file_provider = StubFileProvider({})
    template_provider = StubTemplateProvider()

    with pytest.raises(FileNotFoundError, match="Layout file not found"):
        load_layout_file(path, file_provider, template_provider=template_provider)


def test_template_context_is_empty_dict(tmp_path: Path, valid_layout_json: str) -> None:
    """Verify that template context is currently an empty dict."""
    path = tmp_path / "layout.json"
    file_provider = StubFileProvider({path: valid_layout_json.replace("Sample", "{name}")})
    template_provider = StubTemplateProvider()

    load_layout_file(
        path,
        file_provider=file_provider,
        template_provider=template_provider,
    )

    # Verify empty context was passed
    assert len(template_provider.render_calls) == 1
    _, context = template_provider.render_calls[0]
    assert context == {}


def test_variable_resolution_flag_isolation(tmp_path: Path, valid_layout_json: str) -> None:
    """Ensure global flag is properly restored after processing."""
    from zmk_layout.utils.json_operations import _skip_variable_resolution
    
    path = tmp_path / "layout.json"
    file_provider = StubFileProvider({path: valid_layout_json})
    
    # Check initial state
    initial_value = _skip_variable_resolution
    
    # Load with skip_variable_resolution=True
    load_layout_file(
        path,
        file_provider=file_provider,
        skip_variable_resolution=True,
    )
    
    # Flag should be restored to initial value
    assert _skip_variable_resolution == initial_value