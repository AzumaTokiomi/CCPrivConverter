""" formatter.py
    機能：テキストの変換
"""
import re
from typing import List, NamedTuple

from bs4 import BeautifulSoup

from app.logic import globals
from app.model.chat import Chat, ConvertFlags
from app.model.settings import ConfigKey, ConvertLogType
from system.resources import ResourcesKey

"""
定数定義
"""
HTML_LINE_BREAK = "<br>"
HTML_SPAN_CLOSE = "</span>"
TEXT_NEWLINE = "\n"
HTML_SPAN_FOR_PRIVATTER = '<span style="color:#'
HTML_SPAN_FOR_PRIVATTER_CLOSE = ';">'
HTML_SPAN_FOR_WEB = '<span class="'
HTML_SPAN_FOR_WEB_CLOSE = '">'
HTML_STYLE = "<style>"
HTML_STYLE_CLASS = ".{class_name}{{color:#{color_code}}}"



class ConvertedLog(NamedTuple):
    """ ConvertedLog
        機能：変換処理で出力するログタイプ
    """
    privatter_log: str     # 通常変換
    web_log: str           # web用出力
    iframe_log: list       # iframe用分割



class CharacterList(NamedTuple):
    """ CharacterList
        機能：キャラクターリスト
    """
    unknown_characters: list    # 未設定の発言者リスト
    use_classes: list           # 登場した発言者リスト



def convert_log_to_chat_list(html_content: str, convert_config: dict, character_config: list) -> tuple[list[Chat], CharacterList]:
    """ convert_log_to_chat_list
        機能：HTMLのログを解析して、Chat型Listに変換する

    Args:
        html_content (str): ココフォリアのログテキスト
        convert_config (dict): 変換設定の設定値
        character_config (list): キャラ設定の設定値

    Returns:
        tuple[list[Chat], CharacterList: リスト化した発言、未設定や使用したキャラのリスト
    """
    ################
    # 変換設定
    ################
    # chatオブジェクトをこのリストに追加する
    chats = []

    # 変換無視タブの取り出し
    all_ignore_tabs = convert_config.get(ConfigKey.IGNORE_TABS, "")
    ignore_tabs = [s.strip() for s in all_ignore_tabs.split(",") if s.strip()]

    #デフォルト設定の取り出し
    for default_cfg in character_config:
        if default_cfg.get(ConfigKey.CHARACTER) == globals.RESOURCES[ResourcesKey.CHARACTER_DEFAULT_NAME]:
            break

    old_group = None            # 前回の発言のグループ
    old_color_code = None       # 前回の発言色
    unknown_characters = []     # 未設定の発言者リスト※キャラ名
    use_classes = []            # 登場した発言者リスト※クラス名

    ################
    # pタグ取得
    ################
    # HTMLを解析する
    soup = BeautifulSoup(html_content, "html.parser")

    for p_tag in soup.find_all("p", style=True):
        # style属性からcolorを抽出する
        style = p_tag.get("style")
        # color指定がない場合はスキップ
        if not style.startswith("color:"):
            continue

        # カラーコードを抽出
        color_code = style.split(":")[-1].strip(";").lstrip("#")

        # タブ、キャラ名、発言内容の3項目が無ければスキップ
        spans = p_tag.find_all("span")
        if len(spans) < 3:
            continue

        # spanタグから抽出
        tab         = spans[0].get_text().strip().strip("[]")
        character   = spans[1].get_text()

        # 改行タグを置換
        for html_message in spans[2].find_all("br"):
            html_message.replace_with(TEXT_NEWLINE)
        message = spans[2].get_text(strip=False)
        message = message.strip()

        # 初期設定
        group = default_cfg.get(ConfigKey.GROUP)
        delete_name = default_cfg.get(ConfigKey.DELETE_NAME)
        class_name = default_cfg.get(ConfigKey.CLASS_NAME)

        tmp_delete_name_flag = False

        ################
        # system発言の変換
        ################
        if character == "system":
            # [ キャラ名 ]を抽出
            match = re.search(r"\[\s*(.*?)\s*\]", message)
            if match:
                character = match.group(1)      # キャラを上書き（着色設定をキャラ名で取り出すため）
                tmp_delete_name_flag = True     # 名前削除を有効にするためのフラグ

        ################
        # 変換設定別処理
        ################
        # キャラ設定を取り出しておく
        for character_cfg in character_config:
            # キャラ設定があるキャラクターの場合（ただし、着色無効の場合は無視する）
            if character_cfg.get(ConfigKey.CHARACTER) == character and character_cfg.get(ConfigKey.ENABLE_PAINT):
                color_code = character_cfg.get(ConfigKey.COLOR_CODE)
                group = character_cfg.get(ConfigKey.GROUP)
                delete_name = character_cfg.get(ConfigKey.DELETE_NAME)
                class_name = character_cfg.get(ConfigKey.CLASS_NAME)
                break
        # キャラ設定がない場合
        else:
            # 未設定の発言者にデフォルト設定を使用する
            if convert_config.get(ConfigKey.USE_DEFAULT_SETTING):
                color_code = default_cfg.get(ConfigKey.COLOR_CODE)

            # 未設定の発言者がいた場合に通知する
            if convert_config.get(ConfigKey.REPORT_UNKNOWN_CHARACTER):
                # まだ記憶していない発言者なら、通知用に記憶
                if character not in unknown_characters:
                    unknown_characters.append(character)

        # 変換無視タブの場合、無視する
        if tab in ignore_tabs:
            continue

        # 空の発言は変換を無視する
        if convert_config.get(ConfigKey.IGNORE_EMPTY_MESSAGE):
            if message == "":
                continue

        # 【。」】を【」】に変換する
        if convert_config.get(ConfigKey.CONVERT_QUOTATION):
            message = message.replace("。」", "」")

        # 【*】を【＊】に変換する
        if convert_config.get(ConfigKey.CONVERT_ASTERISK):
            message = message.replace("*", "＊")

        # 【~】を【～】に変換する
        if convert_config.get(ConfigKey.CONVERT_WAVE):
            message = message.replace("~", "～")

        # system発言の、名前を削除するフラグ
        if tmp_delete_name_flag:
            delete_name = True

        # 使用したクラス名を保存する（重複しない）
        if class_name not in use_classes:
            use_classes.append(class_name)

        flags = ConvertFlags(
            # 前回の発言者のグループと異なる場合、先頭に改行を挿入する
            pre_indent = group != old_group and old_group is not None,
            # 名前削除の有効無効
            delete_name = delete_name,
            # 前回の発言と色が変わってないかつ、コンパクトモード時はフラグを立てる
            compact = (
                color_code == old_color_code
                and convert_config.get(ConfigKey.COMPACT_MODE)
                and old_color_code is not None
            ),
            # クラス名の設定
            class_name = class_name
        )

        # 発言リストに追加
        chats.append(Chat(
            character=character,
            color_code=color_code,
            message=message,
            convert_flags=flags
        ))

        # 前回値の保存
        old_group = group
        old_color_code = color_code

    return chats, CharacterList(unknown_characters, use_classes)


