""" resource.py
    機能：リソース設定
"""

"""
定数定義
"""
# APPアイコンのパス
from dataclasses import dataclass
from typing import Literal

APP_ICON_PATH = "assets/icon.ico"
# 変換後ログを格納するディレクトリ
OUTPUT_DIR_NAME = "output"
# 変換後ログの出力ファイル名
OUTPUT_FILE_NAME = "output.txt"
# ユーザーが設定可能な設定ディレクトリ
SETTINGS_DIR_NAME = "settings"
# リソース設定ファイル名
RESOURCES_FILE_NAME = "resources.json"
# 変換設定ファイル名
CONFIG_FILE_NAME = "config.json"
# キャラ設定ファイル名
CHARACTER_FILE_NAME = "character.json"
# エラーログのファイル名
ERROR_LOG_NAME = "error.log"


class ResourcesKey:
    """ ResourcesKey
        機能：リソース設定キー
    """
    MAX_LOG_CHARCTER_LENGTH     = "max_log_character_length"
    CHARACTER_DEFAULT_NAME      = "character_default_name"
    WEB_STYLE_BASE              = "web_style_base"
    IFRAME_MAX_CHARCTER         = "iframe_max_character"
    MAX_LOG_BYTE_SIZE           = "max_log_byte_size"
    DEBUG_MODE                  = "debug_mode"
    DEBUG_MAX_TRACE_LINES       = "debug_max_trace_lines"



@dataclass
class ResourcesConfig:
    """ ResourcesConfig
        機能：リソース設定
    """
    key:            str                             # キー
    config_type:    Literal["bool", "str", "int"]   # 設定タイプ：チェックか入力か
    default:        object                          # デフォルト値：汎用のためobject型

RESOURCES_CONFIG = [
    ResourcesConfig(ResourcesKey.MAX_LOG_CHARCTER_LENGTH,    "int", 250000),
    ResourcesConfig(ResourcesKey.CHARACTER_DEFAULT_NAME,     "str", "Default"),
    ResourcesConfig(ResourcesKey.WEB_STYLE_BASE,             "str", '*{padding:0;margin:0;margin-bottom:1px;font-size:16px;line-height:25px;} body{font-family: "游明朝", serif;}'),
    ResourcesConfig(ResourcesKey.IFRAME_MAX_CHARCTER,        "int", 29000),
    ResourcesConfig(ResourcesKey.MAX_LOG_BYTE_SIZE,          "int", 1024*20),
    ResourcesConfig(ResourcesKey.DEBUG_MODE,                 "bool", False),
    ResourcesConfig(ResourcesKey.DEBUG_MAX_TRACE_LINES,      "int", 10),
]
