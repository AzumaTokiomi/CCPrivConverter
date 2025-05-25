""" main.py
    機能：メイン関数
"""
import ctypes
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from app.logic import globals
from app.logic.fileio import check_dir_exist, get_resource_path
from app.logic.processor import (load_convert_config, load_resources,
                                 save_resources)
from app.model.settings import ConfigKey
from app.model.uitexts import TextKey
from app.ui import CharacterTab, ConfigTab, LogTab, PreviewTab
from app.ui.developer import DeveloperTab
from system.ja import TEXTS
from system.resources import APP_ICON_PATH, OUTPUT_DIR_NAME, SETTINGS_DIR_NAME

if __name__ == "__main__":

    # アプリに必要なフォルダ確認、無ければ生成
    check_dir_exist(OUTPUT_DIR_NAME)
    check_dir_exist(SETTINGS_DIR_NAME)

    # リソース設定の読み込み、保存（起動時のみ）
    globals.RESOURCES = load_resources()
    save_resources(globals.RESOURCES)

    # メインウィンドウの生成
    root = tk.Tk()
    root.title(TEXTS[TextKey.APP_TITLE])
    myappid = u'AzumaTokiomi.CCPrivConverter'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # タスクバーにアイコンを設定するための処理
    icon = Image.open(get_resource_path(APP_ICON_PATH))
    icon = ImageTk.PhotoImage(icon)
    root.iconphoto(True, icon)

    # ルートにgridの拡張を設定
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # 変換設定の読み込み（開発者向けタブの非表示のため）
    convert_config = load_convert_config()
    valid_developer_tab_flag = convert_config.get(ConfigKey.CONVERT_WEB_LOG, False)

    # メインウィンドウにタブを作成（幅と高さは可変）
    notebook = ttk.Notebook(root)
    notebook.grid(row=0, column=0, sticky="nsew")

    # Frame作成
    log_frame       = tk.Frame(notebook)
    config_frame    = tk.Frame(notebook)
    character_frame = tk.Frame(notebook)
    preview_frame   = tk.Frame(notebook)
    preview_frame.grid_rowconfigure(0, weight=1)
    preview_frame.grid_columnconfigure(0, weight=1)
    developer_frame = tk.Frame(notebook)

    # 各タブのクラスのインスタンス作成
    config_tab      = ConfigTab(
        config_frame,
        notebook=notebook,
        developer_frame=developer_frame,
        log_tab=None
    )
    character_tab   = CharacterTab(character_frame)
    log_tab = LogTab(
        log_frame,
        config_tab=config_tab,
        character_tab=character_tab,
    )
    # プレビュー用のコールバック関数を渡す
    preview_tab = PreviewTab(preview_frame, get_html_callback=lambda: log_tab.text_area.get("1.0", tk.END))
    config_tab._log_tab = log_tab   # 相互参照のため後から追加
    developer_tab = DeveloperTab(
        developer_frame,
        get_web_log_callback=lambda: log_tab.get_web_log(),
        get_iframe_logs_callback=lambda: log_tab.get_iframe_logs()
    )

    # タブを追加
    notebook.add(log_frame, text=TEXTS[TextKey.LOG_TAB], sticky="nsew")
    notebook.add(config_frame, text=TEXTS[TextKey.CONFIG_TAB], sticky="nsew")
    notebook.add(character_frame, text=TEXTS[TextKey.CHARACTER_TAB], sticky="nsew")
    notebook.add(preview_frame, text=TEXTS[TextKey.PREVIEW_TAB], sticky="nsew")

    # 開発者向けタブの表示、非表示
    if valid_developer_tab_flag:
        notebook.add(developer_frame, text=TEXTS[TextKey.WEB_TAB], sticky="nsew")

    root.mainloop()

