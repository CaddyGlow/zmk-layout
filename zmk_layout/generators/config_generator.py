"""Layout generation utilities for configuration and keymap files."""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Any

from zmk_layout.models import LayoutData
from zmk_layout.models.metadata import LayoutResult
from zmk_layout.providers import FileProvider

# Type aliases for placeholder types
KeyboardProfile = Any
BehaviorManagementService = Any
ZmkFileContentGenerator = Any

logger = logging.getLogger(__name__)


# Stub function until analysis module is implemented
def get_required_includes_for_layout(profile: "KeyboardProfile", keymap_data: LayoutData) -> list[str]:
    """Get required includes for layout - stub implementation."""
    return []


def generate_config_file(
    file_adapter: FileProvider,
    profile: "KeyboardProfile",
    keymap_data: LayoutData,
    output_path: Path,
) -> dict[str, str | int]:
    """Generate configuration file and return settings.

    Args:
        file_adapter: File adapter for writing files
        profile: Keyboard profile with configuration
        keymap_data: Layout data for configuration generation
        output_path: Path to write the configuration file

    Returns:
        Dictionary of kconfig settings
    """
    # Generate the config using the function
    conf_content, kconfig_settings = generate_kconfig_conf(keymap_data, profile)

    # Write the config file
    file_adapter.write_text(output_path, conf_content)

    if kconfig_settings:
        options_summary = " | ".join(f"{k}={v}" for k, v in kconfig_settings.items())
        logger.debug(
            "Generated Kconfig with %d options: %s",
            len(kconfig_settings),
            options_summary,
        )

    return kconfig_settings


def build_template_context(
    keymap_data: LayoutData,
    profile: "KeyboardProfile",
    dtsi_generator: "ZmkFileContentGenerator",
    behavior_manager: "BehaviorManagementService | None" = None,
) -> dict[str, Any]:
    """Build template context with generated DTSI content.

    Args:
        keymap_data: Keymap data model
        profile: Keyboard profile with configuration
        dtsi_generator: DTSI generator for creating template content
        behavior_manager: Optional behavior management service (will create one if None)

    Returns:
        Dictionary with template context
    """
    # Extract data for generation with fallback to empty lists
    layer_names = keymap_data.layer_names
    layers_data = keymap_data.layers
    getattr(keymap_data, "input_listeners", [])

    # Get resolved includes from the profile and format them as #include <>
    resolved_includes = []
    if (
        hasattr(profile, "keyboard_config")
        and hasattr(profile.keyboard_config, "keymap")
        and (
            hasattr(profile.keyboard_config.keymap, "header_includes")
            and profile.keyboard_config.keymap.header_includes is not None
        )
    ):
        # Format bare header names as #include <header_name>
        resolved_includes = [f"#include <{include}>" for include in profile.keyboard_config.keymap.header_includes]

    additional_includes = get_required_includes_for_layout(profile, keymap_data)
    resolved_includes.extend([f"#include <{include}>" for include in additional_includes])

    # Prepare behaviors using the management service
    if behavior_manager is None:
        # Stub behavior manager until behavior management is implemented
        class StubBehaviorManager:
            def prepare_behaviors(self, profile: Any, keymap_data: LayoutData) -> None:
                pass

            def get_behavior_registry(self) -> dict[str, Any]:
                return {}

        behavior_manager = StubBehaviorManager()

    behavior_manager.prepare_behaviors(profile, keymap_data)

    # Update the dtsi_generator's behavior registry to use the managed registry
    if hasattr(dtsi_generator, "_behavior_registry"):
        dtsi_generator._behavior_registry = behavior_manager.get_behavior_registry()

    # Generate DTSI components - stub implementations
    layer_defines = ""
    behaviors_dtsi = ""
    combos_dtsi = ""
    macros_dtsi = ""
    input_listeners_dtsi = ""
    keymap_node = ""

    # Get template elements from the keyboard profile - with safe access
    key_position_header = ""
    system_behaviors_dts = ""

    if hasattr(profile, "keyboard_config") and hasattr(profile.keyboard_config, "keymap"):
        if hasattr(profile.keyboard_config.keymap, "key_position_header"):
            key_position_header = profile.keyboard_config.keymap.key_position_header or ""
        if hasattr(profile.keyboard_config.keymap, "system_behaviors_dts"):
            system_behaviors_dts = profile.keyboard_config.keymap.system_behaviors_dts or ""

    # Profile identifiers - with safe access
    profile_name = "unknown"
    firmware_version = "unknown"

    if hasattr(profile, "keyboard_name") and hasattr(profile, "firmware_version"):
        profile_name = f"{profile.keyboard_name}/{profile.firmware_version}"
        firmware_version = profile.firmware_version

    # Build and return the template context with defaults for missing values
    context = {
        "keyboard": keymap_data.keyboard,
        "layer_names": layer_names,
        "layers": layers_data,
        "layer_defines": layer_defines,
        "keymap_node": keymap_node,
        "user_behaviors_dtsi": behaviors_dtsi,
        "combos_dtsi": combos_dtsi,
        "input_listeners_dtsi": input_listeners_dtsi,
        "user_macros_dtsi": macros_dtsi,
        "resolved_includes": "\n".join(resolved_includes),
        "key_position_header": key_position_header,
        "system_behaviors_dts": system_behaviors_dts,
        "custom_defined_behaviors": keymap_data.custom_defined_behaviors or "",
        "custom_devicetree": keymap_data.custom_devicetree or "",
        "profile_name": profile_name,
        "firmware_version": firmware_version,
        "generation_timestamp": datetime.now().isoformat(),
    }

    return context


