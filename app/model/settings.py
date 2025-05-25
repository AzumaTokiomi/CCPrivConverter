""" settings.py
    機能：設定項目のオブジェクト群
"""
from dataclasses import dataclass
from enum import Enum
from typing import Literal


class ConfigKey:
    """ ConfigKey
        機能：設定キー
    """
    #ResourcesConfig
    MAX_LOG_CHARCTER_LENGTH     = "max_log_character_length"
    CHARACTER_DEFAULT_NAME      = "character_default_name"
    WEB_STYLE_BASE              = "web_style_base"
    IFRAME_MAX_CHARCTER         = "iframe_max_character"
    MAX_LOG_BYTE_SIZE           = "max_log_byte_size"
    DEBUG_MODE                  = "debug_mode"
    DEBUG_MAX_TRACE_LINES       = "debug_max_trace_lines"

    # ConverterConfig
    USE_DEFAULT_SETTING         = "use_default_setting"
    REPORT_UNKNOWN_CHARACTER    = "report_unknown_character"
    REPORT_OVER_CHARACTER       = "report_over_character"
    INFO_OPEN_OUTPUT_FILE       = "info_open_output_file"
    IGNORE_TABS                 = "ignore_tabs"
    IGNORE_EMPTY_MESSAGE        = "ignore_empty_message"
    CONVERT_QUOTATION           = "convert_quotation"
    COMPACT_MODE                = "compact_mode"

    CONVERT_ASTERISK            = "convert_asterisk"
    CONVERT_WAVE                = "convert_wave"

    CONVERT_WEB_LOG             = "convert_web_log"

    PREVIEW_BG_COLOR            = "preview_bg_color"

    # CharacterConfig
    ENABLE_PAINT    = "enable_paint"
    CHARACTER       = "character"
    CLASS_NAME      = "class_name"
    COLOR_CODE      = "color_code"
    GROUP           = "group"
    DELETE_NAME     = "delete_name"



@dataclass
class ConvertConfig:
    """ ConvertConfig
        機能：変換設定
    """
    key:            str                     # キー
    label:          str                     # ラベルのキー
    config_type:    Literal["bool", "str"]  # 設定タイプ：チェックか入力か
    default:        object                  # デフォルト値：汎用のためobject型
    group:          str = "general"         # 設定項目のグループ指定：なしの場合general

# 通常設定
GENERAL_CONFIG = [
    ConvertConfig(ConfigKey.USE_DEFAULT_SETTING,      "use_default_setting_label", "bool", True),
    ConvertConfig(ConfigKey.REPORT_UNKNOWN_CHARACTER, "report_unknown_character_label", "bool", True),
    ConvertConfig(ConfigKey.REPORT_OVER_CHARACTER,    "report_over_character_label", "bool", True),
    ConvertConfig(ConfigKey.INFO_OPEN_OUTPUT_FILE,    "info_open_output_file_label", "bool", True),
    ConvertConfig(ConfigKey.IGNORE_TABS,              "ignore_tabs_label", "str", "雑談,other,"),
    ConvertConfig(ConfigKey.IGNORE_EMPTY_MESSAGE,     "ignore_empty_message_label", "bool", True),
    ConvertConfig(ConfigKey.CONVERT_QUOTATION,        "convert_quotation_label", "bool", True),
    ConvertConfig(ConfigKey.COMPACT_MODE,             "compact_mode_label", "bool", False),
]

# Privatter+向け設定
PRIVATTERPLUS_CONFIG = [
    ConvertConfig(ConfigKey.CONVERT_ASTERISK, "convert_asterisk_label", "bool", False, "privatter"),
    ConvertConfig(ConfigKey.CONVERT_WAVE,     "convert_wave_label", "bool", False, "privatter"),
]

# 開発者向け設定
DEVELOPER_CONFIG = [
    ConvertConfig(ConfigKey.CONVERT_WEB_LOG,  "convert_web_log_label", "bool", False, "developer"),
]

# プレビュー設定
PREVIEW_CONFIG = [
    ConvertConfig(ConfigKey.PREVIEW_BG_COLOR, "preview_bg_color_label", "str", "ffffff", "hidden"),
]

CONVERT_CONFIG = GENERAL_CONFIG + PRIVATTERPLUS_CONFIG + DEVELOPER_CONFIG + PREVIEW_CONFIG


@dataclass
class CharacterConfig:
    """ CharacterConfig
        機能：キャラ設定
    """
    key:            str                     # キー
    label:          str                     # ラベル
    config_type:    Literal["bool", "str"]  # 設定タイプ：チェックか入力か
    default:        object                  # デフォルト値：汎用のためobject型

CHARACTER_CONFIG = [
    CharacterConfig(ConfigKey.ENABLE_PAINT,  "valid_setting_label", "bool", True),
    CharacterConfig(ConfigKey.CHARACTER,     "character_label", "str", ""),
    CharacterConfig(ConfigKey.CLASS_NAME,    "class_name_label", "str", "unset"),
    CharacterConfig(ConfigKey.COLOR_CODE,    "color_code_label", "str", "000000"),
    CharacterConfig(ConfigKey.GROUP,         "group_label", "str", "None"),
    CharacterConfig(ConfigKey.DELETE_NAME,   "delete_name_label", "bool", False),
]



class ConvertLogType(Enum):
    """ ConvertLogType
        機能：ログの種別の定数設定
    """
    PRIVATTER  = "convert_log_type_privatter"
    WEB        = "convert_log_type_web"
    IFRAME     = "convert_log_type_iframe"
