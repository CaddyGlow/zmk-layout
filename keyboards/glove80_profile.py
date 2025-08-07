"""
Complete Glove80 Keyboard Profile

This module provides the comprehensive Glove80 keyboard profile with all hardware
specifications, behaviors, and configuration data extracted from the zmk-glovebox
repository.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Glove80HardwareConfig:
    """Complete Glove80 hardware configuration."""

    keyboard: str = "glove80"
    description: str = "MoErgo Glove80 split ergonomic keyboard"
    vendor: str = "MoErgo"
    key_count: int = 80
    is_split: bool = True

    # Physical layout (6 rows, split ergonomic)
    physical_layout: list[list[int]] = field(
        default_factory=lambda: [
            [0, 1, 2, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, 5, 6, 7, 8, 9],
            [10, 11, 12, 13, 14, 15, -1, -1, -1, -1, -1, -1, 16, 17, 18, 19, 20, 21],
            [22, 23, 24, 25, 26, 27, -1, -1, -1, -1, -1, -1, 28, 29, 30, 31, 32, 33],
            [34, 35, 36, 37, 38, 39, -1, -1, -1, -1, -1, -1, 40, 41, 42, 43, 44, 45],
            [46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63],
            [64, 65, 66, 67, 68, -1, 69, 70, 71, 72, 73, 74, -1, 75, 76, 77, 78, 79],
        ]
    )

    # Build configuration
    boards: list[str] = field(default_factory=lambda: ["glove80_lh", "glove80_rh"])
    shields: list[str] = field(default_factory=list)

    # Flash configuration
    flash_method: dict[str, Any] = field(
        default_factory=lambda: {
            "method_type": "usb",
            "device_query": "serial~=GLV80-.* and removable=true",
            "mount_timeout": 120,
            "copy_timeout": 60,
            "sync_after_copy": True,
        }
    )


@dataclass
class Glove80BehaviorDefinitions:
    """Complete Glove80 behavior definitions including ZMK and Glove80-specific behaviors."""

    # ZMK Standard Behaviors
    zmk_behaviors: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {
                "code": "&kp",
                "name": "Key Press",
                "description": "Send standard keycodes on press/release",
                "url": "https://zmk.dev/docs/behaviors/key-press",
                "expected_params": 1,
                "params": ["code"],
                "includes": ["dt-bindings/zmk/keys.h"],
                "origin": "zmk",
            },
            {
                "code": "&trans",
                "name": "Transparent",
                "description": "Pass key through to next layer",
                "url": "https://zmk.dev/docs/behaviors/misc",
                "expected_params": 0,
                "params": [],
                "origin": "zmk",
            },
            {
                "code": "&none",
                "name": "None",
                "description": "Swallow and stop key presses",
                "url": "https://zmk.dev/docs/behaviors/misc",
                "expected_params": 0,
                "params": [],
                "origin": "zmk",
            },
            {
                "code": "&mt",
                "name": "Mod Tap",
                "description": "Modifier on hold, key on tap",
                "url": "https://zmk.dev/docs/behaviors/mod-tap",
                "expected_params": 2,
                "params": ["modifier", "code"],
                "origin": "zmk",
            },
            {
                "code": "&lt",
                "name": "Layer Tap",
                "description": "Layer on hold, key on tap",
                "url": "https://zmk.dev/docs/behaviors/layers",
                "expected_params": 2,
                "params": ["layer", "code"],
                "origin": "zmk",
            },
            {
                "code": "&mo",
                "name": "Momentary Layer",
                "description": "Enable layer while held",
                "url": "https://zmk.dev/docs/behaviors/layers",
                "expected_params": 1,
                "params": ["layer"],
                "origin": "zmk",
            },
            {
                "code": "&to",
                "name": "To Layer",
                "description": "Switch to layer",
                "url": "https://zmk.dev/docs/behaviors/layers",
                "expected_params": 1,
                "params": ["layer"],
                "origin": "zmk",
            },
            {
                "code": "&tog",
                "name": "Toggle Layer",
                "description": "Toggle layer on/off",
                "url": "https://zmk.dev/docs/behaviors/layers",
                "expected_params": 1,
                "params": ["layer"],
                "origin": "zmk",
            },
            {
                "code": "&bt",
                "name": "Bluetooth",
                "description": "Bluetooth management commands",
                "url": "https://zmk.dev/docs/behaviors/bluetooth",
                "expected_params": 1,
                "params": ["command"],
                "includes": ["dt-bindings/zmk/bt.h"],
                "origin": "zmk",
                "commands": [
                    {"code": "BT_CLR", "description": "Clear bond information"},
                    {"code": "BT_CLR_ALL", "description": "Clear all profiles"},
                    {"code": "BT_NXT", "description": "Next profile"},
                    {"code": "BT_PRV", "description": "Previous profile"},
                    {
                        "code": "BT_SEL",
                        "description": "Select profile",
                        "additional_params": ["profile_number"],
                    },
                    {
                        "code": "BT_DISC",
                        "description": "Disconnect profile",
                        "additional_params": ["profile_number"],
                    },
                ],
            },
            {
                "code": "&out",
                "name": "Output Selection",
                "description": "Select USB or Bluetooth output",
                "url": "https://zmk.dev/docs/behaviors/outputs",
                "expected_params": 1,
                "params": ["command"],
                "includes": ["dt-bindings/zmk/outputs.h"],
                "origin": "zmk",
                "commands": [
                    {"code": "OUT_BLE", "description": "Prefer bluetooth"},
                    {"code": "OUT_USB", "description": "Prefer USB"},
                    {"code": "OUT_TOG", "description": "Toggle USB/BLE"},
                ],
            },
            {
                "code": "&rgb_ug",
                "name": "RGB Underglow",
                "description": "RGB underglow control",
                "url": "https://zmk.dev/docs/behaviors/underglow",
                "expected_params": 1,
                "params": ["command"],
                "includes": ["dt-bindings/zmk/rgb.h"],
                "origin": "zmk",
                "commands": [
                    {"code": "RGB_TOG", "description": "Toggle RGB"},
                    {"code": "RGB_HUI", "description": "Increase hue"},
                    {"code": "RGB_HUD", "description": "Decrease hue"},
                    {"code": "RGB_SAI", "description": "Increase saturation"},
                    {"code": "RGB_SAD", "description": "Decrease saturation"},
                    {"code": "RGB_BRI", "description": "Increase brightness"},
                    {"code": "RGB_BRD", "description": "Decrease brightness"},
                    {"code": "RGB_EFF", "description": "Next effect"},
                    {"code": "RGB_EFR", "description": "Previous effect"},
                    {"code": "RGB_SPI", "description": "Increase speed"},
                    {"code": "RGB_SPD", "description": "Decrease speed"},
                ],
            },
            {
                "code": "&reset",
                "name": "Reset Half",
                "description": "Reset keyboard half",
                "url": "https://zmk.dev/docs/behaviors/reset",
                "expected_params": 0,
                "params": [],
                "origin": "zmk",
            },
            {
                "code": "&bootloader",
                "name": "Half Bootloader",
                "description": "Enter bootloader mode",
                "url": "https://zmk.dev/docs/behaviors/reset",
                "expected_params": 0,
                "params": [],
                "origin": "zmk",
            },
            {
                "code": "&sk",
                "name": "Sticky Key",
                "description": "Sticky modifier key",
                "url": "https://zmk.dev/docs/behaviors/sticky-key",
                "expected_params": 1,
                "params": ["code"],
                "origin": "zmk",
            },
            {
                "code": "&sl",
                "name": "Sticky Layer",
                "description": "Sticky layer activation",
                "url": "https://zmk.dev/docs/behaviors/sticky-layer",
                "expected_params": 1,
                "params": ["layer"],
                "origin": "zmk",
            },
            {
                "code": "&caps_word",
                "name": "Caps Word",
                "description": "Smart caps lock",
                "url": "https://zmk.dev/docs/behaviors/caps-word",
                "expected_params": 0,
                "params": [],
                "origin": "zmk",
            },
            {
                "code": "&key_repeat",
                "name": "Key Repeat",
                "description": "Repeat last keypress",
                "url": "https://zmk.dev/docs/behaviors/key-repeat",
                "expected_params": 0,
                "params": [],
                "origin": "zmk",
            },
        ]
    )

    # Glove80-specific behaviors
    glove80_behaviors: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {
                "code": "&magic",
                "name": "Magic Key",
                "description": "Tap to show indicators, hold for Magic layer",
                "url": "https://www.moergo.com/files/layout-editor-user-guide.pdf",
                "expected_params": 0,
                "params": [],
                "origin": "moergo",
            },
            {
                "code": "&lower",
                "name": "Lower Layer Key",
                "description": "Hold for Lower layer, double-tap to lock",
                "url": "https://www.moergo.com/files/layout-editor-user-guide.pdf",
                "expected_params": 0,
                "params": [],
                "origin": "moergo",
            },
            {
                "code": "&bt_0",
                "name": "Bluetooth Profile 0",
                "description": "Select BT profile 0, double-tap to disconnect",
                "url": "https://www.moergo.com/files/layout-editor-user-guide.pdf",
                "expected_params": 0,
                "params": [],
                "origin": "moergo",
            },
            {
                "code": "&bt_1",
                "name": "Bluetooth Profile 1",
                "description": "Select BT profile 1, double-tap to disconnect",
                "url": "https://www.moergo.com/files/layout-editor-user-guide.pdf",
                "expected_params": 0,
                "params": [],
                "origin": "moergo",
            },
            {
                "code": "&bt_2",
                "name": "Bluetooth Profile 2",
                "description": "Select BT profile 2, double-tap to disconnect",
                "url": "https://www.moergo.com/files/layout-editor-user-guide.pdf",
                "expected_params": 0,
                "params": [],
                "origin": "moergo",
            },
            {
                "code": "&bt_3",
                "name": "Bluetooth Profile 3",
                "description": "Select BT profile 3, double-tap to disconnect",
                "url": "https://www.moergo.com/files/layout-editor-user-guide.pdf",
                "expected_params": 0,
                "params": [],
                "origin": "moergo",
            },
            {
                "code": "Custom",
                "name": "Custom Behavior",
                "description": "Custom behavior via text input",
                "url": "https://www.moergo.com/files/layout-editor-user-guide.pdf",
                "expected_params": 1,
                "params": ["text_command"],
                "origin": "moergo",
            },
        ]
    )


@dataclass
class Glove80FirmwareConfig:
    """Glove80 firmware configurations."""

    available_firmwares: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "v25.05": {
                "version": "v25.05",
                "description": "Stable MoErgo firmware v25.05",
                "repository": "moergo-sc/zmk",
                "branch": "v25.05",
                "is_stable": True,
            },
            "v25.08-beta.1": {
                "version": "v25.08-beta.1",
                "description": "Beta MoErgo firmware v25.08-beta.1",
                "repository": "moergo-sc/zmk",
                "branch": "v25.08-beta.1",
                "is_stable": False,
            },
            "pr36": {
                "version": "pr36.per-key-rgb",
                "description": "PR36 with per-key RGB support",
                "repository": "moergo-sc/zmk",
                "branch": "pull/36/head",
                "is_stable": False,
                "kconfig": {
                    "CONFIG_EXPERIMENTAL_RGB_LAYER": {
                        "type": "bool",
                        "default": False,
                        "description": "Enables per-layer RGB settings",
                    }
                },
            },
        }
    )

    default_firmware: str = "v25.05"

    compile_methods: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {
                "method_type": "moergo",
                "image": "glove80-zmk-config-docker",
                "repository": "moergo-sc/zmk",
                "branch": "v25.05",
            },
            {
                "method_type": "zmk_config",
                "image": "zmkfirmware/zmk-build-arm:stable",
                "repository": "moergo-sc/zmk",
                "branch": "v25.05",
                "build_config": {"board": ["glove80_lh", "glove80_rh"], "shield": []},
            },
        ]
    )


@dataclass
class Glove80KeymapConfig:
    """Glove80 keymap configuration and templates."""

    # Default includes
    header_includes: list[str] = field(
        default_factory=lambda: [
            "behaviors.dtsi",
            "dt-bindings/zmk/keys.h",
            "dt-bindings/zmk/bt.h",
            "dt-bindings/zmk/outputs.h",
            "dt-bindings/zmk/rgb.h",
        ]
    )

    # Layer name mappings
    layer_names: dict[str, int] = field(
        default_factory=lambda: {"Base": 0, "Lower": 1, "Magic": 2}
    )

    # Key position definitions (Glove80 specific)
    key_position_defines: str = """
