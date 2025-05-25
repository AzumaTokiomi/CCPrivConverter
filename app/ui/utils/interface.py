
import tkinter as tk


def on_mousewheel(canvas, event):
    """ _on_mousewheel
        ホイール：マウスホイール動作
    """
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def update_scrollregion(canvas, frame, event=None):
    """ update_scrollregion
        機能：scrollregion の高さ（y2）を、キャンバス自身の高さ以下にはしないように制限する
    """
    bbox = canvas.bbox("all")
    if bbox:
        x1, y1, x2, y2 = bbox
        min_height = canvas.winfo_height()
        y2 = max(y2, min_height)
        canvas.configure(scrollregion=(x1, y1, x2, y2))


def update_canvas_width(canvas, event, tag="frame_window"):
    """ update_canvas_width
        機能：キャンバスの横幅を更新する
    """
    canvas.itemconfig(tag, width=event.width)

def bind_canvas_mousewheel(canvas):
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

def unbind_canvas_mousewheel(canvas):
    canvas.unbind_all("<MouseWheel>")

def copy_text_to_clipboard(widget: tk.Widget, text_widget: tk.Text):
    text = text_widget.get("1.0", "end-1c")
    widget.clipboard_clear()
    widget.clipboard_append(text)
