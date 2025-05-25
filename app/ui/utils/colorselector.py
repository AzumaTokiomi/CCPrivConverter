""" colorselector.py
    機能：カラーセレクタのコンポーネント
"""
import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor


def create_color_selector(parent, row, column, color_var):
    """ create_color_selector
        機能：カラーセレクタ（カラーコード入力欄とカラーピッカーと色表示）を作成する
    Args:
        row (int): 行番号
        column (int): 列番号
        color_var (StringVar): 色選択変数
    """
    # 親フレームに作成
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=column, padx=2, pady=2, sticky="nsew")

    # カラーコード入力欄
    entry = ttk.Entry(frame, textvariable=color_var, width=10, takefocus=False)
    entry.grid(row=0, column=0, sticky="nsew", padx=2)

    # カラーピッカーボタン
    def choose_color():
        """ choose_color
            クリック：色選択
        """
        result = askcolor(color="#" + color_var.get().lstrip("#"))
        # HEXカラーコードをチェック
        if result[1]:
            color_var.set(result[1].lstrip("#"))        # 先頭のシャープはトリミングして入力欄に設定
            canvas.itemconfig(rect, fill=result[1])     # キャンバスの色表示を更新

    button = ttk.Button(frame, text="🎨", width=3, command=choose_color, takefocus=False)
    button.grid(row=0, padx=2,column=1)

    # 色表示
    canvas = tk.Canvas(frame, width=20, height=20, highlightthickness=0, bd=0, bg="SystemButtonFace")
    canvas.grid(row=0, column=2, padx=2)
    rect = canvas.create_rectangle(0, 0, 20, 20, fill=f"#{color_var.get().lstrip('#')}", outline="#aaa")


    def change_color_code(*args):
        """ on_entry_change
            機能：カラーコードの変更時に色表示を更新する
        """
        color = color_var.get()
        if not color.startswith("#"):
            color = "#"+ color
        try:
            canvas.itemconfig(rect, fill=color)
        except tk.TclError:
            pass

    # カラーコードの更新時に更新
    color_var.trace_add("write", change_color_code)
