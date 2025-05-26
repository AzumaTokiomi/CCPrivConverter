""" ja.py
    機能：日本語
"""

from app.model.uitexts import TextKey

TEXTS = {
    # メイン
    TextKey.APP_TITLE: "CCぷらいべった～こんば～た～",

    # タブ
    TextKey.LOG_TAB:        "ログ変換",
    TextKey.CONFIG_TAB:     "変換設定",
    TextKey.CHARACTER_TAB:  "キャラ設定",
    TextKey.PREVIEW_TAB:    "プレビュー",
    TextKey.WEB_TAB:        "開発者向け",

    # ログ変換
    TextKey.CCFOLIA_LOG_LABEL:      "ココフォリアのログ（html）",
    TextKey.OUTPUT_TEXT_LABEL:      "出力ファイル（txt）",
    TextKey.REFERENCE_BUTTON:       "参照",
    TextKey.CONVERT_BUTTON:         "ログ変換",
    TextKey.COPY_TEXT_BUTTON:       "内容を全てコピー",
    TextKey.CHARACTER_COUNT_LABEL:  "文字数：{count}",

    # 変換設定
    TextKey.PRIVATTER_PLUS_SETTINGS:        "Privatter+向け設定",
    TextKey.DEVELOPER_SETTINGS:             "開発者向け設定",
    TextKey.USE_DEFAULT_SETTING_LABEL:      "未設定や着色無視の発言者にデフォルトの発言色を使用する\n※無効の場合はココフォリアでの発言色を設定",
    TextKey.REPORT_UNKNOWN_CHARACTER_LABEL: "未設定の発言者がいた場合に通知する",
    TextKey.REPORT_OVER_CHARACTER_LABEL:    "Privatterの最大文字数を超えそうな時に通知する",
    TextKey.INFO_OPEN_OUTPUT_FILE_LABEL:    "ログ変換後、出力ファイルを開くかどうかの確認ダイアログを表示する",
    TextKey.IGNORE_TABS_LABEL:              "変換しないタブ設定（【,】区切りで複数入力）",
    TextKey.IGNORE_EMPTY_MESSAGE_LABEL:     "空の発言は変換を無視する",
    TextKey.COMPACT_MODE_LABEL:             "前回と同じ色の時はspanタグを省略する（コンパクトモード）",
    TextKey.CONVERT_QUOTATION_LABEL:        "【。」】を【」】に変換する",
    TextKey.CONVERT_ASTERISK_LABEL:         "【*】を【＊】に変換する",
    TextKey.CONVERT_WAVE_LABEL:             "【~】を【～】に変換する",
    TextKey.CONVERT_WEB_LOG_LABEL:          "web向けのログ変換をする",

    # キャラ設定
    TextKey.CHARACTER_LABEL:        "キャラクター",
    TextKey.CLASS_NAME_LABEL:       "class名",
    TextKey.COLOR_CODE_LABEL:       "カラーコード",
    TextKey.GROUP_LABEL:            "グループ",
    TextKey.DELETE_NAME_LABEL:      "名前削除",
    TextKey.VALID_SETTING_LABEL:    "着色有効",
    TextKey.DELETE_ROW_LABEL:       "行削除",
    TextKey.ADD_ROW_LABEL:          "行追加",
    TextKey.SWAP_ROW_LABEL:         "並び替え",

    # プレビュー
    TextKey.BACKGROUND_COLOR_LABEL: "背景色",
    TextKey.UPDATE_LOG_BUTTON:      "最新の変換後ログを表示",
    TextKey.MISSING_LOG_MESSAGE:    "（変換結果がありません）",

    # 開発者向け
    TextKey.WEB_LOG_LABEL:          "webログ",
    TextKey.IFRAME_LOG_LABEL:       "iframeログ",
    TextKey.COPY_LABEL:             "コピー",

    # ダイアログ
    TextKey.WARNING_DIALOG_TITLE:       "注意",
    TextKey.OVER_CHARACTER_MESSAGE:     "{max_character_count}文字を超えているため、ぷらいべったーに投稿できない可能性があります。",
    TextKey.UNKNOWN_CHARACTERS_MESSAGE: "以下のキャラが着色未設定です。\n\n対象：\n{unknown_characters}",

    TextKey.INFO_DIALOG_TITLE:          "お知らせ",
    TextKey.COMPLETED_CONVERT_MESSAGE:  "変換が完了しました。\n出力ファイルを開きますか？",

    TextKey.CHECK_DIALOG_TITLE:         "確認",
    TextKey.REMOVE_ROW_MESSAGE:         "行を削除しますか？",

    TextKey.ERROR_DIALOG_TITLE:         "エラー",
    TextKey.DETAIL_MESSAGE:             "詳細",
    TextKey.COLOR_CODE_ERR_MESSAGE:     "カラーコードの設定に問題があります。\n6桁のカラーコードが設定されているか確認してください。",
    TextKey.FAILED_READ_LOG_MESSAGE:    "ファイルの読み込みに失敗しました。",
    TextKey.FAILED_CONVERT_LOG_MESSAGE: "ログの変換に失敗しました。",
    TextKey.FAILED_WRITE_LOG_MESSGE:    "ファイルの保存に失敗しました",
}