def generate_kconfig_conf(
    keymap_data: LayoutData,
    profile: "KeyboardProfile",
) -> tuple[str, dict[str, str | int]]:
    """Generate kconfig content and settings from keymap data.

    Args:
        keymap_data: Keymap data with configuration parameters
        profile: Keyboard profile with kconfig options

    Returns:
        Tuple of (kconfig_content, kconfig_settings)
    """
    # Stub implementation - get options from profile if available
    kconfig_options = {}
    if hasattr(profile, "kconfig_options"):
        kconfig_options = profile.kconfig_options

    user_options: dict[str, str | int] = {}

    lines = []
    lines.append("# Generated ZMK configuration")
    lines.append("")

    # Extract user config_parameters (kconfig) options from LayoutData
    for opt in keymap_data.config_parameters:
        line = ""
        comment_prefix = ""

        if opt.param_name in kconfig_options:
            # Supported option - get the real option name
            option_config = kconfig_options[opt.param_name]
            name = option_config.name if hasattr(option_config, "name") else opt.param_name
            default_value = option_config.default if hasattr(option_config, "default") else None

            if opt.value == default_value:
                # User is setting same value as default
                # Comment it out to allow easier firmware switching
                comment_prefix = "# "

            # Track user options (only non-commented ones)
            if not comment_prefix:
                user_options[name] = opt.value

        else:
            # Unsupported option - add warning and comment out
            logger.warning(
                "Unsupported kconfig option '%s' found. This option is not registered "
                "in the keyboard or firmware configuration. Adding as commented line.",
                opt.param_name,
            )

            name = opt.param_name
            # Add kconfig prefix if needed
            kconfig_prefix = "CONFIG_ZMK_"  # Default prefix
            if (
                hasattr(profile, "keyboard_config")
                and hasattr(profile.keyboard_config, "zmk")
                and hasattr(profile.keyboard_config.zmk, "patterns")
            ):
                kconfig_prefix = profile.keyboard_config.zmk.patterns.kconfig_prefix

            if not name.startswith(kconfig_prefix):
                name = kconfig_prefix + name

            # Comment out unsupported options with explanation
            comment_prefix = "# "
            lines.append(f"# Warning: '{opt.param_name}' is not a supported kconfig option")

        line = f"{comment_prefix}{name}={opt.value}"
        lines.append(line)
        lines.append("")  # Add blank line after each option for readability

    # Remove the last blank line if present
    if lines and lines[-1] == "":
        lines.pop()

    kconfig_content = "\n".join(lines)
    return kconfig_content, user_options


def generate_keymap_file(
    file_adapter: FileProvider,
    template_adapter: Any,
    dtsi_generator: "ZmkFileContentGenerator",
    keymap_data: LayoutData,
    profile: "KeyboardProfile",
    output_path: Path,
    behavior_manager: "BehaviorManagementService | None" = None,
) -> None:
    """Generate keymap file.

    Args:
        file_adapter: File adapter for writing files
        template_adapter: Template adapter for rendering
        dtsi_generator: DTSI generator for creating template content
        keymap_data: Layout data for keymap generation
        profile: Keyboard profile with configuration
        output_path: Path to write the keymap file
        behavior_manager: Optional behavior management service

    Raises:
        LayoutError: If keymap generation fails
    """
    logger.info(
        "Building .keymap file for profile",
    )

    # Build template context using the function
    context = build_template_context(keymap_data, profile, dtsi_generator, behavior_manager)

    # Get template content from keymap configuration - support both inline and file templates
    keymap_content = "/* Generated ZMK keymap */\n" + str(context)  # Placeholder content

    if hasattr(profile, "keyboard_config") and hasattr(profile.keyboard_config, "keymap"):
        keymap_section = profile.keyboard_config.keymap
        inline_template = getattr(keymap_section, "keymap_dtsi", None)
        template_file = getattr(keymap_section, "keymap_dtsi_file", None)

        # Render template based on source type
        if inline_template:
            logger.debug("Using inline keymap template")
            keymap_content = template_adapter.render_string(inline_template, context)
        elif template_file:
            # Resolve template file path
            from zmk_layout.utils import resolve_template_file_path

            template_path = resolve_template_file_path(profile.keyboard_name, template_file)
            keymap_content = template_adapter.render_template(template_path, context)

    file_adapter.write_text(output_path, keymap_content)


