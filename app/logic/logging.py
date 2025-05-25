""" logging.py
    機能：ロギング処理
"""
import os
import traceback
from datetime import datetime

from app.logic import globals
from app.logic.fileio import get_executable_path
from system.resources import ERROR_LOG_NAME, OUTPUT_DIR_NAME, ResourcesKey


def check_log_size():
    """ check_log_size
        機能：ログファイルが上限を超えていたらリセットする
    """
    full_path = get_executable_path(os.path.join(OUTPUT_DIR_NAME, ERROR_LOG_NAME))

    # ログファイルが無ければチェック不要
    if not os.path.exists(full_path):
            return

    max_size = globals.RESOURCES[ResourcesKey.MAX_LOG_BYTE_SIZE]
    # 現在のログを格納
    with open(full_path, "r", encoding="utf-8") as f:
        lines: list = f.readlines()

    while True:
        text = "".join(lines)
        if len(text.encode("utf-8")) <= max_size:
            break
        if lines:
            # 古い行から削除
            lines.pop(0)
        else:
            break

    # ログの書き戻し
    with open(full_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def logging_error(error_title: str, path: str, exc: Exception):
    """ logging_error
        機能：指定された情報をエラーログとして記録

    Args:
        error_title (str): エラー種別（呼び出し元で記述）
        path (str): エラー発生元のファイルパス
        exc (Exception): エラー内容
    """
    full_apth = get_executable_path(os.path.join(OUTPUT_DIR_NAME, ERROR_LOG_NAME))

    # ログの最大サイズチェック
    check_log_size()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = str(exc) or "不明なエラー"

    if globals.RESOURCES[ResourcesKey.DEBUG_MODE] == True:
        traceback_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
        shortened_traceback = "".join(traceback_lines[:globals.RESOURCES[ResourcesKey.DEBUG_MAX_TRACE_LINES]]).strip()
    else:
        shortened_traceback = ""

    error_log = (
        f"[{timestamp}]"
        f"{error_title}\n"
        f"error_massage: {error_message}\n"
        f"path: {path}\n"
        f"{shortened_traceback}"
        f"\n{'-'*40}\n"
    )

    # エラー内容をロギング
    os.makedirs(os.path.dirname(full_apth), exist_ok=True)
    with open(full_apth, "a", encoding="utf-8") as f:
        f.write(error_log)
