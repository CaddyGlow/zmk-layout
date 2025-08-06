"""Tests for profile parser fallback functionality."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

from zmk_layout.parsers.parsing_models import get_default_extraction_config
from zmk_layout.parsers.zmk_keymap_parser import ZMKKeymapParser


def test_extraction_config_from_profile() -> None:
    """Test extraction config when profile has keymap_extraction."""
    profile = SimpleNamespace(
        keymap_extraction=SimpleNamespace(sections=["layers", "behaviors"]),
        keyboard_name="kb",
    )
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(profile)  # type: ignore[arg-type]
    assert cfg == ["layers", "behaviors"]


def test_extraction_config_default_when_missing() -> None:
    """Test fallback to default when no profile provided."""
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(None)
    assert cfg is None


def test_extraction_config_default_when_profile_none() -> None:
    """Test fallback to default when profile is None."""
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(None)
    assert cfg is None


def test_extraction_config_default_on_profile_error() -> None:
    """Test fallback to default when profile access raises exception."""

    class BadProfile:
        keyboard_name = "kb"

        # accessing keymap_extraction will raise
        @property
        def keymap_extraction(self) -> None:
            raise RuntimeError("broken profile")

    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(BadProfile())  # type: ignore[arg-type]
    assert cfg is None


def test_extraction_config_profile_missing_keymap_extraction() -> None:
    """Test when profile exists but lacks keymap_extraction attribute."""
    profile = SimpleNamespace(keyboard_name="kb")  # No keymap_extraction
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(profile)  # type: ignore[arg-type]
    assert cfg is None


def test_extraction_config_profile_keymap_extraction_none() -> None:
    """Test when profile has keymap_extraction but it's None."""
    profile = SimpleNamespace(
        keymap_extraction=None,
        keyboard_name="kb",
    )
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(profile)  # type: ignore[arg-type]
    assert cfg is None


def test_extraction_config_profile_keymap_extraction_false() -> None:
    """Test when profile has keymap_extraction but it's falsy."""
    profile = SimpleNamespace(
        keymap_extraction=False,
        keyboard_name="kb",
    )
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(profile)  # type: ignore[arg-type]
    assert cfg is None


def test_extraction_config_with_logger_warning(caplog: Any) -> None:
    """Test that logger warnings are emitted on profile errors."""

    class BadProfile:
        keyboard_name = "test_kb"

        @property
        def keymap_extraction(self) -> None:
            raise ValueError("Profile error")

    # Create mock logger
    mock_logger = Mock()
    parser = ZMKKeymapParser(logger=mock_logger)

    cfg = parser._get_extraction_config(BadProfile())  # type: ignore[arg-type]

    # Should fallback to default
    assert cfg is None

    # Should log warning
    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args
    assert "Failed to load extraction config from profile" in call_args[0][0]
    assert call_args[1]["profile_name"] == "test_kb"
    assert "Profile error" in call_args[1]["error"]


def test_extraction_config_profile_without_keyboard_name() -> None:
    """Test profile error handling when keyboard_name is missing."""

    class ProfileWithoutName:
        @property
        def keymap_extraction(self) -> None:
            raise RuntimeError("broken")

    mock_logger = Mock()
    parser = ZMKKeymapParser(logger=mock_logger)

    cfg = parser._get_extraction_config(ProfileWithoutName())  # type: ignore[arg-type]

    assert cfg is None

    # Should log warning with "unknown" profile name
    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args
    assert call_args[1]["profile_name"] == "unknown"


def test_extraction_config_sections_list_conversion() -> None:
    """Test that sections are properly converted to list."""
    # Use tuple instead of list to test conversion
    profile = SimpleNamespace(
        keymap_extraction=SimpleNamespace(sections=("layers", "behaviors")),
        keyboard_name="kb",
    )
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(profile)  # type: ignore[arg-type]
    assert cfg == ["layers", "behaviors"]
    assert isinstance(cfg, list)


def test_extraction_config_complex_profile_structure() -> None:
    """Test with more complex profile structure."""
    profile = SimpleNamespace(
        keymap_extraction=SimpleNamespace(
            sections=["layers", "behaviors", "macros", "combos"]
        ),
        keyboard_name="complex_kb",
        other_attributes="should_be_ignored",
    )
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(profile)  # type: ignore[arg-type]
    expected = ["layers", "behaviors", "macros", "combos"]
    assert cfg == expected


def test_extraction_config_empty_sections() -> None:
    """Test with empty sections list."""
    profile = SimpleNamespace(
        keymap_extraction=SimpleNamespace(sections=[]),
        keyboard_name="kb",
    )
    parser = ZMKKeymapParser()
    cfg = parser._get_extraction_config(profile)  # type: ignore[arg-type]
    assert cfg == []


def test_extraction_config_without_logger() -> None:
    """Test error handling when no logger is provided."""

    class BadProfile:
        keyboard_name = "kb"

        @property
        def keymap_extraction(self) -> None:
            raise RuntimeError("broken profile")

    parser = ZMKKeymapParser(logger=None)  # No logger
    cfg = parser._get_extraction_config(BadProfile())  # type: ignore[arg-type]

    # Should still fallback gracefully
    assert cfg is None


def test_get_default_extraction_config_returns_list() -> None:
    """Ensure get_default_extraction_config returns a list of ExtractionConfig."""
    config = get_default_extraction_config()
    assert isinstance(config, list)
    # Current implementation returns list of ExtractionConfig objects
    assert len(config) > 0  # Should have default extraction configs
