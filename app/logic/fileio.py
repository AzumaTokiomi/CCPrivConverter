""" fileio.py
    機能：ファイル入出力
"""
import inspect
import json
import os
import sys

from app.logic.globals import is_executable

"""
定数定義
"""
# ルートパス（main.pyを基準にする）
APP_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))



def get_root_relative_path() -> str:
    """ get_root_relative_path
        機能：ルートからの相対パスを返す

    Returns:
        str: 相対パス
    """
    try :
        frame = inspect.stack()[1]
        abs_path = os.path.abspath(frame.filename)
        return os.path.relpath(abs_path, start=APP_ROOT)
    except Exception:
        return "{unknown}"


def get_executable_path(add_path):
    """ get_executable_path
        機能：実行ファイルの場所を基準にしてパスを追加し、フルパスを返す

    Args:
        add_path (str): 追加するパス

    Returns:
        str: 実行ファイルのあるパス(絶対パス)
    """
    # exeで動いている場合
    if is_executable():
        base_path = os.path.dirname(sys.executable)
    # .pyで動いている場合
    else:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

   #パスのバックスラッシュをスラッシュに置換する
    full_path = os.path.join(base_path, add_path).replace("\\", "/")

    # ドライブ文字を大文字に統一
    if len(full_path) >= 2 and full_path[1] == ":":
        full_path = full_path[0].upper() + full_path[1:]

    return full_path


def get_resource_path(add_path):
    """ get_resource_path
        機能：リソースの展開先を基準にしてパスを追加し、フルパスを返す

    Args:
        add_path (str): 追加するパス

    Returns:
        str: リソースのあるパス(絶対パス)
    """
    # .exeで動いている場合、PyInstallerの仮展開ディレクトリ + 相対パス
    if is_executable():
        base_path = sys._MEIPASS
    else:
        # .pyで動いている場合、実行中ファイルからの相対パス
        base_path = os.path.abspath(os.path.dirname(sys.argv[0]))

   #パスのバックスラッシュをスラッシュに置換する
    full_path = os.path.join(base_path, add_path).replace("\\", "/")

    # ドライブ文字を大文字に統一
    if len(full_path) >= 2 and full_path[1] == ":":
        full_path = full_path[0].upper() + full_path[1:]

    return full_path


def check_dir_exist(dir):
    """ check_dir_exist
        機能：ディレクトリがあるか確認して、無ければ作る
        ※exeと同じ場所に作ることを想定

    Args:
        dir (sir): ディレクトリ名
    """
    path = get_executable_path(dir)
    os.makedirs(path, exist_ok=True)


def open_file(path: str):
    """ open_file
        機能：ファイルを開く

    Args:
        path (str): 開くパス
    """
    import os
    import platform
    import subprocess

    full_path = get_executable_path(path)

    if platform.system() == "Windows":
        # windowsの場合、既定のアプリで開く
        os.startfile(full_path)
    elif platform.system() == "Darwin":
        # macの場合、openコマンドでファイルを開く
        subprocess.run(["open", full_path])
    else:
        # Linuxの場合、規定のアプリで開く
        subprocess.run(["xdg-open", full_path])


def save_json(data: dict, path: str):
    """ save_json
        機能：指定されたパスにJSONファイルとして保存する

    Args:
        data (dict): 保存データ
        path (str): 保存するパス
    """
    full_path = get_executable_path(path)

    # ディレクトリが無ければ作成する（あったら作成しない）
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    #JSON形式でファイル書き込み
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        from app.logic.logging import logging_error
        logging_error("設定ファイル(JSON)の保存失敗", get_root_relative_path(), e)



def load_json(path: str) -> dict:
    """ load_json
        機能：指定されたパスからJSONファイルを読み込む。存在しない場合は空のdictを返す

    Args:
        path (str): 読み込むパス

    Returns:
        dict: dictに変換されたjsonデータ
    """
    full_path = get_executable_path(path)

    # 指定したパスに無かった場合、空データを返す
    if not os.path.exists(full_path):
        return {}

    # JSON形式のファイル読み込み
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        from app.logic.logging import logging_error
        logging_error("設定ファイル(JSON)の読み込み失敗", get_root_relative_path(), e)
        return {}