def convert_chats_to_text(chats: List[Chat], convert_config: dict) -> ConvertedLog:
    """ convert_chats_to_text
        機能：Chat型Listをテキスト表示する

    Args:
        chats (List[Chat]): 発言のリスト
        convert_config (dict): 変換設定の設定値

    Returns:
        ConvertedLog: log3種
    """
    privatter_log = ""      # 戻り値
    web_log = ""
    iframe_logs = []

    privatter_lines = []    # 作業用リストやテキスト
    web_lines = []
    iframe_text = ""

    total_len = 0           # 文字数カウント（iframe log用）

    # web用変換の有効フラグ
    enable_convert_web_log = convert_config.get(ConfigKey.CONVERT_WEB_LOG)
    pattern = re.escape(HTML_SPAN_CLOSE)    # 正規表現のためにエスケープ

    for chat in chats:
        # 変換フラグの取得
        flag = chat.convert_flags

        ################
        # 本文変換
        ################
        # 名前削除が有効の場合
        if flag.delete_name:
            text = chat.message
        else:
            text = f"{chat.character}：{chat.message}"

        line = build_line(chat, text, ConvertLogType.PRIVATTER)
        privatter_lines.append(line)

        # web用変換が有効な場合
        if enable_convert_web_log:
            #web log作成
            line = build_line(chat, text, ConvertLogType.WEB)
            web_lines.append(line)
            # iframe log作成
            line = build_line(chat, text, ConvertLogType.IFRAME)
            total_len += len(line)      # 今回の発言内容を文字数に加算する
            # iframeの最大文字数を超えている場合
            if total_len > globals.RESOURCES[ResourcesKey.IFRAME_MAX_CHARCTER]:
                iframe_text = re.sub(pattern, "", iframe_text, count=1)     # 先頭のspanタグを削除
                iframe_text += HTML_SPAN_CLOSE                              # 最後に閉じタグを追加
                iframe_logs.append(iframe_text + HTML_SPAN_CLOSE)           # 前回の読み込み行までをリストに追加

                total_len = len(line)       # 今回の文字数からカウント
                iframe_text = line          # textを今回読み込んだ内容で初期化
            else:
                iframe_text += line

    # web用変換をする場合、chatsの全変換後、iframe_textが残っている時はlogsに追加する
    if enable_convert_web_log:
        if iframe_text:
            iframe_text = re.sub(pattern, "", iframe_text, count=1)     # 先頭のspanタグを削除
            iframe_text += HTML_SPAN_CLOSE                              # 最後に閉じタグを追加
            iframe_logs.append(iframe_text + HTML_SPAN_CLOSE)           # 前回の読み込み行までをリストに追加

    ################
    # 両端の処理
    ################
    # 変換対象が存在する
    if privatter_lines:
        privatter_lines[0] = privatter_lines[0].replace(HTML_SPAN_CLOSE, "")  # 最初の行の閉じタグを削除
        privatter_lines[-1] += HTML_SPAN_CLOSE                                # 最後の行に閉じタグを追加
        privatter_log = TEXT_NEWLINE.join(privatter_lines)

        # web用変換をする場合
        if enable_convert_web_log:
            web_lines[0] = web_lines[0].replace(HTML_SPAN_CLOSE, "")          # 最初の行の閉じタグを削除
            web_lines[-1] += HTML_SPAN_CLOSE                                  # 最後の行に閉じタグを追加
            web_log = (HTML_LINE_BREAK + TEXT_NEWLINE).join(web_lines)

    return ConvertedLog(privatter_log, web_log, iframe_logs)


