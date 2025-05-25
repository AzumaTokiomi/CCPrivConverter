""" chat.py
    機能：chatオブジェクト（ココフォリアのログ構造）
"""
from dataclasses import dataclass


@dataclass
class ConvertFlags:
    pre_indent: bool                # 改行
    delete_name: bool               # 名前削除
    compact: bool                   # コンパクト化するか
    class_name: str                 # クラス名



@dataclass
class Chat:
#    tab:            str            # 発言タブ
                                    # 発言毎に保持する必要がない（出力しない）ためコメントアウト
    character:      str             # 発言者
    color_code:     str             # カラーコード
    message:        str             # 発言内容
    convert_flags:  ConvertFlags    # 変換フラグ
