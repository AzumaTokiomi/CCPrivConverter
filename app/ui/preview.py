""" preview.py
    機能：プレビュー画面
"""
import re
import tkinter as tk
from tkinter import ttk

from app.logic.processor import load_convert_config, save_convert_config
from app.model.uitexts import TextKey
from app.ui.utils.colorselector import create_color_selector
from system.ja import TEXTS


class PreviewTab:
    def __init__(self, parent, get_html_callback):
        self.parent = parent
        self.get_html_callback = get_html_callback

        # 親フレーム作成
        outer_frame = tk.Frame(parent)
        outer_frame.grid(row=0, column=0, sticky="nsew")

        # 親のグリッド設定（縦・横方向に伸ばす）
        outer_frame.grid_rowconfigure(1, weight=1)      # テキストエリア行
        outer_frame.grid_columnconfigure(0, weight=1)

        # 背景色設定フレーム
        top_frame = ttk.Frame(outer_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        top_frame.grid_columnconfigure(2, weight=1)

        # 背景色ラベル
        ttk.Label(top_frame, text=TEXTS[TextKey.BACKGROUND_COLOR_LABEL], takefocus=False).grid(row=0, column=0, sticky="nw", padx=(0, 5), pady=(5, 0))

        # 設定ファイルから背景色読み込み
        bg_color = load_convert_config().get("preview_bg_color")
        self._bg_color_var = tk.StringVar(value=bg_color)

        # 背景色を変更した時に設定ファイルを更新する
        def save_color(*_):
            save_convert_config({"preview_bg_color": self._bg_color_var.get()})
        self._bg_color_var.trace_add("write", save_color)

        # カラーセレクタ作成
        create_color_selector(top_frame, row=0, column=1, color_var=self._bg_color_var)

        # 更新ボタンをtop_frame内に配置
        refresh_button = ttk.Button(top_frame, text=TEXTS[TextKey.UPDATE_LOG_BUTTON], takefocus=False, command=self.update_preview)
        refresh_button.grid(row=0, column=2, sticky="e", padx=16, ipadx=4, ipady=10)

        # プレビュー表示フレーム作成
        text_frame = ttk.Frame(outer_frame)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(10, 5))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # テキストエリア（フォント設定あり）
        self.text_area = tk.Text(
            text_frame,
            wrap="char",            # 文字ごとに折り返し
            state="disabled",
            bg=self.get_color(),
            font=("Yu Gothic UI", 10)
        )
        self.text_area.grid(row=0, column=0, sticky="nsew")

        # スクロールバー（縦）
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_area.configure(yscrollcommand=scrollbar.set)


    def get_color(self):
        """ get_color
            機能：カラーコードを#付きで取得する
        """
        color = self._bg_color_var.get()
        return f"#{color.lstrip('#')}"


    def update_preview(self):
        """ update_preview
            機能：変換後ログを表示する
        """
        html = self.get_html_callback()

        # ログが無い場合
        if not html.strip():
            html = "<i>" + TEXTS[TextKey.MISSING_LOG_MESSAGE] + "</i>"

        self.text_area.config(state="normal")
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(bg=self.get_color())

        for text, color in self.extract_all_lines(html):
            if color:
                tag = f"color_{color.lower()}"
                if tag not in self.text_area.tag_names():
                    self.text_area.tag_config(tag, foreground=color)
                self.text_area.insert(tk.END, text + "\n", tag)
            else:
                self.text_area.insert(tk.END, text + "\n")

        self.text_area.config(state="disabled")


    def extract_all_lines(self, html: str) -> list[tuple[str, str | None]]:
        """ extract_all_lines
            機能：HTML文字列を色が付いたテキスト単位のリストに変換する

        Returns:
            list[tuple[str, str | None]]: [テキスト、色 / なし（色なしテキスト）]
        """
        html = re.sub(r'<br\s*/?>', '\n', html)
        html = re.sub(r'</p>', '\n\n', html)
        html = re.sub(r'<p>', '', html)
        html = html.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        span_pattern = re.compile(r'<span style="color:\s*(#[0-9a-fA-F]{6})\s*;">(.*?)</span>', re.DOTALL)
        color_blocks = []
        last_end = 0

        for match in span_pattern.finditer(html):
            if match.start() > last_end:
                color_blocks.append((html[last_end:match.start()], None))
            color_blocks.append((match.group(2), match.group(1)))
            last_end = match.end()

        if last_end < len(html):
            color_blocks.append((html[last_end:], None))

        lines: list[tuple[str, str | None]] = []
        for block_text, color in color_blocks:
            block_text = re.sub(r'<[^>]+>', '', block_text)
            for line in block_text.splitlines():
                if line.strip():
                    lines.append((line.strip(), color))
                else:
                    lines.append(("", None))
        return lines