#define POS_LH_T1 52
#define POS_LH_T2 53
#define POS_LH_T3 54
#define POS_LH_T4 69
#define POS_LH_T5 70
#define POS_LH_T6 71
#define POS_LH_C1R2 15
#define POS_LH_C1R3 27
#define POS_LH_C1R4 39
#define POS_LH_C1R5 51
#define POS_LH_C2R1 4
#define POS_LH_C2R2 14
#define POS_LH_C2R3 26
#define POS_LH_C2R4 38
#define POS_LH_C2R5 50
#define POS_LH_C2R6 68
#define POS_LH_C3R1 3
#define POS_LH_C3R2 13
#define POS_LH_C3R3 25
#define POS_LH_C3R4 37
#define POS_LH_C3R5 49
#define POS_LH_C3R6 67
#define POS_LH_C4R1 2
#define POS_LH_C4R2 12
#define POS_LH_C4R3 24
#define POS_LH_C4R4 36
#define POS_LH_C4R5 48
#define POS_LH_C4R6 66
#define POS_LH_C5R1 1
#define POS_LH_C5R2 11
#define POS_LH_C5R3 23
#define POS_LH_C5R4 35
#define POS_LH_C5R5 47
#define POS_LH_C5R6 65
#define POS_LH_C6R1 0
#define POS_LH_C6R2 10
#define POS_LH_C6R3 22
#define POS_LH_C6R4 34
#define POS_LH_C6R5 46
#define POS_LH_C6R6 64
#define POS_RH_T1 57
#define POS_RH_T2 56
#define POS_RH_T3 55
#define POS_RH_T4 74
#define POS_RH_T5 73
#define POS_RH_T6 72
#define POS_RH_C1R2 16
#define POS_RH_C1R3 28
#define POS_RH_C1R4 40
#define POS_RH_C1R5 58
#define POS_RH_C2R1 5
#define POS_RH_C2R2 17
#define POS_RH_C2R3 29
#define POS_RH_C2R4 41
#define POS_RH_C2R5 59
#define POS_RH_C2R6 75
#define POS_RH_C3R1 6
#define POS_RH_C3R2 18
#define POS_RH_C3R3 30
#define POS_RH_C3R4 42
#define POS_RH_C3R5 60
#define POS_RH_C3R6 76
#define POS_RH_C4R1 7
#define POS_RH_C4R2 19
#define POS_RH_C4R3 31
#define POS_RH_C4R4 43
#define POS_RH_C4R5 61
#define POS_RH_C4R6 77
#define POS_RH_C5R1 8
#define POS_RH_C5R2 20
#define POS_RH_C5R3 32
#define POS_RH_C5R4 44
#define POS_RH_C5R5 62
#define POS_RH_C5R6 78
#define POS_RH_C6R1 9
#define POS_RH_C6R2 21
#define POS_RH_C6R3 33
#define POS_RH_C6R4 45
#define POS_RH_C6R5 63
#define POS_RH_C6R6 79
"""

    # Layer name defines
    layer_defines: str = """
