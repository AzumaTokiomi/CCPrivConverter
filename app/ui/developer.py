""" developer.py
    機能：開発者向け画面（web text変換＋iframeログ表示）
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.model.uitexts import TextKey
from app.ui.utils.interface import (bind_canvas_mousewheel,
                                    copy_text_to_clipboard, on_mousewheel,
                                    unbind_canvas_mousewheel,
                                    update_canvas_width, update_scrollregion)
from system.ja import TEXTS


class DeveloperTab:
    def __init__(self, parent, get_web_log_callback: Callable[[], str], get_iframe_logs_callback: Callable[[], list[str]]):
        self.parent = parent
        self.get_web_log_callback = get_web_log_callback
        self.get_iframe_logs_callback = get_iframe_logs_callback

        # スクロール可能なキャンバスの構成
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # 親フレーム作成
        outer_frame = tk.Frame(parent)
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

        # frame_developer：メインフレーム作成
        self.frame_developer = ttk.Frame(self.canvas, padding=(10, 0))
        self.frame_developer.grid_columnconfigure(0, weight=1)

        # キャンバス上に描画
        self.canvas.create_window(
            (0, 0),
            window=self.frame_developer,
            anchor="nw",
            tags="frame_window",
            width=self.canvas.winfo_width()     # 横に広げる
        )

        # サイズ変更やレイアウト変更時に再配置する
        self.canvas.bind("<Configure>", lambda e: update_canvas_width(self.canvas, e))
        self.frame_developer.bind("<Configure>", lambda e: update_scrollregion(self.canvas, self.frame_developer, e))

        # ボタン表示フレーム
        top_frame = ttk.Frame(self.frame_developer)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        top_frame.grid_columnconfigure(0, weight=1)

        # 更新ボタンをtop_frame内に配置
        refresh_button = ttk.Button(top_frame, text=TEXTS[TextKey.UPDATE_LOG_BUTTON], takefocus=False, command=self.update_text)
        refresh_button.grid(row=0, column=0, sticky="e", ipadx=4, ipady=10)

        # webログフレーム
        web_frame = ttk.LabelFrame(self.frame_developer, text=TEXTS[TextKey.WEB_LOG_LABEL], padding=(10, 5, 0, 10))
        web_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        web_frame.grid_columnconfigure(0, weight=1)

        # web logのテキストエリア
        self.web_log_text_area = tk.Text(
            web_frame,
            height=1,
            state="disabled",
            wrap="none"         # 折り返さない
        )
        self.web_log_text_area.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)

        # コピーボタン
        ttk.Button(
            web_frame,
            text=TEXTS[TextKey.COPY_LABEL],
            command=self.copy_web_log,
            takefocus=False
        ).grid(row=0, column=1, sticky="e", padx=(5, 10))

        # iframeログフレーム
        iframe_frame = ttk.LabelFrame(self.frame_developer, text=TEXTS[TextKey.IFRAME_LOG_LABEL], padding=(10, 5, 0, 10))
        iframe_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        iframe_frame.grid_columnconfigure(0, weight=1)

        # iframe logのテキストエリア
        self.iframe_logs_container = ttk.Frame(iframe_frame)
        self.iframe_logs_container.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(2, 0), pady=5)  # padxを調整
        self.iframe_logs_container.grid_columnconfigure(0, weight=1)

        self.iframe_log_widgets = []  # テキストウィジェットとボタン

        # 初期状態で1行分だけ追加
        self.add_iframe_logs_row(count=1)


    def update_text(self):
        """ update_text
            機能：webログ、iframeログを取得して画面に反映する
        """
        web_log = self.get_web_log_callback()
        iframe_logs = self.get_iframe_logs_callback()

        # 中身が空の場合、メッセージを表示
        if not web_log:
            web_log = TEXTS[TextKey.MISSING_LOG_MESSAGE]
            iframe_logs.append(TEXTS[TextKey.MISSING_LOG_MESSAGE])

        # Webログ更新
        self.web_log_text_area.config(state="normal")
        self.web_log_text_area.delete("1.0", tk.END)
        self.web_log_text_area.insert(tk.END, web_log.strip())
        self.web_log_text_area.config(state="disabled")

        # iframeログ更新
        self.clear_iframe_logs()
        self.add_iframe_logs_row(count=len(iframe_logs))

        for i, (text_widget, _) in enumerate(self.iframe_log_widgets):
            if i < len(iframe_logs):
                text_widget.config(state="normal")
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, iframe_logs[i].strip())
                text_widget.config(state="disabled")


    def clear_iframe_logs(self):
        """ clear_iframe_logs
            機能：iframeログ用のTextとButtonを全部消す
        """
        for text_widget, button in self.iframe_log_widgets:
            text_widget.destroy()
            button.destroy()
        self.iframe_log_widgets.clear()


    def add_iframe_logs_row(self, count: int):
        """ add_iframe_logs_row
        機能：iframeログの行数分、Text+Buttonを生成

        Args:
            count (int): iframe logsの要素数
        """
        for i in range(count):
            text = tk.Text(
                self.iframe_logs_container,
                height=1,
                state="disabled",
                wrap="none"         # 折り返さない
            )
            text.grid(row=i, column=0, sticky="ew", padx=(5, 0), pady=2)

            # コピーボタン
            button = ttk.Button(
                self.iframe_logs_container,
                text=TEXTS[TextKey.COPY_LABEL],
                takefocus=False,
                command=lambda t=text: self.copy_text(t)
            )
            button.grid(row=i, column=1, sticky="e", padx=(5, 10))
            self.iframe_log_widgets.append((text, button))


    def copy_web_log(self):
        """ copy_web_log
            機能：webログのコピー
        """
        self.copy_text(self.web_log_text_area)


    def copy_text(self, text_widget):
        """ copy_text
            機能：クリップボードへのコピー
        """
        copy_text_to_clipboard(self.parent, text_widget)
