""" global.py
    機能：全体で使用する設定や関数
"""
import sys

"""
変数・テーブル定義
"""
RESOURCES = None        # resources.json設定値のdist



def is_executable() -> bool:
    """ is_executable

    Returns:
        bool: exeで動作しているかどうか
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS")


def get_int(value, default: int) -> int:
    """ get_int
        機能：int型のチェック。intでない時はdefault値を返す

    Args:
        value (object): 数値かどうかチェックする値
        default (int): 初期値

    Returns:
        int: 数値
    """
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        return default


def get_bool(value, default: bool) -> bool:
    """ get_bool
        機能：bool型のチェック。boolでない時はdefault値を返す

    Args:
        value (object): bool型かどうかチェックする値
        default (bool): 初期値

    Returns:
        bool: bool値
    """
    if isinstance(value, bool):
        return value
    elif str(value).lower() == "true":
        return True
    elif str(value).lower() == "false":
        return False
    else:
        return default
