""" log.py
    機能：ログ変換画面
"""
import os
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog, ttk

from app.logic import globals
from app.logic.fileio import get_executable_path, open_file
from app.logic.processor import check_valid_color_code, convert_log
from app.model.settings import ConfigKey
from app.model.uitexts import TextKey
from app.ui.utils.interface import copy_text_to_clipboard
from system.ja import TEXTS
from system.resources import OUTPUT_DIR_NAME, OUTPUT_FILE_NAME, ResourcesKey

"""
定数定義
"""
LABEL_WIDTH         = 22
ENTRY_WIDTH         = 60
FRAME_PADDING       = 10
BUTTON_WIDTH        = 20
BUTTON_HEIGHT       = 10



class LogTab:
    """ LogTab
        ログ変換タブ
    """
    def __init__(self, parent, config_tab, character_tab):
        self.parent = parent
        self.config_tab = config_tab
        self.character_tab = character_tab
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # 親フレーム作成
        outer_frame = tk.Frame(parent)
        outer_frame.grid(row=0, column=0, sticky="nsew")
        outer_frame.grid_columnconfigure(0, weight=1)

        # 親のグリッド設定（縦・横方向に伸ばす）
        outer_frame.rowconfigure(3, weight=1)
        outer_frame.columnconfigure(0, weight=1)

        # frame_input：入力ファイル選択
        frame_input = ttk.Frame(outer_frame, padding=FRAME_PADDING)
        frame_input.grid(row=0, column=0, sticky="ew")
        frame_input.columnconfigure(1, weight=1)

        # 入力ファイルラベル
        ttk.Label(
            frame_input, text=TEXTS[TextKey.CCFOLIA_LOG_LABEL], width=LABEL_WIDTH, padding=(5, 2)
        ).grid(row=0, column=0, sticky="w")

        # 入力ファイルパス
        self.input_file = tk.StringVar()
        self.input_file.set("")         # inputは空
        ttk.Entry(
            frame_input, textvariable=self.input_file, width=ENTRY_WIDTH, takefocus=False
        ).grid(row=0, column=1, sticky="ew")

        # 入力ファイルの参照ボタン
        ttk.Button(
            frame_input, text=TEXTS[TextKey.REFERENCE_BUTTON], command=self.click_input_file_dialog, takefocus=False
        ).grid(row=0, column=2, padx=(5, 15))

        # frame_output：出力ファイル選択
        frame_output = ttk.Frame(outer_frame, padding=FRAME_PADDING)
        frame_output.grid(row=1, column=0, sticky="ew")
        frame_output.columnconfigure(1, weight=1)

        # 出力ファイルラベル
        ttk.Label(
            frame_output, text=TEXTS[TextKey.OUTPUT_TEXT_LABEL], width=LABEL_WIDTH, padding=(5, 2)
        ).grid(row=0, column=0, sticky="w")

        # 出力ファイルパス
        self.output_file = tk.StringVar()
        self.output_file.set(get_executable_path(os.path.join(OUTPUT_DIR_NAME, OUTPUT_FILE_NAME)))
        ttk.Entry(
            frame_output, textvariable=self.output_file, width=ENTRY_WIDTH, takefocus=False
        ).grid(row=0, column=1, sticky="ew")

        # 出力ファイルの参照ボタン
        ttk.Button(
            frame_output, text=TEXTS[TextKey.REFERENCE_BUTTON], command=self.click_output_file_dialog, takefocus=False
        ).grid(row=0, column=2, padx=(5, 15))

        # frame_button：変換・コピー ボタン
        frame_button = ttk.Frame(outer_frame, padding=FRAME_PADDING)
        frame_button.grid(row=2, column=0, sticky="ew")
        frame_button.columnconfigure(0, weight=1)
        frame_button.columnconfigure(1, weight=1)

        # 中央寄せ用の内フレーム
        f_button_center = ttk.Frame(frame_button)
        f_button_center.pack(anchor="center")

        # ログ変換実行ボタン
        self.convert_button = ttk.Button(
            f_button_center,
            text=TEXTS[TextKey.CONVERT_BUTTON],
            command=self.click_convert_log,
            width=BUTTON_WIDTH,
            takefocus=False
        )
        self.convert_button.grid(row=0, column=0, padx=5, pady=10, ipady=BUTTON_HEIGHT)

        # コピーボタン
        self.copy_button = ttk.Button(
            f_button_center,
            text=TEXTS[TextKey.COPY_TEXT_BUTTON],
            command=self.copy_text,
            width=BUTTON_WIDTH,
            takefocus=False
        )
        self.copy_button.grid(row=0, column=1, padx=5, pady=10, ipady=BUTTON_HEIGHT)

        # frame_text：表示エリア
        frame_text = ttk.Frame(outer_frame, padding=FRAME_PADDING)
        frame_text.grid(row=3, column=0, sticky="nsew")
        frame_text.columnconfigure(0, weight=1)
        frame_text.rowconfigure(0, weight=1)

        # スクロールバー（縦）
        scrollbar = ttk.Scrollbar(frame_text, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # テキストエリア
        self.text_area = tk.Text(
            frame_text,
            wrap="word",
            width=100,
            height=20,
            yscrollcommand=scrollbar.set,
            state="disabled"
        )
        self.text_area.grid(row=0, column=0, sticky="nsew")

        # スクロールバーとテキストエリアを接続
        scrollbar.config(command=self.text_area.yview)

        self.char_count_label = ttk.Label(frame_text, text=TEXTS[TextKey.CHARACTER_COUNT_LABEL].format(count=0))
        self.char_count_label.grid(row=1, column=0, sticky="e", pady=(5, 0))


    def click_input_file_dialog(self):
        """ click_input_file_dialog
            クリック；ココフォリアのログの参照クリック
        """
        # current_path = check_path_valid(self.input_file.get())
        current_path = self.input_file.get()

        # パスが未設定・不正の場合はOSに任せる

        file_path = filedialog.askopenfilename(
            filetypes=[("HTML files", "*.html")],
            initialdir=os.path.dirname(current_path)
        )

        if file_path:
            self.input_file.set(file_path)


    def click_output_file_dialog(self):
        """click_output_file_dialog
            クリック：出力ファイルの参照クリック
        """
        current_path = self.output_file.get()

        # パスが未設定・不正の場合
        if not current_path or not os.path.exists(os.path.dirname(current_path)):
            current_path = get_executable_path(os.path.join(OUTPUT_DIR_NAME, OUTPUT_FILE_NAME))

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialdir=os.path.dirname(current_path),
            initialfile=os.path.basename(current_path)
        )

        if file_path:
            self.output_file.set(file_path)


    def click_convert_log(self):
        """click_convert_log
            クリック：ログ変換
        """
        convert_cfg = self.config_tab.get_convert_config_from_vars()
        character_cfg = self.character_tab.get_character_config_from_vars()

        # カラーコードの有効確認
        for c_cfg in character_cfg:
            color_code = c_cfg.get(ConfigKey.COLOR_CODE)
            # 無効なカラーコードがあった場合、エラーダイアログを表示して終了
            if not check_valid_color_code(color_code):
                messagebox.showerror(
                    TEXTS[TextKey.ERROR_DIALOG_TITLE],
                    TEXTS[TextKey.COLOR_CODE_ERR_MESSAGE],
                    parent=self.parent
                )
                return

        # ログ変換処理を実行
        success, result, characters = convert_log(
            input_path=self.input_file.get(),
            output_path=self.output_file.get(),
            convert_config=convert_cfg,
            character_config=character_cfg
        )

        # 変換失敗
        if not success:
            e_message, error = result
            messagebox.showerror(TEXTS[TextKey.ERROR_DIALOG_TITLE], f'{e_message}\n\n{TEXTS[TextKey.DETAIL_MESSAGE]}：\n{error}', parent=self.parent)
            return

        # 変換成功
        text, total_len = result
        privatter_log, web_log, iframe_logs = text
        unknown_characters, use_classes = characters
        self.text_area.configure(state="normal")        # 書き込みのために一時的に有効化
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, privatter_log)
        self.text_area.configure(state="disabled")     # 再び無効化

        self._web_log = web_log
        self._iframe_logs = iframe_logs

        # 文字数カウントしてラベルに表示
        self.char_count_label.config(text=TEXTS[TextKey.CHARACTER_COUNT_LABEL].format(count=total_len))

        # 未設定の発言者がいた場合に通知する機能が有効なら、通知する
        if convert_cfg.get("report_unknown_character") == True:
            if unknown_characters:
                messagebox.showwarning(
                    TEXTS[TextKey.WARNING_DIALOG_TITLE],
                    TEXTS[TextKey.UNKNOWN_CHARACTERS_MESSAGE].format(unknown_characters=unknown_characters),
                    parent=self.parent
                )

        # Privatterの最大文字数を超えそうな時に通知する機能が有効なら、文字数チェック
        max_len = globals.RESOURCES[ResourcesKey.MAX_LOG_CHARCTER_LENGTH]
        if convert_cfg.get(ConfigKey.REPORT_OVER_CHARACTER):
            if total_len > max_len:
                messagebox.showwarning(
                    TEXTS[TextKey.WARNING_DIALOG_TITLE],
                    TEXTS[TextKey.OVER_CHARACTER_MESSAGE].format(max_character_count=max_len),
                    parent=self.parent
                )

        # 出力ファイルを開くかどうかの確認ダイアログを表示する機能が有効なら、ダイアログを表示
        if convert_cfg.get(ConfigKey.INFO_OPEN_OUTPUT_FILE):
            ret = messagebox.askyesno(
                TEXTS[TextKey.INFO_DIALOG_TITLE],
                TEXTS[TextKey.COMPLETED_CONVERT_MESSAGE],
                parent=self.parent
            )
            # 出力ファイルを開く場合、エディタを開く
            if True == ret:
                open_file(self.output_file.get())


    def copy_text(self):
        """ copy_text
            機能：クリップボードに変換後ログをコピーする
        """
        copy_text_to_clipboard(self.parent, self.text_area)


    def get_web_log(self) -> str:
        """ 変換したwebログの取得

        Returns:
            str: webログ
        """
        return getattr(self, "_web_log", "")


    def get_iframe_logs(self) -> list[str]:
        """ get_iframe_logs

        Returns:
            list[str]: iframeのログ リスト
        """
        return getattr(self, "_iframe_logs", [])
