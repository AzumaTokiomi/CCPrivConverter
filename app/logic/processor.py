""" processor.py
    機能：入出力・連携
"""
import os
import re

from app.logic import globals
from app.logic.fileio import get_root_relative_path, load_json, save_json
from app.logic.formatter import (CharacterList, ConvertedLog,
                                 convert_chats_to_text,
                                 convert_log_to_chat_list,
                                 create_style_tag_text)
from app.logic.logging import logging_error
from app.model.settings import *
from app.model.settings import CHARACTER_CONFIG, CONVERT_CONFIG
from app.model.uitexts import TextKey
from system.ja import TEXTS
from system.resources import (CHARACTER_FILE_NAME, CONFIG_FILE_NAME,
                              RESOURCES_CONFIG, RESOURCES_FILE_NAME,
                              SETTINGS_DIR_NAME, ResourcesKey)


def convert_log(input_path: str, output_path: str, convert_config: dict, character_config: list) -> tuple[bool, tuple[ConvertedLog, int], list[str]] | tuple[bool, Exception, CharacterList]:

    """ convert_log
    機能：ログ変換処理

    Args:
        input_path (str): ココフォリアのログのパス
        output_path (str): 変換後のログを出力するパス
        convert_config (dict): 変換設定の設定値
        character_config (list): キャラ設定の設定値

    Returns:
        tuple[bool, tuple[str, int] | tuple[str, Exception], list[str]]:
            変換の成功or失敗 / [変換後テキスト / 文字数] または [ダイアログメッセージ / Exception] / 未設定または着色無効のキャラクターリスト
    """
    characters = []
    try:
        # 指定されたココフォリアのログを読み込む
        with open(input_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        logging_error("ココフォリアログの読み込み失敗", get_root_relative_path(), e)
        return False, (TEXTS[TextKey.FAILED_READ_LOG_MESSAGE], e), characters

    try:
        # 読み込んだココフォリアのログを変換する
        chats, characters = convert_log_to_chat_list(html_content, convert_config, character_config)    # Chatリストへの変換
        logs = convert_chats_to_text(chats, convert_config)
        privatter_log, web_log, iframe_logs = logs
        total_len = len(privatter_log)

        # web用ログ変換が有効な場合
        if convert_config.get(ConfigKey.CONVERT_WEB_LOG):
            #styleタグのテキストを作る
            style_tag_text = create_style_tag_text(character_config, characters.use_classes)
            for i in range(len(iframe_logs)):
                iframe_logs[i] += style_tag_text
        converted_text = privatter_log, web_log, iframe_logs

    except Exception as e:
        logging_error("ログ変換失敗", get_root_relative_path(), e)
        return False, (TEXTS[TextKey.FAILED_CONVERT_LOG_MESSAGE], e), characters

    try:
        # 変換したテキストを出力する
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(privatter_log)
    except Exception as e:
        logging_error("変換後ファイル保存失敗", get_root_relative_path(), e)
        return False, (TEXTS[TextKey.FAILED_WRITE_LOG_MESSGE], e), characters

    return True, (converted_text, total_len), characters


def load_resources() -> dict:
    """ load_resources
        機能：リソースファイルから設定値読み込み。設定がなければ初期値を設定する

    Returns:
        dict: 設定値
    """
    # 設定ファイルを読み込む
    resources_data: dict = load_json(os.path.join(SETTINGS_DIR_NAME, RESOURCES_FILE_NAME))

    # 変換設定
    for resource_cfg in RESOURCES_CONFIG:
        key = resource_cfg.key
        # 読み込んだ設定ファイルに設定値があるか探す
        if key not in resources_data:
            # 設定値がない場合、初期値を設定
            resources_data[key] = resource_cfg.default
        else:
            value = resources_data[key]
            # 設定値がある場合のbool型の設定値チェック
            if resource_cfg.config_type == "bool":
                resources_data[key] = globals.get_bool(value, resource_cfg.default)
            # int型の設定値チェック
            elif resource_cfg.config_type == "int":
                resources_data[key] = globals.get_int(value, resource_cfg.default)

    return resources_data


def save_resources(resources: dict, *args):
    """ save_resources
        機能：リソース設定を上書きする
            ※初期値設定したものがあるかもしれないので、念のため

    Args:
        resources (dict): リソース設定の設定値
    """
    save_json(resources, os.path.join(SETTINGS_DIR_NAME, RESOURCES_FILE_NAME))


def load_convert_config() -> dict:
    """ load_convert_config
        機能：設定ファイルから設定値読み込み。設定がなければ初期値を設定する

    Returns:
        dict: 設定値
    """
    # 設定ファイルを読み込む
    config_data: dict = load_json(os.path.join(SETTINGS_DIR_NAME, CONFIG_FILE_NAME))

    # 変換設定
    for convert_cfg in CONVERT_CONFIG:
        key = convert_cfg.key
        # 読み込んだ設定ファイルに設定値があるか探す
        if key not in config_data:
            # 設定値がない場合、初期値を設定
            config_data[key] = convert_cfg.default
        else:
            value = config_data[key]
            # 設定値がある場合のbool型の設定値チェック
            if convert_cfg.config_type == "bool":
                config_data[key] = globals.get_bool(value, convert_cfg.default)

    return config_data


def save_convert_config(convert_config: dict, *args):
    """ save_convert_config
        機能：ログ変換画面で設定された設定値を保存する
    """
    current_config = load_convert_config()
    current_config.update(convert_config)
    save_json(current_config, os.path.join(SETTINGS_DIR_NAME, CONFIG_FILE_NAME))


def load_character_config() -> tuple[dict, list[dict]]:
    """ load_character_config
        機能：設定ファイルから設定値読み込み

    Returns:
        tuple[dict, list[dict]: 初期値の設定値 / 設定値
    """
    # 設定ファイルを読み込む
    config_data: list = load_json(os.path.join(SETTINGS_DIR_NAME, CHARACTER_FILE_NAME))

    default_cfg = None
    character_cfg = []

    # デフォルト設定とその他設定の区別
    for cfg in config_data:
        if cfg.get(ConfigKey.CHARACTER) == globals.RESOURCES[ResourcesKey.CHARACTER_DEFAULT_NAME]:
            default_cfg = cfg
        else:
            character_cfg.append(cfg)

    # 初期設定がなかった場合
    if default_cfg is None:
        default_cfg = {}
        for character_config in CHARACTER_CONFIG:
            default_cfg[character_config.key] = character_config.default
        default_cfg[ConfigKey.CHARACTER] = globals.RESOURCES[ResourcesKey.CHARACTER_DEFAULT_NAME]

    return default_cfg, character_cfg


def save_character_config(character_config: list, *args):
    """ save_character_config
        機能：キャラ設定画面で設定された設定値を保存する
    """
    save_json(character_config, os.path.join(SETTINGS_DIR_NAME, CHARACTER_FILE_NAME))


def check_valid_color_code(color_code: str) -> bool:
    """ check_valid_color_code
        機能：有効なカラーコードが設定されているか確認する

    Args:
        color_code (str): カラーコード設定値

    Returns:
        bool: Trueで有効
    """
    return bool(re.fullmatch(r"[0-9a-fA-F]{6}", color_code))