#define LAYER_Base 0
#define LAYER_Lower 1
#define LAYER_Magic 2

#ifndef LAYER_Lower
#define LAYER_Lower 0
#endif
"""

    # System behaviors device tree
    system_behaviors_dts: str = """
/ {
    behaviors {
        lower: lower {
            compatible = "zmk,behavior-tap-dance";
            label = "LAYER_Lower";
            #binding-cells = <0>;
            tapping-term-ms = <200>;
            bindings = <&mo 1>, <&to 1>;
        };
    };
};

/ {
    macros {
        rgb_ug_status_macro: rgb_ug_status_macro {
            label = "RGB_UG_STATUS";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&rgb_ug RGB_STATUS>;
        };
    };
};

/ {
#ifdef BT_DISC_CMD
    behaviors {
        bt_0: bt_0 {
            compatible = "zmk,behavior-tap-dance";
            label = "BT_0";
            #binding-cells = <0>;
            tapping-term-ms = <200>;
            bindings = <&bt_select_0>, <&bt BT_DISC 0>;
        };
        bt_1: bt_1 {
            compatible = "zmk,behavior-tap-dance";
            label = "BT_1";
            #binding-cells = <0>;
            tapping-term-ms = <200>;
            bindings = <&bt_select_1>, <&bt BT_DISC 1>;
        };
        bt_2: bt_2 {
            compatible = "zmk,behavior-tap-dance";
            label = "BT_2";
            #binding-cells = <0>;
            tapping-term-ms = <200>;
            bindings = <&bt_select_2>, <&bt BT_DISC 2>;
        };
        bt_3: bt_3 {
            compatible = "zmk,behavior-tap-dance";
            label = "BT_3";
            #binding-cells = <0>;
            tapping-term-ms = <200>;
            bindings = <&bt_select_3>, <&bt BT_DISC 3>;
        };
    };
    macros {
        bt_select_0: bt_select_0 {
            label = "BT_SELECT_0";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&out OUT_BLE>, <&bt BT_SEL 0>;
        };
        bt_select_1: bt_select_1 {
            label = "BT_SELECT_1";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&out OUT_BLE>, <&bt BT_SEL 1>;
        };
        bt_select_2: bt_select_2 {
            label = "BT_SELECT_2";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&out OUT_BLE>, <&bt BT_SEL 2>;
        };
        bt_select_3: bt_select_3 {
            label = "BT_SELECT_3";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&out OUT_BLE>, <&bt BT_SEL 3>;
        };
    };
#else
    macros {
        bt_0: bt_0 {
            label = "BT_0";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&out OUT_BLE>, <&bt BT_SEL 0>;
        };
        bt_1: bt_1 {
            label = "BT_1";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&out OUT_BLE>, <&bt BT_SEL 1>;
        };
        bt_2: bt_2 {
            label = "BT_2";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&out OUT_BLE>, <&bt BT_SEL 2>;
        };
        bt_3: bt_3 {
            label = "BT_3";
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            bindings = <&out OUT_BLE>, <&bt BT_SEL 3>;
        };
    };
#endif
};

