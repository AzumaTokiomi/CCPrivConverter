""" config.py
    機能：変換設定画面
"""
import tkinter as tk
from tkinter import ttk

from app.logic.processor import load_convert_config, save_convert_config
from app.model.settings import CONVERT_CONFIG, ConfigKey
from app.model.uitexts import TextKey
from app.ui.developer import DeveloperTab
from app.ui.utils.interface import (bind_canvas_mousewheel, on_mousewheel,
                                    unbind_canvas_mousewheel,
                                    update_canvas_width, update_scrollregion)
from system.ja import TEXTS


class ConfigTab:
    def __init__(self, parent, notebook=None, developer_frame=None, log_tab=None):
        self.parent = parent
        self._config_vars = {}
        self._notebook = notebook
        self._developer_frame = developer_frame
        self._log_tab = log_tab

        # スクロール可能なキャンバスの構成
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # 親フレーム作成
        outer_frame = ttk.Frame(parent)
        outer_frame.grid(row=0, column=0, sticky="nsew")

        # 親のグリッド設定（縦・横方向に伸ばす）
        outer_frame.grid_rowconfigure(0, weight=1)
        outer_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            outer_frame,
            height=50,              # 一応設定
            highlightthickness=0,   # フォーカス枠を非表示
            bd=0,                   # 枠線を非表示
            relief="flat"           # 立体感なし
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # スクロールバー（縦）
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # ホイール操作を有効にする
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        self.canvas.bind_all("<MouseWheel>", lambda e: on_mousewheel(self.canvas, e))

        self.canvas.bind("<Enter>", lambda e: bind_canvas_mousewheel(self.canvas))
        self.canvas.bind("<Leave>", lambda e: unbind_canvas_mousewheel(self.canvas))

        # frame_config：メインフレーム作成
        self.frame_config = ttk.Frame(self.canvas, padding=(10, 0))
        self.frame_config.grid_columnconfigure(0, weight=1)

        # キャンバス上に描画
        self.canvas.create_window(
            (0, 0),
            window=self.frame_config,
            anchor="nw",
            tags="frame_window",
            width=self.canvas.winfo_width()     # 横に広げる
        )

        # サイズ変更やレイアウト変更時に再配置する
        self.canvas.bind("<Configure>", lambda e: update_canvas_width(self.canvas, e))
        self.frame_config.bind("<Configure>", lambda e: update_scrollregion(self.canvas, self.frame_config, e))

        # 通常設定フレーム
        general_frame = ttk.Frame(self.frame_config)
        general_frame.grid(row=0, column=0, sticky="ew")
        general_frame.grid_columnconfigure(1, weight=1)

        # privatter+向けフレーム
        privatter_frame = ttk.LabelFrame(self.frame_config, text=TEXTS[TextKey.PRIVATTER_PLUS_SETTINGS], padding=(10, 5, 10, 10))
        privatter_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        privatter_frame.grid_columnconfigure(1, weight=1)

        # 開発者向けフレーム
        developer_frame = ttk.LabelFrame(self.frame_config, text=TEXTS[TextKey.DEVELOPER_SETTINGS], padding=(10, 5, 10, 10))
        developer_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        developer_frame.grid_columnconfigure(1, weight=1)

        # 設定値読み込み
        load_convert_cfg_data: dict = load_convert_config()

        # 設定項目作成
        row_general = 0
        row_privatter = 0
        row_developer = 0

        for convert_setting in CONVERT_CONFIG:
            key = convert_setting.key

            # 通常設定項目の画面追加
            if convert_setting.group == "general":
                target_frame = general_frame
                row = row_general
                row_general += 1
            # Privatter+向け項目の画面追加
            elif convert_setting.group == "privatter":
                target_frame = privatter_frame
                row = row_privatter
                row_privatter += 1
            # 開発者向け項目の画面追加
            elif convert_setting.group == "developer":
                target_frame = developer_frame
                row = row_developer
                row_developer += 1
            else:       # プレビュー画面用設定など
                continue

            # 設定値をUI用変数に設定
            if convert_setting.config_type == "bool":
                var = tk.BooleanVar(value=load_convert_cfg_data[key])
            elif convert_setting.config_type == "str":
                var = tk.StringVar(value=load_convert_cfg_data[key])
            else:
                continue

            # 設定値を対応するキーと紐づけて保管
            self._config_vars[key] = var

            # 開発者向けタブの表示監視
            if key == ConfigKey.CONVERT_WEB_LOG:
                def toggle_developer_tab(*_):
                    """ toggle_developer_tab
                        機能：開発者向けタブの表示切替
                    """
                    # webログへの変換機能が有効
                    if var.get():
                        # 開発者向けタブが非表示中の時、表示する
                        if not is_developer_tab_enabled(self._notebook, self._developer_frame):
                            self._notebook.add(self._developer_frame, text=TEXTS[TextKey.WEB_TAB], sticky="nsew")
                    else:
                        try:
                            # 開発者向けタブを非表示にする
                            self._notebook.forget(self._developer_frame)
                        except tk.TclError:
                            pass
                var.trace_add("write", toggle_developer_tab)

            if convert_setting.config_type == "str":
                ttk.Label(target_frame, text=TEXTS[convert_setting.label], takefocus=False).grid(row=row, column=0, sticky="w")
                ttk.Entry(target_frame, textvariable=var, takefocus=False).grid(row=row, column=1, padx=(15, 0), pady=5, sticky="ew")
                target_frame.grid_columnconfigure(1, weight=1)
            else:
                ttk.Checkbutton(target_frame, text=TEXTS[convert_setting.label], variable=var, takefocus=False).grid(row=row, column=0, sticky="w", pady=5)

            # 設定が変更されたら設定ファイルに保存する
            def change_config_var(*_):
                save_convert_config(self.get_convert_config_from_vars())
            var.trace_add("write", change_config_var)

        # 読み込んだ時に初期値設定をしたかもしれないので、いったん保存しておく
        save_convert_config(self.get_convert_config_from_vars())


    def get_convert_config_from_vars(self) -> dict:
        """ get_convert_config_from_vars
            機能：UI用変数から設定値を取得する

        Returns:
            dict: 設定値
        """
        result = {}
        for key, var in self._config_vars.items():
            result[key] = var.get()
        return result


def is_developer_tab_enabled(notebook, frame):
    try:
        notebook.index(frame)
        return True
    except tk.TclError:
        # タブが見つからない
        return False