def build_line(chat: Chat, text: str, mode: ConvertLogType) -> str:
    """ build_line
        機能：ログタイプ別の行を作成する

    Args:
        chat (Chat): 発言設定
        text (str): 発言内容
        mode (ConvertLogType): 変換するログタイプ

    Returns:
        str: 着色設定をしたテキスト
    """
    # 変換フラグの取得
    flag = chat.convert_flags

    ################
    # タグの追加
    ################
    # web logの場合
    if mode == ConvertLogType.WEB:
        # \nを<br>\nに再置換
        text = text.replace(TEXT_NEWLINE, HTML_LINE_BREAK + TEXT_NEWLINE)
    # iframe logの場合
    elif mode == ConvertLogType.IFRAME:
        # \nを<br>に再置換
        text = text.replace(TEXT_NEWLINE, HTML_LINE_BREAK)

    # コンパクト有効
    if flag.compact:
        line = text
    # コンパクト無効
    else:
        if mode == ConvertLogType.PRIVATTER:
            line = f'{HTML_SPAN_CLOSE}{HTML_SPAN_FOR_PRIVATTER}{chat.color_code}{HTML_SPAN_FOR_PRIVATTER_CLOSE}{text}'
        elif mode == ConvertLogType.WEB:
            line = f'{HTML_SPAN_CLOSE}{HTML_SPAN_FOR_WEB}{flag.class_name}{HTML_SPAN_FOR_WEB_CLOSE}{text}'
        elif mode == ConvertLogType.IFRAME:
            line = f'{HTML_SPAN_CLOSE}{HTML_SPAN_FOR_WEB}{flag.class_name}{HTML_SPAN_FOR_WEB_CLOSE}{text}{HTML_LINE_BREAK}'

    ################
    # その他変換
    ################
    # 前のテキストから改行する場合
    if flag.pre_indent:
        if mode == ConvertLogType.PRIVATTER:
            line = TEXT_NEWLINE + line
        elif mode == ConvertLogType.WEB:
            line = HTML_LINE_BREAK + TEXT_NEWLINE + line
        elif mode == ConvertLogType.IFRAME:
            line = HTML_LINE_BREAK + line

    return line


def  create_style_tag_text(character_config: list, use_classes: list) -> str:
    """ create_style_tag_text
        機能：styleタグの中身を作成する

    Args:
        character_config (list): キャラ設定の設定値
        use_characters (list): 使用クラスのリスト

    Returns:
        str: styleタグのテキスト
    """
    style_tag_text = HTML_STYLE + globals.RESOURCES[ResourcesKey.WEB_STYLE_BASE]

    # 使用したクラスを、キャラ設定から抽出してカラーコードと紐づける
    for chara_class in use_classes:
        for character_cfg in character_config:
            if chara_class == character_cfg.get(ConfigKey.CLASS_NAME):
                style_tag_text += HTML_STYLE_CLASS.format(
                    class_name=chara_class,
                    color_code=character_cfg.get(ConfigKey.COLOR_CODE)
                )
                break

    return style_tag_text