/ {
    behaviors {
        magic: magic {
            compatible = "zmk,behavior-hold-tap";
            label = "MAGIC_HOLD_TAP";
            #binding-cells = <2>;
            flavor = "tap-preferred";
            tapping-term-ms = <200>;
            bindings = <&mo>, <&rgb_ug_status_macro>;
        };
    };
};
"""

    # Formatting configuration - matches Glove80 hardware.yaml exactly
    formatting: dict[str, Any] = field(
        default_factory=lambda: {
            "key_gap": "  ",
            "base_indent": "",
            "rows": [
                [0, 1, 2, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, 5, 6, 7, 8, 9],
                [10, 11, 12, 13, 14, 15, -1, -1, -1, -1, -1, -1, 16, 17, 18, 19, 20, 21],
                [22, 23, 24, 25, 26, 27, -1, -1, -1, -1, -1, -1, 28, 29, 30, 31, 32, 33],
                [34, 35, 36, 37, 38, 39, -1, -1, -1, -1, -1, -1, 40, 41, 42, 43, 44, 45],
                [46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63],
                [64, 65, 66, 67, 68, -1, 69, 70, 71, 72, 73, 74, -1, 75, 76, 77, 78, 79],
            ],
        }
    )


@dataclass
class Glove80KConfigOptions:
    """Glove80 kconfig options and advanced configuration."""

    # Standard ZMK configuration options
    standard_options: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "CONFIG_ZMK_RGB_UNDERGLOW": {
                "type": "bool",
                "default": True,
                "description": "Enable RGB underglow support",
            },
            "CONFIG_ZMK_BLE": {
                "type": "bool",
                "default": True,
                "description": "Enable Bluetooth Low Energy support",
            },
            "CONFIG_ZMK_USB": {
                "type": "bool",
                "default": True,
                "description": "Enable USB connectivity",
            },
            "CONFIG_BT_CTLR_TX_PWR_PLUS_8": {
                "type": "bool",
                "default": True,
                "description": "Increase Bluetooth transmit power",
            },
            "CONFIG_ZMK_SLEEP": {
                "type": "bool",
                "default": True,
                "description": "Enable deep sleep power management",
            },
        }
    )

    # Experimental options
    experimental_options: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "CONFIG_EXPERIMENTAL_RGB_LAYER": {
                "type": "bool",
                "default": False,
                "description": "Enable per-layer RGB settings",
                "firmware_requirements": ["pr36", "pr38", "darknao-v25.04"],
            },
            "CONFIG_ZMK_RGB_LAYER": {
                "type": "bool",
                "default": False,
                "description": "RGB layer indication support",
                "firmware_requirements": ["pr36", "pr38", "darknao-v25.04"],
            },
        }
    )


@dataclass
class Glove80ValidationRules:
    """Validation rules and constraints for Glove80."""

    max_layers: int = 10
    key_positions: list[int] = field(default_factory=lambda: list(range(80)))

    supported_behaviors: list[str] = field(
        default_factory=lambda: [
            # Basic ZMK behaviors
            "kp",
            "trans",
            "none",
            "mt",
            "lt",
            "mo",
            "to",
            "tog",
            "sk",
            "sl",
            "caps_word",
            "key_repeat",
            "bt",
            "out",
            "rgb_ug",
            "reset",
            "bootloader",
            # Glove80-specific behaviors
            "magic",
            "lower",
            "bt_0",
            "bt_1",
            "bt_2",
            "bt_3",
            # Custom behavior
            "Custom",
        ]
    )

    bluetooth_profiles: list[int] = field(default_factory=lambda: [0, 1, 2, 3])

    rgb_commands: list[str] = field(
        default_factory=lambda: [
            "RGB_TOG",
            "RGB_HUI",
            "RGB_HUD",
            "RGB_SAI",
            "RGB_SAD",
            "RGB_BRI",
            "RGB_BRD",
            "RGB_EFF",
            "RGB_EFR",
            "RGB_SPI",
            "RGB_SPD",
        ]
    )

    bt_commands: list[str] = field(
        default_factory=lambda: [
            "BT_CLR",
            "BT_CLR_ALL",
            "BT_NXT",
            "BT_PRV",
            "BT_SEL",
            "BT_DISC",
        ]
    )

    out_commands: list[str] = field(
        default_factory=lambda: ["OUT_BLE", "OUT_USB", "OUT_TOG"]
    )


@dataclass
class CompleteGlove80Profile:
    """Complete Glove80 keyboard profile with all specifications."""

    hardware: Glove80HardwareConfig = field(default_factory=Glove80HardwareConfig)
    behaviors: Glove80BehaviorDefinitions = field(
        default_factory=Glove80BehaviorDefinitions
    )
    firmware: Glove80FirmwareConfig = field(default_factory=Glove80FirmwareConfig)
    keymap: Glove80KeymapConfig = field(default_factory=Glove80KeymapConfig)
    kconfig: Glove80KConfigOptions = field(default_factory=Glove80KConfigOptions)
    validation: Glove80ValidationRules = field(default_factory=Glove80ValidationRules)

    def get_template_paths(self) -> list[Path]:
        """Get template search paths."""
        return [
            Path(__file__).parent / "examples" / "layouts",
            Path.cwd(),
            Path("/home/rick/projects-caddy/zmk-glovebox/keyboards/config/templates"),
        ]

    def get_all_behaviors(self) -> list[dict[str, Any]]:
        """Get combined list of all behaviors."""
        return self.behaviors.zmk_behaviors + self.behaviors.glove80_behaviors

    def get_includes(self) -> list[str]:
        """Get all required include files."""
        includes = set(self.keymap.header_includes)

        # Add includes from behaviors
        for behavior in self.get_all_behaviors():
            if "includes" in behavior:
                includes.update(behavior["includes"])

        return sorted(includes)

    def to_dict(self) -> dict[str, Any]:
        """Convert the complete profile to a dictionary."""
        return {
            "keyboard": self.hardware.keyboard,
            "description": self.hardware.description,
            "vendor": self.hardware.vendor,
            "key_count": self.hardware.key_count,
            "is_split": self.hardware.is_split,
            "physical_layout": self.hardware.physical_layout,
            "behaviors": self.get_all_behaviors(),
            "includes": self.get_includes(),
            "validation_rules": {
                "max_layers": self.validation.max_layers,
                "key_positions": self.validation.key_positions,
                "supported_behaviors": self.validation.supported_behaviors,
                "bluetooth_profiles": self.validation.bluetooth_profiles,
                "rgb_commands": self.validation.rgb_commands,
                "bt_commands": self.validation.bt_commands,
                "out_commands": self.validation.out_commands,
            },
            "keymap_config": {
                "header_includes": self.keymap.header_includes,
                "layer_names": self.keymap.layer_names,
                "key_position_defines": self.keymap.key_position_defines,
                "layer_defines": self.keymap.layer_defines,
                "system_behaviors_dts": self.keymap.system_behaviors_dts,
                "formatting": self.keymap.formatting,
            },
            "firmware_config": {
                "available_firmwares": self.firmware.available_firmwares,
                "default_firmware": self.firmware.default_firmware,
                "compile_methods": self.firmware.compile_methods,
            },
            "hardware_config": {
                "boards": self.hardware.boards,
                "shields": self.hardware.shields,
                "flash_method": self.hardware.flash_method,
            },
            "kconfig_options": {
                "standard": self.kconfig.standard_options,
                "experimental": self.kconfig.experimental_options,
            },
        }


def create_complete_glove80_profile() -> CompleteGlove80Profile:
    """Create a complete Glove80 keyboard profile."""
    return CompleteGlove80Profile()


def get_glove80_profile_dict() -> dict[str, Any]:
    """Get the complete Glove80 profile as a dictionary."""
    profile = create_complete_glove80_profile()
    return profile.to_dict()