def convert_keymap_section_from_dict(keymap_dict: dict[str, Any]) -> dict[str, Any]:
    """Convert keymap section dictionary - simplified stub implementation.

    Args:
        keymap_dict: Dictionary containing keymap section data

    Returns:
        Simplified keymap section dictionary
    """
    # Simplified stub implementation until proper models are available
    return {
        "header_includes": keymap_dict.get("header_includes", keymap_dict.get("includes", [])),
        "system_behaviors": keymap_dict.get("system_behaviors", []),
        "kconfig_options": keymap_dict.get("kconfig_options", {}),
        "keymap_dtsi": keymap_dict.get("keymap_dtsi"),
        "keymap_dtsi_file": keymap_dict.get("keymap_dtsi_file"),
        "system_behaviors_dts": keymap_dict.get("system_behaviors_dts"),
        "key_position_header": keymap_dict.get("key_position_header"),
    }


def generate_keymap_file_with_result(
    profile: "KeyboardProfile",
    keymap_data: LayoutData,
    components: dict[str, Any],
    output_path: Path,
    behavior_formatter: Any,
    template_adapter: Any,
    file_adapter: FileProvider,
    force: bool = False,
) -> "LayoutResult":
    """Generate keymap file and return result object for LayoutService.

    This is a wrapper function that matches the signature expected by LayoutService
    and returns a LayoutResult object instead of void.

    Args:
        profile: Keyboard profile configuration
        keymap_data: Layout data for keymap generation
        components: Processed component data (unused but kept for compatibility)
        output_path: Path to write the keymap file
        behavior_formatter: Behavior formatter (unused but kept for compatibility)
        template_adapter: Template adapter for rendering
        file_adapter: File adapter for writing files
        force: Whether to overwrite existing files

    Returns:
        LayoutResult with generation status

    Raises:
        LayoutError: If keymap generation fails
    """
    result = LayoutResult(success=False)

    try:
        # Check if file exists and force flag
        if file_adapter.exists(output_path) and not force:
            error_msg = f"Keymap file already exists: {output_path}"
            result.add_error(error_msg)
            return result

        # Create stub dtsi_generator and behavior components
        class StubDtsiGenerator:
            def __init__(self) -> None:
                self._behavior_registry: dict[str, Any] = {}

        dtsi_generator = StubDtsiGenerator()

        # Use the existing generate_keymap_file function
        generate_keymap_file(
            file_adapter=file_adapter,
            template_adapter=template_adapter,
            dtsi_generator=dtsi_generator,
            keymap_data=keymap_data,
            profile=profile,
            output_path=output_path,
            behavior_manager=None,  # Let it create its own
        )

        result.success = True
        result.keymap_path = str(output_path)
        result.add_message(f"Generated keymap file: {output_path}")

        return result

    except Exception as e:
        exc_info = logger.isEnabledFor(logging.DEBUG)
        logger.error("Keymap generation failed: %s", e, exc_info=exc_info)
        result.add_error(f"Keymap generation failed: {e}")
        return result


def generate_config_file_with_result(
    profile: "KeyboardProfile",
    keymap_data: LayoutData,
    components: dict[str, Any],
    output_path: Path,
    dtsi_generator: Any,
    file_adapter: FileProvider,
    force: bool = False,
) -> "LayoutResult":
    """Generate config file and return result object for LayoutService.

    This is a wrapper function that matches the signature expected by LayoutService
    and returns a LayoutResult object instead of a simple dictionary.

    Args:
        profile: Keyboard profile configuration
        keymap_data: Layout data for configuration generation
        components: Processed component data (unused but kept for compatibility)
        output_path: Path to write the configuration file
        dtsi_generator: DTSI generator (unused but kept for compatibility)
        file_adapter: File adapter for writing files
        force: Whether to overwrite existing files

    Returns:
        LayoutResult with generation status

    Raises:
        LayoutError: If config generation fails
    """
    result = LayoutResult(success=False)

    try:
        # Check if file exists and force flag
        if file_adapter.exists(output_path) and not force:
            error_msg = f"Config file already exists: {output_path}"
            result.add_error(error_msg)
            return result

        # Use the existing generate_config_file function
        kconfig_settings = generate_config_file(
            file_adapter=file_adapter,
            profile=profile,
            keymap_data=keymap_data,
            output_path=output_path,
        )

        result.success = True
        result.conf_path = str(output_path)
        result.add_message(f"Generated config file: {output_path}")
        if kconfig_settings:
            result.add_message(f"Applied {len(kconfig_settings)} configuration options")

        return result

    except Exception as e:
        exc_info = logger.isEnabledFor(logging.DEBUG)
        logger.error("Config generation failed: %s", e, exc_info=exc_info)
        result.add_error(f"Config generation failed: {e}")
        return result
