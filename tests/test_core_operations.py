"""Tests for ZMK layout core operations.

This module provides comprehensive tests for the core operations in the generators module,
specifically testing the resolve_template_file_path function which is currently a stub
implementation.
"""

from pathlib import Path

import pytest

from zmk_layout.generators.core_operations import resolve_template_file_path


class TestResolveTemplateFilePath:
    """Test the resolve_template_file_path function."""

    @pytest.mark.parametrize(
        "keyboard_name, template_file, expected",
        [
            # Falsy template_file inputs should return None
            ("test_keyboard", "", None),
            ("any_keyboard", "  ", Path("  ")),  # whitespace is truthy in Python
            # Truthy template_file inputs should return Path object
            ("test_keyboard", "template.txt", Path("template.txt")),
            ("glove80", "keymap.keymap", Path("keymap.keymap")),
            ("split_keyboard", "/absolute/path/template.j2", Path("/absolute/path/template.j2")),
            ("crkbd", "relative/path/config.conf", Path("relative/path/config.conf")),
            ("ferris", "sub/dir/template.dtsi.j2", Path("sub/dir/template.dtsi.j2")),
        ],
    )
    def test_resolve_template_file_path_basic_cases(
        self, keyboard_name: str, template_file: str, expected: Path | None
    ) -> None:
        """Test basic functionality with various input combinations."""
        result = resolve_template_file_path(keyboard_name, template_file)

        if expected is None:
            assert result is None
        else:
            assert isinstance(result, Path)
            assert result == expected

    def test_falsy_template_file_returns_none(self) -> None:
        """Test that falsy template_file values return None."""
        # Empty string should return None
        result = resolve_template_file_path("keyboard", "")
        assert result is None

    def test_truthy_template_file_returns_path(self) -> None:
        """Test that truthy template_file values return Path objects."""
        test_cases = [
            "simple.txt",
            "path/to/file.j2",
            "/absolute/path/template.keymap",
            "file-with-dashes.conf",
            "file_with_underscores.dtsi",
            "file.with.dots.txt",
        ]

        for template_file in test_cases:
            result = resolve_template_file_path("test_keyboard", template_file)
            assert isinstance(result, Path)
            assert result == Path(template_file)

    def test_keyboard_name_parameter_ignored(self) -> None:
        """Test that different keyboard_name values don't affect the result (stub behavior)."""
        template_file = "test_template.txt"

        # Different keyboard names should produce identical results
        result1 = resolve_template_file_path("keyboard_one", template_file)
        result2 = resolve_template_file_path("keyboard_two", template_file)
        result3 = resolve_template_file_path("completely_different_keyboard", template_file)

        assert result1 == result2 == result3 == Path(template_file)

    @pytest.mark.parametrize(
        "template_file",
        [
            "unicode_café.txt",
            "emojis_🎹⌨️.keymap",
            "spaces in filename.conf",
            "special-chars!@#$%^&*().j2",
            "very_long_filename_" + "x" * 200 + ".txt",
            ".hidden_file",
            "file_with_no_extension",
            "UPPERCASE_FILE.KEYMAP",
        ],
    )
    def test_edge_case_template_filenames(self, template_file: str) -> None:
        """Test edge cases with special characters, unicode, and unusual filenames."""
        result = resolve_template_file_path("test_keyboard", template_file)

        assert isinstance(result, Path)
        assert result == Path(template_file)
        # Verify the path string representation matches the input
        assert str(result) == template_file

    def test_whitespace_only_template_file(self) -> None:
        """Test that whitespace-only strings are treated as truthy."""
        test_cases = [
            " ",  # single space
            "  ",  # multiple spaces
            "\t",  # tab
            "\n",  # newline
            " \t\n",  # mixed whitespace
        ]

        for template_file in test_cases:
            result = resolve_template_file_path("keyboard", template_file)
            assert isinstance(result, Path)
            assert result == Path(template_file)

    def test_path_separators_handled_correctly(self) -> None:
        """Test that different path separators are handled by Path constructor."""
        test_cases = [
            "unix/style/path.txt",
            "windows\\style\\path.txt",
            "mixed/style\\path.txt",
            "./relative/path.txt",
            "../parent/path.txt",
            "/absolute/unix/path.txt",
            "C:\\absolute\\windows\\path.txt",
        ]

        for template_file in test_cases:
            result = resolve_template_file_path("keyboard", template_file)
            assert isinstance(result, Path)
            assert result == Path(template_file)

    def test_return_type_consistency(self) -> None:
        """Test that return types are consistent with function signature."""
        # None case
        none_result = resolve_template_file_path("keyboard", "")
        assert none_result is None

        # Path case
        path_result = resolve_template_file_path("keyboard", "file.txt")
        assert isinstance(path_result, Path)
        assert path_result == Path("file.txt")

    def test_function_is_pure(self) -> None:
        """Test that the function is pure (same inputs produce same outputs)."""
        keyboard_name = "test_keyboard"
        template_file = "test_template.txt"

        # Multiple calls with same inputs should produce identical results
        result1 = resolve_template_file_path(keyboard_name, template_file)
        result2 = resolve_template_file_path(keyboard_name, template_file)
        result3 = resolve_template_file_path(keyboard_name, template_file)

        assert result1 == result2 == result3
        assert all(isinstance(r, Path) for r in [result1, result2, result3])

    def test_stub_implementation_behavior(self) -> None:
        """Test the current stub implementation behavior explicitly."""
        # This test documents the current stub behavior
        # When the real implementation is added, this test may need updates

        # Test 1: keyboard_name is completely ignored
        assert resolve_template_file_path("kbd1", "file.txt") == resolve_template_file_path("kbd2", "file.txt")

        # Test 2: Only template_file truthiness matters
        assert resolve_template_file_path("any_keyboard", "") is None
        assert resolve_template_file_path("any_keyboard", "anything") == Path("anything")

        # Test 3: No actual file resolution occurs (stub behavior)
        non_existent_file = "definitely_does_not_exist_12345.txt"
        result = resolve_template_file_path("keyboard", non_existent_file)
        assert result == Path(non_existent_file)  # Returns Path even if file doesn't exist

    @pytest.mark.parametrize(
        "keyboard_name",
        [
            "simple_keyboard",
            "keyboard-with-dashes",
            "keyboard_with_underscores",
            "KeyboardWithCamelCase",
            "UPPERCASE_KEYBOARD",
            "keyboard.with.dots",
            "keyboard/with/slashes",
            "keyboard with spaces",
            "unicode_кeyboard",
            "emojis_🎹",
            "",  # empty keyboard name
            "very_long_keyboard_name_" + "x" * 100,
        ],
    )
    def test_various_keyboard_names_ignored(self, keyboard_name: str) -> None:
        """Test that various keyboard name formats don't affect the result."""
        template_file = "test.txt"
        result = resolve_template_file_path(keyboard_name, template_file)

        # Result should always be the same regardless of keyboard_name
        assert result == Path(template_file)
