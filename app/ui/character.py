""" character.py
    機能：キャラ設定画面
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional

from app.logic import globals
from app.logic.processor import load_character_config, save_character_config
from app.model.settings import CHARACTER_CONFIG, ConfigKey
from app.model.uitexts import TextKey
from app.ui.utils.colorselector import create_color_selector
from app.ui.utils.interface import (bind_canvas_mousewheel, on_mousewheel,
                                    unbind_canvas_mousewheel,
                                    update_scrollregion)
from system.ja import TEXTS
from system.resources import ResourcesKey


class CharacterTab:
    def __init__(self, parent):
        self.parent = parent
        self._character_config = []

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
            height=50,              # ウィジェットが無かった時のために一応設定
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

        # frame_character：メインフレーム作成
        self.frame_character = ttk.Frame(self.canvas, padding=(10, 0))

        #for i in range(2):  # ↑と↓ボタンの列
        #    self.frame_character.grid_columnconfigure(i, weight=0, minsize=1)

        # キャンバス上に描画
        self.canvas.create_window(
            (0, 0),
            window=self.frame_character,
            anchor="nw",
            tags="frame_window"
        )

        # サイズ変更やレイアウト変更時に再配置する
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("frame_window", width=e.width))
        self.frame_character.bind("<Configure>", lambda e: update_scrollregion(self.canvas, self.frame_character, e))

        # ヘッダーの描画
        self.build_header()

        # 設定値読み込み
        load_default_cfg_data, load_character_cfg_data = load_character_config()

        # ウィジェットの削除
        self.clear_all()

        # デフォルト行の追加
        self.add_row(initial_values=load_default_cfg_data, is_default=True)

        # 読み込んだキャラ設定に基づいて行追加
        for character_config in load_character_cfg_data:
            self.add_row(initial_values=character_config)

        # 読み込んだデータから5行追加
        for _ in range(5):
            self.add_row()

        # 行追加ボタンを追加
        self.update_add_row_button()


    def build_header(self):
        """ build_header
            機能：ヘッダーの描画
        """
        col_num = 0

        # 列移動ラベル（列0〜1をまたぐ）
        ttk.Label(self.frame_character, text=TEXTS[TextKey.SWAP_ROW_LABEL], padding=4, anchor="center").grid(row=0, column=col_num, columnspan=2, sticky="we")
        col_num += 2

        for character_config in CHARACTER_CONFIG:
            # フレームにラベル追加
            ttk.Label(self.frame_character, text=TEXTS[character_config.label], padding=4).grid(row=0, column=col_num, sticky="")
            col_num += 1

        # 削除ラベルの追加
        ttk.Label(self.frame_character, text=TEXTS[TextKey.DELETE_ROW_LABEL]).grid(row=0, column=col_num, sticky="")


    def add_row(self, initial_values: Optional[Dict[str, Any]] = None, is_default: bool = False):
        """ add_row
            機能：設定行を追加する。空行の追加ができるように引数は自由にしておく

        Args:
            initial_values (Optional[Dict[str, Any]], optional): キャラ設定. Defaults to None.
            is_default (bool, optional): デフォルト行かどうか. Defaults to False.
        """
        # 追加されている設定項目の数から行番号を取得
        row = len(self._character_config) + 1
        row_vars = {}
        widgets = []
        index = len(self._character_config)
        col_num = 0

        # 行移動ボタンの追加
        if not is_default:
            # ↑ボタン
            up_btn = ttk.Button(self.frame_character, text="↑", width=2, command=lambda idx=index: self.move_row_up(idx))
            up_btn.grid(row=row, column=col_num, padx=1)
            col_num += 1

            # ↓ボタン
            down_btn = ttk.Button(self.frame_character, text="↓", width=2, command=lambda idx=index: self.move_row_down(idx))
            down_btn.grid(row=row, column=col_num, padx=1)
            col_num += 1

            widgets.extend([up_btn, down_btn])
        else:
            col_num += 2    # デフォルト行の場合は場所を空ける

        # 列にウィジェットを追加
        for setting in CHARACTER_CONFIG:
            if initial_values is not None:
                # initial_valuesがあれば、そのキーから値を取得（なければデフォルト）
                value = initial_values.get(setting.key, setting.default)
            else:
                # initial_valuesが無ければ、デフォルトを使う
                value = setting.default

            # 文字列項目の場合
            if setting.config_type == "str":
                var = tk.StringVar(value=value)
                if setting.key == ConfigKey.COLOR_CODE:
                    # カラーコードのみカラーピッカーを含めたウィジェットを追加する
                    create_color_selector(self.frame_character, row, col_num, var)
                    widgets.append(self.frame_character.grid_slaves(row=row, column=col_num)[0])
                else:
                    entry = ttk.Entry(self.frame_character, textvariable=var, width=12, takefocus=False)
                    entry.grid(row=row, column=col_num, padx=2, pady=2, sticky="nsew")

                    # Default行の場合入力を受け付けない
                    if is_default and setting.key == ConfigKey.CHARACTER:
                        entry.configure(state="readonly")
                    widgets.append(entry)
            # チェックボックス項目の場合
            elif setting.config_type == "bool":
                var = tk.BooleanVar(value=value)
                check = ttk.Checkbutton(
                    self.frame_character,
                    variable=var,
                    text="",             # 明示的にtextを空にしておく
                    takefocus=False      # フォーカス枠を抑制
                )
                # デフォルト行は着色を有効にする
                if is_default and setting.key == ConfigKey.ENABLE_PAINT:
                    var.set(True)
                    check.configure(state="disabled")

                check.grid(row=row, column=col_num, sticky="", padx=2)
                widgets.append(check)
            else:
                continue

            def change_character_config_var(*_):
                """ change_character_config_var
                    機能：設定が変更されたら設定ファイルに保存する
                """
                save_character_config(self.get_character_config_from_vars())

            var.trace_add("write", change_character_config_var)
            row_vars[setting.key] = var

            col_num += 1    # 列番号の加算

        # デフォルト行以外は削除ボタンを追加する
        if not is_default:
            index = len(self._character_config)
            delete_btn = ttk.Button(
                self.frame_character,
                text="🗑️",
                width=3,
                command=lambda idx=index: self.click_remove_row(idx)
            )
            delete_btn.grid(row=row, column=col_num, padx=4)
            widgets.append(delete_btn)
            col_num += 1

        self._character_config.append({"values": row_vars, "widgets": widgets})

        # 行追加ボタンを更新する
        self.update_add_row_button()


    def click_remove_row(self, index: int):
        """ confirm_and_remove
            クリック：行を削除する
        """
        if messagebox.askyesno(TEXTS[TextKey.CHECK_DIALOG_TITLE], TEXTS[TextKey.REMOVE_ROW_MESSAGE]):
            self.remove_row(index)


    def remove_row(self, index):
        """ remove_row
            機能：行を削除する

        Args:
            index (int): 削除する行番号
        """
        for widget in self._character_config[index]["widgets"]:
            widget.destroy()
        del self._character_config[index]
        # 画面を再構築する
        self.rebuild_all_rows()

        # 削除後のキャラ設定で設定ファイルを更新
        save_character_config(self.get_character_config_from_vars())


    def rebuild_all_rows(self):
        """ rebuild_all_rows
            機能：キャラ設定項目の再構築
        """
        default_row_flag = 0
        data: list = self.get_character_config_from_vars()
        # 画面削除
        self.clear_all()
        # 行追加（デフォルト行と追加処理を分ける）
        for i, item in enumerate(data):
            if item.get("character") == globals.RESOURCES[ResourcesKey.CHARACTER_DEFAULT_NAME] and default_row_flag == 0:
                self.add_row(initial_values=item, is_default=True)
                default_row_flag = 1        # 一応デフォルト行設定は1行のみになるようにしておくか…
            else:
                self.add_row(initial_values=item)

        # 読み込んだデータから5行追加
        for _ in range(5):
            self.add_row()

        # 行追加ボタンを追加
        self.update_add_row_button()

        # 並び順を含めて保存する
        save_character_config(self.get_character_config_from_vars())


    def update_add_row_button(self):
        """ update_add_row_button
            機能：行追加ボタンの更新
        """
        # すでに存在している場合は破棄して再配置
        if hasattr(self, "add_btn") and self.add_btn.winfo_exists():
            self.add_btn.destroy()

        self.add_btn = ttk.Button(self.frame_character, text=TEXTS[TextKey.ADD_ROW_LABEL], command=self.add_row)
        # ヘッダーが row=0のため
        row = len(self._character_config) + 1
        self.add_btn.grid(row=row, column=0, columnspan=3, padx=4, pady=10, ipadx=4, ipady=10, sticky="w")


    def clear_all(self):
        """ clear_all
            機能：フレーム内のウィジェットを削除する
        """
        for widget in self.frame_character.winfo_children():
            widget.destroy()
        self._character_config.clear()
        # ヘッダーは描画する
        self.build_header()


    def get_character_config_from_vars(self) -> List[Dict[str, Any]]:
        """ get_character_config_from_vars
            機能：UI用変数から設定値を取得する

        Returns:
            List[Dict[str, Any]: 設定値
        """
        result = []
        for character_config in self._character_config:
            item = {}
            for key, var in character_config["values"].items():
                item[key] = var.get()

            # キャラクターの記入がない場合はスキップ
            if item.get(ConfigKey.CHARACTER, "").strip():
                result.append(item)

        return result


    def move_row_up(self, index: int):
        """ move_row_up
            機能：行を上に移動する

        Args:
            index (int): 移動対象の行番号
        """
        # 最上段以外の時
        if index > 0:
            # スワップ
            self._character_config[index], self._character_config[index - 1] = \
                self._character_config[index - 1], self._character_config[index]
            self.rebuild_all_rows()


    def move_row_down(self, index: int):
        """ move_row_up
            機能：行を下に移動する

        Args:
            index (int): 移動対象の行番号
        """
        # 最下段以外の時
        if index < len(self._character_config) - 1:
            # スワップ
            self._character_config[index], self._character_config[index + 1] = \
                self._character_config[index + 1], self._character_config[index]
            self.rebuild_all_rows()
